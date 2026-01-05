#!/usr/bin/env python3
"""
Generate comprehensive fine-tuning readiness report for Hassaniya dataset.
Analyzes all data sources, formats, quality metrics, and provides recommendations.
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']

BASE_DIR = Path("/tmp/hassania-qwen-finetune-main")
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def count_jsonl_lines(filepath):
    """Count lines in a JSONL file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0

def analyze_jsonl_file(filepath):
    """Analyze a JSONL file for structure and content."""
    stats = {
        'total_lines': 0,
        'fields': defaultdict(int),
        'avg_message_length': 0,
        'sample': None,
        'has_system': 0,
        'has_user': 0,
        'has_assistant': 0,
        'total_tokens_estimate': 0
    }
    
    total_length = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    data = json.loads(line)
                    stats['total_lines'] += 1
                    
                    # Track fields
                    for key in data.keys():
                        stats['fields'][key] += 1
                    
                    # Check for OpenAI format
                    if 'messages' in data:
                        for msg in data['messages']:
                            role = msg.get('role', '')
                            content = msg.get('content', '')
                            total_length += len(content)
                            stats['total_tokens_estimate'] += len(content.split())
                            
                            if role == 'system':
                                stats['has_system'] += 1
                            elif role == 'user':
                                stats['has_user'] += 1
                            elif role == 'assistant':
                                stats['has_assistant'] += 1
                    
                    # Get sample
                    if i == 0:
                        stats['sample'] = data
                        
                except json.JSONDecodeError:
                    pass
        
        if stats['total_lines'] > 0:
            stats['avg_message_length'] = total_length / stats['total_lines']
            
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
    
    return stats

