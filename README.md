# Hassania Dialect Fine-Tuning for Qwen 2.5

This repository contains compiled datasets and resources for fine-tuning the Qwen 2.5 language model on the Hassania (Hassaniya) Arabic dialect, spoken primarily in Mauritania, Western Sahara, and neighboring regions.

## Overview

Hassania is a low-resource Arabic dialect with limited digital representation. This project aims to:

1. **Aggregate** all available Hassania dialect datasets
2. **Preprocess** and normalize the data for fine-tuning
3. **Provide scripts** for fine-tuning Qwen 2.5 using QLoRA
4. **Document** best practices for low-resource dialect adaptation

## Dataset Sources

| Dataset | Size | Type | Source |
|---------|------|------|--------|
| DAH | 3,002 rows | Bilingual (English-Hassania) | [Hugging Face](https://huggingface.co/datasets/hassan-IA/dah) |
| Hassaniya Speech | 294 rows | Audio + Transcription | [Hugging Face](https://huggingface.co/datasets/Mamadou-Aw/Hassaniya-speech-dataset) |
| HASSANIYA Sentiment | 2,000 records | Sentiment Analysis | [Mendeley Data](https://data.mendeley.com/datasets/m2swkr2bhx) |
| Casablanca (Mauritanian) | 1,910 rows | Multi-dialect ASR | [Hugging Face](https://huggingface.co/datasets/UBC-NLP/Casablanca) |

**Total compiled samples: ~7,200+ text/audio samples**

## Repository Structure

```
hassania-qwen-finetune/
├── data/
│   ├── raw/                    # Original downloaded datasets
│   └── processed/              # Cleaned and combined datasets
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
git clone https://github.com/YOUR_USERNAME/hassania-qwen-finetune.git
cd hassania-qwen-finetune
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Datasets

```bash
python scripts/download_data.py
```

### 4. Preprocess Data

```bash
python scripts/preprocess_data.py
```

### 5. Fine-tune Qwen 2.5

```bash
python scripts/finetune_qwen.py \
    --model_name Qwen/Qwen2.5-1.5B \
    --data_path ./data/processed/hassania_combined.jsonl \
    --output_dir ./models/qwen2.5-hassania \
    --num_epochs 3
```

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

### Casablanca Mauritanian Subset
- **Format**: Parquet with audio and transcriptions
- **Use Case**: Multi-dialect ASR, dialect identification
- **License**: CC-BY-NC-ND-4.0

## Fine-Tuning Approach

We use **QLoRA (Quantized Low-Rank Adaptation)** for efficient fine-tuning:

- **4-bit quantization** to reduce memory usage
- **LoRA rank**: 16-64 (adjustable based on GPU memory)
- **Learning rate**: 2e-5
- **Batch size**: 1-4 with gradient accumulation

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
- Universite de Nouakchott for the HASSANIYA Sentiment dataset
- UBC-NLP for the Casablanca dataset
