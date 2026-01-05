#!/usr/bin/env python3
"""
Upload cleaned dataset and create OpenAI fine-tuning job for Hassania dialect.
Uses poetry-free, conversational data only.
"""

import os
import json
import time
from openai import OpenAI

def main():
    client = OpenAI()
    
    # Path to cleaned training file
    training_file_path = "/home/ubuntu/hassania-qwen-finetune/data/openai_cleaned/hassania_train_cleaned_curated.jsonl"
    validation_file_path = "/home/ubuntu/hassania-qwen-finetune/data/openai_cleaned/hassania_val_cleaned.jsonl"
    
    print("="*60)
    print("OPENAI HASSANIA FINE-TUNING (CLEANED DATA)")
    print("="*60)
    print("Dataset: Poetry removed, conversational data only")
    print("Training samples: 2,000 curated")
    
    # Step 1: Upload training file
    print("\n[1/4] Uploading cleaned training file...")
    with open(training_file_path, "rb") as f:
        training_file = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    print(f"  Training file uploaded: {training_file.id}")
    
    # Step 2: Upload validation file
    print("\n[2/4] Uploading cleaned validation file...")
    with open(validation_file_path, "rb") as f:
        validation_file = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    print(f"  Validation file uploaded: {validation_file.id}")
    
    # Wait for files to be processed
    print("\n[3/4] Waiting for files to be processed...")
    for file_obj in [training_file, validation_file]:
        while True:
            file_status = client.files.retrieve(file_obj.id)
            if file_status.status == "processed":
                print(f"  File {file_obj.id} processed successfully")
                break
            elif file_status.status == "error":
                print(f"  Error processing file {file_obj.id}")
                return
            time.sleep(5)
    
    # Step 3: Create fine-tuning job
    print("\n[4/4] Creating fine-tuning job...")
    
    fine_tune_job = client.fine_tuning.jobs.create(
        training_file=training_file.id,
        validation_file=validation_file.id,
        model="gpt-4o-mini-2024-07-18",
        suffix="hassania-v2",
        hyperparameters={
            "n_epochs": 3,
            "batch_size": "auto",
            "learning_rate_multiplier": "auto"
        }
    )
    
    print(f"\n{'='*60}")
    print("FINE-TUNING JOB CREATED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"\nJob ID: {fine_tune_job.id}")
    print(f"Model: {fine_tune_job.model}")
    print(f"Status: {fine_tune_job.status}")
    print(f"Training file: {fine_tune_job.training_file}")
    print(f"Validation file: {fine_tune_job.validation_file}")
    
    # Save job info
    job_info = {
        "job_id": fine_tune_job.id,
        "model": fine_tune_job.model,
        "status": fine_tune_job.status,
        "training_file": fine_tune_job.training_file,
        "validation_file": fine_tune_job.validation_file,
        "created_at": fine_tune_job.created_at,
        "version": "v2-cleaned",
        "notes": "Poetry removed, conversational data only, 2000 curated samples"
    }
    
    with open("/home/ubuntu/hassania-qwen-finetune/finetune_job_v2_info.json", "w") as f:
        json.dump(job_info, f, indent=2, default=str)
    
    print(f"\nJob info saved to: finetune_job_v2_info.json")
    
    return fine_tune_job.id

if __name__ == "__main__":
    main()
