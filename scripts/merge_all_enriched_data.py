#!/usr/bin/env python3
"""
Merge all enriched Hassania data including books into final dataset.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def load_jsonl(filepath):
    """Load JSONL file."""
    samples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    samples.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return samples

def save_jsonl(samples, filepath):
    """Save samples to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

def main():
    base_dir = Path("/home/ubuntu/hassania-qwen-finetune")
    
    # Load existing enriched dataset
    existing_train = base_dir / "data/final/hassania_train.jsonl"
    existing_val = base_dir / "data/final/hassania_val.jsonl"
    
    all_samples = []
    
    # Load existing training data
    if existing_train.exists():
        existing_samples = load_jsonl(existing_train)
        print(f"Loaded {len(existing_samples)} existing training samples")
        all_samples.extend(existing_samples)
    
    # Load book training samples
    books_samples_file = base_dir / "data/enrichment/books_processed/books_training_samples.jsonl"
    if books_samples_file.exists():
        books_samples = load_jsonl(books_samples_file)
        print(f"Loaded {len(books_samples)} book training samples")
        all_samples.extend(books_samples)
    
    # Load synthetic data
    synthetic_file = base_dir / "data/enrichment/synthetic/synthetic_hassania.jsonl"
    if synthetic_file.exists():
        synthetic_samples = load_jsonl(synthetic_file)
        print(f"Loaded {len(synthetic_samples)} synthetic samples")
        # Don't add duplicates
        existing_outputs = set(s.get('output', '')[:100] for s in all_samples)
        new_synthetic = [s for s in synthetic_samples if s.get('output', '')[:100] not in existing_outputs]
        all_samples.extend(new_synthetic)
        print(f"Added {len(new_synthetic)} new synthetic samples")
    
    # Deduplicate by output
    seen_outputs = set()
    unique_samples = []
    for sample in all_samples:
        output_key = sample.get('output', '')[:200]
        if output_key and output_key not in seen_outputs:
            seen_outputs.add(output_key)
            unique_samples.append(sample)
    
    print(f"\nAfter deduplication: {len(unique_samples)} unique samples")
    
    # Split into train/val (95/5)
    import random
    random.seed(42)
    random.shuffle(unique_samples)
    
    val_size = max(100, int(len(unique_samples) * 0.05))
    train_samples = unique_samples[val_size:]
    val_samples = unique_samples[:val_size]
    
    # Save final datasets
    final_dir = base_dir / "data/final_enriched"
    final_dir.mkdir(exist_ok=True)
    
    save_jsonl(train_samples, final_dir / "hassania_train.jsonl")
    save_jsonl(val_samples, final_dir / "hassania_val.jsonl")
    
    # Calculate statistics
    task_counts = defaultdict(int)
    source_counts = defaultdict(int)
    
    for sample in unique_samples:
        task = sample.get('task', 'unknown')
        source = sample.get('source', 'unknown')
        task_counts[task] += 1
        source_counts[source] += 1
    
    # Save statistics
    stats = {
        "total_samples": len(unique_samples),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "task_distribution": dict(task_counts),
        "source_distribution": dict(source_counts)
    }
    
    with open(final_dir / "dataset_statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # Create combined corpus
    corpus_texts = set()
    for sample in unique_samples:
        output = sample.get('output', '')
        if output and len(output) > 20:
            corpus_texts.add(output)
    
    with open(final_dir / "hassania_corpus.txt", 'w', encoding='utf-8') as f:
        for text in corpus_texts:
            f.write(text + '\n')
    
    print(f"\n{'='*60}")
    print("FINAL ENRICHED DATASET CREATED")
    print(f"{'='*60}")
    print(f"Total unique samples: {len(unique_samples)}")
    print(f"Training samples: {len(train_samples)}")
    print(f"Validation samples: {len(val_samples)}")
    print(f"Unique corpus texts: {len(corpus_texts)}")
    print(f"\nTask distribution:")
    for task, count in sorted(task_counts.items(), key=lambda x: -x[1]):
        print(f"  {task}: {count}")
    print(f"\nSource distribution:")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")
    print(f"\nOutput saved to: {final_dir}")

if __name__ == "__main__":
    main()
