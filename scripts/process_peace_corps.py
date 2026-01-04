#!/usr/bin/env python3
"""
Process Peace Corps Hassaniya language materials into training samples.
Extracts romanized vocabulary, phrases, dialogues, and grammar examples.
The Peace Corps materials use romanized transcription (not Arabic script).
"""

import json
import re
import os
from pathlib import Path

def clean_text(text):
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()

def extract_romanized_hassaniya(text):
    """Extract romanized Hassaniya phrases enclosed in slashes."""
    # Pattern for romanized Hassaniya: /word/ or /phrase with spaces/
    pattern = r'/([a-zA-Z\-\:\'\s\.]+)/'
    matches = re.findall(pattern, text)
    
    # Clean and filter
    phrases = []
    for match in matches:
        phrase = match.strip()
        if len(phrase) > 2 and not phrase.isdigit():
            phrases.append(phrase)
    
    return phrases

def extract_lesson_content(text):
    """Extract lesson dialogues and vocabulary from Peace Corps format."""
    samples = []
    
    lines = text.split('\n')
    current_english = ""
    
    for i, line in enumerate(lines):
        line = clean_text(line)
        
        # Look for romanized Hassaniya in slashes
        hassaniya_matches = re.findall(r'/([a-zA-Z\-\:\'\s\.]+)/', line)
        
        if hassaniya_matches:
            for hassaniya in hassaniya_matches:
                hassaniya = hassaniya.strip()
                if len(hassaniya) > 3:
                    # Try to find English context
                    english_context = ""
                    
                    # Look for English in same line (outside slashes)
                    english_part = re.sub(r'/[^/]+/', '', line).strip()
                    if english_part and len(english_part) > 3:
                        english_context = english_part
                    
                    samples.append({
                        'hassaniya_romanized': hassaniya,
                        'english': english_context,
                        'line': line
                    })
    
    return samples

def extract_vocabulary_sections(text):
    """Extract vocabulary lists from the text."""
    vocab = []
    
    # Look for common vocabulary patterns
    lines = text.split('\n')
    
    for line in lines:
        line = clean_text(line)
        
        # Pattern: English word followed by romanized Hassaniya
        # e.g., "hello    /salam/"
        match = re.search(r'([A-Za-z][a-z\s]+)\s+/([^/]+)/', line)
        if match:
            english = match.group(1).strip()
            hassaniya = match.group(2).strip()
            if len(english) > 2 and len(hassaniya) > 2:
                vocab.append({
                    'english': english,
                    'hassaniya_romanized': hassaniya
                })
    
    return vocab

def extract_grammar_examples(text):
    """Extract grammar examples and explanations."""
    examples = []
    
    # Look for example sentences with translations
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = clean_text(line)
        
        # Look for lines with both romanized Hassaniya and English explanation
        if re.search(r'/[a-zA-Z\-\:\'\s]+/', line):
            # Check if there's explanatory text
            if len(line) > 30:
                examples.append(line)
    
    return examples

def create_training_samples(lesson_content, vocab, grammar_examples, source_name):
    """Create training samples from extracted content."""
    samples = []
    
    # From lesson content
    for item in lesson_content:
        if item['hassaniya_romanized']:
            samples.append({
                "instruction": "Write this in Hassaniya (romanized):",
                "input": item.get('english', ''),
                "output": item['hassaniya_romanized'],
                "source": source_name,
                "task": "hassaniya_romanized"
            })
    
    # From vocabulary
    for item in vocab:
        samples.append({
            "instruction": "Translate to Hassaniya (romanized):",
            "input": item['english'],
            "output": item['hassaniya_romanized'],
            "source": source_name,
            "task": "vocabulary_romanized"
        })
    
    # From grammar examples
    for example in grammar_examples[:100]:  # Limit grammar examples
        samples.append({
            "instruction": "Hassaniya grammar example:",
            "input": "",
            "output": example,
            "source": source_name,
            "task": "grammar_example"
        })
    
    return samples

def process_file(filepath, source_name):
    """Process a single Peace Corps text file."""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    # Extract different types of content
    romanized_phrases = extract_romanized_hassaniya(text)
    lesson_content = extract_lesson_content(text)
    vocab = extract_vocabulary_sections(text)
    grammar_examples = extract_grammar_examples(text)
    
    print(f"  Found {len(romanized_phrases)} romanized phrases")
    print(f"  Found {len(lesson_content)} lesson items")
    print(f"  Found {len(vocab)} vocabulary items")
    print(f"  Found {len(grammar_examples)} grammar examples")
    
    # Create training samples
    samples = create_training_samples(lesson_content, vocab, grammar_examples, source_name)
    
    return samples, romanized_phrases

def main():
    peace_corps_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/enrichment/peace_corps")
    output_dir = Path("/home/ubuntu/hassania-qwen-finetune/data/enrichment/peace_corps_processed")
    output_dir.mkdir(exist_ok=True)
    
    # Files to process
    files = {
        "hassaniya_language_lessons.txt": "Peace Corps Language Lessons",
        "mauritanian_arabic_course.txt": "Peace Corps Arabic Course",
        "mauritanian_arabic_grammar.txt": "Peace Corps Grammar Handbook",
        "dliflc_hassaniya_cultural.txt": "DLIFLC Cultural Orientation",
        "hassaniya_linguistic_paper.txt": "Hassaniya Linguistic Paper"
    }
    
    all_samples = []
    all_phrases = []
    
    for filename, source_name in files.items():
        filepath = peace_corps_dir / filename
        if filepath.exists():
            samples, phrases = process_file(filepath, source_name)
            all_samples.extend(samples)
            all_phrases.extend(phrases)
        else:
            print(f"File not found: {filepath}")
    
    # Deduplicate samples
    seen = set()
    unique_samples = []
    for sample in all_samples:
        key = sample.get('output', '')[:100]
        if key and key not in seen:
            seen.add(key)
            unique_samples.append(sample)
    
    # Save training samples
    output_file = output_dir / "peace_corps_training_samples.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in unique_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Save all romanized phrases
    phrases_file = output_dir / "romanized_hassaniya_phrases.txt"
    with open(phrases_file, 'w', encoding='utf-8') as f:
        for phrase in set(all_phrases):
            f.write(phrase + '\n')
    
    # Save statistics
    stats = {
        "total_samples": len(unique_samples),
        "unique_romanized_phrases": len(set(all_phrases)),
        "sources": list(files.values())
    }
    
    with open(output_dir / "peace_corps_stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print("PEACE CORPS PROCESSING COMPLETE")
    print(f"{'='*50}")
    print(f"Total unique samples: {len(unique_samples)}")
    print(f"Unique romanized phrases: {len(set(all_phrases))}")
    print(f"Output saved to: {output_dir}")

if __name__ == "__main__":
    main()
