#!/usr/bin/env python3
"""
Preprocess and combine all Hassania dialect datasets into a unified format
suitable for fine-tuning Qwen 2.5.
"""

import os
import json
import re
from pathlib import Path
import pandas as pd
from tqdm import tqdm

# Define paths
RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def clean_arabic_text(text):
    """
    Clean and normalize Arabic text.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Keep Arabic letters, numbers, and common punctuation
    # This preserves Hassania dialect characters
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\s\d.,!?؟،؛:\-\'"()]', '', text)
    
    return text.strip()


def process_dah_dataset():
    """Process DAH bilingual dataset."""
    print("\nProcessing DAH Dataset...")
    
    input_path = RAW_DATA_DIR / "dah_dataset.csv"
    if not input_path.exists():
        print(f"  ✗ File not found: {input_path}")
        return []
    
    df = pd.read_csv(input_path)
    samples = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="  DAH"):
        # Get all three columns
        hassaniya_ar = clean_arabic_text(str(row.get('hassaniya-ar', '')))
        hassaniya_en = str(row.get('hassaniya-en', '')).strip()
        english = str(row.get('english', '')).strip()
        
        if hassaniya_ar and english:
            # English to Hassania translation
            samples.append({
                "instruction": f"Translate the following English text to Hassania Arabic dialect:\n{english}",
                "input": "",
                "output": hassaniya_ar,
                "source": "dah",
                "task": "translation_en_to_hassania"
            })
            
            # Hassania to English translation
            samples.append({
                "instruction": f"Translate the following Hassania Arabic dialect text to English:\n{hassaniya_ar}",
                "input": "",
                "output": english,
                "source": "dah",
                "task": "translation_hassania_to_en"
            })
            
            # Text generation (continue the text)
            if len(hassaniya_ar) > 20:
                half_len = len(hassaniya_ar) // 2
                samples.append({
                    "instruction": "Continue writing in Hassania Arabic dialect:",
                    "input": hassaniya_ar[:half_len],
                    "output": hassaniya_ar,
                    "source": "dah",
                    "task": "text_generation"
                })
    
    print(f"  ✓ Generated {len(samples)} samples from DAH dataset")
    return samples


def process_speech_transcriptions():
    """Process Hassaniya Speech transcriptions."""
    print("\nProcessing Hassaniya Speech Transcriptions...")
    
    input_path = RAW_DATA_DIR / "hassaniya_speech_transcriptions.csv"
    if not input_path.exists():
        print(f"  ✗ File not found: {input_path}")
        return []
    
    df = pd.read_csv(input_path)
    samples = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="  Speech"):
        transcription = clean_arabic_text(str(row.get('transcription', '')))
        
        if transcription and len(transcription) > 5:
            # Text completion task
            if len(transcription) > 15:
                third_len = len(transcription) // 3
                samples.append({
                    "instruction": "Complete the following Hassania Arabic text:",
                    "input": transcription[:third_len],
                    "output": transcription,
                    "source": "hassaniya_speech",
                    "task": "text_completion"
                })
            
            # Text understanding
            samples.append({
                "instruction": "This is an example of Hassania Arabic dialect. Repeat it:",
                "input": "",
                "output": transcription,
                "source": "hassaniya_speech",
                "task": "dialect_example"
            })
    
    print(f"  ✓ Generated {len(samples)} samples from Speech dataset")
    return samples


def process_casablanca_mauritanian():
    """Process Casablanca Mauritanian subset."""
    print("\nProcessing Casablanca Mauritanian Dataset...")
    
    input_path = RAW_DATA_DIR / "casablanca_mauritanian.csv"
    if not input_path.exists():
        print(f"  ✗ File not found: {input_path}")
        return []
    
    df = pd.read_csv(input_path)
    samples = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="  Casablanca"):
        transcription = clean_arabic_text(str(row.get('transcription', '')))
        
        if transcription and len(transcription) > 5:
            samples.append({
                "instruction": "This is Mauritanian Arabic (Hassania dialect). Provide a similar phrase:",
                "input": "",
                "output": transcription,
                "source": "casablanca_mauritanian",
                "task": "dialect_example"
            })
            
            # Text generation
            if len(transcription) > 20:
                half_len = len(transcription) // 2
                samples.append({
                    "instruction": "Continue this Hassania Arabic text:",
                    "input": transcription[:half_len],
                    "output": transcription,
                    "source": "casablanca_mauritanian",
                    "task": "text_generation"
                })
    
    print(f"  ✓ Generated {len(samples)} samples from Casablanca dataset")
    return samples


def process_sentiment_dataset():
    """Process HASSANIYA Sentiment dataset."""
    print("\nProcessing HASSANIYA Sentiment Dataset...")
    
    input_path = RAW_DATA_DIR / "hassaniya_sentiment.csv"
    if not input_path.exists():
        print(f"  ✗ File not found: {input_path}")
        return []
    
    df = pd.read_csv(input_path)
    samples = []
    
    # The dataset has columns: id, annotations, created_at, Annotation results, text, updated_at
    text_col = 'text'
    label_col = ' Annotation results'  # Note the leading space
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="  Sentiment"):
        text = clean_arabic_text(str(row.get(text_col, '')))
        label = str(row.get(label_col, 'neutral')).strip().lower()
        
        if text and len(text) > 3:
            # Sentiment analysis task
            samples.append({
                "instruction": f"Analyze the sentiment of this Hassania Arabic text. Respond with: positive, negative, or neutral.\n\nText: {text}",
                "input": "",
                "output": label,
                "source": "hassaniya_sentiment",
                "task": "sentiment_analysis"
            })
            
            # Sentiment-guided text generation
            samples.append({
                "instruction": f"Write a {label} sentiment text in Hassania Arabic dialect:",
                "input": "",
                "output": text,
                "source": "hassaniya_sentiment",
                "task": "sentiment_generation"
            })
            
            # Dialect example
            samples.append({
                "instruction": "This is an example of Hassania Arabic from Mauritania:",
                "input": "",
                "output": text,
                "source": "hassaniya_sentiment",
                "task": "dialect_example"
            })
    
    print(f"  ✓ Generated {len(samples)} samples from Sentiment dataset")
    return samples


def save_combined_dataset(samples, output_format="jsonl"):
    """Save combined dataset in specified format."""
    print(f"\nSaving combined dataset ({len(samples)} samples)...")
    
    if output_format == "jsonl":
        output_path = PROCESSED_DATA_DIR / "hassania_combined.jsonl"
        with open(output_path, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    elif output_format == "json":
        output_path = PROCESSED_DATA_DIR / "hassania_combined.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ Saved to {output_path}")
    
    # Also save as CSV for easy viewing
    csv_path = PROCESSED_DATA_DIR / "hassania_combined.csv"
    pd.DataFrame(samples).to_csv(csv_path, index=False)
    print(f"  ✓ Also saved CSV version to {csv_path}")
    
    return output_path


def save_raw_text_corpus(samples):
    """Save a raw text corpus for pretraining or continued pretraining."""
    print("\nSaving raw text corpus...")
    
    # Extract unique Hassania texts
    texts = set()
    for sample in samples:
        output = sample.get('output', '')
        if output and len(output) > 5:
            # Skip non-Arabic outputs (like sentiment labels)
            if any('\u0600' <= c <= '\u06FF' for c in output):
                texts.add(output)
    
    # Save as plain text
    corpus_path = PROCESSED_DATA_DIR / "hassania_corpus.txt"
    with open(corpus_path, 'w', encoding='utf-8') as f:
        for text in sorted(texts):
            f.write(text + '\n')
    
    print(f"  ✓ Saved {len(texts)} unique texts to {corpus_path}")


def generate_statistics(samples):
    """Generate and save dataset statistics."""
    print("\nDataset Statistics:")
    print("="*50)
    
    df = pd.DataFrame(samples)
    
    # By source
    print("\nSamples by Source:")
    source_counts = df['source'].value_counts()
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    
    # By task
    print("\nSamples by Task:")
    task_counts = df['task'].value_counts()
    for task, count in task_counts.items():
        print(f"  {task}: {count}")
    
    # Save statistics
    stats = {
        "total_samples": len(samples),
        "by_source": source_counts.to_dict(),
        "by_task": task_counts.to_dict()
    }
    
    stats_path = PROCESSED_DATA_DIR / "dataset_statistics.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"\n  ✓ Statistics saved to {stats_path}")
    
    return stats


def main():
    """Main preprocessing pipeline."""
    print("\n" + "#"*60)
    print("# HASSANIA DATASET PREPROCESSING")
    print("#"*60)
    
    all_samples = []
    
    # Process each dataset
    all_samples.extend(process_dah_dataset())
    all_samples.extend(process_speech_transcriptions())
    all_samples.extend(process_casablanca_mauritanian())
    all_samples.extend(process_sentiment_dataset())
    
    if not all_samples:
        print("\n✗ No samples generated. Please run download_data.py first.")
        return
    
    # Save combined dataset
    save_combined_dataset(all_samples)
    
    # Save raw text corpus
    save_raw_text_corpus(all_samples)
    
    # Generate statistics
    stats = generate_statistics(all_samples)
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE")
    print("="*60)
    print(f"Total samples: {len(all_samples)}")
    print(f"Output directory: {PROCESSED_DATA_DIR}")
    print("\nNext step: Run finetune_qwen.py to fine-tune the model")


if __name__ == "__main__":
    main()
