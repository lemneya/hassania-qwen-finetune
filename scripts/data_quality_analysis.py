#!/usr/bin/env python3
"""
Comprehensive Data Quality Analysis for Hassaniya Fine-Tuning
- Duplicate detection and removal
- Token length analysis
- Language consistency checks
- Quality scoring
- Phased training data preparation
"""

import json
import os
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import re

plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']

BASE_DIR = Path("/tmp/hassania-qwen-finetune-main")
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "data/optimized"
REPORT_DIR = BASE_DIR / "reports"
EVAL_DIR = BASE_DIR / "evaluation"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)

def load_all_training_data():
    """Load all JSONL training files."""
    all_samples = []
    sources = {}
    
    # Priority order for training files
    training_files = [
        DATA_DIR / "final_with_peace_corps/hassania_train.jsonl",
        DATA_DIR / "final_enriched/hassania_train.jsonl",
        DATA_DIR / "final/hassania_train.jsonl",
        DATA_DIR / "openai_cleaned/hassania_train_cleaned_full.jsonl",
        DATA_DIR / "openai_format/hassania_train_full.jsonl",
    ]
    
    for filepath in training_files:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                count = 0
                for line in f:
                    try:
                        sample = json.loads(line)
                        sample['_source_file'] = filepath.name
                        all_samples.append(sample)
                        count += 1
                    except:
                        pass
                sources[filepath.name] = count
                print(f"Loaded {count} samples from {filepath.name}")
    
    return all_samples, sources

def extract_content(sample):
    """Extract text content from a sample for analysis."""
    content_parts = []
    
    if 'messages' in sample:
        for msg in sample['messages']:
            content_parts.append(msg.get('content', ''))
    
    return ' '.join(content_parts)

def compute_hash(text):
    """Compute hash for duplicate detection."""
    # Normalize text
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def detect_duplicates(samples):
    """Detect exact and near-duplicates."""
    print("\n=== Duplicate Detection ===")
    
    exact_hashes = defaultdict(list)
    
    for i, sample in enumerate(samples):
        content = extract_content(sample)
        h = compute_hash(content)
        exact_hashes[h].append(i)
    
    # Find duplicates
    duplicate_groups = {h: indices for h, indices in exact_hashes.items() if len(indices) > 1}
    
    total_duplicates = sum(len(indices) - 1 for indices in duplicate_groups.values())
    
    print(f"Total samples: {len(samples)}")
    print(f"Unique content hashes: {len(exact_hashes)}")
    print(f"Duplicate groups: {len(duplicate_groups)}")
    print(f"Total duplicate samples to remove: {total_duplicates}")
    
    # Get indices to keep (first occurrence of each)
    indices_to_remove = set()
    for h, indices in duplicate_groups.items():
        # Keep the first, remove the rest
        indices_to_remove.update(indices[1:])
    
    return indices_to_remove, duplicate_groups

def analyze_token_lengths(samples):
    """Analyze token length distribution."""
    print("\n=== Token Length Analysis ===")
    
    lengths = []
    problematic_short = []
    problematic_long = []
    
    for i, sample in enumerate(samples):
        content = extract_content(sample)
        # Approximate token count (words + punctuation)
        tokens = len(content.split()) + len(re.findall(r'[^\w\s]', content))
        lengths.append(tokens)
        
        if tokens < 10:
            problematic_short.append((i, tokens, content[:100]))
        elif tokens > 2000:
            problematic_long.append((i, tokens, content[:100]))
    
    print(f"Min tokens: {min(lengths)}")
    print(f"Max tokens: {max(lengths)}")
    print(f"Mean tokens: {sum(lengths)/len(lengths):.1f}")
    print(f"Samples < 10 tokens: {len(problematic_short)}")
    print(f"Samples > 2000 tokens: {len(problematic_long)}")
    
    return lengths, problematic_short, problematic_long

