# Hassaniya Qwen Fine-Tuning - HDRP Compliant

A fully HDRP-compliant (Hassaniya Dialect Resource Protocol) dataset and pipeline for fine-tuning language models on the Hassaniya Arabic dialect.

## Protocol Compliance Status

| Gate | Requirement | Achieved | Status |
|------|-------------|----------|--------|
| **H1 Corpus Gate** | - | - | ✓ PASSED |
| DAPT Tokens | ≥50,000 | 323,900 | ✓ |
| SFT Turns | ≥5,000 | 21,336 | ✓ |
| Dialogue Ratio | ≥60% | 100% | ✓ |
| Leakage | 0 | 0 | ✓ |

## Repository Structure

```
hassania-qwen-finetune/
├── hdrp/
│   ├── data/
│   │   ├── raw/                    # Source data by type
│   │   │   ├── whatsapp_exports/
│   │   │   ├── facebook/
│   │   │   ├── websites/
│   │   │   ├── youtube_transcripts/
│   │   │   ├── tv_radio/
│   │   │   ├── parliament/
│   │   │   ├── film/
│   │   │   ├── poetry_azawan/
│   │   │   ├── celebrities/
│   │   │   └── religion/
│   │   └── processed/
│   │       ├── episodes/           # HDRP Episode format
│   │       ├── dqs/                # Quality-scored data
│   │       ├── exports/            # Train-ready outputs
│   │       │   ├── dapt/           # Continued pretraining
│   │       │   ├── sft/            # Instruction tuning
│   │       │   └── eval/           # Evaluation set
│   │       └── manifests/          # Run manifests
│   ├── pipeline/
│   │   ├── collector/              # Episode converter
│   │   └── refinery/               # Processing pipeline
│   ├── specs/
│   │   └── sampling_config.json    # Chat-first weights
│   └── docs/
│       └── README.md               # HDRP documentation
└── README.md
```

## Train-Ready Exports

| File | Records | Purpose |
|------|---------|---------|
| `hdrp/data/processed/exports/dapt/dapt_hassaniya_v2.jsonl` | 6,478 | Continued pretraining |
| `hdrp/data/processed/exports/sft/sft_hassaniya_v2.jsonl` | 10,668 | Instruction tuning |
| `hdrp/data/processed/exports/eval/eval_hassaniya_v2.jsonl` | 593 | Evaluation |

## Data Formats

### DAPT Format
```json
{"text": "<NORMALIZED_TEXT>", "meta": {"episode_id": "...", "bucket": "...", "topic": "..."}}
```

### SFT Format
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful Hassaniya assistant."},
    {"role": "user", "content": "<USER_TURN>"},
    {"role": "assistant", "content": "<ASSISTANT_TURN>"}
  ],
  "meta": {"episode_id": "...", "bucket": "...", "topic": "..."}
}
```

## Chat-First Sampling

### DAPT Weights
| Bucket | Weight |
|--------|--------|
| everyday_chat | 75% |
| marketplace_qa | 10% |
| public_comments | 7% |
| tv_discussion | 5% |
| culture_story_poetry | 2% |
| monologue_specialist | 1% |

### SFT Weights
| Bucket | Weight |
|--------|--------|
| everyday_chat | 85% |
| public_comments | 10% |
| tv_discussion | 5% |

## Pipeline Usage

```bash
# Step 1: Convert source data to Episodes
python3 hdrp/pipeline/collector/convert_to_episodes.py

# Step 2: Run Refinery (Normalize → DQS → Dedup)
python3 hdrp/pipeline/refinery/refinery.py

# Step 3: Export train-ready data
python3 hdrp/pipeline/refinery/exporter_v2.py
```

## Episode Schema

Each episode follows the HDRP standard:

```json
{
  "episode_id": "EP-20260105-ABC123",
  "source_type": "whatsapp_desktop|facebook|website|...",
  "bucket": "everyday_chat|marketplace_qa|public_comments|...",
  "interaction_mode": "dialogue|qa|narrative|monologue",
  "topic": "social_family|religion|trade_econ|...",
  "heat": 0,
  "segments": [
    {
      "segment_id": "SEG-001",
      "speaker": "spk1|spk2",
      "raw_text": "...",
      "text_variants": {"raw": "...", "norm": "...", "diac": null},
      "lang_probs": {"hassaniya": 0.95, "msa": 0.03, "french": 0.02},
      "dqs": 85,
      "decision": "ACCEPT|REVIEW|REJECT"
    }
  ]
}
```

## Leakage Prevention

- Split by `episode_id` only (never by segment)
- Hash-based verification ensures no text overlap between train/eval
- All manifests include leakage check results

## License

MIT License. Individual source datasets retain their original licenses.

---

*HDRP Protocol v1.0 Compliant*
