# Hassania Dialect Fine-Tuning for Qwen 2.5

This repository contains compiled and enriched datasets for fine-tuning the Qwen 2.5 language model on the Hassania (Hassaniya) Arabic dialect, spoken primarily in Mauritania, Western Sahara, and neighboring regions.

## Overview

Hassania is a low-resource Arabic dialect with limited digital representation. This project aims to:

1. **Aggregate** all available Hassania dialect datasets
2. **Enrich** the data with literature, poetry, and synthetic generation
3. **Preprocess** and normalize the data for fine-tuning
4. **Provide scripts** for fine-tuning Qwen 2.5 using QLoRA

## Dataset Summary

### Final Enriched Dataset

| Metric | Value |
|--------|-------|
| **Total Unique Samples** | 12,240 |
| **Training Samples** | 11,628 |
| **Validation Samples** | 612 |
| **Training File Size** | 2.9 MB |

### Data Sources

| Source | Samples | Type |
|--------|---------|------|
| DAH Dataset | 5,971 | Bilingual (English-Hassania) |
| Diwan Poetry | 1,934 | Literature/Poetry |
| Casablanca (Mauritanian) | 1,884 | Multi-dialect ASR |
| HASSANIYA Sentiment | 1,828 | Sentiment Analysis |
| Hassaniya Speech | 290 | Speech Transcriptions |
| Synthetic (OpenAI) | 221 | AI-Generated |
| Hassaniya Dictionary | 112 | Vocabulary |

### Task Distribution

| Task | Samples |
|------|---------|
| Translation (EN→Hassania) | 2,986 |
| Translation (Hassania→EN) | 2,985 |
| Dialect Examples | 1,939 |
| Text Generation | 1,934 |
| Sentiment Generation | 1,824 |
| Text Completion | 235 |
| Synthetic Content | 134 |
| Vocabulary | 112 |

## Repository Structure

```
hassania-qwen-finetune/
├── data/
│   ├── raw/                    # Original downloaded datasets
│   ├── processed/              # Cleaned individual datasets
│   ├── enrichment/             # Additional data sources
│   │   ├── books/              # Poetry and literature
│   │   ├── processed_books/    # Processed book samples
│   │   └── synthetic/          # AI-generated samples
│   └── final/                  # Final merged datasets
│       ├── hassania_enriched_full.jsonl  # Complete dataset
│       ├── hassania_train.jsonl          # Training set (95%)
│       ├── hassania_val.jsonl            # Validation set (5%)
│       └── dataset_statistics.json
├── scripts/
│   ├── download_data.py        # Download all datasets
│   ├── preprocess_data.py      # Clean and normalize data
│   ├── process_books.py        # Process literature
│   ├── generate_synthetic_data.py  # Generate synthetic data
│   ├── merge_enriched_data.py  # Merge all sources
│   └── finetune_qwen.py        # QLoRA fine-tuning script
├── models/                     # Fine-tuned model checkpoints
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

### 3. Fine-tune Qwen 2.5

```bash
python scripts/finetune_qwen.py \
    --model_name Qwen/Qwen2.5-1.5B-Instruct \
    --data_path ./data/final/hassania_train.jsonl \
    --val_path ./data/final/hassania_val.jsonl \
    --output_dir ./models/qwen2.5-hassania \
    --num_epochs 3 \
    --lora_r 16 \
    --lora_alpha 32
```

## Data Format

The dataset uses the instruction-tuning format:

```json
{
  "instruction": "Translate to Hassania Arabic: Hello, how are you?",
  "input": "",
  "output": "السلام عليكم، شخبارك؟",
  "source": "synthetic_openai",
  "task": "translation"
}
```

## Data Enrichment Process

### 1. Original Datasets
- **DAH**: Bilingual English-Hassania translations from Hugging Face
- **HASSANIYA Sentiment**: Facebook comments with sentiment labels from Mendeley
- **Casablanca**: Mauritanian subset from multi-dialect ASR corpus
- **Hassaniya Speech**: Audio transcriptions from Hugging Face

### 2. Literature & Poetry
- **Diwan Wald Anjarto**: Traditional Hassania poetry collection (1,934 text segments)
- **English-Hassaniya Dictionary**: Vocabulary and word translations

### 3. Synthetic Generation
- Generated using GPT-4o with few-shot prompting
- Includes: conversations, proverbs, poetry, daily expressions, stories
- Uses authentic Hassania examples as reference

## Fine-Tuning Approach

We use **QLoRA (Quantized Low-Rank Adaptation)** for efficient fine-tuning:

- **4-bit quantization** to reduce memory usage
- **LoRA rank**: 16-64 (adjustable based on GPU memory)
- **LoRA alpha**: 32 (typically 2x rank)
- **Learning rate**: 2e-5
- **Batch size**: 1-4 with gradient accumulation

### Recommended Hardware

| Model Size | Minimum VRAM | Recommended |
|------------|--------------|-------------|
| Qwen2.5-0.5B | 4GB | Consumer GPU |
| Qwen2.5-1.5B | 8GB | RTX 3060/4060 |
| Qwen2.5-7B | 16GB | RTX 3090/4080 |
| Qwen2.5-14B+ | 24GB+ | A100/H100 |

## Original Data Sources

| Dataset | License | Citation |
|---------|---------|----------|
| [DAH](https://huggingface.co/datasets/hassan-IA/dah) | HF | Hassan-IA |
| [HASSANIYA Sentiment](https://data.mendeley.com/datasets/m2swkr2bhx) | CC BY 4.0 | El ARBY (2025) |
| [Casablanca](https://huggingface.co/datasets/UBC-NLP/Casablanca) | CC-BY-NC-ND-4.0 | UBC-NLP |
| [Hassaniya Speech](https://huggingface.co/datasets/Mamadou-Aw/Hassaniya-speech-dataset) | HF | Mamadou-Aw |
| [Diwan Poetry](https://archive.org/details/akforda_yahoo) | Public | Archive.org |
| [Dictionary](https://archive.org/details/eng-hass-dict-a-z) | Public | Archive.org |

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
- Archive.org for hosting Mauritanian literature
- OpenAI for synthetic data generation capabilities