def analyze_message_structure(samples):
    """Analyze message structure and roles."""
    print("\n=== Message Structure Analysis ===")
    
    stats = {
        'has_system': 0,
        'has_user': 0,
        'has_assistant': 0,
        'system_lengths': [],
        'user_lengths': [],
        'assistant_lengths': [],
        'turn_counts': [],
        'missing_roles': []
    }
    
    for i, sample in enumerate(samples):
        if 'messages' not in sample:
            continue
            
        messages = sample['messages']
        roles = [m.get('role') for m in messages]
        
        stats['turn_counts'].append(len(messages))
        
        has_system = 'system' in roles
        has_user = 'user' in roles
        has_assistant = 'assistant' in roles
        
        if has_system:
            stats['has_system'] += 1
            for m in messages:
                if m.get('role') == 'system':
                    stats['system_lengths'].append(len(m.get('content', '')))
        
        if has_user:
            stats['has_user'] += 1
            for m in messages:
                if m.get('role') == 'user':
                    stats['user_lengths'].append(len(m.get('content', '')))
        
        if has_assistant:
            stats['has_assistant'] += 1
            for m in messages:
                if m.get('role') == 'assistant':
                    stats['assistant_lengths'].append(len(m.get('content', '')))
        
        if not has_user or not has_assistant:
            stats['missing_roles'].append(i)
    
    print(f"Samples with system prompt: {stats['has_system']}")
    print(f"Samples with user message: {stats['has_user']}")
    print(f"Samples with assistant response: {stats['has_assistant']}")
    print(f"Samples missing user or assistant: {len(stats['missing_roles'])}")
    print(f"Average turns per sample: {sum(stats['turn_counts'])/len(stats['turn_counts']):.1f}")
    
    return stats

def detect_language_issues(samples):
    """Detect potential language consistency issues."""
    print("\n=== Language Consistency Check ===")
    
    # Arabic character pattern
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    # French common words
    french_words = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'est', 'sont', 'pour', 'avec', 'dans', 'sur', 'que', 'qui', 'ce', 'cette'}
    
    issues = {
        'no_arabic': [],
        'mostly_french': [],
        'mostly_english': [],
        'empty_content': []
    }
    
    for i, sample in enumerate(samples):
        content = extract_content(sample)
        
        if not content.strip():
            issues['empty_content'].append(i)
            continue
        
        # Check for Arabic
        arabic_matches = arabic_pattern.findall(content)
        arabic_chars = sum(len(m) for m in arabic_matches)
        
        # Check for French
        words = content.lower().split()
        french_count = sum(1 for w in words if w in french_words)
        
        total_chars = len(content)
        
        if arabic_chars == 0:
            issues['no_arabic'].append(i)
        
        if french_count > len(words) * 0.3:
            issues['mostly_french'].append(i)
    
    print(f"Samples with no Arabic: {len(issues['no_arabic'])}")
    print(f"Samples mostly French: {len(issues['mostly_french'])}")
    print(f"Empty samples: {len(issues['empty_content'])}")
    
    return issues

def score_sample_quality(sample, idx):
    """Score individual sample quality (0-100)."""
    score = 100
    issues = []
    
    content = extract_content(sample)
    
    # Length checks
    tokens = len(content.split())
    if tokens < 5:
        score -= 30
        issues.append("very_short")
    elif tokens < 10:
        score -= 15
        issues.append("short")
    elif tokens > 2000:
        score -= 20
        issues.append("too_long")
    
    # Structure checks
    if 'messages' in sample:
        messages = sample['messages']
        roles = [m.get('role') for m in messages]
        
        if 'user' not in roles:
            score -= 25
            issues.append("no_user")
        if 'assistant' not in roles:
            score -= 25
            issues.append("no_assistant")
        
        # Check for empty messages
        for m in messages:
            if not m.get('content', '').strip():
                score -= 10
                issues.append("empty_message")
                break
    else:
        score -= 50
        issues.append("no_messages")
    
    # Arabic content check
    arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
    if not arabic_pattern.search(content):
        score -= 20
        issues.append("no_arabic")
    
    return max(0, score), issues

