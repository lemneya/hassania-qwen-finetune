#!/usr/bin/env python3
"""
Clean the Hassania dataset by removing poetry and non-conversational content.
Focus on practical, conversational Hassania dialect data.
"""

import json
from pathlib import Path
from collections import Counter

def load_jsonl(filepath):
    """Load JSONL file."""
    samples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples

def is_poetry_or_literary(sample):
    """Check if sample is poetry or literary content to exclude."""
    task = sample.get('task', '').lower()
    source = sample.get('source', '').lower()
    instruction = sample.get('instruction', '').lower()
    output = sample.get('output', '')
    
    # Exclude poetry-related tasks
    poetry_indicators = [
        'poetry', 'poem', 'لغن', 'diwan', 'ديوان',
        'verse', 'rhyme', 'شعر', 'قصيدة'
    ]
    
    for indicator in poetry_indicators:
        if indicator in task or indicator in source or indicator in instruction:
            return True
    
    # Exclude literary/book sources that aren't practical
    literary_sources = [
        'diwan', 'poetry', 'aesthetics', 'jamaliyat',
        'mrug_alharf', 'linguistic'
    ]
    
    for src in literary_sources:
        if src in source:
            return True
    
    # Exclude synthetic poetry
    if 'synthetic_poetry' in task or 'synthetic_stories' in task:
        return True
    
    return False

def is_good_conversational(sample):
    """Check if sample is good conversational/practical content."""
    task = sample.get('task', '').lower()
    source = sample.get('source', '').lower()
    output = sample.get('output', '')
    
    # Keep these task types
    good_tasks = [
        'translation', 'dialect_example', 'vocabulary',
        'grammar', 'greeting', 'conversation',
        'sentiment', 'hassaniya_romanized'
    ]
    
    for good in good_tasks:
        if good in task:
            return True
    
    # Keep Peace Corps materials (practical language learning)
    if 'peace corps' in source or 'dliflc' in source:
        return True
    
    # Keep DAH dataset (bilingual translations)
    if 'dah' in source:
        return True
    
    # Keep Casablanca (speech transcriptions)
    if 'casablanca' in source:
        return True
    
    # Keep dictionary entries
    if 'dictionary' in source or 'vocabulary' in task:
        return True
    
    # Keep sentiment data (social media - real dialect usage)
    if 'sentiment' in source or 'sentiment' in task:
        return True
    
    # Keep speech transcriptions
    if 'speech' in source:
        return True
    
    return False

def clean_sample(sample):
    """Clean and improve sample quality."""
    # Remove samples with very short outputs
    output = sample.get('output', '')
    if len(output.strip()) < 3:
        return None
    
    # Remove samples with empty instructions
    instruction = sample.get('instruction', '')
    if not instruction.strip():
        return None
    
    return sample

def main():
    input_file = Path("/home/ubuntu/hassania-qwen-finetune/data/final_with_peace_corps/hassania_train.jsonl")
    val_file = Path("/home/ubuntu/hassania-qwen-finetune/data/final_with_peace_corps/hassania_val.jsonl")
    output_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/cleaned")
    output_dir.mkdir(exist_ok=True)
    
    print("Loading datasets...")
    train_samples = load_jsonl(input_file)
    val_samples = load_jsonl(val_file)
    
    print(f"Original train samples: {len(train_samples)}")
    print(f"Original val samples: {len(val_samples)}")
    
    # Analyze current task distribution
    print("\n=== ORIGINAL TASK DISTRIBUTION ===")
    task_counts = Counter(s.get('task', 'unknown') for s in train_samples)
    for task, count in task_counts.most_common():
        print(f"  {task}: {count}")
    
    print("\n=== ORIGINAL SOURCE DISTRIBUTION ===")
    source_counts = Counter(s.get('source', 'unknown') for s in train_samples)
    for source, count in source_counts.most_common():
        print(f"  {source}: {count}")
    
    # Filter samples
    print("\n=== CLEANING DATASET ===")
    
    cleaned_train = []
    removed_poetry = 0
    removed_other = 0
    
    for sample in train_samples:
        if is_poetry_or_literary(sample):
            removed_poetry += 1
            continue
        
        cleaned = clean_sample(sample)
        if cleaned is None:
            removed_other += 1
            continue
        
        if is_good_conversational(sample):
            cleaned_train.append(cleaned)
        else:
            removed_other += 1
    
    print(f"Removed poetry/literary: {removed_poetry}")
    print(f"Removed other (low quality): {removed_other}")
    print(f"Kept samples: {len(cleaned_train)}")
    
    # Clean validation set
    cleaned_val = []
    for sample in val_samples:
        if is_poetry_or_literary(sample):
            continue
        cleaned = clean_sample(sample)
        if cleaned and is_good_conversational(sample):
            cleaned_val.append(cleaned)
    
    print(f"Cleaned validation samples: {len(cleaned_val)}")
    
    # Show new distribution
    print("\n=== CLEANED TASK DISTRIBUTION ===")
    task_counts = Counter(s.get('task', 'unknown') for s in cleaned_train)
    for task, count in task_counts.most_common():
        print(f"  {task}: {count}")
    
    print("\n=== CLEANED SOURCE DISTRIBUTION ===")
    source_counts = Counter(s.get('source', 'unknown') for s in cleaned_train)
    for source, count in source_counts.most_common():
        print(f"  {source}: {count}")
    
    # Save cleaned datasets
    with open(output_dir / "hassania_train_cleaned.jsonl", 'w', encoding='utf-8') as f:
        for sample in cleaned_train:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    with open(output_dir / "hassania_val_cleaned.jsonl", 'w', encoding='utf-8') as f:
        for sample in cleaned_val:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Save statistics
    stats = {
        "original_train": len(train_samples),
        "original_val": len(val_samples),
        "cleaned_train": len(cleaned_train),
        "cleaned_val": len(cleaned_val),
        "removed_poetry": removed_poetry,
        "removed_other": removed_other,
        "task_distribution": dict(task_counts),
        "source_distribution": dict(source_counts)
    }
    
    with open(output_dir / "cleaning_stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== CLEANING COMPLETE ===")
    print(f"Output: {output_dir}")
    print(f"Train: {len(cleaned_train)} samples")
    print(f"Val: {len(cleaned_val)} samples")

if __name__ == "__main__":
    main()
