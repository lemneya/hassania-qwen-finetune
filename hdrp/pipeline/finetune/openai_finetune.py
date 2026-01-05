#!/usr/bin/env python3
"""
OpenAI Fine-Tuning Script for Hassaniya
Converts HDRP SFT format to OpenAI format and starts fine-tuning job.
"""

import json
import os
from pathlib import Path
from openai import OpenAI

# Paths
BASE_DIR = Path("/tmp/hassania-qwen-finetune-main")
SFT_FILE = BASE_DIR / "hdrp/data/processed/exports/sft/sft_hassaniya_v2.jsonl"
EVAL_FILE = BASE_DIR / "hdrp/data/processed/exports/eval/eval_hassaniya_v2.jsonl"
OUTPUT_DIR = BASE_DIR / "hdrp/data/processed/exports/openai"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def convert_to_openai_format(input_file: Path, output_file: Path) -> int:
    """Convert HDRP SFT format to OpenAI fine-tuning format."""
    records = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                messages = data.get("messages", [])
                
                # OpenAI format only needs messages array
                # Remove meta field for training
                openai_record = {"messages": messages}
                records.append(openai_record)
            except:
                pass
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(records)

def validate_format(file_path: Path) -> dict:
    """Validate OpenAI fine-tuning format."""
    errors = []
    warnings = []
    total = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            total += 1
            try:
                data = json.loads(line)
                messages = data.get("messages", [])
                
                if not messages:
                    errors.append(f"Line {i}: No messages")
                    continue
                
                roles = [m.get("role") for m in messages]
                
                # Check for required roles
                if "assistant" not in roles:
                    errors.append(f"Line {i}: No assistant message")
                
                # Check message structure
                for j, msg in enumerate(messages):
                    if "role" not in msg:
                        errors.append(f"Line {i}, msg {j}: Missing role")
                    if "content" not in msg:
                        errors.append(f"Line {i}, msg {j}: Missing content")
                    elif not msg["content"].strip():
                        warnings.append(f"Line {i}, msg {j}: Empty content")
                        
            except json.JSONDecodeError:
                errors.append(f"Line {i}: Invalid JSON")
    
    return {
        "total": total,
        "errors": len(errors),
        "warnings": len(warnings),
        "error_details": errors[:10],  # First 10 errors
        "valid": len(errors) == 0
    }

def start_finetune_job(train_file: Path, val_file: Path = None):
    """Upload files and start OpenAI fine-tuning job."""
    client = OpenAI()
    
    print("\n[1] Uploading training file...")
    with open(train_file, 'rb') as f:
        train_response = client.files.create(file=f, purpose="fine-tune")
    print(f"    Training file ID: {train_response.id}")
    
    val_file_id = None
    if val_file and val_file.exists():
        print("\n[2] Uploading validation file...")
        with open(val_file, 'rb') as f:
            val_response = client.files.create(file=f, purpose="fine-tune")
        val_file_id = val_response.id
        print(f"    Validation file ID: {val_file_id}")
    
    print("\n[3] Starting fine-tuning job...")
    
    # Create fine-tuning job
    job_params = {
        "training_file": train_response.id,
        "model": "gpt-4o-mini-2024-07-18",
        "suffix": "hassaniya-v1",
        "hyperparameters": {
            "n_epochs": 3
        }
    }
    
    if val_file_id:
        job_params["validation_file"] = val_file_id
    
    job = client.fine_tuning.jobs.create(**job_params)
    
    print(f"\n{'='*60}")
    print("FINE-TUNING JOB STARTED")
    print(f"{'='*60}")
    print(f"Job ID: {job.id}")
    print(f"Model: {job.model}")
    print(f"Status: {job.status}")
    print(f"Created: {job.created_at}")
    
    # Save job info
    job_info = {
        "job_id": job.id,
        "model": job.model,
        "status": job.status,
        "training_file": train_response.id,
        "validation_file": val_file_id,
        "created_at": job.created_at,
        "hyperparameters": job_params["hyperparameters"]
    }
    
    job_file = OUTPUT_DIR / "finetune_job.json"
    with open(job_file, 'w') as f:
        json.dump(job_info, f, indent=2, default=str)
    
    print(f"\nJob info saved to: {job_file}")
    print(f"\nMonitor progress with:")
    print(f"  python3 -c \"from openai import OpenAI; c=OpenAI(); print(c.fine_tuning.jobs.retrieve('{job.id}'))\"")
    
    return job

def main():
    print("="*60)
    print("OPENAI FINE-TUNING FOR HASSANIYA")
    print("="*60)
    
    # Convert to OpenAI format
    print("\n[Step 1] Converting HDRP SFT to OpenAI format...")
    
    train_output = OUTPUT_DIR / "hassaniya_train_openai.jsonl"
    val_output = OUTPUT_DIR / "hassaniya_val_openai.jsonl"
    
    train_count = convert_to_openai_format(SFT_FILE, train_output)
    print(f"  Training: {train_count} records -> {train_output}")
    
    val_count = convert_to_openai_format(EVAL_FILE, val_output)
    print(f"  Validation: {val_count} records -> {val_output}")
    
    # Validate format
    print("\n[Step 2] Validating format...")
    
    train_validation = validate_format(train_output)
    print(f"  Training: {train_validation['total']} records, {train_validation['errors']} errors")
    
    val_validation = validate_format(val_output)
    print(f"  Validation: {val_validation['total']} records, {val_validation['errors']} errors")
    
    if not train_validation['valid']:
        print("\n  Errors found:")
        for err in train_validation['error_details']:
            print(f"    - {err}")
        print("\n  Fixing errors...")
        
        # Filter out invalid records
        valid_records = []
        with open(train_output, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    messages = data.get("messages", [])
                    roles = [m.get("role") for m in messages]
                    
                    # Must have assistant and all messages must have content
                    if "assistant" in roles:
                        valid = True
                        for msg in messages:
                            if not msg.get("content", "").strip():
                                valid = False
                                break
                        if valid:
                            valid_records.append(data)
                except:
                    pass
        
        with open(train_output, 'w', encoding='utf-8') as f:
            for record in valid_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"  Filtered to {len(valid_records)} valid records")
    
    # Start fine-tuning
    print("\n[Step 3] Starting OpenAI fine-tuning job...")
    
    try:
        job = start_finetune_job(train_output, val_output)
        return job
    except Exception as e:
        print(f"\nError starting fine-tuning: {e}")
        return None

if __name__ == "__main__":
    main()
