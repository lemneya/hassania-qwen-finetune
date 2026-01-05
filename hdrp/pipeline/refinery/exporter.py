#!/usr/bin/env python3
"""
HDRP Exporter
Generates DAPT, SFT, and Eval exports with chat-first sampling.
"""

import json
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Paths
BASE_DIR = Path("/tmp/hassania-qwen-finetune-main")
DQS_DIR = BASE_DIR / "hdrp/data/processed/dqs"
EXPORTS_DIR = BASE_DIR / "hdrp/data/processed/exports"
MANIFESTS_DIR = BASE_DIR / "hdrp/data/processed/manifests"
SPECS_DIR = BASE_DIR / "hdrp/specs"

# Create export directories
(EXPORTS_DIR / "dapt").mkdir(parents=True, exist_ok=True)
(EXPORTS_DIR / "sft").mkdir(parents=True, exist_ok=True)
(EXPORTS_DIR / "eval").mkdir(parents=True, exist_ok=True)

# Load sampling config
def load_sampling_config() -> Dict:
    config_file = SPECS_DIR / "sampling_config.json"
    with open(config_file, 'r') as f:
        return json.load(f)

# ============================================================
# SPLIT BY EPISODE (E1)
# ============================================================

def split_episodes(episodes: List[Dict], eval_ratio: float = 0.10) -> tuple:
    """
    Split by episode_id only (never by segment) to avoid leakage.
    """
    random.seed(42)  # Reproducible split
    
    # Shuffle episode IDs
    episode_ids = [ep["episode_id"] for ep in episodes]
    random.shuffle(episode_ids)
    
    # Split
    split_idx = int(len(episode_ids) * (1 - eval_ratio))
    train_ids = set(episode_ids[:split_idx])
    eval_ids = set(episode_ids[split_idx:])
    
    train_episodes = [ep for ep in episodes if ep["episode_id"] in train_ids]
    eval_episodes = [ep for ep in episodes if ep["episode_id"] in eval_ids]
    
    return train_episodes, eval_episodes

# ============================================================
# DAPT EXPORT (E2)
# ============================================================

def export_dapt(episodes: List[Dict], config: Dict, output_file: Path) -> int:
    """
    Export DAPT (continued pretraining) format.
    Format: {"text":"<NORM_TEXT>", "meta":{"episode_id":"...","bucket":"...","topic":"..."}}
    
    Diacritics mixing (hard):
    - 90%: use norm
    - 10%: use diac only from diac_auto eligible segments
    """
    dapt_weights = config["dapt_weights"]
    diac_ratio = config.get("diac_mixing_ratio", 0.10)
    
    # Group episodes by bucket
    bucket_episodes = defaultdict(list)
    for ep in episodes:
        bucket = ep.get("bucket", "everyday_chat")
        # Map to DAPT weight categories
        if bucket in ["parliament_politics"]:
            bucket = "monologue_specialist"
        bucket_episodes[bucket].append(ep)
    
    # Sample according to weights
    sampled_records = []
    
    for bucket, weight in dapt_weights.items():
        available = bucket_episodes.get(bucket, [])
        if not available:
            continue
        
        # Calculate target count based on weight
        target_count = int(len(episodes) * weight)
        
        # Sample with replacement if needed
        if len(available) >= target_count:
            sampled = random.sample(available, target_count)
        else:
            sampled = available * (target_count // len(available) + 1)
            sampled = sampled[:target_count]
        
        for ep in sampled:
            for seg in ep.get("segments", []):
                if seg.get("decision") != "ACCEPT":
                    continue
                
                text_variants = seg.get("text_variants", {})
                
                # Diacritics mixing
                if random.random() < diac_ratio and text_variants.get("diac"):
                    text = text_variants["diac"]
                else:
                    text = text_variants.get("norm", text_variants.get("raw", ""))
                
                if not text or len(text.strip()) < 10:
                    continue
                
                record = {
                    "text": text,
                    "meta": {
                        "episode_id": ep["episode_id"],
                        "bucket": ep.get("bucket", "unknown"),
                        "topic": ep.get("topic", "mixed")
                    }
                }
                sampled_records.append(record)
    
    # Shuffle and write
    random.shuffle(sampled_records)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in sampled_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(sampled_records)

# ============================================================
# SFT EXPORT (E3)
# ============================================================

def export_sft(episodes: List[Dict], config: Dict, output_file: Path) -> int:
    """
    Export SFT (instruction tuning) format.
    Only from: WhatsApp chat, real Q/A threads, dialogue TV, comment reply chains.
    
    Format:
    {
      "messages": [
        {"role":"system","content":"You are a helpful Hassaniya assistant."},
        {"role":"user","content":"<USER_TURN>"},
        {"role":"assistant","content":"<ASSISTANT_TURN>"}
      ],
      "meta":{"episode_id":"...","bucket":"...","topic":"..."}
    }
    """
    sft_weights = config["sft_weights"]
    
    # Filter to SFT-eligible episodes
    sft_eligible_buckets = ["everyday_chat", "public_comments", "tv_discussion", "marketplace_qa"]
    sft_eligible_modes = ["dialogue", "qa"]
    
    eligible_episodes = [
        ep for ep in episodes
        if ep.get("bucket") in sft_eligible_buckets
        and ep.get("interaction_mode") in sft_eligible_modes
    ]
    
    # Group by bucket
    bucket_episodes = defaultdict(list)
    for ep in eligible_episodes:
        bucket = ep.get("bucket", "everyday_chat")
        bucket_episodes[bucket].append(ep)
    
    # Sample according to weights
    sampled_records = []
    
    for bucket, weight in sft_weights.items():
        available = bucket_episodes.get(bucket, [])
        if not available:
            continue
        
        target_count = int(len(eligible_episodes) * weight)
        
        if len(available) >= target_count:
            sampled = random.sample(available, target_count)
        else:
            sampled = available
        
        for ep in sampled:
            segments = [s for s in ep.get("segments", []) if s.get("decision") == "ACCEPT"]
            
            if len(segments) < 2:
                continue
            
            # Build conversation
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful Hassaniya assistant. You speak the authentic Hassania (Hassaniya) Arabic dialect from Mauritania."
                }
            ]
            
            for i, seg in enumerate(segments):
                speaker = seg.get("speaker", "unknown")
                text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
                
                if not text or len(text.strip()) < 5:
                    continue
                
                if speaker in ["spk1", "user"]:
                    role = "user"
                elif speaker in ["spk2", "assistant"]:
                    role = "assistant"
                else:
                    role = "user" if i % 2 == 0 else "assistant"
                
                messages.append({"role": role, "content": text})
            
            # Ensure we have at least user + assistant
            roles = [m["role"] for m in messages]
            if "user" not in roles or "assistant" not in roles:
                continue
            
            record = {
                "messages": messages,
                "meta": {
                    "episode_id": ep["episode_id"],
                    "bucket": ep.get("bucket", "unknown"),
                    "topic": ep.get("topic", "mixed")
                }
            }
            sampled_records.append(record)
    
    # Shuffle and write
    random.shuffle(sampled_records)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in sampled_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(sampled_records)

