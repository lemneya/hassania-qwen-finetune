# Hassaniya Qwen Fine-Tuning Dataset

A curated, high-quality dataset for fine-tuning language models on the Hassaniya (Hassania) Arabic dialect spoken in Mauritania and Western Sahara.

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Training Samples** | 28,612 |
| **Validation Samples** | 500 |
| **Evaluation Samples** | 200 |
| **Quality Score** | 98.5% High Quality (≥90) |
| **Format** | OpenAI Chat Format (JSONL) |

## Repository Structure

```
hassania-qwen-finetune/
├── data/
│   ├── training/
│   │   ├── train_phase1_curated.jsonl   # 28,176 samples (Phase 1)
│   │   ├── train_phase2_quality.jsonl   # 28,612 samples (Phase 2)
│   │   ├── train_full.jsonl             # 28,612 samples (Full)
│   │   └── validation.jsonl             # 500 samples
│   └── evaluation/
│       ├── eval_holdout.jsonl           # 200 samples
│       ├── evaluation_benchmark.jsonl
│       └── benchmark_summary.json
├── reports/
│   ├── FINAL_PREPARATION_REPORT.md
│   └── optimized_data_analysis.png
├── scripts/
│   └── ...
└── README.md
```

## Data Format

Each sample follows the OpenAI chat format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant specialized in the Hassania (Hassaniya) Arabic dialect..."
    },
    {
      "role": "user",
      "content": "Translate to Hassaniya: Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "اشحالك"
    }
  ]
}
```

## Training Strategy

### Phase 1: Quick Validation
- **File:** `data/training/train_phase1_curated.jsonl`
- **Samples:** 28,176
- **Epochs:** 3
- **Time:** ~1-2 hours
- **Purpose:** Verify training pipeline works

### Phase 2: Main Training
- **File:** `data/training/train_phase2_quality.jsonl`
- **Samples:** 28,612
- **Epochs:** 3-5
- **Time:** ~4-8 hours
- **Purpose:** Full fine-tuning

### Evaluation
- **File:** `data/evaluation/eval_holdout.jsonl`
- **Samples:** 200 (50 per category)
- **Categories:** Translation, Generation, Greeting, General

## Quality Metrics

- **98.5%** of samples scored ≥90 (Tier 1 - High Quality)
- **Token range:** 40-100 tokens (optimal for training)
- **100%** proper OpenAI chat format
- **0%** duplicates (fully deduplicated)

## Evaluation Categories

| Category | Samples | Description |
|----------|---------|-------------|
| Translation | 50 | English ↔ Hassaniya translation |
| Generation | 50 | Hassaniya text generation |
| Greeting | 50 | Common greetings and phrases |
| General | 50 | General conversation |

## Usage

### For OpenAI Fine-Tuning
```bash
openai api fine_tunes.create \
  -t data/training/train_phase2_quality.jsonl \
  -v data/training/validation.jsonl \
  -m gpt-3.5-turbo
```

### For Local Fine-Tuning (Qwen, LLaMA, etc.)
The JSONL format is compatible with most fine-tuning frameworks including:
- Hugging Face Transformers
- Axolotl
- LLaMA-Factory
- OpenAI API

## Original Data Sources

| Dataset | License | Citation |
|---------|---------|----------|
| [DAH](https://huggingface.co/datasets/hassan-IA/dah) | HF | Hassan-IA |
| [HASSANIYA Sentiment](https://data.mendeley.com/datasets/m2swkr2bhx) | CC BY 4.0 | El ARBY (2025) |
| [Casablanca](https://huggingface.co/datasets/UBC-NLP/Casablanca) | CC-BY-NC-ND-4.0 | UBC-NLP |
| [Hassaniya Speech](https://huggingface.co/datasets/Mamadou-Aw/Hassaniya-speech-dataset) | HF | Mamadou-Aw |
| [Peace Corps Materials](https://www.livelingua.com/course/peace-corps/arabic-(mauritanian)-language-lessons) | Public | Peace Corps |

## License

This project is licensed under the MIT License. Individual datasets retain their original licenses as specified above.

---

*Prepared by Manus AI*
