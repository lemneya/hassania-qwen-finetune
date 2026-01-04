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
    """Download Hassaniya Speech dataset transcriptions from Hugging Face."""
    print("\n" + "="*60)
    print("Downloading Hassaniya Speech Dataset (Transcriptions Only)")
    print("="*60)
    
    try:
        # Load without audio decoding by using streaming and extracting text only
        from huggingface_hub import hf_hub_download
        import pyarrow.parquet as pq
        
        # Download the parquet file directly
        parquet_path = hf_hub_download(
            repo_id="Mamadou-Aw/Hassaniya-speech-dataset",
            filename="audios_dataset.parquet",
            repo_type="dataset"
        )
        
        # Read only the transcription column
        table = pq.read_table(parquet_path, columns=['transcription'])
        df = table.to_pandas()
        
        output_path = RAW_DATA_DIR / "hassaniya_speech_transcriptions.csv"
        df.to_csv(output_path, index=False)
        print(f"✓ Saved {len(df)} transcriptions to {output_path}")
        return len(df)
    except Exception as e:
        print(f"✗ Error downloading Hassaniya Speech dataset: {e}")
        return 0


def download_casablanca_mauritanian():
    """Download Mauritanian subset transcriptions from Casablanca dataset."""
    print("\n" + "="*60)
    print("Downloading Casablanca Dataset (Mauritanian Transcriptions)")
    print("="*60)
    
    try:
        from huggingface_hub import hf_hub_download
        import pyarrow.parquet as pq
        
        transcriptions = []
        
        # Download validation parquet files
        for i in range(2):
            try:
                parquet_path = hf_hub_download(
                    repo_id="UBC-NLP/Casablanca",
                    filename=f"Mauritania/validation-0000{i}-of-00002.parquet",
                    repo_type="dataset"
                )
                table = pq.read_table(parquet_path, columns=['seg_id', 'transcription', 'gender', 'duration'])
                df = table.to_pandas()
                df['split'] = 'validation'
                transcriptions.append(df)
                print(f"  ✓ Loaded validation part {i+1}")
            except Exception as e:
                print(f"  ✗ Error loading validation part {i+1}: {e}")
        
        # Download test parquet files
        for i in range(2):
            try:
                parquet_path = hf_hub_download(
                    repo_id="UBC-NLP/Casablanca",
                    filename=f"Mauritania/test-0000{i}-of-00002.parquet",
                    repo_type="dataset"
                )
                table = pq.read_table(parquet_path, columns=['seg_id', 'transcription', 'gender', 'duration'])
                df = table.to_pandas()
                df['split'] = 'test'
                transcriptions.append(df)
                print(f"  ✓ Loaded test part {i+1}")
            except Exception as e:
                print(f"  ✗ Error loading test part {i+1}: {e}")
        
        if transcriptions:
            combined_df = pd.concat(transcriptions, ignore_index=True)
            output_path = RAW_DATA_DIR / "casablanca_mauritanian.csv"
            combined_df.to_csv(output_path, index=False)
            print(f"✓ Saved {len(combined_df)} rows to {output_path}")
            return len(combined_df)
        else:
            print("✗ No data loaded from Casablanca dataset")
            return 0
            
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
    alt_path = RAW_DATA_DIR / "projectHA_DATASET - VF.csv"
    
    if sentiment_path.exists():
        df = pd.read_csv(sentiment_path)
        print(f"✓ Found existing file with {len(df)} rows")
        return len(df)
    elif alt_path.exists():
        df = pd.read_csv(alt_path)
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