# ============================================================
# EVAL EXPORT
# ============================================================

def export_eval(episodes: List[Dict], output_file: Path) -> int:
    """Export evaluation set in SFT format."""
    records = []
    
    for ep in episodes:
        segments = [s for s in ep.get("segments", []) if s.get("decision") in ["ACCEPT", "REVIEW"]]
        
        if len(segments) < 2:
            continue
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful Hassaniya assistant."
            }
        ]
        
        for i, seg in enumerate(segments):
            text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
            if not text:
                continue
            
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": text})
        
        if len(messages) < 3:
            continue
        
        record = {
            "messages": messages,
            "meta": {
                "episode_id": ep["episode_id"],
                "bucket": ep.get("bucket", "unknown"),
                "topic": ep.get("topic", "mixed")
            }
        }
        records.append(record)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(records)

# ============================================================
# LEAKAGE CHECK
# ============================================================

def check_leakage(train_episodes: List[Dict], eval_episodes: List[Dict]) -> Dict:
    """Check for data leakage between train and eval sets."""
    train_ids = set(ep["episode_id"] for ep in train_episodes)
    eval_ids = set(ep["episode_id"] for ep in eval_episodes)
    
    # Episode ID overlap
    id_overlap = train_ids & eval_ids
    
    # Text hash overlap
    def get_text_hashes(episodes):
        hashes = set()
        for ep in episodes:
            for seg in ep.get("segments", []):
                text = seg.get("text_variants", {}).get("norm", "")
                if text:
                    h = hashlib.md5(text.encode()).hexdigest()
                    hashes.add(h)
        return hashes
    
    train_hashes = get_text_hashes(train_episodes)
    eval_hashes = get_text_hashes(eval_episodes)
    hash_overlap = train_hashes & eval_hashes
    
    return {
        "train_episode_count": len(train_ids),
        "eval_episode_count": len(eval_ids),
        "overlap_episode_count": len(id_overlap),
        "train_text_hash_count": len(train_hashes),
        "eval_text_hash_count": len(eval_hashes),
        "overlap_text_hash_count": len(hash_overlap),
        "leakage_free": len(id_overlap) == 0 and len(hash_overlap) == 0
    }

# ============================================================
# MAIN EXPORTER
# ============================================================

