# Hassania Dialect Fine-Tuning for Qwen 2.5

This repository contains compiled and enriched datasets for fine-tuning the Qwen 2.5 language model on the Hassania (Hassaniya) Arabic dialect, spoken primarily in Mauritania, Western Sahara, and neighboring regions.

## Overview

Hassania is a low-resource Arabic dialect with limited digital representation. This project aims to:

1. **Aggregate** all available Hassania dialect datasets
2. **Enrich** the data with literature, poetry, Peace Corps materials, and synthetic generation
3. **Preprocess** and normalize the data for fine-tuning
4. **Provide scripts** for fine-tuning Qwen 2.5 using QLoRA

## Dataset Summary

### Final Enriched Dataset (Latest)

| Metric | Value |
|--------|-------|
| **Total Unique Samples** | 17,877 |
| **Training Samples** | 16,984 |
| **Validation Samples** | 893 |
| **Unique Corpus Texts** | 20,076 |
| **Training File Size** | 4.5 MB |

### Data Sources

| Source | Samples | Type |
|--------|---------|------|
| DAH Dataset | 5,659 | Bilingual (English-Hassania) |
| Diwan Wald Anjarto | 1,839 | Classical Poetry |
| Diwan Poetry (Archive.org) | 1,826 | Traditional Poetry |
| Casablanca (Mauritanian) | 1,806 | Multi-dialect ASR |
| HASSANIYA Sentiment | 1,737 | Sentiment Analysis |
| English-Hassaniya Dictionary | 1,159 | Vocabulary |
| **Peace Corps Arabic Course** | 986 | Language Learning (Romanized) |
| **Peace Corps Grammar Handbook** | 762 | Grammar Examples (Romanized) |
| Mrug Alharf | 664 | First Hassaniya Book (19th c.) |
| Aesthetics of Hassani Poetry | 570 | Literary Analysis |
| Hassaniya Speech | 276 | Speech Transcriptions |
| **DLIFLC Cultural Orientation** | 244 | Cultural/Language Guide |
| Synthetic (OpenAI GPT-4o) | 221 | AI-Generated |
| Hassaniya Dictionary | 102 | Additional Vocabulary |
| Hassaniya Linguistic Paper | 26 | Academic Linguistics |

### Task Distribution

| Task | Samples |
|------|---------|
| Dialect Examples | 3,395 |
| Translation (EN→Hassania) | 2,837 |
| Translation (Hassania→EN) | 2,822 |
| Poetry (لغن) | 1,957 |
| Text Generation | 1,839 |
| Sentiment Generation | 1,733 |
| **Hassaniya Romanized** | 1,644 |
| Text Completion | 949 |
| **Grammar Examples** | 286 |
| Vocabulary (Romanized) | 88 |
| Other | 327 |

## Repository Structure

```
hassania-qwen-finetune/
├── data/
│   ├── raw/                        # Original downloaded datasets
│   ├── processed/                  # Cleaned individual datasets
│   ├── enrichment/                 # Additional data sources
│   │   ├── books/                  # Poetry and literature PDFs/texts
│   │   ├── books_processed/        # Extracted book samples
│   │   ├── peace_corps/            # Peace Corps language materials
│   │   ├── peace_corps_processed/  # Processed Peace Corps samples
│   │   └── synthetic/              # AI-generated samples
│   ├── final_enriched/             # Previous enriched version
│   └── final_with_peace_corps/     # Latest dataset ⭐
│       ├── hassania_train.jsonl    # Training set (4.5 MB)
│       ├── hassania_val.jsonl      # Validation set (240 KB)
│       ├── hassania_corpus.txt     # Raw text corpus
│       └── dataset_statistics.json
├── scripts/
│   ├── download_data.py            # Download all datasets
│   ├── preprocess_data.py          # Clean and normalize data
│   ├── process_all_books.py        # Process literature
│   ├── process_peace_corps.py      # Process Peace Corps materials
│   ├── generate_synthetic_data.py  # Generate synthetic data
│   ├── merge_peace_corps_data.py   # Merge all sources
│   └── finetune_qwen.py            # QLoRA fine-tuning script
├── models/                         # Fine-tuned model checkpoints
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
    --data_path ./data/final_with_peace_corps/hassania_train.jsonl \
    --val_path ./data/final_with_peace_corps/hassania_val.jsonl \
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
  "source": "dah",
  "task": "translation_en_to_hassania"
}
```

## Peace Corps Materials

The following Peace Corps Hassaniya language learning materials were processed:

1. **Mauritanian Arabic Communication and Culture Handbook** - Comprehensive language course with dialogues, vocabulary, and cultural notes
2. **Mauritanian Arabic Grammar Handbook** - Grammar explanations with romanized Hassaniya examples
3. **Hassaniya Language Lessons** - Basic vocabulary and phrases
4. **DLIFLC Hassaniya Cultural Orientation** - Defense Language Institute guide with cultural and linguistic content

Note: Peace Corps materials use romanized transcription (Latin script) for Hassaniya, which provides valuable phonetic information for the dialect.

## Book Sources

The following Hassania literature was collected and processed:

1. **جماليات الشعر العربي الحساني** - Aesthetics of Hassani Arabic Poetry
2. **امروك الحرف (Mrug Alharf)** - First book written in Hassaniya dialect (19th century)
3. **ديوان الشعر الحساني** - Hassania Poetry Collection from Archive.org
4. **قاموس إنجليزي-حساني** - English-Hassaniya Dictionary

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
| [Chinguitipedia Books](https://chinguitipedia.net) | Various | Chinguitipedia |
| [Peace Corps Materials](https://www.livelingua.com/course/peace-corps/arabic-(mauritanian)-language-lessons) | Public | Peace Corps |
| [DLIFLC Materials](https://fieldsupport.dliflc.edu/products/hassaniya/) | Public | DLIFLC |

## References

- [RIM-AI: Leveraging LLM Foundation Models for Hassania](https://www.rim-ai.com/en/blog/hassania-llm)
- [Qwen Arabic Fine-tuning Project](https://github.com/prakash-aryan/qwen-arabic-project)
- [Casablanca: Data and Models for Multidialectal Arabic Speech Recognition](https://arxiv.org/abs/2410.04527)
- [Hassâniyya Arabic - Encyclopedia of Arabic Language and Linguistics](https://shs.hal.science/halshs-00563853)

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
- Chinguitipedia for Mauritanian cultural resources
- Peace Corps for language learning materials
- Defense Language Institute (DLIFLC) for cultural orientation materials
- OpenAI for synthetic data generation capabilities
