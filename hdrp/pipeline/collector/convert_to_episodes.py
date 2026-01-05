#!/usr/bin/env python3
"""
HDRP Episode Converter
Converts existing OpenAI-format training data to HDRP Episode schema.
"""

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Paths
BASE_DIR = Path("/tmp/hassania-qwen-finetune-main")
INPUT_FILE = BASE_DIR / "data/training/train_phase2_quality.jsonl"
OUTPUT_DIR = BASE_DIR / "hdrp/data/processed/episodes"

# Bucket classification keywords
BUCKET_KEYWORDS = {
    "everyday_chat": [
        "hello", "hi", "greet", "how are", "اشحالك", "لاباس", "مرحبا", "السلام",
        "good morning", "good evening", "صباح", "مساء", "thank", "شكر"
    ],
    "marketplace_qa": [
        "price", "buy", "sell", "سعر", "بيع", "شراء", "نيمرو", "ابرتماه",
        "market", "trade", "cost", "كم", "فلوس"
    ],
    "public_comments": [
        "comment", "reply", "post", "تعليق", "رد"
    ],
    "culture_story_poetry": [
        "poem", "poetry", "story", "قصيدة", "شعر", "قصة", "لغن", "azawan"
    ],
    "tv_discussion": [
        "interview", "show", "program", "برنامج", "مقابلة"
    ],
    "parliament_politics": [
        "parliament", "politics", "government", "برلمان", "سياسة", "حكومة"
    ]
}

# Topic classification keywords
TOPIC_KEYWORDS = {
    "social_family": ["family", "عائلة", "أهل", "زواج", "marriage", "children", "أطفال"],
    "religion": ["allah", "الله", "prayer", "صلاة", "mosque", "مسجد", "islam", "إسلام"],
    "trade_econ": ["money", "فلوس", "price", "سعر", "business", "تجارة", "work", "عمل"],
    "lifestyle": ["food", "أكل", "house", "دار", "car", "سيارة", "clothes", "ملابس"],
    "entertainment_sports": ["football", "كرة", "music", "موسيقى", "game", "لعب"],
    "politics": ["government", "حكومة", "election", "انتخاب", "president", "رئيس"],
    "local_services": ["hospital", "مستشفى", "school", "مدرسة", "shop", "دكان"]
}

def generate_episode_id() -> str:
    """Generate unique episode ID."""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique = uuid.uuid4().hex[:6].upper()
    return f"EP-{timestamp}-{unique}"

def generate_segment_id(index: int) -> str:
    """Generate segment ID."""
    return f"SEG-{index:03d}"

def classify_bucket(text: str) -> str:
    """Classify text into HDRP bucket."""
    text_lower = text.lower()
    
    scores = {}
    for bucket, keywords in BUCKET_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        scores[bucket] = score
    
    # Default to everyday_chat if no strong signal
    best_bucket = max(scores, key=scores.get)
    if scores[best_bucket] == 0:
        return "everyday_chat"
    return best_bucket

def classify_topic(text: str) -> str:
    """Classify text into HDRP topic."""
    text_lower = text.lower()
    
    scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        scores[topic] = score
    
    best_topic = max(scores, key=scores.get)
    if scores[best_topic] == 0:
        return "mixed"
    return best_topic

def detect_interaction_mode(messages: List[Dict]) -> str:
    """Detect interaction mode from messages."""
    roles = [m.get("role") for m in messages]
    
    # Check for Q/A pattern
    user_count = roles.count("user")
    assistant_count = roles.count("assistant")
    
    if user_count >= 1 and assistant_count >= 1:
        # Check if it looks like Q/A
        user_content = " ".join(m.get("content", "") for m in messages if m.get("role") == "user")
        if any(q in user_content.lower() for q in ["?", "؟", "translate", "what", "how", "ما", "كيف", "شنو"]):
            return "qa"
        return "dialogue"
    
    if user_count == 0 and assistant_count >= 1:
        return "monologue"
    
    return "narrative"

def calculate_heat(text: str) -> int:
    """Calculate heat score (0-3) based on content sensitivity."""
    heat_keywords = {
        3: ["حرب", "war", "قتل", "kill", "موت", "death"],
        2: ["سياسة", "politics", "حكومة", "government", "انتخاب"],
        1: ["دين", "religion", "الله", "allah"]
    }
    
    text_lower = text.lower()
    for heat_level, keywords in sorted(heat_keywords.items(), reverse=True):
        if any(kw in text_lower for kw in keywords):
            return heat_level
    return 0

def detect_language_probs(text: str) -> Dict[str, float]:
    """Estimate language probabilities."""
    # Arabic characters
    arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
    # French common words
    french_words = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'est', 'pour', 'avec'}
    # English common words
    english_words = {'the', 'is', 'are', 'and', 'to', 'in', 'for', 'with', 'you', 'this'}
    
    words = text.lower().split()
    total_words = len(words) if words else 1
    
    arabic_chars = sum(len(m) for m in arabic_pattern.findall(text))
    total_chars = len(text) if text else 1
    
    french_count = sum(1 for w in words if w in french_words)
    english_count = sum(1 for w in words if w in english_words)
    
    arabic_ratio = arabic_chars / total_chars
    french_ratio = french_count / total_words
    english_ratio = english_count / total_words
    
    # Hassaniya is Arabic-based
    hassaniya_prob = min(0.95, arabic_ratio * 1.2) if arabic_ratio > 0.3 else arabic_ratio
    msa_prob = max(0, arabic_ratio - hassaniya_prob)
    french_prob = french_ratio
    
    # Normalize
    total = hassaniya_prob + msa_prob + french_prob + 0.01
    
    return {
        "hassaniya": round(hassaniya_prob / total, 3),
        "msa": round(msa_prob / total, 3),
        "french": round(french_prob / total, 3),
        "mixed": round(0.01 / total, 3)
    }

