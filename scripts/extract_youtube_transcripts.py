#!/usr/bin/env python3
"""
Extract transcripts from Mauritanian YouTube channels for Hassania dialect data.
"""

import os
import json
import subprocess
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "enrichment" / "youtube"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Mauritanian YouTube channels to extract from
CHANNELS = [
    {
        "name": "Mauritanian TV",
        "channel_id": "UCK3909NQ9meg2KDYKF51Kmg",
        "url": "https://www.youtube.com/@mauritaniantv"
    },
    {
        "name": "Mauritania is my country",
        "channel_id": "UCZkvQRB_vZABFMC_LEOpdNw",
        "url": "https://www.youtube.com/channel/UCZkvQRB_vZABFMC_LEOpdNw"
    },
    {
        "name": "TV Sahel",
        "channel_id": "TVSAHEL",
        "url": "https://www.youtube.com/@TVSAHEL"
    }
]

# Individual videos known to have Hassania content
HASSANIA_VIDEOS = [
    "dhezXZR24NM",  # The Sound of the Hassaniya Arabic dialect
    "8bbUMyJ86hY",  # Learn Hassaniya: Lessons for Beginners
    "4cJsMyJeNYc",  # Learn Hassaniya vocabulary
    "7EJud2CMRyo",  # WIKITONGUES: Ibrahim speaking multiple languages
]


def get_channel_videos(channel_url, max_videos=50):
    """Get video IDs from a YouTube channel using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "id", 
             "--playlist-end", str(max_videos), channel_url],
            capture_output=True, text=True, timeout=120
        )
        video_ids = result.stdout.strip().split('\n')
        return [vid for vid in video_ids if vid]
    except Exception as e:
        print(f"  Error getting videos: {e}")
        return []


def extract_transcript(video_id):
    """Extract transcript from a YouTube video using the new API."""
    try:
        # New API format - get transcript directly
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id, 
            languages=['ar', 'ar-SA', 'ar-MA', 'en']
        )
        
        if transcript_data:
            # Combine all text segments
            full_text = ' '.join([entry['text'] for entry in transcript_data])
            return {
                'video_id': video_id,
                'language': 'ar',
                'text': full_text,
                'segments': transcript_data
            }
    except Exception as e:
        # Try without language preference
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            if transcript_data:
                full_text = ' '.join([entry['text'] for entry in transcript_data])
                return {
                    'video_id': video_id,
                    'language': 'auto',
                    'text': full_text,
                    'segments': transcript_data
                }
        except Exception as e2:
            pass
    
    return None


def extract_with_ytdlp(video_id):
    """Alternative: Extract subtitles using yt-dlp."""
    try:
        output_path = OUTPUT_DIR / f"temp_{video_id}"
        result = subprocess.run(
            ["yt-dlp", "--write-auto-sub", "--sub-lang", "ar,en",
             "--skip-download", "--sub-format", "vtt",
             "-o", str(output_path), f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=60
        )
        
        # Check for subtitle files
        for ext in ['.ar.vtt', '.en.vtt', '.vtt']:
            sub_file = Path(str(output_path) + ext)
            if sub_file.exists():
                with open(sub_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                sub_file.unlink()  # Clean up
                
                # Parse VTT content
                lines = content.split('\n')
                text_lines = []
                for line in lines:
                    # Skip timestamps and metadata
                    if '-->' not in line and not line.strip().startswith('WEBVTT') and line.strip():
                        # Remove HTML tags
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        if clean_line.strip():
                            text_lines.append(clean_line.strip())
                
                if text_lines:
                    return {
                        'video_id': video_id,
                        'language': 'ar' if '.ar.' in ext else 'en',
                        'text': ' '.join(text_lines),
                        'segments': []
                    }
    except Exception as e:
        pass
    
    return None


def main():
    print("\n" + "#"*60)
    print("# YOUTUBE TRANSCRIPT EXTRACTION FOR HASSANIA")
    print("#"*60)
    
    all_transcripts = []
    
    # Extract from specific Hassania videos
    print("\nExtracting from known Hassania videos...")
    for video_id in HASSANIA_VIDEOS:
        print(f"  Processing {video_id}...")
        transcript = extract_transcript(video_id)
        if not transcript:
            transcript = extract_with_ytdlp(video_id)
        
        if transcript:
            all_transcripts.append(transcript)
            print(f"    ✓ Got transcript ({len(transcript['text'])} chars)")
        else:
            print(f"    ✗ No transcript available")
    
    # Extract from Mauritanian channels
    for channel in CHANNELS:
        print(f"\nProcessing channel: {channel['name']}")
        video_ids = get_channel_videos(channel['url'], max_videos=30)
        print(f"  Found {len(video_ids)} videos")
        
        success_count = 0
        for video_id in video_ids[:20]:  # Limit to 20 per channel
            transcript = extract_transcript(video_id)
            if not transcript:
                transcript = extract_with_ytdlp(video_id)
            
            if transcript:
                transcript['channel'] = channel['name']
                all_transcripts.append(transcript)
                success_count += 1
                print(f"    ✓ {video_id}: {len(transcript['text'])} chars")
        
        print(f"  Extracted {success_count} transcripts from {channel['name']}")
    
    # Save transcripts
    if all_transcripts:
        output_file = OUTPUT_DIR / "youtube_transcripts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_transcripts, f, ensure_ascii=False, indent=2)
        
        # Also save as plain text corpus
        text_file = OUTPUT_DIR / "youtube_corpus.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            for t in all_transcripts:
                f.write(t['text'] + '\n\n')
        
        print(f"\n✓ Saved {len(all_transcripts)} transcripts to {output_file}")
        print(f"✓ Saved text corpus to {text_file}")
        
        # Calculate total text
        total_chars = sum(len(t['text']) for t in all_transcripts)
        print(f"Total characters: {total_chars:,}")
    else:
        print("\n✗ No transcripts extracted")


if __name__ == "__main__":
    main()
