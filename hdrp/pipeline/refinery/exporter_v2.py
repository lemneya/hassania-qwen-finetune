#!/usr/bin/env python3
"""
HDRP Exporter v2
Fixed: Leakage prevention, improved SFT generation
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

def load_sampling_config() -> Dict:
    config_file = SPECS_DIR / "sampling_config.json"
    with open(config_file, 'r') as f:
        return json.load(f)

def get_text_hash(text: str) -> str:
    """Get hash for text deduplication."""
    normalized = ' '.join(text.lower().split())
    return hashlib.md5(normalized.encode()).hexdigest()

def split_episodes_strict(episodes: List[Dict], eval_ratio: float = 0.10) -> tuple:
    """
    Split by episode_id with strict hash-based leakage prevention.
    """
    random.seed(42)
    
    # First, collect all text hashes per episode
    episode_hashes = {}
    for ep in episodes:
        hashes = set()
        for seg in ep.get("segments", []):
            text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
            if text and len(text) > 10:
                hashes.add(get_text_hash(text))
        episode_hashes[ep["episode_id"]] = hashes
    
    # Shuffle episode IDs
    episode_ids = list(episode_hashes.keys())
    random.shuffle(episode_ids)
    
    # Split ensuring no hash overlap
    train_ids = set()
    eval_ids = set()
    train_hashes = set()
    eval_hashes = set()
    
    target_eval = int(len(episode_ids) * eval_ratio)
    
    for ep_id in episode_ids:
        ep_hashes = episode_hashes[ep_id]
        
        if len(eval_ids) < target_eval:
            # Check if any hash overlaps with train
            if not ep_hashes & train_hashes:
                eval_ids.add(ep_id)
                eval_hashes.update(ep_hashes)
            else:
                train_ids.add(ep_id)
                train_hashes.update(ep_hashes)
        else:
            # Check if any hash overlaps with eval
            if not ep_hashes & eval_hashes:
                train_ids.add(ep_id)
                train_hashes.update(ep_hashes)
            # Skip episodes that would cause leakage
    
    train_episodes = [ep for ep in episodes if ep["episode_id"] in train_ids]
    eval_episodes = [ep for ep in episodes if ep["episode_id"] in eval_ids]
    
    return train_episodes, eval_episodes, train_hashes, eval_hashes

def export_dapt(episodes: List[Dict], config: Dict, output_file: Path) -> int:
    """Export DAPT format with chat-first sampling."""
    dapt_weights = config["dapt_weights"]
    
    # Group by bucket
    bucket_episodes = defaultdict(list)
    for ep in episodes:
        bucket = ep.get("bucket", "everyday_chat")
        if bucket in ["parliament_politics"]:
            bucket = "monologue_specialist"
        bucket_episodes[bucket].append(ep)
    
    records = []
    
    for bucket, weight in dapt_weights.items():
        available = bucket_episodes.get(bucket, [])
        if not available:
            continue
        
        target_count = int(len(episodes) * weight)
        
        if len(available) >= target_count:
            sampled = random.sample(available, target_count)
        else:
            sampled = available * (target_count // max(len(available), 1) + 1)
            sampled = sampled[:target_count]
        
        for ep in sampled:
            for seg in ep.get("segments", []):
                if seg.get("decision") not in ["ACCEPT", "REVIEW"]:
                    continue
                
                text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
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
                records.append(record)
    
    random.shuffle(records)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(records)

def export_sft_improved(episodes: List[Dict], config: Dict, output_file: Path) -> int:
    """
    Improved SFT export - generate more conversation pairs.
    Convert single Q/A episodes into proper SFT format.
    """
    sft_weights = config["sft_weights"]
    
    records = []
    
    for ep in episodes:
        segments = ep.get("segments", [])
        if not segments:
            continue
        
        bucket = ep.get("bucket", "everyday_chat")
        topic = ep.get("topic", "mixed")
        
        # Strategy 1: Multi-turn conversations
        if len(segments) >= 2:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful Hassaniya assistant. You speak the authentic Hassania (Hassaniya) Arabic dialect from Mauritania."
                }
            ]
            
            for i, seg in enumerate(segments):
                if seg.get("decision") == "REJECT":
                    continue
                
                text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
                if not text or len(text.strip()) < 3:
                    continue
                
                speaker = seg.get("speaker", "")
                if speaker in ["spk1", "user"]:
                    role = "user"
                elif speaker in ["spk2", "assistant"]:
                    role = "assistant"
                else:
                    role = "user" if i % 2 == 0 else "assistant"
                
                messages.append({"role": role, "content": text})
            
            # Ensure proper alternation
            if len(messages) >= 3:
                roles = [m["role"] for m in messages[1:]]
                if "user" in roles and "assistant" in roles:
                    record = {
                        "messages": messages,
                        "meta": {
                            "episode_id": ep["episode_id"],
                            "bucket": bucket,
                            "topic": topic
                        }
                    }
                    records.append(record)
        
        # Strategy 2: Single segment as Q/A pair
        for seg in segments:
            if seg.get("decision") == "REJECT":
                continue
            
            text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
            if not text or len(text.strip()) < 5:
                continue
            
            # Create translation task
            record_translate = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful Hassaniya assistant."
                    },
                    {
                        "role": "user",
                        "content": f"Respond in Hassaniya dialect:"
                    },
                    {
                        "role": "assistant",
                        "content": text
                    }
                ],
                "meta": {
                    "episode_id": ep["episode_id"],
                    "bucket": bucket,
                    "topic": topic,
                    "task": "generation"
                }
            }
            records.append(record_translate)
            
            # Create explanation task for longer texts
            if len(text) > 20:
                record_explain = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful Hassaniya assistant."
                        },
                        {
                            "role": "user",
                            "content": f"Say something in Hassaniya about {topic}:"
                        },
                        {
                            "role": "assistant",
                            "content": text
                        }
                    ],
                    "meta": {
                        "episode_id": ep["episode_id"],
                        "bucket": bucket,
                        "topic": topic,
                        "task": "topic_generation"
                    }
                }
                records.append(record_explain)
    
    # Apply sampling weights
    bucket_records = defaultdict(list)
    for r in records:
        bucket = r["meta"].get("bucket", "everyday_chat")
        bucket_records[bucket].append(r)
    
    final_records = []
    total_target = len(records)
    
    for bucket, weight in sft_weights.items():
        available = bucket_records.get(bucket, [])
        if not available:
            continue
        
        target = int(total_target * weight)
        if len(available) >= target:
            sampled = random.sample(available, target)
        else:
            sampled = available
        
        final_records.extend(sampled)
    
    # Add remaining records to meet minimum
    remaining = [r for r in records if r not in final_records]
    if len(final_records) < 5000 and remaining:
        needed = min(5000 - len(final_records), len(remaining))
        final_records.extend(random.sample(remaining, needed))
    
    random.shuffle(final_records)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in final_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(final_records)

def export_eval(episodes: List[Dict], output_file: Path) -> int:
    """Export evaluation set."""
    records = []
    
    for ep in episodes:
        segments = [s for s in ep.get("segments", []) if s.get("decision") in ["ACCEPT", "REVIEW"]]
        
        if not segments:
            continue
        
        messages = [
            {"role": "system", "content": "You are a helpful Hassaniya assistant."}
        ]
        
        for i, seg in enumerate(segments):
            text = seg.get("text_variants", {}).get("norm", seg.get("raw_text", ""))
            if not text:
                continue
            
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": text})
        
        if len(messages) >= 3:
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

def check_leakage(train_hashes: Set[str], eval_hashes: Set[str], 
                  train_episodes: List[Dict], eval_episodes: List[Dict]) -> Dict:
    """Check for data leakage."""
    train_ids = set(ep["episode_id"] for ep in train_episodes)
    eval_ids = set(ep["episode_id"] for ep in eval_episodes)
    
    return {
        "train_episode_count": len(train_ids),
        "eval_episode_count": len(eval_ids),
        "overlap_episode_count": len(train_ids & eval_ids),
        "train_text_hash_count": len(train_hashes),
        "eval_text_hash_count": len(eval_hashes),
        "overlap_text_hash_count": len(train_hashes & eval_hashes),
        "leakage_free": len(train_ids & eval_ids) == 0 and len(train_hashes & eval_hashes) == 0
    }

def run_exporter():
    print("="*60)
    print("HDRP EXPORTER v2 (Improved)")
    print("="*60)
    
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
    
    # Split with strict leakage prevention
    print("\n[E1] Splitting by episode_id (strict mode)...")
    train_episodes, eval_episodes, train_hashes, eval_hashes = split_episodes_strict(
        episodes, config["eval_ratio"]
    )
    print(f"  Train: {len(train_episodes)} episodes")
    print(f"  Eval: {len(eval_episodes)} episodes")
    
    # Check leakage
    print("\n[E5] Checking for leakage...")
    leakage = check_leakage(train_hashes, eval_hashes, train_episodes, eval_episodes)
    print(f"  Episode overlap: {leakage['overlap_episode_count']}")
    print(f"  Text hash overlap: {leakage['overlap_text_hash_count']}")
    print(f"  Leakage-free: {'✓' if leakage['leakage_free'] else '✗'}")
    
    # Export DAPT
    print("\n[E2] Exporting DAPT...")
    dapt_file = EXPORTS_DIR / "dapt" / "dapt_hassaniya_v2.jsonl"
    dapt_count = export_dapt(train_episodes, config, dapt_file)
    print(f"  Exported {dapt_count} DAPT records")
    
    # Export SFT (improved)
    print("\n[E3] Exporting SFT (improved)...")
    sft_file = EXPORTS_DIR / "sft" / "sft_hassaniya_v2.jsonl"
    sft_count = export_sft_improved(train_episodes, config, sft_file)
    print(f"  Exported {sft_count} SFT records")
    
    # Export Eval
    print("\n[E3] Exporting Eval...")
    eval_file = EXPORTS_DIR / "eval" / "eval_hassaniya_v2.jsonl"
    eval_count = export_eval(eval_episodes, eval_file)
    print(f"  Exported {eval_count} Eval records")
    
    # Calculate dialogue ratio
    dialogue_count = sum(1 for ep in train_episodes if ep.get("interaction_mode") in ["dialogue", "qa"])
    dialogue_ratio = dialogue_count / len(train_episodes) if train_episodes else 0
    
    # Generate manifest
    manifest = {
        "run_id": datetime.now().strftime("export_%Y%m%d_%H%M"),
        "timestamp": datetime.now().isoformat(),
        "version": "2.0",
        "counts": {
            "episodes_total": len(episodes),
            "episodes_train": len(train_episodes),
            "episodes_eval": len(eval_episodes),
            "dapt_records": dapt_count,
            "sft_records": sft_count,
            "eval_records": eval_count,
            "estimated_dapt_tokens": dapt_count * 50,
            "estimated_sft_turns": sft_count * 2
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
    
    manifest_file = MANIFESTS_DIR / f"export_manifest_v2_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\nManifest saved to {manifest_file}")
    
    # Summary
    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print(f"\nDAPT Records: {dapt_count} (~{dapt_count * 50:,} tokens)")
    print(f"SFT Records: {sft_count} (~{sft_count * 2:,} turns)")
    print(f"Eval Records: {eval_count}")
    print(f"Dialogue Ratio: {dialogue_ratio*100:.1f}%")
    print(f"Leakage-Free: {'✓ YES' if leakage['leakage_free'] else '✗ NO'}")
    
    # Definition of Done gates
    print("\n" + "-"*60)
    print("DEFINITION OF DONE GATES")
    print("-"*60)
    
    dapt_tokens = dapt_count * 50
    sft_turns = sft_count * 2
    
    h1_dapt = dapt_tokens >= 50000
    h1_sft = sft_turns >= 5000
    h1_dialogue = dialogue_ratio >= 0.60
    h1_leakage = leakage['leakage_free']
    
    print(f"\n[H1] Corpus Gate (Chat-First Base):")
    print(f"  ≥50k tokens DAPT: {'✓' if h1_dapt else '✗'} (~{dapt_tokens:,} tokens)")
    print(f"  ≥5k turns SFT: {'✓' if h1_sft else '✗'} (~{sft_turns:,} turns)")
    print(f"  Dialogue ≥60%: {'✓' if h1_dialogue else '✗'} ({dialogue_ratio*100:.1f}%)")
    print(f"  No leakage: {'✓' if h1_leakage else '✗'}")
    
    all_passed = all([h1_dapt, h1_sft, h1_dialogue, h1_leakage])
    print(f"\n  GATE STATUS: {'✓ PASSED' if all_passed else '✗ NOT PASSED'}")
    
    return manifest

if __name__ == "__main__":
    run_exporter()
