#!/usr/bin/env python3
"""
Process all Hassania book text files and create training samples.
"""

import json
import re
import os
from pathlib import Path

def clean_text(text):
    """Clean and normalize Arabic/Hassania text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers and headers
    text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove common PDF artifacts
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()

def extract_paragraphs(text, min_length=50, max_length=1000):
    """Extract meaningful paragraphs from text."""
    paragraphs = []
    
    # Split by double newlines or periods followed by newlines
    chunks = re.split(r'\n\s*\n|\.\s*\n', text)
    
    for chunk in chunks:
        chunk = clean_text(chunk)
        if len(chunk) >= min_length and len(chunk) <= max_length:
            # Check if it contains Arabic characters
            if re.search(r'[\u0600-\u06FF]', chunk):
                paragraphs.append(chunk)
    
    return paragraphs

def extract_poetry_lines(text):
    """Extract poetry lines (تافلويت) from Hassania poetry texts."""
    lines = []
    
    # Split by newlines
    for line in text.split('\n'):
        line = clean_text(line)
        # Poetry lines typically have specific patterns
        if len(line) >= 20 and len(line) <= 200:
            if re.search(r'[\u0600-\u06FF]', line):
                # Check for poetry markers or patterns
                lines.append(line)
    
    return lines

def create_training_samples(paragraphs, source_name):
    """Create training samples from paragraphs."""
    samples = []
    
    for i, para in enumerate(paragraphs):
        # Create different types of training samples
        
        # 1. Text completion
        if len(para) > 100:
            mid = len(para) // 2
            samples.append({
                "instruction": "أكمل النص التالي بالحسانية:",
                "input": para[:mid],
                "output": para[mid:],
                "source": source_name,
                "task": "text_completion"
            })
        
        # 2. Dialect example
        samples.append({
            "instruction": "اكتب نصاً باللهجة الحسانية:",
            "input": "",
            "output": para,
            "source": source_name,
            "task": "dialect_example"
        })
        
        # 3. Text generation (for longer texts)
        if len(para) > 150:
            # Extract first sentence as prompt
            first_sentence = para.split('.')[0] if '.' in para else para[:50]
            samples.append({
                "instruction": f"اكتب نصاً حسانياً يبدأ بـ: {first_sentence}",
                "input": "",
                "output": para,
                "source": source_name,
                "task": "text_generation"
            })
    
    return samples

def process_book_file(filepath, source_name):
    """Process a single book text file."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    # Extract paragraphs
    paragraphs = extract_paragraphs(text)
    print(f"  Found {len(paragraphs)} paragraphs")
    
    # Extract poetry lines
    poetry_lines = extract_poetry_lines(text)
    print(f"  Found {len(poetry_lines)} poetry lines")
    
    # Create training samples
    samples = create_training_samples(paragraphs, source_name)
    
    # Add poetry samples
    for line in poetry_lines[:500]:  # Limit poetry lines
        samples.append({
            "instruction": "اكتب بيتاً من الشعر الحساني (لغن):",
            "input": "",
            "output": line,
            "source": source_name,
            "task": "poetry"
        })
    
    return samples, paragraphs, poetry_lines

def main():
    books_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/enrichment/books")
    output_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/enrichment/books_processed")
    output_dir.mkdir(exist_ok=True)
    
    # Book files to process
    book_files = {
        "diwan_poetry.txt": "Diwan Poetry (Archive.org)",
        "hassaniya_dictionary.txt": "English-Hassaniya Dictionary",
        "jamaliyat_text.txt": "Aesthetics of Hassani Poetry",
        "mrug_alharf_text.txt": "Mrug Alharf (First Hassaniya Book)",
        "hassaniyya_linguistic_text.txt": "Hassaniya Linguistic Study"
    }
    
    all_samples = []
    all_paragraphs = []
    all_poetry = []
    
    for filename, source_name in book_files.items():
        filepath = books_dir / filename
        if filepath.exists():
            samples, paragraphs, poetry = process_book_file(filepath, source_name)
            all_samples.extend(samples)
            all_paragraphs.extend(paragraphs)
            all_poetry.extend(poetry)
        else:
            print(f"File not found: {filepath}")
    
    # Save all samples
    output_file = output_dir / "books_training_samples.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in all_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Save raw corpus
    corpus_file = output_dir / "books_corpus.txt"
    with open(corpus_file, 'w', encoding='utf-8') as f:
        for para in all_paragraphs:
            f.write(para + '\n\n')
    
    # Save poetry corpus
    poetry_file = output_dir / "poetry_corpus.txt"
    with open(poetry_file, 'w', encoding='utf-8') as f:
        for line in all_poetry:
            f.write(line + '\n')
    
    # Statistics
    stats = {
        "total_samples": len(all_samples),
        "total_paragraphs": len(all_paragraphs),
        "total_poetry_lines": len(all_poetry),
        "sources": list(book_files.values())
    }
    
    stats_file = output_dir / "books_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"BOOKS PROCESSING COMPLETE")
    print(f"{'='*50}")
    print(f"Total training samples: {len(all_samples)}")
    print(f"Total paragraphs: {len(all_paragraphs)}")
    print(f"Total poetry lines: {len(all_poetry)}")
    print(f"Output saved to: {output_dir}")

if __name__ == "__main__":
    main()
