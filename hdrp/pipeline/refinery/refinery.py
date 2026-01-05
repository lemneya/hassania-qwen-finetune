#!/usr/bin/env python3
"""
HDRP Refinery Pipeline
Stages: Normalize → DQS Score → Dedup → Decision
"""

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Paths
BASE_DIR = Path("/tmp/hassania-qwen-finetune-main")
EPISODES_DIR = BASE_DIR / "hdrp/data/processed/episodes"
DQS_DIR = BASE_DIR / "hdrp/data/processed/dqs"
MANIFESTS_DIR = BASE_DIR / "hdrp/data/processed/manifests"

DQS_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# STAGE D1: NORMALIZE
# ============================================================

def normalize_text(text: str) -> str:
    """
    HDRP Normalization function (hard rules):
    1. Collapse elongation repeats: عاااادي → عادي
    2. Normalize Alef: أ/إ/آ → ا
    3. Normalize punctuation: ؟ ، ؛ .
    4. Normalize whitespace (single spaces)
    5. Wrap code-switch spans: detect Latin words → <FR>…</FR> or <EN>
    """
    if not text:
        return ""
    
    result = text
    
    # 1. Collapse Arabic elongation (tatweel and repeated letters)
    result = re.sub(r'ـ+', '', result)  # Remove tatweel
    result = re.sub(r'(.)\1{2,}', r'\1\1', result)  # Max 2 repeated chars
    
    # 2. Normalize Alef variants
    result = re.sub(r'[أإآ]', 'ا', result)
    
    # 3. Normalize Taa Marbuta and Haa
    result = re.sub(r'ة', 'ه', result)  # Optional: normalize taa marbuta
    
    # 4. Normalize punctuation
    result = re.sub(r'[،,]', '،', result)  # Arabic comma
    result = re.sub(r'[؟?]', '؟', result)  # Arabic question mark
    result = re.sub(r'[؛;]', '؛', result)  # Arabic semicolon
    
    # 5. Normalize whitespace
    result = re.sub(r'\s+', ' ', result).strip()
    
    # 6. Wrap code-switch spans (French/English)
    # Detect sequences of Latin characters
    def wrap_latin(match):
        word = match.group(0)
        # Simple heuristic: French if common French words, else English
        french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'est', 'pour', 'avec', 'dans', 'sur', 'que', 'qui']
        if word.lower() in french_indicators:
            return f'<FR>{word}</FR>'
        return f'<EN>{word}</EN>'
    
    # Only wrap Latin words that are 2+ characters
    result = re.sub(r'\b[a-zA-Z]{2,}\b', wrap_latin, result)
    
    return result

# ============================================================
# STAGE D3: DQS SCORING
# ============================================================

def calculate_dqs(segment: Dict, episode: Dict) -> int:
    """
    Calculate Data Quality Score (DQS) 0-100:
    - Hassaniya confidence (0-35)
    - Cleanliness/noise (0-20)
    - Uniqueness (0-15) - calculated in dedup stage
    - Informativeness (0-20)
    - Domain value (0-10)
    """
    score = 0
    flags = []
    
    text = segment.get("raw_text", "")
    lang_probs = segment.get("lang_probs", {})
    bucket = episode.get("bucket", "")
    
    # 1. Hassaniya confidence (0-35)
    hassaniya_prob = lang_probs.get("hassaniya", 0)
    hassaniya_score = int(hassaniya_prob * 35)
    score += hassaniya_score
    
    if hassaniya_prob < 0.5:
        flags.append("low_hassaniya_confidence")
    
    # 2. Cleanliness/noise (0-20)
    cleanliness_score = 20
    
    # Check for noise patterns
    if re.search(r'[^\w\s\u0600-\u06FF،؟؛.!?\'"()\[\]<>/-]', text):
        cleanliness_score -= 5
        flags.append("special_chars")
    
    # Check for excessive punctuation
    punct_ratio = len(re.findall(r'[^\w\s]', text)) / max(len(text), 1)
    if punct_ratio > 0.2:
        cleanliness_score -= 5
        flags.append("excessive_punctuation")
    
    # Check for very short text
    word_count = len(text.split())
    if word_count < 5:
        cleanliness_score -= 10
        flags.append("very_short")
    elif word_count < 10:
        cleanliness_score -= 5
        flags.append("short")
    
    score += max(0, cleanliness_score)
    
    # 3. Uniqueness (0-15) - placeholder, calculated in dedup
    uniqueness_score = 15  # Assume unique until dedup
    score += uniqueness_score
    
    # 4. Informativeness (0-20)
    informativeness_score = 0
    
    # Longer texts are generally more informative
    if word_count >= 20:
        informativeness_score += 10
    elif word_count >= 10:
        informativeness_score += 5
    
    # Check for Arabic content
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    if arabic_chars > 10:
        informativeness_score += 5
    
    # Check for complete sentences (has punctuation)
    if re.search(r'[.؟!،]', text):
        informativeness_score += 5
    
    score += min(20, informativeness_score)
    
    # 5. Domain value (0-10)
    domain_score = 5  # Base score
    
    # Boost for chat-first buckets
    if bucket == "everyday_chat":
        domain_score += 5
    elif bucket == "marketplace_qa":
        domain_score += 4
    elif bucket == "public_comments":
        domain_score += 3
    elif bucket in ["tv_discussion", "culture_story_poetry"]:
        domain_score += 2
    
    score += min(10, domain_score)
    
    return min(100, score), flags