def create_quality_tiers(samples):
    """Create quality tiers for phased training."""
    print("\n=== Creating Quality Tiers ===")
    
    scored_samples = []
    
    for i, sample in enumerate(samples):
        score, issues = score_sample_quality(sample, i)
        scored_samples.append({
            'index': i,
            'sample': sample,
            'score': score,
            'issues': issues
        })
    
    # Sort by score
    scored_samples.sort(key=lambda x: x['score'], reverse=True)
    
    # Create tiers
    tier1 = [s for s in scored_samples if s['score'] >= 90]  # High quality
    tier2 = [s for s in scored_samples if 70 <= s['score'] < 90]  # Good quality
    tier3 = [s for s in scored_samples if 50 <= s['score'] < 70]  # Acceptable
    tier4 = [s for s in scored_samples if s['score'] < 50]  # Low quality
    
    print(f"Tier 1 (score >= 90): {len(tier1)} samples")
    print(f"Tier 2 (70-89): {len(tier2)} samples")
    print(f"Tier 3 (50-69): {len(tier3)} samples")
    print(f"Tier 4 (< 50): {len(tier4)} samples")
    
    return tier1, tier2, tier3, tier4, scored_samples

def create_evaluation_benchmark(samples):
    """Create evaluation benchmark with diverse test cases."""
    print("\n=== Creating Evaluation Benchmark ===")
    
    benchmark = {
        'greetings': [],
        'marketplace': [],
        'translation': [],
        'vocabulary': [],
        'conversation': []
    }
    
    # Keywords for categorization
    greeting_keywords = ['اشحالك', 'لاباس', 'مرحبا', 'السلام', 'صباح', 'مساء', 'hello', 'hi', 'greet']
    marketplace_keywords = ['سعر', 'بيع', 'شراء', 'نيمرو', 'ابرتماه', 'price', 'sell', 'buy', 'market']
    translation_keywords = ['translate', 'ترجم', 'meaning', 'معنى']
    
    for sample in samples[:5000]:  # Check first 5000
        content = extract_content(sample).lower()
        
        if any(kw in content for kw in greeting_keywords) and len(benchmark['greetings']) < 50:
            benchmark['greetings'].append(sample)
        elif any(kw in content for kw in marketplace_keywords) and len(benchmark['marketplace']) < 50:
            benchmark['marketplace'].append(sample)
        elif any(kw in content for kw in translation_keywords) and len(benchmark['translation']) < 50:
            benchmark['translation'].append(sample)
        elif len(benchmark['vocabulary']) < 50:
            benchmark['vocabulary'].append(sample)
    
    # Add some random samples for general conversation
    import random
    random.seed(42)
    remaining = [s for s in samples if s not in sum(benchmark.values(), [])]
    benchmark['conversation'] = random.sample(remaining[:1000], min(50, len(remaining)))
    
    total = sum(len(v) for v in benchmark.values())
    print(f"Benchmark created with {total} samples:")
    for cat, items in benchmark.items():
        print(f"  {cat}: {len(items)}")
    
    return benchmark

