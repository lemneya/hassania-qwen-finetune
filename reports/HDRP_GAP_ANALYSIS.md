# HDRP Protocol Gap Analysis

**Generated:** January 5, 2026

This report analyzes the `hassania-qwen-finetune` repository against the **HDRP Corpus Build Protocol v1.0**.

---

## A) Standard Data Contract

### A1) Folder Contract

| HDRP Requirement | Current Status | Gap |
|------------------|----------------|-----|
| `hdrp/data/raw/` | ❌ Missing | **Critical** - No raw data folders (whatsapp, facebook, etc.) |
| `hdrp/data/processed/episodes/` | ❌ Missing | **Critical** - No `episodes.jsonl` in this structure |
| `hdrp/data/processed/exports/` | ❌ Missing | **Critical** - No DAPT/SFT/Eval exports in this structure |
| `hdrp/specs/` | ❌ Missing | **Critical** - No `sampling_config.json` |
| `hdrp/pipeline/` | ❌ Missing | **Critical** - No refinery pipeline scripts |
| `hdrp/audit/` | ❌ Missing | **Critical** - No audit trail |

**Assessment:** The current repository structure **does not comply** with the HDRP folder contract. It uses a simplified `data/training` and `data/evaluation` structure.

### A2) Batch Contract

| HDRP Requirement | Current Status | Gap |
|------------------|----------------|-----|
| `batch_YYYYMMDD_HHMM/` | ❌ Missing | **Critical** - Data is not organized into timestamped batches |
| `manifest.json` | ❌ Missing | **Critical** - No batch manifests |
| `episodes.jsonl` | ❌ Missing | **Critical** - No per-batch episode files |

**Assessment:** The repository **lacks the batch-based processing** required by HDRP. Data is aggregated into large training files, not processed in traceable batches.

---

## B) Episode Schema

| HDRP Field | Current Status | Gap |
|----------------|----------------|-----|
| `episode_id` | ❌ Missing | **Critical** - No unique episode IDs |
| `source_type` | ❌ Missing | **Critical** - Source is in `_source` field, not standardized |
| `source_uri` | ❌ Missing | **Critical** - No source URI for traceability |
| `captured_at` | ❌ Missing | **Critical** - No capture timestamp |
| `bucket` | ❌ Missing | **Critical** - No standardized buckets (e.g., `everyday_chat`) |
| `interaction_mode` | ❌ Missing | **Critical** - No mode (dialogue, qa, etc.) |
| `topic` | ❌ Missing | **Critical** - No topic classification |
| `heat` | ❌ Missing | **Critical** - No heat score |
| `segments` | ❌ Missing | **Critical** - Data is in `messages` array, not `segments` |
| `segment_id` | ❌ Missing | **Critical** - No segment IDs |
| `speaker` | ✅ Present (as `role`) | Minor - `role` needs to be mapped to `speaker` |
| `raw_text` | ✅ Present (as `content`) | Minor - `content` needs to be mapped to `raw_text` |
| `text_variants` | ❌ Missing | **Critical** - No `norm`, `diac`, `diac_candidate` fields |
| `lang_probs` | ❌ Missing | **Critical** - No language probability scores |
| `dqs` | ❌ Missing | **Critical** - No Data Quality Score (DQS) |
| `decision` | ❌ Missing | **Critical** - No ACCEPT/REVIEW/REJECT decision |
| `flags` | ❌ Missing | **Critical** - No quality flags |

**Assessment:** The current data format (`messages` array) is **fundamentally different** from the HDRP `Episode` schema. It lacks almost all of the required metadata and processing fields.

---

## D) Refinery Stages

| HDRP Stage | Current Status | Gap |
|--------------|----------------|-----|
| **D1) Normalize** | ❌ Missing | **Critical** - No normalization function (elongation, Alef, etc.) |
| **D2) Diacritize** | ❌ Missing | **Critical** - No diacritization pipeline or confidence scores |
| **D3) DQS Scoring** | ❌ Missing | **Critical** - No DQS calculation |
| **D4) Dedup** | ✅ Partial | Deduplication was run, but not based on `norm` text hash |

**Assessment:** The dataset has not been processed through the HDRP refinery stages. Key steps like normalization, diacritization, and DQS scoring are missing.

---

## E) Export Products

| HDRP Export | Current Status | Gap |
|---------------|----------------|-----|
| **E1) Split Rule** | ❌ Violated | Split is not by `episode_id` (leakage risk) |
| **E2) DAPT Export** | ❌ Missing | No DAPT export with `{"text":"..."}` format |
| **E3) SFT Export** | ✅ Partial | `messages` format is similar, but lacks `meta` field |
| **E4) DIAC Shards** | ❌ Missing | No diacritization review queue |
| **E5) Run Manifest** | ❌ Missing | No run manifests with leakage checks |

**Assessment:** The current training files do not meet the HDRP export specifications. The train/val split method is a major violation that could lead to data leakage.

---

## F) Sampling Configuration

| HDRP Requirement | Current Status | Gap |
|------------------|----------------|-----|
| `sampling_config.json` | ❌ Missing | **Critical** - No sampling configuration file |
| DAPT/SFT weights | ❌ Not applied | **Critical** - Data is not sampled according to chat-first weights |
| Global caps | ❌ Not applied | **Critical** - No caps on influencers, monologues, etc. |

**Assessment:** The dataset is not balanced according to the **chat-first** sampling strategy. It is a simple aggregation of all available data.

---

## H) Definition of Done Gates

| HDRP Gate | Current Status | Gap |
|-------------|----------------|-----|
| **H1) Corpus Gate** | ❌ Not Met | **Critical** - DAPT/SFT exports don't exist, dialogue quotas not enforced |
| **H2) DIAC Gate** | ❌ Not Met | **Critical** - No diacritization pipeline or gold set |

**Assessment:** The project has not met the minimum requirements for a "ready" corpus according to HDRP.

---

## Overall Conclusion

The current `hassania-qwen-finetune` repository is a **Level 0** dataset (raw aggregation) and **does not comply with the HDRP protocol**. To become compliant, it would require a complete overhaul of the data processing pipeline, including:

1. **Implementing the HDRP folder structure**
2. **Converting all data into the `Episode` schema**
3. **Building the Refinery pipeline** (Normalize, Diacritize, DQS, Dedup)
4. **Creating a `sampling_config.json`** and re-sampling the data
5. **Generating compliant DAPT and SFT exports** with proper train/eval splits

**Recommendation:** Treat the current dataset as a raw input and build an HDRP-compliant pipeline from scratch to process it.
