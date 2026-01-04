#!/usr/bin/env python3
"""
Merge all enriched data sources into a unified dataset for fine-tuning.
"""

import os
import json
import random
from pathlib import Path
from collections import Counter

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
ENRICHMENT_DIR = DATA_DIR / "enrichment"
OUTPUT_DIR = DATA_DIR / "final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_jsonl(filepath):
    """Load samples from a JSONL file."""
    samples = []
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    samples.append(json.loads(line))
                except:
                    continue
    return samples


def deduplicate_samples(samples):
    """Remove duplicate samples based on output text."""
    seen = set()
    unique = []
    for sample in samples:
        output = sample.get('output', '').strip()
        if output and output not in seen:
            seen.add(output)
            unique.append(sample)
    return unique


def main():
    print("\n" + "#"*60)
    print("# MERGING ALL HASSANIA DATA SOURCES")
    print("#"*60)
    
    all_samples = []
    
    # 1. Load original processed data
    print("\n1. Loading original processed data...")
    original_file = PROCESSED_DIR / "hassania_combined.jsonl"
    original_samples = load_jsonl(original_file)
    print(f"   ✓ Loaded {len(original_samples)} samples from original dataset")
    all_samples.extend(original_samples)
    
    # 2. Load book/literature data
    print("\n2. Loading book/literature data...")
    books_file = ENRICHMENT_DIR / "processed_books" / "books_samples.jsonl"
    books_samples = load_jsonl(books_file)
    print(f"   ✓ Loaded {len(books_samples)} samples from books")
    all_samples.extend(books_samples)
    
    # 3. Load synthetic data
    print("\n3. Loading synthetic data...")
    synthetic_file = ENRICHMENT_DIR / "synthetic" / "synthetic_hassania.jsonl"
    synthetic_samples = load_jsonl(synthetic_file)
    print(f"   ✓ Loaded {len(synthetic_samples)} samples from synthetic generation")
    all_samples.extend(synthetic_samples)
    
    # 4. Load YouTube transcripts (if any)
    print("\n4. Loading YouTube transcripts...")
    youtube_file = ENRICHMENT_DIR / "youtube" / "youtube_transcripts.json"
    if youtube_file.exists():
        with open(youtube_file, 'r', encoding='utf-8') as f:
            youtube_data = json.load(f)
        youtube_samples = []
        for item in youtube_data:
            text = item.get('text', '')
            if text and len(text) > 20:
                youtube_samples.append({
                    "instruction": "This is Hassania Arabic from a Mauritanian video:",
                    "input": "",
                    "output": text,
                    "source": "youtube_transcript",
                    "task": "dialect_example"
                })
        print(f"   ✓ Loaded {len(youtube_samples)} samples from YouTube")
        all_samples.extend(youtube_samples)
    else:
        print("   ✗ No YouTube transcripts available")
    
    print(f"\nTotal samples before deduplication: {len(all_samples)}")
    
    # 5. Deduplicate
    print("\n5. Deduplicating samples...")
    unique_samples = deduplicate_samples(all_samples)
    print(f"   ✓ {len(unique_samples)} unique samples after deduplication")
    
    # 6. Shuffle
    print("\n6. Shuffling dataset...")
    random.seed(42)
    random.shuffle(unique_samples)
    
    # 7. Create train/validation split
    print("\n7. Creating train/validation split...")
    split_idx = int(len(unique_samples) * 0.95)
    train_samples = unique_samples[:split_idx]
    val_samples = unique_samples[split_idx:]
    print(f"   ✓ Training: {len(train_samples)} samples")
    print(f"   ✓ Validation: {len(val_samples)} samples")
    
    # 8. Save final datasets
    print("\n8. Saving final datasets...")
    
    # Full dataset
    full_file = OUTPUT_DIR / "hassania_enriched_full.jsonl"
    with open(full_file, 'w', encoding='utf-8') as f:
        for sample in unique_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    print(f"   ✓ Saved full dataset to {full_file}")
    
    # Training set
    train_file = OUTPUT_DIR / "hassania_train.jsonl"
    with open(train_file, 'w', encoding='utf-8') as f:
        for sample in train_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    print(f"   ✓ Saved training set to {train_file}")
    
    # Validation set
    val_file = OUTPUT_DIR / "hassania_val.jsonl"
    with open(val_file, 'w', encoding='utf-8') as f:
        for sample in val_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    print(f"   ✓ Saved validation set to {val_file}")
    
    # 9. Generate statistics
    print("\n9. Generating statistics...")
    
    source_counts = Counter(s.get('source', 'unknown') for s in unique_samples)
    task_counts = Counter(s.get('task', 'unknown') for s in unique_samples)
    
    stats = {
        "total_samples": len(unique_samples),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "by_source": dict(source_counts),
        "by_task": dict(task_counts)
    }
    
    stats_file = OUTPUT_DIR / "dataset_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved statistics to {stats_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("FINAL DATASET SUMMARY")
    print("="*60)
    print(f"\nTotal unique samples: {len(unique_samples):,}")
    print(f"Training samples: {len(train_samples):,}")
    print(f"Validation samples: {len(val_samples):,}")
    
    print("\nSamples by source:")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count:,}")
    
    print("\nSamples by task:")
    for task, count in sorted(task_counts.items(), key=lambda x: -x[1]):
        print(f"  {task}: {count:,}")
    
    print("\nOutput files:")
    print(f"  {full_file}")
    print(f"  {train_file}")
    print(f"  {val_file}")
    print(f"  {stats_file}")


if __name__ == "__main__":
    main()
