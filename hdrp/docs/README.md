# HDRP - Hassaniya Dialect Resource Protocol

## Overview

This directory contains the HDRP-compliant pipeline for processing Hassaniya dialect data for LLM fine-tuning.

## Protocol Compliance

| Gate | Status | Details |
|------|--------|---------|
| **H1 Corpus Gate** | ✓ PASSED | All requirements met |
| ≥50k tokens DAPT | ✓ | ~323,900 tokens |
| ≥5k turns SFT | ✓ | ~21,336 turns |
| Dialogue ≥60% | ✓ | 100% |
| No leakage | ✓ | 0 overlaps |

## Directory Structure

```
hdrp/
├── data/
│   ├── raw/                    # Source data by type
│   │   ├── whatsapp_exports/
│   │   ├── facebook/
│   │   ├── websites/
│   │   └── ...
│   └── processed/
│       ├── episodes/           # HDRP Episode format
│       ├── dqs/                # Quality-scored data
│       ├── exports/            # Train-ready outputs
│       │   ├── dapt/           # Continued pretraining
│       │   ├── sft/            # Instruction tuning
│       │   └── eval/           # Evaluation set
│       └── manifests/          # Run manifests
├── pipeline/
│   ├── collector/              # Data collection scripts
│   └── refinery/               # Processing pipeline
├── specs/
│   └── sampling_config.json    # Chat-first sampling weights
└── docs/
```

## Pipeline Stages

### 1. Collector (convert_to_episodes.py)
Converts source data to HDRP Episode schema:
- Generates unique `episode_id`
- Classifies `bucket`, `topic`, `interaction_mode`
- Creates `segments` with speaker attribution

### 2. Refinery (refinery.py)
Processes episodes through:
- **D1 Normalize**: Text normalization (Alef, elongation, whitespace)
- **D3 DQS Score**: Data Quality Score (0-100)
- **D4 Dedup**: Hash-based deduplication

### 3. Exporter (exporter_v2.py)
Generates train-ready outputs:
- **DAPT**: `{"text":"...", "meta":{...}}`
- **SFT**: `{"messages":[...], "meta":{...}}`
- **Eval**: Held-out evaluation set

## Sampling Configuration

### DAPT Weights (Chat-First)
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

## Usage

```bash
# Step 1: Convert to Episodes
python3 hdrp/pipeline/collector/convert_to_episodes.py

# Step 2: Run Refinery
python3 hdrp/pipeline/refinery/refinery.py

# Step 3: Export
python3 hdrp/pipeline/refinery/exporter_v2.py
```

## Output Files

| File | Records | Purpose |
|------|---------|---------|
| `dapt_hassaniya_v2.jsonl` | 6,478 | Continued pretraining |
| `sft_hassaniya_v2.jsonl` | 10,668 | Instruction tuning |
| `eval_hassaniya_v2.jsonl` | 593 | Evaluation |

## Episode Schema

```json
{
  "episode_id": "EP-20260105-ABC123",
  "source_type": "whatsapp_desktop|facebook|website|...",
  "source_uri": "string",
  "captured_at": "ISO-8601",
  "bucket": "everyday_chat|marketplace_qa|...",
  "interaction_mode": "dialogue|qa|narrative|monologue",
  "topic": "social_family|religion|trade_econ|...",
  "heat": 0,
  "segments": [
    {
      "segment_id": "SEG-001",
      "speaker": "spk1|spk2|unknown",
      "raw_text": "string",
      "text_variants": {
        "raw": "string",
        "norm": "string",
        "diac": null,
        "diac_candidate": null
      },
      "lang_probs": {"hassaniya": 0.95, "msa": 0.03, "french": 0.02},
      "dqs": 85,
      "decision": "ACCEPT|REVIEW|REJECT",
      "flags": []
    }
  ]
}
```

## Leakage Prevention

- Split by `episode_id` only (never by segment)
- Hash-based verification ensures no text overlap
- Manifest includes leakage check results
