#!/usr/bin/env python3
"""
Scrape articles from top Mauritanian news websites for Hassania/Arabic content.
"""

import os
import re
import json
import time
import random
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "enrichment" / "news"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# News sources to scrape
NEWS_SOURCES = [
    {
        "name": "Al Akhbar",
        "base_url": "https://alakhbar.info/",
        "article_selector": "article a, .post-title a, h2 a, h3 a",
        "content_selector": ".entry-content, .post-content, article p, .article-content",
        "title_selector": "h1, .entry-title, .post-title"
    },
    {
        "name": "Sahara Medias",
        "base_url": "https://saharamedias.net/",
        "article_selector": "article a, .post-title a, h2 a, h3 a, .entry-title a",
        "content_selector": ".entry-content, .post-content, article p, .td-post-content",
        "title_selector": "h1, .entry-title, .td-post-title"
    },
    {
        "name": "Atlas Info",
        "base_url": "https://atlasinfo.info/",
        "article_selector": "article a, .post-title a, h2 a, h3 a",
        "content_selector": ".entry-content, .post-content, article p",
        "title_selector": "h1, .entry-title"
    },
    {
        "name": "Mersal Info",
        "base_url": "https://www.mersal.info/",
        "article_selector": "article a, .post-title a, h2 a, h3 a",
        "content_selector": ".entry-content, .post-content, article p",
        "title_selector": "h1, .entry-title"
    },
    {
        "name": "Rim Now",
        "base_url": "https://www.rimnow.com/",
        "article_selector": "article a, .post-title a, h2 a, h3 a, .item a",
        "content_selector": ".entry-content, .post-content, article p, .content",
        "title_selector": "h1, .entry-title, .title"
    }
]

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.7,en;q=0.3",
}


def is_arabic_text(text):
    """Check if text contains significant Arabic content."""
    if not text:
        return False
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]', text))
    return arabic_chars > 20


def clean_text(text):
    """Clean and normalize Arabic text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common web artifacts
    text = re.sub(r'(اقرأ أيضا|المزيد|شاهد أيضا|مواضيع ذات صلة).*', '', text)
    text = re.sub(r'(تابعونا على|شارك|اشترك).*', '', text)
    
    return text.strip()


def get_article_links(source, session, max_pages=3):
    """Get article links from a news source."""
    links = set()
    
    try:
        # Get main page
        response = session.get(source["base_url"], headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find article links
        for a in soup.select(source["article_selector"]):
            href = a.get('href', '')
            if href:
                full_url = urljoin(source["base_url"], href)
                # Only include links from same domain
                if urlparse(full_url).netloc == urlparse(source["base_url"]).netloc:
                    links.add(full_url)
        
        # Try to find pagination and get more pages
        for page in range(2, max_pages + 1):
            try:
                page_url = f"{source['base_url']}page/{page}/"
                response = session.get(page_url, headers=HEADERS, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for a in soup.select(source["article_selector"]):
                        href = a.get('href', '')
                        if href:
                            full_url = urljoin(source["base_url"], href)
                            if urlparse(full_url).netloc == urlparse(source["base_url"]).netloc:
                                links.add(full_url)
                time.sleep(0.5)
            except:
                break
    
    except Exception as e:
        print(f"  Error getting links from {source['name']}: {e}")
    
    return list(links)


def scrape_article(url, source, session):
    """Scrape content from a single article."""
    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for tag in soup.select('script, style, nav, footer, aside, .sidebar, .comments, .related'):
            tag.decompose()
        
        # Get title
        title = ""
        for selector in source["title_selector"].split(", "):
            title_elem = soup.select_one(selector)
            if title_elem:
                title = clean_text(title_elem.get_text())
                break
        
        # Get content
        content_parts = []
        for selector in source["content_selector"].split(", "):
            for elem in soup.select(selector):
                text = clean_text(elem.get_text())
                if text and len(text) > 30:
                    content_parts.append(text)
        
        content = ' '.join(content_parts)
        
        # Only return if we have Arabic content
        if is_arabic_text(content) and len(content) > 100:
            return {
                "url": url,
                "title": title,
                "content": content,
                "source": source["name"]
            }
    
    except Exception as e:
        pass
    
    return None


def scrape_source(source, max_articles=50):
    """Scrape articles from a single news source."""
    print(f"\n  Scraping {source['name']}...")
    
    articles = []
    session = requests.Session()
    
    # Get article links
    links = get_article_links(source, session)
    print(f"    Found {len(links)} article links")
    
    # Scrape articles
    scraped = 0
    for url in links[:max_articles]:
        article = scrape_article(url, source, session)
        if article:
            articles.append(article)
            scraped += 1
        
        # Rate limiting
        time.sleep(random.uniform(0.3, 0.8))
        
        if scraped >= max_articles:
            break
    
    print(f"    ✓ Scraped {len(articles)} articles with Arabic content")
    return articles


def main():
    print("\n" + "#"*60)
    print("# SCRAPING MAURITANIAN NEWS WEBSITES")
    print("#"*60)
    
    all_articles = []
    
    for source in NEWS_SOURCES:
        articles = scrape_source(source, max_articles=100)
        all_articles.extend(articles)
        
        # Save intermediate results
        time.sleep(1)
    
    # Save all articles
    if all_articles:
        output_file = OUTPUT_DIR / "news_articles.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Saved {len(all_articles)} articles to {output_file}")
        
        # Statistics
        by_source = {}
        total_chars = 0
        for article in all_articles:
            source = article['source']
            by_source[source] = by_source.get(source, 0) + 1
            total_chars += len(article['content'])
        
        print("\nArticles by source:")
        for source, count in sorted(by_source.items()):
            print(f"  {source}: {count}")
        
        print(f"\nTotal characters: {total_chars:,}")
    else:
        print("\n✗ No articles scraped")


if __name__ == "__main__":
    main()