def run_exporter():
    print("="*60)
    print("HDRP EXPORTER")
    print("="*60)
    
    # Load config
    config = load_sampling_config()
    print(f"\nLoaded sampling config v{config['version']}")
    
    # Load refined episodes
    input_file = DQS_DIR / "episodes_refined.jsonl"
    print(f"Loading episodes from {input_file}...")
    
    episodes = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                episodes.append(json.loads(line))
            except:
                pass
    
    print(f"Loaded {len(episodes)} episodes")
    
    # Split by episode (E1)
    print("\n[E1] Splitting by episode_id...")
    train_episodes, eval_episodes = split_episodes(episodes, config["eval_ratio"])
    print(f"  Train: {len(train_episodes)} episodes")
    print(f"  Eval: {len(eval_episodes)} episodes")
    
    # Check leakage
    print("\n[E5] Checking for leakage...")
    leakage = check_leakage(train_episodes, eval_episodes)
    print(f"  Episode overlap: {leakage['overlap_episode_count']}")
    print(f"  Text hash overlap: {leakage['overlap_text_hash_count']}")
    print(f"  Leakage-free: {'✓' if leakage['leakage_free'] else '✗'}")
    
    # Export DAPT (E2)
    print("\n[E2] Exporting DAPT...")
    dapt_file = EXPORTS_DIR / "dapt" / "dapt_hassaniya_v1.jsonl"
    dapt_count = export_dapt(train_episodes, config, dapt_file)
    print(f"  Exported {dapt_count} DAPT records to {dapt_file}")
    
    # Export SFT (E3)
    print("\n[E3] Exporting SFT...")
    sft_file = EXPORTS_DIR / "sft" / "sft_hassaniya_v1.jsonl"
    sft_count = export_sft(train_episodes, config, sft_file)
    print(f"  Exported {sft_count} SFT records to {sft_file}")
    
    # Export Eval
    print("\n[E3] Exporting Eval...")
    eval_file = EXPORTS_DIR / "eval" / "eval_hassaniya_v1.jsonl"
    eval_count = export_eval(eval_episodes, eval_file)
    print(f"  Exported {eval_count} Eval records to {eval_file}")
    
    # Calculate dialogue ratio
    dialogue_count = sum(1 for ep in train_episodes if ep.get("interaction_mode") in ["dialogue", "qa"])
    dialogue_ratio = dialogue_count / len(train_episodes) if train_episodes else 0
    
    # Generate run manifest (E5)
    manifest = {
        "run_id": datetime.now().strftime("export_%Y%m%d_%H%M"),
        "timestamp": datetime.now().isoformat(),
        "counts": {
            "episodes_total": len(episodes),
            "episodes_train": len(train_episodes),
            "episodes_eval": len(eval_episodes),
            "dapt_records": dapt_count,
            "sft_records": sft_count,
            "eval_records": eval_count
        },
        "leakage_checks": leakage,
        "chat_first_compliance": {
            "dialogue_ratio": round(dialogue_ratio, 3),
            "min_required": 0.60,
            "compliant": dialogue_ratio >= 0.60
        },
        "sampling_config_hash": hashlib.md5(json.dumps(config).encode()).hexdigest()[:8],
        "exports": {
            "dapt": str(dapt_file),
            "sft": str(sft_file),
            "eval": str(eval_file)
        }
    }
    
    manifest_file = MANIFESTS_DIR / f"export_manifest_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest saved to {manifest_file}")
    
    # Summary
    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print(f"\nDApt Records: {dapt_count}")
    print(f"SFT Records: {sft_count}")
    print(f"Eval Records: {eval_count}")
    print(f"Dialogue Ratio: {dialogue_ratio*100:.1f}% (min 60%)")
    print(f"Leakage-Free: {'✓ YES' if leakage['leakage_free'] else '✗ NO'}")
    
    # Check Definition of Done gates
    print("\n" + "-"*60)
    print("DEFINITION OF DONE GATES")
    print("-"*60)
    
    # H1) Corpus Gate
    dapt_tokens = dapt_count * 50  # Rough estimate
    sft_turns = sft_count * 2  # Rough estimate
    
    h1_dapt = dapt_tokens >= 50000
    h1_sft = sft_turns >= 5000
    h1_dialogue = dialogue_ratio >= 0.60
    h1_leakage = leakage['leakage_free']
    
    print(f"\n[H1] Corpus Gate (Chat-First Base):")
    print(f"  ≥50k tokens DAPT: {'✓' if h1_dapt else '✗'} (~{dapt_tokens:,} tokens)")
    print(f"  ≥5k turns SFT: {'✓' if h1_sft else '✗'} (~{sft_turns:,} turns)")
    print(f"  Dialogue ≥60%: {'✓' if h1_dialogue else '✗'} ({dialogue_ratio*100:.1f}%)")
    print(f"  No leakage: {'✓' if h1_leakage else '✗'}")
    print(f"  GATE STATUS: {'✓ PASSED' if all([h1_dapt, h1_sft, h1_dialogue, h1_leakage]) else '✗ NOT PASSED'}")
    
    return manifest

if __name__ == "__main__":
    run_exporter()
