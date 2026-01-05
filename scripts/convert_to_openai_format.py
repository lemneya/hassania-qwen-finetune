#!/usr/bin/env python3
"""
Convert Hassania dataset to OpenAI fine-tuning format.
OpenAI requires chat completion format with messages array.
"""

import json
from pathlib import Path
import random

def load_jsonl(filepath):
    """Load JSONL file."""
    samples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples

def convert_to_openai_format(sample):
    """Convert a single sample to OpenAI chat format."""
    instruction = sample.get('instruction', '')
    input_text = sample.get('input', '')
    output = sample.get('output', '')
    
    # Create user message
    if input_text:
        user_content = f"{instruction}\n\n{input_text}"
    else:
        user_content = instruction
    
    # OpenAI chat format
    return {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant specialized in the Hassania (Hassaniya) Arabic dialect spoken in Mauritania and Western Sahara. You can translate between English and Hassania, generate Hassania text, explain grammar, and help with vocabulary."
            },
            {
                "role": "user",
                "content": user_content
            },
            {
                "role": "assistant",
                "content": output
            }
        ]
    }

def main():
    # Paths
    input_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/final_with_peace_corps")
    output_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/openai_format")
    output_dir.mkdir(exist_ok=True)
    
    # Load training data
    print("Loading training data...")
    train_samples = load_jsonl(input_dir / "hassania_train.jsonl")
    val_samples = load_jsonl(input_dir / "hassania_val.jsonl")
    
    print(f"Loaded {len(train_samples)} training samples")
    print(f"Loaded {len(val_samples)} validation samples")
    
    # Convert to OpenAI format
    print("\nConverting to OpenAI format...")
    
    openai_train = []
    openai_val = []
    
    for sample in train_samples:
        if sample.get('output') and len(sample.get('output', '')) > 2:
            converted = convert_to_openai_format(sample)
            openai_train.append(converted)
    
    for sample in val_samples:
        if sample.get('output') and len(sample.get('output', '')) > 2:
            converted = convert_to_openai_format(sample)
            openai_val.append(converted)
    
    print(f"Converted {len(openai_train)} training samples")
    print(f"Converted {len(openai_val)} validation samples")
    
    # OpenAI has limits on fine-tuning data size
    # For gpt-4o-mini: max ~50MB, recommended 50-100 examples minimum
    # Let's create different sized datasets
    
    # Full dataset
    with open(output_dir / "hassania_train_full.jsonl", 'w', encoding='utf-8') as f:
        for sample in openai_train:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    with open(output_dir / "hassania_val_full.jsonl", 'w', encoding='utf-8') as f:
        for sample in openai_val:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Smaller curated dataset (1000 samples) - good for initial fine-tuning
    random.seed(42)
    
    # Prioritize diverse task types
    task_samples = {}
    for sample in train_samples:
        task = sample.get('task', 'unknown')
        if task not in task_samples:
            task_samples[task] = []
        task_samples[task].append(sample)
    
    # Sample proportionally from each task
    curated_samples = []
    target_size = 1000
    
    for task, samples in task_samples.items():
        # Take proportional samples, minimum 10 per task
        n_samples = max(10, int(len(samples) / len(train_samples) * target_size))
        n_samples = min(n_samples, len(samples))
        curated_samples.extend(random.sample(samples, n_samples))
    
    # Shuffle and limit to target size
    random.shuffle(curated_samples)
    curated_samples = curated_samples[:target_size]
    
    # Convert curated samples
    openai_curated = [convert_to_openai_format(s) for s in curated_samples if s.get('output')]
    
    with open(output_dir / "hassania_train_curated.jsonl", 'w', encoding='utf-8') as f:
        for sample in openai_curated:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Mini dataset (100 samples) - for quick testing
    mini_samples = random.sample(curated_samples, min(100, len(curated_samples)))
    openai_mini = [convert_to_openai_format(s) for s in mini_samples if s.get('output')]
    
    with open(output_dir / "hassania_train_mini.jsonl", 'w', encoding='utf-8') as f:
        for sample in openai_mini:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Print statistics
    print(f"\n{'='*50}")
    print("CONVERSION COMPLETE")
    print(f"{'='*50}")
    print(f"\nOutput files in: {output_dir}")
    print(f"  - hassania_train_full.jsonl: {len(openai_train)} samples")
    print(f"  - hassania_val_full.jsonl: {len(openai_val)} samples")
    print(f"  - hassania_train_curated.jsonl: {len(openai_curated)} samples")
    print(f"  - hassania_train_mini.jsonl: {len(openai_mini)} samples")
    
    # Check file sizes
    for f in output_dir.glob("*.jsonl"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()