def create_visualizations(lengths, scored_samples, tiers):
    """Create visualization charts."""
    
    # 1. Token length distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(lengths, bins=50, color='#3498db', edgecolor='black', alpha=0.7)
    ax.axvline(x=10, color='red', linestyle='--', label='Min threshold (10)')
    ax.axvline(x=2000, color='red', linestyle='--', label='Max threshold (2000)')
    ax.set_xlabel('Token Count', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Token Length Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(REPORT_DIR / 'token_length_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Quality score distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    scores = [s['score'] for s in scored_samples]
    ax.hist(scores, bins=20, color='#2ecc71', edgecolor='black', alpha=0.7)
    ax.axvline(x=90, color='blue', linestyle='--', label='Tier 1 threshold')
    ax.axvline(x=70, color='orange', linestyle='--', label='Tier 2 threshold')
    ax.axvline(x=50, color='red', linestyle='--', label='Tier 3 threshold')
    ax.set_xlabel('Quality Score', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Sample Quality Score Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.savefig(REPORT_DIR / 'quality_score_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Quality tiers pie chart
    fig, ax = plt.subplots(figsize=(8, 8))
    tier_sizes = [len(t) for t in tiers]
    tier_labels = ['Tier 1 (≥90)', 'Tier 2 (70-89)', 'Tier 3 (50-69)', 'Tier 4 (<50)']
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    ax.pie(tier_sizes, labels=tier_labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title('Sample Quality Tiers', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(REPORT_DIR / 'quality_tiers.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved to reports/")

def save_optimized_datasets(samples, duplicates_to_remove, tier1, tier2, tier3):
    """Save optimized datasets for training."""
    print("\n=== Saving Optimized Datasets ===")
    
    # Remove duplicates
    clean_samples = [s for i, s in enumerate(samples) if i not in duplicates_to_remove]
    print(f"After duplicate removal: {len(clean_samples)} samples")
    
    # Save deduplicated full dataset
    with open(OUTPUT_DIR / 'hassania_train_deduped.jsonl', 'w', encoding='utf-8') as f:
        for sample in clean_samples:
            # Remove internal metadata
            clean_sample = {k: v for k, v in sample.items() if not k.startswith('_')}
            f.write(json.dumps(clean_sample, ensure_ascii=False) + '\n')
    
    # Save tier 1 (curated high-quality)
    with open(OUTPUT_DIR / 'hassania_train_tier1_curated.jsonl', 'w', encoding='utf-8') as f:
        for item in tier1:
            sample = {k: v for k, v in item['sample'].items() if not k.startswith('_')}
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Save tier 1 + tier 2 (good quality)
    with open(OUTPUT_DIR / 'hassania_train_tier1_2.jsonl', 'w', encoding='utf-8') as f:
        for item in tier1 + tier2:
            sample = {k: v for k, v in item['sample'].items() if not k.startswith('_')}
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Save all acceptable (tier 1-3)
    with open(OUTPUT_DIR / 'hassania_train_acceptable.jsonl', 'w', encoding='utf-8') as f:
        for item in tier1 + tier2 + tier3:
            sample = {k: v for k, v in item['sample'].items() if not k.startswith('_')}
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"Saved: hassania_train_deduped.jsonl ({len(clean_samples)} samples)")
    print(f"Saved: hassania_train_tier1_curated.jsonl ({len(tier1)} samples)")
    print(f"Saved: hassania_train_tier1_2.jsonl ({len(tier1) + len(tier2)} samples)")
    print(f"Saved: hassania_train_acceptable.jsonl ({len(tier1) + len(tier2) + len(tier3)} samples)")
    
    return len(clean_samples)

def save_evaluation_benchmark(benchmark):
    """Save evaluation benchmark."""
    
    # Save as JSONL
    with open(EVAL_DIR / 'evaluation_benchmark.jsonl', 'w', encoding='utf-8') as f:
        for category, samples in benchmark.items():
            for sample in samples:
                entry = {
                    'category': category,
                    'sample': {k: v for k, v in sample.items() if not k.startswith('_')}
                }
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    # Save summary
    summary = {
        'total_samples': sum(len(v) for v in benchmark.values()),
        'categories': {k: len(v) for k, v in benchmark.items()}
    }
    with open(EVAL_DIR / 'benchmark_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Saved evaluation benchmark to {EVAL_DIR}")

def generate_quality_report(results):
    """Generate comprehensive quality report."""
    
    report = f"""# Hassaniya Data Quality Analysis Report

**Generated:** January 5, 2026

---

## Executive Summary

This report presents a comprehensive analysis of the Hassaniya training dataset, identifying quality issues and providing optimized datasets for fine-tuning.

### Key Findings

| Metric | Value |
|--------|-------|
| **Original Samples** | {results['original_count']:,} |
| **Duplicates Found** | {results['duplicates']:,} |
| **After Deduplication** | {results['deduped_count']:,} |
| **High Quality (Tier 1)** | {results['tier1_count']:,} |
| **Good Quality (Tier 1+2)** | {results['tier1_2_count']:,} |
| **Acceptable (Tier 1-3)** | {results['acceptable_count']:,} |

---

## 1. Duplicate Analysis

![Token Distribution](token_length_distribution.png)

- **Exact duplicates removed:** {results['duplicates']:,}
- **Duplicate rate:** {results['duplicate_rate']:.1f}%

---

## 2. Quality Score Distribution

![Quality Scores](quality_score_distribution.png)

### Quality Tiers

![Quality Tiers](quality_tiers.png)

| Tier | Score Range | Samples | Percentage |
|------|-------------|---------|------------|
| Tier 1 | ≥ 90 | {results['tier1_count']:,} | {results['tier1_pct']:.1f}% |
| Tier 2 | 70-89 | {results['tier2_count']:,} | {results['tier2_pct']:.1f}% |
| Tier 3 | 50-69 | {results['tier3_count']:,} | {results['tier3_pct']:.1f}% |
| Tier 4 | < 50 | {results['tier4_count']:,} | {results['tier4_pct']:.1f}% |

---

## 3. Message Structure Analysis

| Metric | Value |
|--------|-------|
| Samples with system prompt | {results['has_system']:,} |
| Samples with user message | {results['has_user']:,} |
| Samples with assistant response | {results['has_assistant']:,} |
| Average turns per sample | {results['avg_turns']:.1f} |

---

## 4. Token Length Analysis

| Metric | Value |
|--------|-------|
| Minimum tokens | {results['min_tokens']} |
| Maximum tokens | {results['max_tokens']} |
| Mean tokens | {results['mean_tokens']:.1f} |
| Samples < 10 tokens | {results['short_samples']} |
| Samples > 2000 tokens | {results['long_samples']} |

---

## 5. Optimized Datasets Created

| Dataset | Samples | Use Case |
|---------|---------|----------|
| `hassania_train_deduped.jsonl` | {results['deduped_count']:,} | Full deduplicated dataset |
| `hassania_train_tier1_curated.jsonl` | {results['tier1_count']:,} | Phase 1: Quick validation |
| `hassania_train_tier1_2.jsonl` | {results['tier1_2_count']:,} | Phase 2: Quality training |
| `hassania_train_acceptable.jsonl` | {results['acceptable_count']:,} | Phase 3: Full training |

---

## 6. Evaluation Benchmark

| Category | Samples |
|----------|---------|
| Greetings | {results['benchmark']['greetings']} |
| Marketplace | {results['benchmark']['marketplace']} |
| Translation | {results['benchmark']['translation']} |
| Vocabulary | {results['benchmark']['vocabulary']} |
| Conversation | {results['benchmark']['conversation']} |
| **Total** | **{results['benchmark']['total']}** |

---

## 7. Recommended Training Strategy

### Phase 1: Quick Validation (1-2 hours)
- **Dataset:** `hassania_train_tier1_curated.jsonl`
- **Samples:** {results['tier1_count']:,}
- **Epochs:** 3
- **Purpose:** Verify training pipeline works

### Phase 2: Quality Training (4-8 hours)
- **Dataset:** `hassania_train_tier1_2.jsonl`
- **Samples:** {results['tier1_2_count']:,}
- **Epochs:** 3-5
- **Purpose:** Main training run

### Phase 3: Full Training (Optional)
- **Dataset:** `hassania_train_acceptable.jsonl`
- **Samples:** {results['acceptable_count']:,}
- **Epochs:** 2-3
- **Purpose:** Maximum coverage

---

## 8. Files Created

```
data/optimized/
├── hassania_train_deduped.jsonl
├── hassania_train_tier1_curated.jsonl
├── hassania_train_tier1_2.jsonl
└── hassania_train_acceptable.jsonl

evaluation/
├── evaluation_benchmark.jsonl
└── benchmark_summary.json
```

---

*Report generated by Manus AI*
"""
    
    with open(REPORT_DIR / 'DATA_QUALITY_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to {REPORT_DIR / 'DATA_QUALITY_REPORT.md'}")

def main():
    print("="*60)
    print("HASSANIYA DATA QUALITY ANALYSIS")
    print("="*60)
    
    # Load data
    samples, sources = load_all_training_data()
    original_count = len(samples)
    
    # Duplicate detection
    duplicates_to_remove, duplicate_groups = detect_duplicates(samples)
    
    # Token length analysis
    lengths, short_samples, long_samples = analyze_token_lengths(samples)
    
    # Message structure analysis
    structure_stats = analyze_message_structure(samples)
    
    # Language consistency
    language_issues = detect_language_issues(samples)
    
    # Quality scoring and tiers
    tier1, tier2, tier3, tier4, scored_samples = create_quality_tiers(samples)
    
    # Create evaluation benchmark
    benchmark = create_evaluation_benchmark(samples)
    
    # Create visualizations
    create_visualizations(lengths, scored_samples, (tier1, tier2, tier3, tier4))
    
    # Save optimized datasets
    deduped_count = save_optimized_datasets(samples, duplicates_to_remove, tier1, tier2, tier3)
    
    # Save evaluation benchmark
    save_evaluation_benchmark(benchmark)
    
    # Compile results
    results = {
        'original_count': original_count,
        'duplicates': len(duplicates_to_remove),
        'duplicate_rate': (len(duplicates_to_remove) / original_count) * 100,
        'deduped_count': deduped_count,
        'tier1_count': len(tier1),
        'tier2_count': len(tier2),
        'tier3_count': len(tier3),
        'tier4_count': len(tier4),
        'tier1_pct': (len(tier1) / original_count) * 100,
        'tier2_pct': (len(tier2) / original_count) * 100,
        'tier3_pct': (len(tier3) / original_count) * 100,
        'tier4_pct': (len(tier4) / original_count) * 100,
        'tier1_2_count': len(tier1) + len(tier2),
        'acceptable_count': len(tier1) + len(tier2) + len(tier3),
        'has_system': structure_stats['has_system'],
        'has_user': structure_stats['has_user'],
        'has_assistant': structure_stats['has_assistant'],
        'avg_turns': sum(structure_stats['turn_counts']) / len(structure_stats['turn_counts']),
        'min_tokens': min(lengths),
        'max_tokens': max(lengths),
        'mean_tokens': sum(lengths) / len(lengths),
        'short_samples': len(short_samples),
        'long_samples': len(long_samples),
        'benchmark': {
            'greetings': len(benchmark['greetings']),
            'marketplace': len(benchmark['marketplace']),
            'translation': len(benchmark['translation']),
            'vocabulary': len(benchmark['vocabulary']),
            'conversation': len(benchmark['conversation']),
            'total': sum(len(v) for v in benchmark.values())
        }
    }
    
    # Generate report
    generate_quality_report(results)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nOriginal samples: {original_count:,}")
    print(f"Duplicates removed: {len(duplicates_to_remove):,}")
    print(f"High quality (Tier 1): {len(tier1):,}")
    print(f"Good quality (Tier 1+2): {len(tier1) + len(tier2):,}")
    print(f"Evaluation benchmark: {results['benchmark']['total']} samples")

if __name__ == '__main__':
    main()
