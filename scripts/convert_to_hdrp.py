#!/usr/bin/env python3
"""
Convert collected Hassaniya dialect data to HDRP (Hassaniya Dialect Resource Package) format.

The HDRP format follows a structure similar to the DAH (DAtaset Hassaniya) format on Hugging Face,
with three columns:
- english: English translation
- hassaniya-ar: Hassaniya in Arabic script
- hassaniya-en: Hassaniya in Latin transliteration (Arabizi)

Additionally, we create episode-style data for fine-tuning with:
- bucket: Category (everyday_chat, marketplace_qa, public_comments)
- source: Original data source
- context: Situational context for the dialogue
"""

import json
import os
import csv
from pathlib import Path
from datetime import datetime

# Paths
RAW_DATA_DIR = Path("/home/ubuntu/hassania-data-pipeline/data/raw")
PROCESSED_DIR = Path("/home/ubuntu/hassania-data-pipeline/data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def transliterate_hassaniya(arabic_text):
    """
    Basic transliteration from Arabic to Latin script.
    This is a simplified version - production would need more sophisticated mapping.
    """
    # Common Hassaniya transliteration mappings
    mapping = {
        'ا': 'a', 'أ': '2', 'إ': '2', 'آ': '2a',
        'ب': 'b', 'ت': 't', 'ث': 'th',
        'ج': 'j', 'ح': '7', 'خ': '5',
        'د': 'd', 'ذ': '4', 'ر': 'r', 'ز': 'z',
        'س': 's', 'ش': 'ch', 'ص': 's', 'ض': 'd',
        'ط': '6', 'ظ': '8', 'ع': '3', 'غ': 'gh',
        'ف': 'v', 'ق': '9', 'ك': 'k', 'ل': 'l',
        'م': 'm', 'ن': 'n', 'ه': 'h', 'و': 'w',
        'ي': 'y', 'ى': 'a', 'ة': 'a',
        'ء': '2', 'ئ': '2', 'ؤ': '2',
        'گ': 'g', 'ڤ': 'v', 'ڭ': 'g',
        '،': ',', '؟': '?', '؛': ';',
        ' ': ' ', '\n': '\n'
    }
    
    # Short vowels (diacritics)
    diacritics = {
        'َ': 'a', 'ِ': 'i', 'ُ': 'u',
        'ً': 'an', 'ٍ': 'in', 'ٌ': 'un',
        'ْ': '', 'ّ': ''  # sukun and shadda
    }
    
    result = []
    for char in arabic_text:
        if char in mapping:
            result.append(mapping[char])
        elif char in diacritics:
            result.append(diacritics[char])
        elif char.isascii():
            result.append(char)
        else:
            result.append(char)  # Keep unknown characters
    
    return ''.join(result)

def process_peace_corps_data():
    """Process Peace Corps Hassaniya lessons."""
    filepath = RAW_DATA_DIR / "reference/peace_corps_hassaniya_structured.json"
    if not filepath.exists():
        return []
    
    data = load_json(filepath)
    episodes = []
    
    # Process greetings
    for item in data.get('greetings', []):
        episodes.append({
            'english': item['english'],
            'hassaniya_ar': item['hassaniya'],
            'hassaniya_en': transliterate_hassaniya(item['hassaniya']),
            'bucket': 'everyday_chat',
            'source': 'peace_corps_mauritania',
            'context': 'greeting'
        })
    
    # Process self-introduction phrases
    for item in data.get('self_introduction', []):
        episodes.append({
            'english': item['english'],
            'hassaniya_ar': item['hassaniya'],
            'hassaniya_en': transliterate_hassaniya(item['hassaniya']),
            'bucket': 'everyday_chat',
            'source': 'peace_corps_mauritania',
            'context': 'self_introduction'
        })
    
    # Process leave-taking expressions
    for item in data.get('leave_taking', []):
        episodes.append({
            'english': item['english'],
            'hassaniya_ar': item['hassaniya'],
            'hassaniya_en': transliterate_hassaniya(item['hassaniya']),
            'bucket': 'everyday_chat',
            'source': 'peace_corps_mauritania',
            'context': 'leave_taking'
        })
    
    # Process useful expressions
    for item in data.get('useful_expressions', []):
        episodes.append({
            'english': item['english'],
            'hassaniya_ar': item['hassaniya'],
            'hassaniya_en': transliterate_hassaniya(item['hassaniya']),
            'bucket': 'everyday_chat',
            'source': 'peace_corps_mauritania',
            'context': 'useful_expression'
        })
    
    # Process vocabulary as phrase pairs
    for category, vocab in [
        ('family', data.get('family_vocabulary', {})),
        ('time', data.get('time_vocabulary', {})),
        ('food_drink', data.get('food_and_drink', {})),
        ('places', data.get('places', {})),
        ('objects', data.get('common_objects', {})),
        ('days', data.get('days_of_week', {})),
    ]:
        for hassaniya, english in vocab.items():
            episodes.append({
                'english': english,
                'hassaniya_ar': hassaniya,
                'hassaniya_en': transliterate_hassaniya(hassaniya),
                'bucket': 'everyday_chat',
                'source': 'peace_corps_mauritania',
                'context': f'vocabulary_{category}'
            })
    
    return episodes

def process_youtube_greetings():
    """Process YouTube Hassaniya greetings video content."""
    filepath = RAW_DATA_DIR / "video/youtube_hassaniya_greetings.json"
    if not filepath.exists():
        return []
    
    data = load_json(filepath)
    episodes = []
    
    # Process greeting versions
    for version in data.get('conversational_phrases', {}).get('how_are_you_versions', []):
        episodes.append({
            'english': version['english'],
            'hassaniya_ar': version['question_male'],
            'hassaniya_en': version['question_male'],  # Already in Latin
            'bucket': 'everyday_chat',
            'source': 'youtube_language_beat',
            'context': 'greeting_question'
        })
        episodes.append({
            'english': version['response_english'],
            'hassaniya_ar': version['response'],
            'hassaniya_en': version['response'],  # Already in Latin
            'bucket': 'everyday_chat',
            'source': 'youtube_language_beat',
            'context': 'greeting_response'
        })
    
    # Process additional phrases
    for phrase in data.get('conversational_phrases', {}).get('additional_phrases', []):
        episodes.append({
            'english': phrase['english'],
            'hassaniya_ar': phrase['hassaniya'],
            'hassaniya_en': phrase['hassaniya'],  # Already in Latin
            'bucket': 'everyday_chat',
            'source': 'youtube_language_beat',
            'context': 'conversational_phrase'
        })
    
    return episodes

def process_youtube_lessons():
    """Process YouTube Hassaniya lessons 1-10."""
    filepath = RAW_DATA_DIR / "video/youtube_hassaniya_lessons_1_10.json"
    if not filepath.exists():
        return []
    
    data = load_json(filepath)
    episodes = []
    
    # Process various categories
    categories = [
        ('pronouns', 'pronoun'),
        ('family_vocabulary', 'family'),
        ('time_of_day', 'time'),
        ('common_objects', 'object'),
        ('expressing_feelings', 'feeling'),
        ('likes_and_dislikes', 'preference'),
        ('actions', 'action'),
    ]
    
    for cat_key, context in categories:
        cat_data = data.get(cat_key, {})
        if isinstance(cat_data, dict):
            for hassaniya, english in cat_data.items():
                episodes.append({
                    'english': english,
                    'hassaniya_ar': hassaniya,
                    'hassaniya_en': hassaniya,  # Already in Latin
                    'bucket': 'everyday_chat',
                    'source': 'youtube_language_beat',
                    'context': f'vocabulary_{context}'
                })
        elif isinstance(cat_data, list):
            for item in cat_data:
                if isinstance(item, dict) and 'hassaniya' in item and 'english' in item:
                    episodes.append({
                        'english': item['english'],
                        'hassaniya_ar': item['hassaniya'],
                        'hassaniya_en': item['hassaniya'],
                        'bucket': 'everyday_chat',
                        'source': 'youtube_language_beat',
                        'context': context
                    })
    
    # Process greetings
    for greeting in data.get('greetings', []):
        episodes.append({
            'english': greeting.get('english', ''),
            'hassaniya_ar': greeting.get('hassaniya', ''),
            'hassaniya_en': greeting.get('hassaniya', ''),
            'bucket': 'everyday_chat',
            'source': 'youtube_language_beat',
            'context': 'greeting'
        })
    
    # Process self-introduction
    for intro in data.get('self_introduction', []):
        episodes.append({
            'english': intro.get('english', ''),
            'hassaniya_ar': intro.get('hassaniya', ''),
            'hassaniya_en': intro.get('hassaniya', ''),
            'bucket': 'everyday_chat',
            'source': 'youtube_language_beat',
            'context': 'self_introduction'
        })
    
    return episodes

def process_mo3jam_dictionary():
    """Process mo3jam.com Hassaniya dictionary."""
    filepath = RAW_DATA_DIR / "dictionary/mo3jam_hassaniya.json"
    if not filepath.exists():
        return []
    
    data = load_json(filepath)
    episodes = []
    
    # Process vocabulary
    for item in data.get('vocabulary', []):
        if 'meaning' in item:
            episodes.append({
                'english': item.get('meaning', ''),
                'hassaniya_ar': item.get('term', ''),
                'hassaniya_en': item.get('transliteration', transliterate_hassaniya(item.get('term', ''))),
                'bucket': 'everyday_chat',
                'source': 'mo3jam_dictionary',
                'context': 'vocabulary'
            })
        if 'example' in item:
            episodes.append({
                'english': item.get('example_translation', item.get('meaning', '')),
                'hassaniya_ar': item.get('example', ''),
                'hassaniya_en': transliterate_hassaniya(item.get('example', '')),
                'bucket': 'everyday_chat',
                'source': 'mo3jam_dictionary',
                'context': 'example_sentence'
            })
    
    # Process proverbs
    for proverb in data.get('proverbs', []):
        episodes.append({
            'english': proverb.get('meaning', ''),
            'hassaniya_ar': proverb.get('term', ''),
            'hassaniya_en': transliterate_hassaniya(proverb.get('term', '')),
            'bucket': 'public_comments',
            'source': 'mo3jam_dictionary',
            'context': 'proverb'
        })
    
    return episodes

def process_omniglot_data():
    """Process Omniglot Hassaniya reference data."""
    filepath = RAW_DATA_DIR / "reference/omniglot_hassaniya.json"
    if not filepath.exists():
        return []
    
    data = load_json(filepath)
    episodes = []
    
    # Process sample text vocabulary
    for hassaniya, english in data.get('hassaniya_vocabulary_from_sample', {}).items():
        episodes.append({
            'english': english,
            'hassaniya_ar': hassaniya,
            'hassaniya_en': transliterate_hassaniya(hassaniya),
            'bucket': 'everyday_chat',
            'source': 'omniglot',
            'context': 'vocabulary'
        })
    
    # Process sample text
    sample = data.get('sample_text', {})
    if sample:
        episodes.append({
            'english': sample.get('translation', ''),
            'hassaniya_ar': sample.get('arabic', ''),
            'hassaniya_en': sample.get('latin', ''),
            'bucket': 'everyday_chat',
            'source': 'omniglot',
            'context': 'literary_text'
        })
    
    return episodes

def process_marketplace_data():
    """Process marketplace data from Voursa and Facebook."""
    episodes = []
    
    # Process Voursa detailed listings
    filepath = RAW_DATA_DIR / "marketplace/voursa_detailed_listings.json"
    if filepath.exists():
        data = load_json(filepath)
        # Process detailed_listings
        for listing in data.get('detailed_listings', []):
            if 'description_raw' in listing:
                analysis = listing.get('description_analysis', {})
                translation = analysis.get('translation', f"[Marketplace listing: {listing.get('title', 'Item')}]")
                episodes.append({
                    'english': translation,
                    'hassaniya_ar': listing.get('description_raw', ''),
                    'hassaniya_en': transliterate_hassaniya(listing.get('description_raw', '')),
                    'bucket': 'marketplace_qa',
                    'source': 'voursa_marketplace',
                    'context': 'product_description'
                })
        # Process marketplace vocabulary
        for hassaniya, english in data.get('hassania_marketplace_vocabulary', {}).items():
            episodes.append({
                'english': english,
                'hassaniya_ar': hassaniya,
                'hassaniya_en': transliterate_hassaniya(hassaniya),
                'bucket': 'marketplace_qa',
                'source': 'voursa_marketplace',
                'context': 'marketplace_vocabulary'
            })
    
    # Process Voursa real estate
    filepath = RAW_DATA_DIR / "marketplace/voursa_real_estate.json"
    if filepath.exists():
        try:
            # Read file content and parse JSON (handle multiple JSON objects)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Split by the separator if present
            parts = content.split('--- DETAILED LISTING ---')
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                try:
                    data = json.loads(part)
                except:
                    continue
                
                # Process real_estate_listings
                for listing in data.get('real_estate_listings', []):
                    title = listing.get('title_raw', '')
                    terms = listing.get('hassania_terms', [])
                    terms_str = '; '.join(terms) if terms else ''
                    episodes.append({
                        'english': f"[Real estate: {listing.get('category', 'Property')} in {listing.get('location', 'Nouakchott')} - {listing.get('price', '')}]",
                        'hassaniya_ar': title,
                        'hassaniya_en': transliterate_hassaniya(title),
                        'bucket': 'marketplace_qa',
                        'source': 'voursa_marketplace',
                        'context': 'real_estate_listing'
                    })
                
                # Process real estate vocabulary
                for hassaniya, english in data.get('hassania_real_estate_vocabulary', {}).items():
                    episodes.append({
                        'english': english,
                        'hassaniya_ar': hassaniya,
                        'hassaniya_en': transliterate_hassaniya(hassaniya),
                        'bucket': 'marketplace_qa',
                        'source': 'voursa_marketplace',
                        'context': 'real_estate_vocabulary'
                    })
                
                # Process detailed listing if present
                if 'description_raw' in data:
                    analysis = data.get('description_analysis', {})
                    translation = analysis.get('translation', f"[Real estate listing: {data.get('title', 'Property')}]")
                    episodes.append({
                        'english': translation,
                        'hassaniya_ar': data.get('description_raw', ''),
                        'hassaniya_en': transliterate_hassaniya(data.get('description_raw', '')),
                        'bucket': 'marketplace_qa',
                        'source': 'voursa_marketplace',
                        'context': 'real_estate_description'
                    })
        except Exception as e:
            print(f"Error processing real estate: {e}")
    
    # Process Facebook Marketplace Nouakchott
    filepath = RAW_DATA_DIR / "marketplace/facebook_marketplace_nouakchott.json"
    if filepath.exists():
        try:
            # Read file content and parse JSON (handle multiple JSON objects)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Split by the separator if present
            parts = content.split('--- ADDITIONAL LISTINGS ---')
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                try:
                    data = json.loads(part)
                except:
                    continue
                
                # Process listings
                for listing in data.get('listings', []) + data.get('additional_listings', []):
                    title = listing.get('title', '') or listing.get('description_raw', '') or listing.get('full_description', '')
                    translation = listing.get('translation', f"[Facebook Marketplace: {listing.get('category', 'Item')} - {listing.get('price', '')}]")
                    if title:
                        episodes.append({
                            'english': translation,
                            'hassaniya_ar': title,
                            'hassaniya_en': transliterate_hassaniya(title),
                            'bucket': 'marketplace_qa',
                            'source': 'facebook_marketplace_nouakchott',
                            'context': 'marketplace_listing'
                        })
                    # Process Hassania markers as vocabulary
                    for marker in listing.get('hassania_markers', []):
                        if ' - ' in marker:
                            hassaniya, english = marker.split(' - ', 1)
                            episodes.append({
                                'english': english,
                                'hassaniya_ar': hassaniya,
                                'hassaniya_en': transliterate_hassaniya(hassaniya),
                                'bucket': 'marketplace_qa',
                                'source': 'facebook_marketplace_nouakchott',
                                'context': 'marketplace_vocabulary'
                            })
                
                # Process marketplace vocabulary
                for hassaniya, english in data.get('hassania_marketplace_vocabulary', {}).items():
                    episodes.append({
                        'english': english,
                        'hassaniya_ar': hassaniya,
                        'hassaniya_en': transliterate_hassaniya(hassaniya),
                        'bucket': 'marketplace_qa',
                        'source': 'facebook_marketplace_nouakchott',
                        'context': 'marketplace_vocabulary'
                    })
        except Exception as e:
            print(f"Error processing Facebook marketplace: {e}")
    
    return episodes

def process_social_media_data():
    """Process social media data from Facebook."""
    episodes = []
    
    filepath = RAW_DATA_DIR / "social/facebook_mauritania_hassaniya.json"
    if filepath.exists():
        try:
            data = load_json(filepath)
            for post in data.get('posts_with_hassaniya_content', []):
                if 'content' in post:
                    episodes.append({
                        'english': f"[Social media post about Hassaniya dialect]",
                        'hassaniya_ar': post.get('content', ''),
                        'hassaniya_en': transliterate_hassaniya(post.get('content', '')),
                        'bucket': 'public_comments',
                        'source': 'facebook_mauritania',
                        'context': 'social_media_post'
                    })
        except:
            pass
    
    return episodes

def save_to_csv(episodes, filename):
    """Save episodes to CSV file."""
    filepath = PROCESSED_DIR / filename
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['english', 'hassaniya_ar', 'hassaniya_en', 'bucket', 'source', 'context'])
        writer.writeheader()
        for episode in episodes:
            writer.writerow(episode)
    print(f"Saved {len(episodes)} episodes to {filepath}")
    return filepath

