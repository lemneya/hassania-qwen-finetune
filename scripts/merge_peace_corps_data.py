#!/usr/bin/env python3
"""
Merge Peace Corps Hassaniya data into the final enriched dataset.
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

def save_jsonl(samples, filepath):
    """Save samples to JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

def main():
    # Paths
    final_enriched_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/final_enriched")
    peace_corps_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/enrichment/peace_corps_processed")
    output_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/final_with_peace_corps")
    output_dir.mkdir(exist_ok=True)
    
    # Load existing enriched dataset
    print("Loading existing enriched dataset...")
    existing_train = load_jsonl(final_enriched_dir / "hassania_train.jsonl")
    existing_val = load_jsonl(final_enriched_dir / "hassania_val.jsonl")
    print(f"  Existing train samples: {len(existing_train)}")
    print(f"  Existing val samples: {len(existing_val)}")
    
    # Load Peace Corps data
    print("\nLoading Peace Corps data...")
    peace_corps_samples = load_jsonl(peace_corps_dir / "peace_corps_training_samples.jsonl")
    print(f"  Peace Corps samples: {len(peace_corps_samples)}")
    
    # Combine all samples
    all_samples = existing_train + existing_val + peace_corps_samples
    
    # Deduplicate based on output text
    seen_outputs = set()
    unique_samples = []
    for sample in all_samples:
        output_key = sample.get('output', '')[:200]
        if output_key and output_key not in seen_outputs:
            seen_outputs.add(output_key)
            unique_samples.append(sample)
    
    print(f"\nTotal unique samples after merge: {len(unique_samples)}")
    
    # Split into train/val (95/5)
    import random
    random.seed(42)
    random.shuffle(unique_samples)
    
    val_size = int(len(unique_samples) * 0.05)
    val_samples = unique_samples[:val_size]
    train_samples = unique_samples[val_size:]
    
    print(f"Train samples: {len(train_samples)}")
    print(f"Validation samples: {len(val_samples)}")
    
    # Save new datasets
    save_jsonl(train_samples, output_dir / "hassania_train.jsonl")
    save_jsonl(val_samples, output_dir / "hassania_val.jsonl")
    
    # Create corpus file
    corpus_texts = set()
    for sample in unique_samples:
        if sample.get('output'):
            corpus_texts.add(sample['output'])
        if sample.get('input'):
            corpus_texts.add(sample['input'])
    
    with open(output_dir / "hassania_corpus.txt", 'w', encoding='utf-8') as f:
        for text in corpus_texts:
            f.write(text + '\n')
    
    # Calculate statistics
    task_counts = Counter(s.get('task', 'unknown') for s in unique_samples)
    source_counts = Counter(s.get('source', 'unknown') for s in unique_samples)
    
    stats = {
        "total_samples": len(unique_samples),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "unique_corpus_texts": len(corpus_texts),
        "task_distribution": dict(task_counts),
        "source_distribution": dict(source_counts)
    }
    
    with open(output_dir / "dataset_statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print("MERGE COMPLETE")
    print(f"{'='*50}")
    print(f"Total unique samples: {stats['total_samples']}")
    print(f"Train: {stats['train_samples']}, Val: {stats['val_samples']}")
    print(f"Unique corpus texts: {stats['unique_corpus_texts']}")
    print(f"\nTask distribution:")
    for task, count in sorted(task_counts.items(), key=lambda x: -x[1]):
        print(f"  {task}: {count}")
    print(f"\nSource distribution:")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")
    print(f"\nOutput saved to: {output_dir}")

if __name__ == "__main__":
    main()