def assign_decision(dqs: int) -> str:
    """Assign decision based on DQS thresholds."""
    if dqs >= 75:
        return "ACCEPT"
    elif dqs >= 55:
        return "REVIEW"
    else:
        return "REJECT"

# ============================================================
# STAGE D4: DEDUP
# ============================================================

def compute_text_hash(text: str) -> str:
    """Compute hash for exact deduplication."""
    normalized = re.sub(r'\s+', ' ', text.lower().strip())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def dedup_episodes(episodes: List[Dict]) -> List[Dict]:
    """
    Deduplicate episodes based on normalized text hash.
    Keep highest DQS sample among duplicates.
    """
    # Group by hash
    hash_groups = defaultdict(list)
    
    for episode in episodes:
        for segment in episode.get("segments", []):
            norm_text = segment.get("text_variants", {}).get("norm", "")
            if norm_text:
                h = compute_text_hash(norm_text)
                hash_groups[h].append((episode, segment))
    
    # Track which episodes to keep
    episodes_to_keep = set()
    duplicate_count = 0
    
    for h, items in hash_groups.items():
        if len(items) > 1:
            # Keep the one with highest DQS
            best = max(items, key=lambda x: x[1].get("dqs", 0))
            episodes_to_keep.add(best[0]["episode_id"])
            duplicate_count += len(items) - 1
        else:
            episodes_to_keep.add(items[0][0]["episode_id"])
    
    # Filter episodes
    deduped = [ep for ep in episodes if ep["episode_id"] in episodes_to_keep]
    
    return deduped, duplicate_count

# ============================================================
# MAIN REFINERY PIPELINE
# ============================================================

def run_refinery(input_file: Path) -> Dict:
    """Run the full refinery pipeline."""
    print("="*60)
    print("HDRP REFINERY PIPELINE")
    print("="*60)
    
    # Load episodes
    print(f"\nLoading episodes from {input_file}...")
    episodes = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                episodes.append(json.loads(line))
            except:
                pass
    
    print(f"Loaded {len(episodes)} episodes")
    
    # Stage D1: Normalize
    print("\n[Stage D1] Normalizing text...")
    for episode in episodes:
        for segment in episode.get("segments", []):
            raw_text = segment.get("raw_text", "")
            norm_text = normalize_text(raw_text)
            segment["text_variants"]["raw"] = raw_text
            segment["text_variants"]["norm"] = norm_text
    
    # Stage D3: DQS Scoring
    print("[Stage D3] Calculating DQS scores...")
    dqs_distribution = {"ACCEPT": 0, "REVIEW": 0, "REJECT": 0}
    total_segments = 0
    
    for episode in episodes:
        for segment in episode.get("segments", []):
            dqs, flags = calculate_dqs(segment, episode)
            segment["dqs"] = dqs
            segment["flags"] = flags
            segment["decision"] = assign_decision(dqs)
            
            dqs_distribution[segment["decision"]] += 1
            total_segments += 1
    
    print(f"  ACCEPT: {dqs_distribution['ACCEPT']} ({dqs_distribution['ACCEPT']/total_segments*100:.1f}%)")
    print(f"  REVIEW: {dqs_distribution['REVIEW']} ({dqs_distribution['REVIEW']/total_segments*100:.1f}%)")
    print(f"  REJECT: {dqs_distribution['REJECT']} ({dqs_distribution['REJECT']/total_segments*100:.1f}%)")
    
    # Stage D4: Dedup
    print("\n[Stage D4] Deduplicating...")
    episodes_before = len(episodes)
    episodes, duplicate_count = dedup_episodes(episodes)
    print(f"  Removed {duplicate_count} duplicate segments")
    print(f"  Episodes: {episodes_before} → {len(episodes)}")
    
    # Save refined episodes
    output_file = DQS_DIR / "episodes_refined.jsonl"
    print(f"\nSaving refined episodes to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for episode in episodes:
            f.write(json.dumps(episode, ensure_ascii=False) + '\n')
    
    # Generate manifest
    manifest = {
        "run_id": datetime.now().strftime("run_%Y%m%d_%H%M"),
        "timestamp": datetime.now().isoformat(),
        "input_file": str(input_file),
        "output_file": str(output_file),
        "counts": {
            "episodes_input": episodes_before,
            "episodes_output": len(episodes),
            "segments_total": total_segments,
            "segments_accept": dqs_distribution["ACCEPT"],
            "segments_review": dqs_distribution["REVIEW"],
            "segments_reject": dqs_distribution["REJECT"],
            "duplicates_removed": duplicate_count
        },
        "dqs_thresholds": {
            "accept": 75,
            "review": 55
        }
    }
    
    manifest_file = MANIFESTS_DIR / f"refinery_manifest_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Manifest saved to {manifest_file}")
    
    print("\n" + "="*60)
    print("REFINERY COMPLETE")
    print("="*60)
    
    return manifest

def main():
    input_file = EPISODES_DIR / "episodes_batch_initial.jsonl"
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return
    
    manifest = run_refinery(input_file)
    
    print("\nSummary:")
    print(f"  Episodes processed: {manifest['counts']['episodes_output']}")
    print(f"  Segments accepted: {manifest['counts']['segments_accept']}")
    print(f"  Segments for review: {manifest['counts']['segments_review']}")
    print(f"  Segments rejected: {manifest['counts']['segments_reject']}")

if __name__ == "__main__":
    main()
