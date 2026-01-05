#!/usr/bin/env python3
"""
Convert cleaned Hassania dataset to OpenAI fine-tuning format.
Focus on conversational, practical dialect usage.
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
    
    # Improved system message focusing on conversational Hassania
    system_content = """You are a native Hassania (Hassaniya) Arabic speaker from Mauritania. You speak the authentic Hassania dialect, not Modern Standard Arabic or other dialects.

Key Hassania features you use:
- Unique vocabulary different from MSA
- Specific verb conjugations and grammar patterns  
- Common expressions and greetings used in Mauritania
- Both Arabic script and romanized transcription when helpful

You help with translations, vocabulary, grammar explanations, and natural conversation in Hassania."""

    return {
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": output}
        ]
    }

def main():
    input_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/cleaned")
    output_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/openai_cleaned")
    output_dir.mkdir(exist_ok=True)
    
    print("Loading cleaned datasets...")
    train_samples = load_jsonl(input_dir / "hassania_train_cleaned.jsonl")
    val_samples = load_jsonl(input_dir / "hassania_val_cleaned.jsonl")
    
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
    
    # Create different sized datasets
    random.seed(42)
    
    # Full cleaned dataset
    with open(output_dir / "hassania_train_cleaned_full.jsonl", 'w', encoding='utf-8') as f:
        for sample in openai_train:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    with open(output_dir / "hassania_val_cleaned.jsonl", 'w', encoding='utf-8') as f:
        for sample in openai_val:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Curated subset (2000 samples) - balanced across tasks
    task_samples = {}
    for i, sample in enumerate(train_samples):
        task = sample.get('task', 'unknown')
        if task not in task_samples:
            task_samples[task] = []
        task_samples[task].append(i)
    
    curated_indices = []
    target_size = 2000
    
    # Prioritize translation and dialect examples
    priority_tasks = ['translation_en_to_hassania', 'translation_hassania_to_en', 
                      'dialect_example', 'vocabulary', 'grammar_example',
                      'hassaniya_romanized', 'vocabulary_romanized']
    
    for task in priority_tasks:
        if task in task_samples:
            indices = task_samples[task]
            n_take = min(len(indices), target_size // len(priority_tasks))
            curated_indices.extend(random.sample(indices, n_take))
    
    # Fill remaining with other tasks
    remaining = target_size - len(curated_indices)
    other_indices = []
    for task, indices in task_samples.items():
        if task not in priority_tasks:
            other_indices.extend(indices)
    
    if remaining > 0 and other_indices:
        curated_indices.extend(random.sample(other_indices, min(remaining, len(other_indices))))
    
    random.shuffle(curated_indices)
    curated_samples = [openai_train[i] for i in curated_indices[:target_size]]
    
    with open(output_dir / "hassania_train_cleaned_curated.jsonl", 'w', encoding='utf-8') as f:
        for sample in curated_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Print statistics
    print(f"\n{'='*50}")
    print("CONVERSION COMPLETE")
    print(f"{'='*50}")
    print(f"\nOutput files in: {output_dir}")
    print(f"  - hassania_train_cleaned_full.jsonl: {len(openai_train)} samples")
    print(f"  - hassania_val_cleaned.jsonl: {len(openai_val)} samples")
    print(f"  - hassania_train_cleaned_curated.jsonl: {len(curated_samples)} samples")
    
    # Check file sizes
    for f in output_dir.glob("*.jsonl"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()