def analyze_csv_file(filepath):
    """Analyze a CSV file."""
    stats = {
        'total_rows': 0,
        'columns': [],
        'sample': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            stats['columns'] = reader.fieldnames or []
            for i, row in enumerate(reader):
                stats['total_rows'] += 1
                if i == 0:
                    stats['sample'] = dict(row)
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
    
    return stats

def analyze_all_data():
    """Analyze all data directories."""
    results = {}
    
    # Define data categories
    categories = {
        'raw': DATA_DIR / 'raw',
        'processed': DATA_DIR / 'processed',
        'cleaned': DATA_DIR / 'cleaned',
        'openai_format': DATA_DIR / 'openai_format',
        'openai_cleaned': DATA_DIR / 'openai_cleaned',
        'final': DATA_DIR / 'final',
        'final_enriched': DATA_DIR / 'final_enriched',
        'final_with_peace_corps': DATA_DIR / 'final_with_peace_corps',
        'enrichment': DATA_DIR / 'enrichment',
        'pipeline_raw': DATA_DIR / 'pipeline/raw',
        'pipeline_processed': DATA_DIR / 'pipeline/processed'
    }
    
    for cat_name, cat_path in categories.items():
        if not cat_path.exists():
            continue
            
        results[cat_name] = {
            'path': str(cat_path),
            'files': []
        }
        
        for filepath in cat_path.rglob('*'):
            if filepath.is_file():
                file_info = {
                    'name': filepath.name,
                    'path': str(filepath.relative_to(DATA_DIR)),
                    'size_kb': filepath.stat().st_size / 1024
                }
                
                if filepath.suffix == '.jsonl':
                    file_info['type'] = 'jsonl'
                    file_info['analysis'] = analyze_jsonl_file(filepath)
                elif filepath.suffix == '.json':
                    file_info['type'] = 'json'
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        file_info['content'] = data if isinstance(data, dict) else {'items': len(data)}
                    except:
                        pass
                elif filepath.suffix == '.csv':
                    file_info['type'] = 'csv'
                    file_info['analysis'] = analyze_csv_file(filepath)
                else:
                    file_info['type'] = filepath.suffix
                
                results[cat_name]['files'].append(file_info)
    
    return results

def calculate_readiness_score(data):
    """Calculate overall fine-tuning readiness score."""
    score = 0
    max_score = 100
    issues = []
    recommendations = []
    
    # Check for OpenAI format data
    openai_files = []
    total_training_samples = 0
    total_val_samples = 0
    
    for cat_name, cat_data in data.items():
        for file_info in cat_data.get('files', []):
            if file_info.get('type') == 'jsonl':
                analysis = file_info.get('analysis', {})
                if analysis.get('has_user', 0) > 0 and analysis.get('has_assistant', 0) > 0:
                    openai_files.append(file_info)
                    if 'train' in file_info['name'].lower():
                        total_training_samples += analysis.get('total_lines', 0)
                    elif 'val' in file_info['name'].lower():
                        total_val_samples += analysis.get('total_lines', 0)
    
    # Score: Data quantity (30 points)
    if total_training_samples >= 10000:
        score += 30
    elif total_training_samples >= 5000:
        score += 25
    elif total_training_samples >= 1000:
        score += 20
    elif total_training_samples >= 500:
        score += 15
    elif total_training_samples >= 100:
        score += 10
    else:
        score += 5
        issues.append(f"Low training sample count: {total_training_samples}")
        recommendations.append("Collect more training data (aim for 1000+ samples)")
    
    # Score: Validation data (10 points)
    if total_val_samples >= 100:
        score += 10
    elif total_val_samples >= 50:
        score += 7
    elif total_val_samples > 0:
        score += 5
    else:
        issues.append("No validation data found")
        recommendations.append("Create a validation split (10-20% of training data)")
    
    # Score: OpenAI format compliance (20 points)
    if len(openai_files) > 0:
        score += 20
    else:
        issues.append("No OpenAI-format training files found")
        recommendations.append("Convert data to OpenAI chat format with messages array")
    
    # Score: Data diversity (20 points)
    categories_with_data = sum(1 for cat in data.values() if len(cat.get('files', [])) > 0)
    if categories_with_data >= 5:
        score += 20
    elif categories_with_data >= 3:
        score += 15
    else:
        score += 10
        recommendations.append("Add more diverse data sources")
    
    # Score: Data quality indicators (20 points)
    has_cleaned = 'cleaned' in data or 'openai_cleaned' in data
    has_enriched = 'final_enriched' in data or 'enrichment' in data
    
    if has_cleaned:
        score += 10
    else:
        recommendations.append("Run data cleaning pipeline")
    
    if has_enriched:
        score += 10
    else:
        recommendations.append("Consider data enrichment/augmentation")
    
    return {
        'score': score,
        'max_score': max_score,
        'percentage': (score / max_score) * 100,
        'total_training_samples': total_training_samples,
        'total_val_samples': total_val_samples,
        'openai_format_files': len(openai_files),
        'issues': issues,
        'recommendations': recommendations
    }

def create_visualizations(data, readiness):
    """Create visualization charts."""
    
    # 1. Data distribution by category
    fig, ax = plt.subplots(figsize=(12, 6))
    categories = []
    sample_counts = []
    
    for cat_name, cat_data in data.items():
        total = 0
        for file_info in cat_data.get('files', []):
            if file_info.get('type') == 'jsonl':
                total += file_info.get('analysis', {}).get('total_lines', 0)
            elif file_info.get('type') == 'csv':
                total += file_info.get('analysis', {}).get('total_rows', 0)
        if total > 0:
            categories.append(cat_name)
            sample_counts.append(total)
    
    colors = plt.cm.viridis([i/len(categories) for i in range(len(categories))])
    bars = ax.barh(categories, sample_counts, color=colors)
    ax.set_xlabel('Number of Samples', fontsize=12)
    ax.set_title('Data Distribution by Category', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, sample_counts):
        ax.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(REPORT_DIR / 'data_distribution_by_category.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # 2. Readiness score gauge
    fig, ax = plt.subplots(figsize=(8, 6))
    score = readiness['percentage']
    
    # Create a simple bar chart for readiness
    colors = ['#e74c3c' if score < 50 else '#f39c12' if score < 75 else '#2ecc71']
    ax.barh(['Readiness Score'], [score], color=colors, height=0.5)
    ax.barh(['Readiness Score'], [100], color='#ecf0f1', height=0.5, alpha=0.3)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Score (%)', fontsize=12)
    ax.set_title(f'Fine-Tuning Readiness: {score:.1f}%', fontsize=14, fontweight='bold')
    ax.text(score + 2, 0, f'{score:.1f}%', va='center', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(REPORT_DIR / 'readiness_score.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # 3. Training vs Validation split
    fig, ax = plt.subplots(figsize=(8, 6))
    train = readiness['total_training_samples']
    val = readiness['total_val_samples']
    if train + val > 0:
        ax.pie([train, val], labels=['Training', 'Validation'], 
               autopct='%1.1f%%', colors=['#3498db', '#e74c3c'], startangle=90)
        ax.set_title(f'Train/Val Split\n(Total: {train + val:,} samples)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(REPORT_DIR / 'train_val_split.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Visualizations saved to reports/")

def generate_report(data, readiness):
    """Generate the markdown report."""
    
    report = f"""# Hassaniya Fine-Tuning Readiness Report

**Generated:** January 5, 2026  
**Repository:** [lemneya/hassania-qwen-finetune](https://github.com/lemneya/hassania-qwen-finetune)

---

## Executive Summary

This report assesses the readiness of the Hassaniya dialect dataset for fine-tuning language models. The analysis covers data quantity, quality, format compliance, and provides actionable recommendations.

### Readiness Score: {readiness['percentage']:.1f}%

![Readiness Score](readiness_score.png)

| Metric | Value |
|--------|-------|
| Total Training Samples | {readiness['total_training_samples']:,} |
| Total Validation Samples | {readiness['total_val_samples']:,} |
| OpenAI-Format Files | {readiness['openai_format_files']} |
| Overall Score | {readiness['score']}/{readiness['max_score']} |

---

## 1. Data Inventory

### 1.1 Overview by Category

![Data Distribution](data_distribution_by_category.png)

"""
    
    # Add detailed category breakdown
    for cat_name, cat_data in sorted(data.items()):
        files = cat_data.get('files', [])
        if not files:
            continue
            
        total_samples = 0
        for f in files:
            if f.get('type') == 'jsonl':
                total_samples += f.get('analysis', {}).get('total_lines', 0)
            elif f.get('type') == 'csv':
                total_samples += f.get('analysis', {}).get('total_rows', 0)
        
        report += f"""#### {cat_name.replace('_', ' ').title()}

| File | Type | Size (KB) | Samples |
|------|------|-----------|---------|
"""
        for f in files:
            samples = 0
            if f.get('type') == 'jsonl':
                samples = f.get('analysis', {}).get('total_lines', 0)
            elif f.get('type') == 'csv':
                samples = f.get('analysis', {}).get('total_rows', 0)
            report += f"| {f['name']} | {f.get('type', 'N/A')} | {f['size_kb']:.1f} | {samples:,} |\n"
        
        report += f"\n**Category Total:** {total_samples:,} samples\n\n"
    
    report += """---

## 2. Train/Validation Split

![Train/Val Split](train_val_split.png)

"""
    
    train = readiness['total_training_samples']
    val = readiness['total_val_samples']
    total = train + val
    if total > 0:
        train_pct = (train / total) * 100
        val_pct = (val / total) * 100
        report += f"""| Split | Samples | Percentage |
|-------|---------|------------|
| Training | {train:,} | {train_pct:.1f}% |
| Validation | {val:,} | {val_pct:.1f}% |
| **Total** | **{total:,}** | **100%** |

"""
    
    report += """---

## 3. Data Format Analysis

### 3.1 OpenAI Chat Format Compliance

For fine-tuning with OpenAI or compatible APIs, data must be in the chat format with `messages` array containing `role` and `content` fields.

"""
    
    # Find OpenAI format files and show their structure
    for cat_name, cat_data in data.items():
        for f in cat_data.get('files', []):
            if f.get('type') == 'jsonl':
                analysis = f.get('analysis', {})
                if analysis.get('has_user', 0) > 0:
                    report += f"""#### {f['name']}

- **Total Samples:** {analysis.get('total_lines', 0):,}
- **With System Prompt:** {analysis.get('has_system', 0):,}
- **With User Message:** {analysis.get('has_user', 0):,}
- **With Assistant Response:** {analysis.get('has_assistant', 0):,}
- **Estimated Tokens:** ~{analysis.get('total_tokens_estimate', 0):,}

"""
    
    report += """---

## 4. Quality Assessment

### 4.1 Issues Identified

"""
    
    if readiness['issues']:
        for issue in readiness['issues']:
            report += f"- ⚠️ {issue}\n"
    else:
        report += "✅ No critical issues identified.\n"
    
    report += """
### 4.2 Recommendations

"""
    
    if readiness['recommendations']:
        for i, rec in enumerate(readiness['recommendations'], 1):
            report += f"{i}. {rec}\n"
    else:
        report += "✅ Dataset appears ready for fine-tuning.\n"
    
    report += f"""

---

## 5. Fine-Tuning Recommendations

### 5.1 Recommended Configuration

Based on the dataset analysis, here are the recommended fine-tuning parameters:

| Parameter | Recommended Value | Notes |
|-----------|-------------------|-------|
| Base Model | Qwen2.5-7B or GPT-4o-mini | Depends on budget and requirements |
| Training Samples | {readiness['total_training_samples']:,} | Current dataset size |
| Epochs | 3-5 | Start with 3, increase if underfitting |
| Batch Size | 4-8 | Adjust based on GPU memory |
| Learning Rate | 1e-5 to 5e-5 | Lower for smaller datasets |
| Validation Split | 10-20% | Currently: {(readiness['total_val_samples'] / max(readiness['total_training_samples'], 1) * 100):.1f}% |

### 5.2 Data Quality Checklist

| Criterion | Status |
|-----------|--------|
| OpenAI format compliance | {'✅' if readiness['openai_format_files'] > 0 else '❌'} |
| Sufficient training data (>500) | {'✅' if readiness['total_training_samples'] >= 500 else '❌'} |
| Validation data present | {'✅' if readiness['total_val_samples'] > 0 else '❌'} |
| Data cleaning applied | {'✅' if 'cleaned' in data or 'openai_cleaned' in data else '❌'} |
| Data enrichment applied | {'✅' if 'final_enriched' in data else '❌'} |

### 5.3 Next Steps

1. **If score >= 75%:** Dataset is ready for fine-tuning. Proceed with training.
2. **If score 50-75%:** Address identified issues before training.
3. **If score < 50%:** Significant data preparation needed.

---

## 6. File Inventory Summary

| Category | Files | Total Samples |
|----------|-------|---------------|
"""
    
    for cat_name, cat_data in sorted(data.items()):
        files = cat_data.get('files', [])
        total = 0
        for f in files:
            if f.get('type') == 'jsonl':
                total += f.get('analysis', {}).get('total_lines', 0)
            elif f.get('type') == 'csv':
                total += f.get('analysis', {}).get('total_rows', 0)
        report += f"| {cat_name} | {len(files)} | {total:,} |\n"
    
    report += """

---

*Report generated by Manus AI*
"""
    
    return report

def main():
    print("Analyzing all data in repository...")
    data = analyze_all_data()
    
    print("Calculating readiness score...")
    readiness = calculate_readiness_score(data)
    
    print("Creating visualizations...")
    create_visualizations(data, readiness)
    
    print("Generating report...")
    report = generate_report(data, readiness)
    
    report_path = REPORT_DIR / "FINETUNE_READINESS_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print(f"FINE-TUNING READINESS SCORE: {readiness['percentage']:.1f}%")
    print(f"{'='*60}")
    print(f"Training Samples: {readiness['total_training_samples']:,}")
    print(f"Validation Samples: {readiness['total_val_samples']:,}")
    print(f"OpenAI Format Files: {readiness['openai_format_files']}")
    print(f"\nReport saved to: {report_path}")
    
    if readiness['issues']:
        print("\nIssues:")
        for issue in readiness['issues']:
            print(f"  - {issue}")
    
    if readiness['recommendations']:
        print("\nRecommendations:")
        for rec in readiness['recommendations']:
            print(f"  - {rec}")

if __name__ == '__main__':
    main()
