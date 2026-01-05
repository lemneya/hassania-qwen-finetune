#!/usr/bin/env python3
"""
Generate comprehensive report of all Hassaniya dialect data collected.
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import csv

RAW_DATA_DIR = Path("/home/ubuntu/hassania-data-pipeline/data/raw")
PROCESSED_DIR = Path("/home/ubuntu/hassania-data-pipeline/data/processed")

def count_json_items(filepath):
    """Count items in a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle files with multiple JSON objects separated by markers
        if '---' in content:
            parts = [p.strip() for p in content.split('---') if p.strip()]
            total_items = 0
            for part in parts:
                try:
                    data = json.loads(part)
                    total_items += count_items_in_dict(data)
                except:
                    pass
            return total_items
        else:
            data = json.loads(content)
            return count_items_in_dict(data)
    except Exception as e:
        return 0

def count_items_in_dict(data):
    """Count meaningful items in a dictionary."""
    count = 0
    if isinstance(data, dict):
        # Count list items
        for key, value in data.items():
            if isinstance(value, list):
                count += len(value)
            elif isinstance(value, dict):
                count += len(value)
    return max(count, 1)

def analyze_raw_sources():
    """Analyze all raw data sources."""
    sources = {}
    
    # Dictionary sources
    dict_path = RAW_DATA_DIR / "dictionary/mo3jam_hassaniya.json"
    if dict_path.exists():
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sources['mo3jam_dictionary'] = {
            'file': 'dictionary/mo3jam_hassaniya.json',
            'vocabulary_terms': len(data.get('vocabulary', [])),
            'proverbs': len(data.get('proverbs', [])),
            'total_items': len(data.get('vocabulary', [])) + len(data.get('proverbs', [])),
            'description': 'User-contributed Hassaniya dictionary from mo3jam.com'
        }
    
    # Facebook page data
    fb_path = RAW_DATA_DIR / "facebook/hassaniya_page_data.json"
    if fb_path.exists():
        with open(fb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sources['facebook_hassaniya_page'] = {
            'file': 'facebook/hassaniya_page_data.json',
            'page_followers': data.get('page_info', {}).get('followers', 'N/A'),
            'posts_collected': len(data.get('posts_with_hassaniya_content', [])),
            'description': 'Facebook Hassaniya page with 228K followers'
        }
    
    # Voursa marketplace
    voursa_auto_path = RAW_DATA_DIR / "marketplace/voursa_detailed_listings.json"
    if voursa_auto_path.exists():
        with open(voursa_auto_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sources['voursa_automobiles'] = {
            'file': 'marketplace/voursa_detailed_listings.json',
            'listings': len(data.get('detailed_listings', [])),
            'vocabulary_terms': len(data.get('hassania_marketplace_vocabulary', {})),
            'description': 'Mauritanian marketplace automobile listings'
        }
    
    # Voursa real estate
    voursa_re_path = RAW_DATA_DIR / "marketplace/voursa_real_estate.json"
    if voursa_re_path.exists():
        with open(voursa_re_path, 'r', encoding='utf-8') as f:
            content = f.read()
        parts = content.split('--- DETAILED LISTING ---')
        main_data = json.loads(parts[0].strip())
        sources['voursa_real_estate'] = {
            'file': 'marketplace/voursa_real_estate.json',
            'listings': len(main_data.get('real_estate_listings', [])),
            'vocabulary_terms': len(main_data.get('hassania_real_estate_vocabulary', {})),
            'detailed_listings': len(parts) - 1,
            'description': 'Mauritanian marketplace real estate listings'
        }
    
    # Facebook Marketplace Nouakchott
    fb_market_path = RAW_DATA_DIR / "marketplace/facebook_marketplace_nouakchott.json"
    if fb_market_path.exists():
        with open(fb_market_path, 'r', encoding='utf-8') as f:
            content = f.read()
        parts = content.split('--- ADDITIONAL LISTINGS ---')
        main_data = json.loads(parts[0].strip())
        additional = json.loads(parts[1].strip()) if len(parts) > 1 else {}
        sources['facebook_marketplace_nouakchott'] = {
            'file': 'marketplace/facebook_marketplace_nouakchott.json',
            'listings': len(main_data.get('listings', [])),
            'additional_listings': len(additional.get('additional_listings', [])),
            'vocabulary_terms': len(main_data.get('hassania_marketplace_vocabulary', {})),
            'description': 'Facebook Marketplace listings from Nouakchott'
        }
    
    # Reddit
    reddit_path = RAW_DATA_DIR / "social/reddit_hassaniya.json"
    if reddit_path.exists():
        with open(reddit_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sources['reddit_hassaniya'] = {
            'file': 'social/reddit_hassaniya.json',
            'subreddit': data.get('subreddit', 'r/Hassaniya'),
            'members': data.get('members', 'N/A'),
            'resources': len(data.get('learning_resources', [])),
            'description': 'Reddit Hassaniya community and learning resources'
        }
    
    # Facebook Mauritania Hassaniya search
    fb_search_path = RAW_DATA_DIR / "social/facebook_mauritania_hassaniya.json"
    if fb_search_path.exists():
        try:
            with open(fb_search_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Handle multiple JSON objects
            import re
            json_objects = re.split(r'\}\s*\{', content)
            total_posts = 0
            pages_found = 0
            for i, obj in enumerate(json_objects):
                if i == 0:
                    obj = obj + '}'
                elif i == len(json_objects) - 1:
                    obj = '{' + obj
                else:
                    obj = '{' + obj + '}'
                try:
                    data = json.loads(obj)
                    total_posts += len(data.get('posts_with_hassaniya_content', []))
                    total_posts += len(data.get('additional_posts', []))
                    pages_found += len(data.get('pages_found', []))
                except:
                    pass
            sources['facebook_mauritania_search'] = {
                'file': 'social/facebook_mauritania_hassaniya.json',
                'posts': total_posts,
                'pages_found': pages_found,
                'description': 'Facebook search results for Mauritania Hassaniya content'
            }
        except Exception as e:
            print(f"Error parsing Facebook Mauritania: {e}")
    
    # Omniglot
    omni_path = RAW_DATA_DIR / "reference/omniglot_hassaniya.json"
    if omni_path.exists():
        with open(omni_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sources['omniglot_reference'] = {
            'file': 'reference/omniglot_hassaniya.json',
            'speakers': data.get('speakers', 'N/A'),
            'vocabulary_items': len(data.get('hassaniya_vocabulary_from_sample', {})),
            'has_sample_text': 'sample_text' in data,
            'description': 'Linguistic reference from Omniglot'
        }
    
    # Peace Corps
    pc_path = RAW_DATA_DIR / "reference/peace_corps_hassaniya_structured.json"
    if pc_path.exists():
        with open(pc_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_items = 0
        for key, value in data.items():
            if isinstance(value, list):
                total_items += len(value)
            elif isinstance(value, dict):
                total_items += len(value)
        sources['peace_corps_mauritania'] = {
            'file': 'reference/peace_corps_hassaniya_structured.json',
            'lessons': data.get('total_lessons', 10),
            'greetings': len(data.get('greetings', [])),
            'self_introduction': len(data.get('self_introduction', [])),
            'leave_taking': len(data.get('leave_taking', [])),
            'useful_expressions': len(data.get('useful_expressions', [])),
            'family_vocabulary': len(data.get('family_vocabulary', {})),
            'time_vocabulary': len(data.get('time_vocabulary', {})),
            'food_drink': len(data.get('food_and_drink', {})),
            'places': len(data.get('places', {})),
            'common_objects': len(data.get('common_objects', {})),
            'days_of_week': len(data.get('days_of_week', {})),
            'total_items': total_items,
            'description': 'Official Peace Corps Mauritania language lessons'
        }
    
    # YouTube greetings
    yt1_path = RAW_DATA_DIR / "video/youtube_hassaniya_greetings.json"
    if yt1_path.exists():
        with open(yt1_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        phrases = data.get('conversational_phrases', {})
        sources['youtube_greetings'] = {
            'file': 'video/youtube_hassaniya_greetings.json',
            'video_title': data.get('video_info', {}).get('title', 'N/A'),
            'duration': data.get('video_info', {}).get('duration', 'N/A'),
            'greeting_versions': len(phrases.get('how_are_you_versions', [])),
            'additional_phrases': len(phrases.get('additional_phrases', [])),
            'sample_dialogues': len(data.get('sample_dialogues', [])),
            'description': 'YouTube video: Hassaniya greetings lesson'
        }
    
    # YouTube lessons 1-10
    yt2_path = RAW_DATA_DIR / "video/youtube_hassaniya_lessons_1_10.json"
    if yt2_path.exists():
        with open(yt2_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        sources['youtube_lessons_1_10'] = {
            'file': 'video/youtube_hassaniya_lessons_1_10.json',
            'video_title': data.get('video_info', {}).get('title', 'N/A'),
            'duration': data.get('video_info', {}).get('duration', 'N/A'),
            'pronouns': len(data.get('pronouns', {})),
            'family_vocabulary': len(data.get('family_vocabulary', {})),
            'numbers': len(data.get('numbers_1_to_20', {})),
            'time_of_day': len(data.get('time_of_day', {})),
            'common_objects': len(data.get('common_objects', {})),
            'greetings': len(data.get('greetings', [])),
            'self_introduction': len(data.get('self_introduction', [])),
            'expressing_feelings': len(data.get('expressing_feelings', [])),
            'likes_dislikes': len(data.get('likes_and_dislikes', [])),
            'actions': len(data.get('actions', [])),
            'description': 'YouTube video: Hassaniya lessons 1-10'
        }
    
    return sources

def analyze_processed_data():
    """Analyze processed HDRP data."""
    jsonl_path = PROCESSED_DIR / "hassaniya_hdrp.jsonl"
    
    stats = {
        'total_episodes': 0,
        'by_bucket': defaultdict(int),
        'by_source': defaultdict(int),
        'by_context': defaultdict(int),
        'arabic_script_count': 0,
        'latin_script_count': 0,
        'with_english': 0,
        'unique_hassaniya_ar': set(),
        'unique_hassaniya_en': set()
    }
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            episode = json.loads(line)
            stats['total_episodes'] += 1
            stats['by_bucket'][episode.get('bucket', 'unknown')] += 1
            stats['by_source'][episode.get('source', 'unknown')] += 1
            stats['by_context'][episode.get('context', 'unknown')] += 1
            
            if episode.get('hassaniya_ar'):
                stats['arabic_script_count'] += 1
                stats['unique_hassaniya_ar'].add(episode['hassaniya_ar'])
            if episode.get('hassaniya_en'):
                stats['latin_script_count'] += 1
                stats['unique_hassaniya_en'].add(episode['hassaniya_en'])
            if episode.get('english'):
                stats['with_english'] += 1
    
    stats['unique_arabic_entries'] = len(stats['unique_hassaniya_ar'])
    stats['unique_latin_entries'] = len(stats['unique_hassaniya_en'])
    del stats['unique_hassaniya_ar']
    del stats['unique_hassaniya_en']
    
    return stats

def generate_report():
    """Generate the full report."""
    print("=" * 80)
    print("HASSANIYA DIALECT DATA COLLECTION REPORT")
    print("=" * 80)
    print()
    
    # Analyze raw sources
    sources = analyze_raw_sources()
    
    print("1. RAW DATA SOURCES")
    print("-" * 40)
    print()
    
    total_raw_items = 0
    
    for source_name, source_data in sources.items():
        print(f"📁 {source_name.upper()}")
        print(f"   File: {source_data.get('file', 'N/A')}")
        print(f"   Description: {source_data.get('description', 'N/A')}")
        
        # Print relevant stats
        for key, value in source_data.items():
            if key not in ['file', 'description']:
                if isinstance(value, (int, str)):
                    print(f"   {key.replace('_', ' ').title()}: {value}")
        
        if 'total_items' in source_data:
            total_raw_items += source_data['total_items']
        
        print()
    
    # Analyze processed data
    print()
    print("2. PROCESSED DATA (HDRP FORMAT)")
    print("-" * 40)
    print()
    
    processed_stats = analyze_processed_data()
    
    print(f"Total Episodes: {processed_stats['total_episodes']}")
    print(f"With Arabic Script: {processed_stats['arabic_script_count']}")
    print(f"With Latin Transliteration: {processed_stats['latin_script_count']}")
    print(f"With English Translation: {processed_stats['with_english']}")
    print(f"Unique Arabic Entries: {processed_stats['unique_arabic_entries']}")
    print(f"Unique Latin Entries: {processed_stats['unique_latin_entries']}")
    print()
    
    print("By Bucket:")
    for bucket, count in sorted(processed_stats['by_bucket'].items()):
        pct = (count / processed_stats['total_episodes']) * 100
        print(f"   {bucket}: {count} ({pct:.1f}%)")
    print()
    
    print("By Source:")
    for source, count in sorted(processed_stats['by_source'].items(), key=lambda x: -x[1]):
        pct = (count / processed_stats['total_episodes']) * 100
        print(f"   {source}: {count} ({pct:.1f}%)")
    print()
    
    print("By Context (Top 15):")
    sorted_contexts = sorted(processed_stats['by_context'].items(), key=lambda x: -x[1])[:15]
    for context, count in sorted_contexts:
        print(f"   {context}: {count}")
    print()
    
    # Summary
    print()
    print("3. SUMMARY")
    print("-" * 40)
    print()
    print(f"Total Raw Data Files: {len(sources)}")
    print(f"Total Processed Episodes: {processed_stats['total_episodes']}")
    print()
    
    print("Data Coverage:")
    print(f"   ✓ Everyday Chat: {processed_stats['by_bucket'].get('everyday_chat', 0)} episodes")
    print(f"   ✓ Marketplace Q&A: {processed_stats['by_bucket'].get('marketplace_qa', 0)} episodes")
    print(f"   ✓ Public Comments: {processed_stats['by_bucket'].get('public_comments', 0)} episodes")
    print()
    
    print("Source Diversity:")
    print(f"   ✓ Official Learning Materials: Peace Corps ({processed_stats['by_source'].get('peace_corps_mauritania', 0)})")
    print(f"   ✓ Video Lessons: YouTube ({processed_stats['by_source'].get('youtube_language_beat', 0)})")
    print(f"   ✓ Marketplace: Voursa ({processed_stats['by_source'].get('voursa_marketplace', 0)}) + Facebook ({processed_stats['by_source'].get('facebook_marketplace_nouakchott', 0)})")
    print(f"   ✓ Dictionary: mo3jam ({processed_stats['by_source'].get('mo3jam_dictionary', 0)})")
    print(f"   ✓ Reference: Omniglot ({processed_stats['by_source'].get('omniglot', 0)})")
    print()
    
    return {
        'sources': sources,
        'processed': processed_stats
    }

if __name__ == '__main__':
    report = generate_report()