def save_to_jsonl(episodes, filename):
    """Save episodes to JSONL file (one JSON object per line)."""
    filepath = PROCESSED_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        for episode in episodes:
            f.write(json.dumps(episode, ensure_ascii=False) + '\n')
    print(f"Saved {len(episodes)} episodes to {filepath}")
    return filepath

def create_hdrp_summary(all_episodes):
    """Create a summary of the HDRP dataset."""
    summary = {
        'dataset_name': 'HDRP - Hassaniya Dialect Resource Package',
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'total_episodes': len(all_episodes),
        'buckets': {},
        'sources': {},
        'contexts': {}
    }
    
    for ep in all_episodes:
        bucket = ep.get('bucket', 'unknown')
        source = ep.get('source', 'unknown')
        context = ep.get('context', 'unknown')
        
        summary['buckets'][bucket] = summary['buckets'].get(bucket, 0) + 1
        summary['sources'][source] = summary['sources'].get(source, 0) + 1
        summary['contexts'][context] = summary['contexts'].get(context, 0) + 1
    
    return summary

def main():
    """Main function to process all data and create HDRP format."""
    print("Starting HDRP conversion...")
    
    all_episodes = []
    
    # Process each data source
    print("\nProcessing Peace Corps data...")
    episodes = process_peace_corps_data()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    print("\nProcessing YouTube greetings...")
    episodes = process_youtube_greetings()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    print("\nProcessing YouTube lessons...")
    episodes = process_youtube_lessons()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    print("\nProcessing mo3jam dictionary...")
    episodes = process_mo3jam_dictionary()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    print("\nProcessing Omniglot data...")
    episodes = process_omniglot_data()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    print("\nProcessing marketplace data...")
    episodes = process_marketplace_data()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    print("\nProcessing social media data...")
    episodes = process_social_media_data()
    print(f"  Found {len(episodes)} episodes")
    all_episodes.extend(episodes)
    
    # Filter out empty episodes
    all_episodes = [ep for ep in all_episodes if ep.get('hassaniya_ar') or ep.get('hassaniya_en')]
    
    print(f"\n{'='*50}")
    print(f"Total episodes collected: {len(all_episodes)}")
    
    # Save in multiple formats
    save_to_csv(all_episodes, 'hassaniya_hdrp.csv')
    save_to_jsonl(all_episodes, 'hassaniya_hdrp.jsonl')
    
    # Create and save summary
    summary = create_hdrp_summary(all_episodes)
    summary_path = PROCESSED_DIR / 'hdrp_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved summary to {summary_path}")
    
    # Print summary
    print(f"\n{'='*50}")
    print("HDRP Dataset Summary:")
    print(f"  Total episodes: {summary['total_episodes']}")
    print(f"\n  By bucket:")
    for bucket, count in sorted(summary['buckets'].items()):
        print(f"    {bucket}: {count}")
    print(f"\n  By source:")
    for source, count in sorted(summary['sources'].items()):
        print(f"    {source}: {count}")
    
    return all_episodes

if __name__ == '__main__':
    main()
