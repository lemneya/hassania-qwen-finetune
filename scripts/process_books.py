#!/usr/bin/env python3
"""
Process downloaded Hassania books and literature into training data.
"""

import os
import re
import json
from pathlib import Path

# Paths
BOOKS_DIR = Path(__file__).parent.parent / "data" / "enrichment" / "books"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "enrichment" / "processed_books"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def is_arabic_text(text):
    """Check if text contains significant Arabic content."""
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', text))
    return arabic_chars > 5


def extract_arabic_segments(text, min_length=20, max_length=500):
    """Extract clean Arabic text segments from OCR text."""
    segments = []
    
    # Split by multiple newlines or page breaks
    chunks = re.split(r'\n{2,}|\f', text)
    
    for chunk in chunks:
        # Clean the chunk
        chunk = re.sub(r'\s+', ' ', chunk).strip()
        
        # Skip if too short or no Arabic
        if len(chunk) < min_length:
            continue
        
        # Count Arabic characters
        arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', chunk))
        total_alpha = len(re.findall(r'[a-zA-Z\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', chunk))
        
        # Keep if mostly Arabic (>40%)
        if total_alpha > 0 and arabic_chars / total_alpha > 0.4:
            # Remove non-Arabic noise but keep Arabic punctuation
            cleaned = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s،؛؟!:.٠١٢٣٤٥٦٧٨٩]', ' ', chunk)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            if len(cleaned) >= min_length:
                # Split long segments
                if len(cleaned) > max_length:
                    # Split at sentence boundaries
                    sentences = re.split(r'[.،؛؟!]', cleaned)
                    current = ""
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if len(current) + len(sent) < max_length:
                            current += " " + sent if current else sent
                        else:
                            if len(current) >= min_length:
                                segments.append(current)
                            current = sent
                    if len(current) >= min_length:
                        segments.append(current)
                else:
                    segments.append(cleaned)
    
    return segments


def process_diwan_poetry():
    """Process the Diwan poetry collection."""
    print("\nProcessing Diwan Poetry Collection...")
    
    input_file = BOOKS_DIR / "diwan_poetry.txt"
    if not input_file.exists():
        print(f"  ✗ File not found: {input_file}")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    # Extract Arabic segments
    segments = extract_arabic_segments(raw_text, min_length=15, max_length=300)
    
    # Create training samples
    samples = []
    for segment in segments:
        # Poetry/text generation task
        samples.append({
            "instruction": "اكتب نصاً بالحسانية الموريتانية:",
            "input": "",
            "output": segment,
            "source": "diwan_wald_anjarto",
            "task": "hassania_text_generation"
        })
        
        # Text completion task
        if len(segment) > 40:
            half = len(segment) // 2
            samples.append({
                "instruction": "أكمل هذا النص بالحسانية:",
                "input": segment[:half],
                "output": segment,
                "source": "diwan_wald_anjarto",
                "task": "hassania_text_completion"
            })
        
        # Dialect identification
        samples.append({
            "instruction": "This is an example of Hassania Arabic dialect from Mauritania:",
            "input": "",
            "output": segment,
            "source": "diwan_wald_anjarto",
            "task": "dialect_example"
        })
    
    print(f"  ✓ Extracted {len(segments)} text segments, created {len(samples)} samples")
    
    # Save cleaned segments
    output_file = OUTPUT_DIR / "diwan_segments.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(seg + '\n\n')
    
    return samples


def process_dictionary():
    """Process the English-Hassaniya dictionary."""
    print("\nProcessing English-Hassaniya Dictionary...")
    
    input_file = BOOKS_DIR / "hassaniya_dictionary.txt"
    if not input_file.exists():
        print(f"  ✗ File not found: {input_file}")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    samples = []
    
    # Extract Arabic segments from dictionary
    segments = extract_arabic_segments(raw_text, min_length=10, max_length=200)
    
    for segment in segments:
        samples.append({
            "instruction": "This is Hassaniya Arabic vocabulary:",
            "input": "",
            "output": segment,
            "source": "hassaniya_dictionary",
            "task": "vocabulary"
        })
    
    # Also look for English-Arabic pairs
    lines = raw_text.split('\n')
    entry_pattern = re.compile(r'([A-Za-z][A-Za-z\s]+)\s*[-:]\s*([\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s]+)')
    
    for line in lines:
        match = entry_pattern.search(line)
        if match:
            english = match.group(1).strip()
            hassaniya = match.group(2).strip()
            
            if len(english) > 1 and len(hassaniya) > 1:
                samples.append({
                    "instruction": f"Translate '{english}' to Hassaniya Arabic:",
                    "input": "",
                    "output": hassaniya,
                    "source": "hassaniya_dictionary",
                    "task": "word_translation"
                })
    
    print(f"  ✓ Extracted {len(samples)} dictionary samples")
    return samples


def main():
    print("\n" + "#"*60)
    print("# PROCESSING HASSANIA BOOKS AND LITERATURE")
    print("#"*60)
    
    all_samples = []
    
    # Process poetry
    poetry_samples = process_diwan_poetry()
    all_samples.extend(poetry_samples)
    
    # Process dictionary
    dict_samples = process_dictionary()
    all_samples.extend(dict_samples)
    
    # Save all samples
    if all_samples:
        output_file = OUTPUT_DIR / "books_samples.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in all_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"\n✓ Saved {len(all_samples)} samples to {output_file}")
        
        # Statistics
        by_source = {}
        by_task = {}
        for s in all_samples:
            source = s['source']
            task = s['task']
            by_source[source] = by_source.get(source, 0) + 1
            by_task[task] = by_task.get(task, 0) + 1
        
        print("\nSamples by source:")
        for source, count in by_source.items():
            print(f"  {source}: {count}")
        
        print("\nSamples by task:")
        for task, count in by_task.items():
            print(f"  {task}: {count}")
    else:
        print("\n✗ No samples extracted from books")


if __name__ == "__main__":
    main()