def map_role_to_speaker(role: str, index: int) -> str:
    """Map OpenAI role to HDRP speaker."""
    if role == "system":
        return "system"
    elif role == "user":
        return "spk1"
    elif role == "assistant":
        return "spk2"
    return f"spk{index}"

def convert_message_to_segment(message: Dict, index: int) -> Dict:
    """Convert OpenAI message to HDRP segment."""
    content = message.get("content", "")
    role = message.get("role", "unknown")
    
    return {
        "segment_id": generate_segment_id(index),
        "speaker": map_role_to_speaker(role, index),
        "start_ms": None,
        "end_ms": None,
        "raw_text": content,
        "text_variants": {
            "raw": content,
            "norm": None,  # Will be filled by refinery
            "diac": None,
            "diac_candidate": None
        },
        "lang_probs": detect_language_probs(content),
        "dqs": 0,  # Will be calculated by refinery
        "decision": "PENDING",
        "flags": []
    }

def infer_source_type(source: str, content: str) -> str:
    """Infer source type from metadata."""
    source_lower = source.lower() if source else ""
    
    if "whatsapp" in source_lower:
        return "whatsapp_desktop"
    elif "facebook" in source_lower:
        return "facebook"
    elif "youtube" in source_lower:
        return "youtube_transcript"
    elif "peace_corps" in source_lower or "dliflc" in source_lower:
        return "website"
    elif "dah" in source_lower or "casablanca" in source_lower:
        return "website"
    elif "sentiment" in source_lower:
        return "website"
    elif "poetry" in source_lower or "diwan" in source_lower:
        return "poetry_azawan"
    
    return "website"

def convert_to_episode(sample: Dict, index: int) -> Dict:
    """Convert OpenAI-format sample to HDRP Episode."""
    messages = sample.get("messages", [])
    source = sample.get("_source", "unknown")
    
    # Combine all content for classification
    all_content = " ".join(m.get("content", "") for m in messages)
    
    # Skip system message for segments (but use for classification)
    non_system_messages = [m for m in messages if m.get("role") != "system"]
    
    # Generate episode
    episode = {
        "episode_id": generate_episode_id(),
        "source_type": infer_source_type(source, all_content),
        "source_uri": f"legacy://train_phase2_quality/{index}",
        "captured_at": datetime.now().isoformat(),
        "bucket": classify_bucket(all_content),
        "interaction_mode": detect_interaction_mode(messages),
        "topic": classify_topic(all_content),
        "heat": calculate_heat(all_content),
        "segments": [
            convert_message_to_segment(msg, i) 
            for i, msg in enumerate(non_system_messages, 1)
        ]
    }
    
    return episode

def main():
    print("="*60)
    print("HDRP EPISODE CONVERTER")
    print("="*60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load input data
    print(f"\nLoading data from {INPUT_FILE}...")
    samples = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                samples.append(json.loads(line))
            except:
                pass
    
    print(f"Loaded {len(samples)} samples")
    
    # Convert to episodes
    print("\nConverting to HDRP Episode format...")
    episodes = []
    bucket_counts = {}
    topic_counts = {}
    mode_counts = {}
    
    for i, sample in enumerate(samples):
        episode = convert_to_episode(sample, i)
        episodes.append(episode)
        
        # Track statistics
        bucket = episode["bucket"]
        topic = episode["topic"]
        mode = episode["interaction_mode"]
        
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        if (i + 1) % 5000 == 0:
            print(f"  Converted {i + 1}/{len(samples)} episodes...")
    
    # Save episodes
    output_file = OUTPUT_DIR / "episodes_batch_initial.jsonl"
    print(f"\nSaving {len(episodes)} episodes to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for episode in episodes:
            f.write(json.dumps(episode, ensure_ascii=False) + '\n')
    
    # Save statistics
    stats = {
        "total_episodes": len(episodes),
        "bucket_distribution": bucket_counts,
        "topic_distribution": topic_counts,
        "interaction_mode_distribution": mode_counts,
        "converted_at": datetime.now().isoformat()
    }
    
    stats_file = OUTPUT_DIR / "conversion_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("CONVERSION COMPLETE")
    print("="*60)
    print(f"\nTotal Episodes: {len(episodes)}")
    
    print("\nBucket Distribution:")
    for bucket, count in sorted(bucket_counts.items(), key=lambda x: -x[1]):
        pct = count / len(episodes) * 100
        print(f"  {bucket}: {count} ({pct:.1f}%)")
    
    print("\nInteraction Mode Distribution:")
    for mode, count in sorted(mode_counts.items(), key=lambda x: -x[1]):
        pct = count / len(episodes) * 100
        print(f"  {mode}: {count} ({pct:.1f}%)")
    
    print("\nTopic Distribution:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
        pct = count / len(episodes) * 100
        print(f"  {topic}: {count} ({pct:.1f}%)")

if __name__ == "__main__":
    main()
