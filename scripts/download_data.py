#!/usr/bin/env python3
"""
Download all available Hassania dialect datasets from various sources.
"""

import os
import requests
from pathlib import Path
from datasets import load_dataset
import pandas as pd
from tqdm import tqdm

# Define paths
RAW_DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_dah_dataset():
    """Download DAH bilingual Hassania-English dataset from Hugging Face."""
    print("\n" + "="*60)
    print("Downloading DAH Dataset (Hassania-English Bilingual)")
    print("="*60)
    
    try:
        dataset = load_dataset("hassan-IA/dah", split="train")
        output_path = RAW_DATA_DIR / "dah_dataset.csv"
        dataset.to_pandas().to_csv(output_path, index=False)
        print(f"✓ Saved {len(dataset)} rows to {output_path}")
        return len(dataset)
    except Exception as e:
        print(f"✗ Error downloading DAH dataset: {e}")
        return 0


def download_hassaniya_speech_dataset():
    """Download Hassaniya Speech dataset from Hugging Face."""
    print("\n" + "="*60)
    print("Downloading Hassaniya Speech Dataset")
    print("="*60)
    
    try:
        dataset = load_dataset("Mamadou-Aw/Hassaniya-speech-dataset", split="train")
        
        # Save transcriptions
        transcriptions = []
        for item in dataset:
            transcriptions.append({
                "transcription": item.get("transcription", ""),
            })
        
        output_path = RAW_DATA_DIR / "hassaniya_speech_transcriptions.csv"
        pd.DataFrame(transcriptions).to_csv(output_path, index=False)
        print(f"✓ Saved {len(transcriptions)} transcriptions to {output_path}")
        
        # Note: Audio files can be accessed via the dataset object
        print("  Note: Audio files available via HuggingFace datasets API")
        return len(transcriptions)
    except Exception as e:
        print(f"✗ Error downloading Hassaniya Speech dataset: {e}")
        return 0


def download_casablanca_mauritanian():
    """Download Mauritanian subset from Casablanca dataset."""
    print("\n" + "="*60)
    print("Downloading Casablanca Dataset (Mauritanian Subset)")
    print("="*60)
    
    try:
        # Load Mauritanian subset
        dataset_val = load_dataset("UBC-NLP/Casablanca", "Mauritania", split="validation")
        dataset_test = load_dataset("UBC-NLP/Casablanca", "Mauritania", split="test")
        
        # Combine validation and test
        transcriptions = []
        for item in dataset_val:
            transcriptions.append({
                "seg_id": item.get("seg_id", ""),
                "transcription": item.get("transcription", ""),
                "gender": item.get("gender", ""),
                "duration": item.get("duration", 0),
                "split": "validation"
            })
        for item in dataset_test:
            transcriptions.append({
                "seg_id": item.get("seg_id", ""),
                "transcription": item.get("transcription", ""),
                "gender": item.get("gender", ""),
                "duration": item.get("duration", 0),
                "split": "test"
            })
        
        output_path = RAW_DATA_DIR / "casablanca_mauritanian.csv"
        pd.DataFrame(transcriptions).to_csv(output_path, index=False)
        print(f"✓ Saved {len(transcriptions)} rows to {output_path}")
        return len(transcriptions)
    except Exception as e:
        print(f"✗ Error downloading Casablanca dataset: {e}")
        return 0


def download_hassaniya_sentiment():
    """
    Download HASSANIYA Sentiment dataset from Mendeley.
    Note: This requires manual download due to Mendeley's access restrictions.
    """
    print("\n" + "="*60)
    print("HASSANIYA Sentiment Dataset (Mendeley)")
    print("="*60)
    
    mendeley_url = "https://data.mendeley.com/datasets/m2swkr2bhx"
    print(f"  This dataset requires manual download from:")
    print(f"  {mendeley_url}")
    print(f"  ")
    print(f"  After downloading, place the CSV file in:")
    print(f"  {RAW_DATA_DIR / 'hassaniya_sentiment.csv'}")
    
    # Check if file already exists
    sentiment_path = RAW_DATA_DIR / "hassaniya_sentiment.csv"
    if sentiment_path.exists():
        df = pd.read_csv(sentiment_path)
        print(f"✓ Found existing file with {len(df)} rows")
        return len(df)
    else:
        print("  File not found - please download manually")
        return 0


def main():
    """Download all datasets."""
    print("\n" + "#"*60)
    print("# HASSANIA DIALECT DATASET DOWNLOADER")
    print("#"*60)
    
    total_samples = 0
    
    # Download each dataset
    total_samples += download_dah_dataset()
    total_samples += download_hassaniya_speech_dataset()
    total_samples += download_casablanca_mauritanian()
    total_samples += download_hassaniya_sentiment()
    
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Total samples downloaded: {total_samples}")
    print(f"Data saved to: {RAW_DATA_DIR}")
    print("\nNext step: Run preprocess_data.py to combine and clean the data")


if __name__ == "__main__":
    main()
