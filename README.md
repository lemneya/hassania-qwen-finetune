# Hassania Dialect Fine-Tuning for Qwen 2.5

This repository contains compiled datasets and resources for fine-tuning the Qwen 2.5 language model on the Hassania (Hassaniya) Arabic dialect, spoken primarily in Mauritania, Western Sahara, and neighboring regions.

## Overview

Hassania is a low-resource Arabic dialect with limited digital representation. This project aims to:

1. **Aggregate** all available Hassania dialect datasets
2. **Preprocess** and normalize the data for fine-tuning
3. **Provide scripts** for fine-tuning Qwen 2.5 using QLoRA
4. **Document** best practices for low-resource dialect adaptation

## Dataset Summary

**Total Compiled Samples: 16,773**
**Unique Hassania Texts: 6,889**

### Source Datasets

| Dataset | Raw Samples | Processed Samples | Type | Source |
|---------|-------------|-------------------|------|--------|
| DAH | 3,002 | 7,211 | Bilingual (English-Hassania) | [Hugging Face](https://huggingface.co/datasets/hassan-IA/dah) |
| HASSANIYA Sentiment | 1,852 | 5,517 | Sentiment Analysis | [Mendeley Data](https://data.mendeley.com/datasets/m2swkr2bhx) |
| Casablanca (Mauritanian) | 1,906 | 3,520 | Multi-dialect ASR | [Hugging Face](https://huggingface.co/datasets/UBC-NLP/Casablanca) |
| Hassaniya Speech | 294 | 525 | Speech Transcriptions | [Hugging Face](https://huggingface.co/datasets/Mamadou-Aw/Hassaniya-speech-dataset) |

### Task Distribution

| Task | Samples |
|------|---------|
| Dialect Examples | 4,020 |
| Translation (Hassania → English) | 3,002 |
| Translation (English → Hassania) | 3,002 |
| Text Generation | 2,836 |
| Sentiment Analysis | 1,839 |
| Sentiment-guided Generation | 1,839 |
| Text Completion | 235 |

## Repository Structure

```
hassania-qwen-finetune/
├── data/
│   ├── raw/                    # Original downloaded datasets
│   │   ├── dah_dataset.csv
│   │   ├── hassaniya_speech_transcriptions.csv
│   │   ├── casablanca_mauritanian.csv
│   │   ├── hassaniya_sentiment.csv
│   │   └── H-Stopwords.txt
│   └── processed/              # Cleaned and combined datasets
│       ├── hassania_combined.jsonl   # Main training file (4.1 MB)
│       ├── hassania_combined.csv     # CSV version (3.0 MB)
│       ├── hassania_corpus.txt       # Raw text corpus (399 KB)
│       └── dataset_statistics.json
├── scripts/
│   ├── download_data.py        # Script to download all datasets
│   ├── preprocess_data.py      # Data cleaning and normalization
│   └── finetune_qwen.py        # QLoRA fine-tuning script
├── models/                     # Fine-tuned model checkpoints
├── docs/                       # Documentation and guides
└── README.md
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/lemneya/hassania-qwen-finetune.git
cd hassania-qwen-finetune
```

### 2. Set Up Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Download Datasets (Optional - data already included)

```bash
python scripts/download_data.py
```

### 4. Preprocess Data (Optional - processed data already included)

```bash
python scripts/preprocess_data.py
```

### 5. Fine-tune Qwen 2.5

```bash
python scripts/finetune_qwen.py \
    --model_name Qwen/Qwen2.5-1.5B-Instruct \
    --data_path ./data/processed/hassania_combined.jsonl \
    --output_dir ./models/qwen2.5-hassania \
    --num_epochs 3 \
    --lora_r 16 \
    --lora_alpha 32
```

## Data Format

The processed dataset (`hassania_combined.jsonl`) uses the instruction-tuning format:

```json
{
  "instruction": "Translate the following English text to Hassania Arabic dialect:\nHello, how are you?",
  "input": "",
  "output": "السلام عليكم، كيف حالك؟",
  "source": "dah",
  "task": "translation_en_to_hassania"
}
```

## Fine-Tuning Approach

We use **QLoRA (Quantized Low-Rank Adaptation)** for efficient fine-tuning:

- **4-bit quantization** to reduce memory usage
- **LoRA rank**: 16-64 (adjustable based on GPU memory)
- **LoRA alpha**: 32 (typically 2x rank)
- **Learning rate**: 2e-5
- **Batch size**: 1-4 with gradient accumulation

### Recommended Hardware

- **Minimum**: GPU with 4GB VRAM (Qwen2.5-0.5B)
- **Recommended**: GPU with 8-16GB VRAM (Qwen2.5-1.5B to 7B)
- **Optimal**: GPU with 24GB+ VRAM (Qwen2.5-14B+)

## Dataset Details

### DAH Dataset
- **Format**: CSV with columns: `english`, `hassaniya-ar`, `hassaniya-en`
- **Use Case**: Translation, bilingual understanding
- **License**: Available on Hugging Face

### Hassaniya Speech Dataset
- **Format**: Parquet with audio files and transcriptions
- **Use Case**: ASR, speech-to-text
- **License**: Available on Hugging Face

### HASSANIYA Sentiment Dataset
- **Format**: CSV with sentiment labels (positive, negative, neutral)
- **Use Case**: Sentiment analysis, text classification
- **License**: CC BY 4.0
- **Citation**: El ARBY, Med El Moustapha (2025), "HASSANIYA Dataset", Mendeley Data, V1, doi: 10.17632/m2swkr2bhx.1

### Casablanca Mauritanian Subset
- **Format**: Parquet with audio and transcriptions
- **Use Case**: Multi-dialect ASR, dialect identification
- **License**: CC-BY-NC-ND-4.0

## References

- [RIM-AI: Leveraging LLM Foundation Models for Hassania](https://www.rim-ai.com/en/blog/hassania-llm)
- [Qwen Arabic Fine-tuning Project](https://github.com/prakash-aryan/qwen-arabic-project)
- [Casablanca: Data and Models for Multidialectal Arabic Speech Recognition](https://arxiv.org/abs/2410.04527)

## Contributing

Contributions are welcome! If you have additional Hassania data or improvements to the fine-tuning pipeline, please open a pull request.

## License

This project is licensed under the MIT License. Individual datasets retain their original licenses as specified above.

## Acknowledgments

- Hassan-IA for the DAH dataset
- Mamadou-Aw for the Hassaniya Speech dataset
- Med El Moustapha El ARBY and Universite de Nouakchott for the HASSANIYA Sentiment dataset
- UBC-NLP for the Casablanca dataset
