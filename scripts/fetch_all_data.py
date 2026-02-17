#!/usr/bin/env python3
"""
Comprehensive Moltbook data fetcher for EDM analysis.
Paginates through all posts to maximize dataset size.
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

API_KEY = "YOUR_MOLTBOOK_API_KEY"
BASE_URL = "https://www.moltbook.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

DATA_DIR = Path("data/edm-full")
DATA_DIR.mkdir(parents=True, exist_ok=True)

all_posts = {}  # id -> post (deduplicated)
stats = {"api_calls": 0, "posts_fetched": 0, "errors": 0}

def fetch_posts(endpoint, params=None, max_pages=50):
    """Fetch posts with pagination."""
    if params is None:
        params = {}
    
    page = 0
    while page < max_pages:
        try:
            params['limit'] = 100
            if page > 0:
                params['offset'] = page * 100
            
            resp = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=30)
            stats["api_calls"] += 1
            
            if resp.status_code != 200:
                print(f"  Error {resp.status_code}: {resp.text[:100]}")
                stats["errors"] += 1
                break
            
            data = resp.json()
            posts = data if isinstance(data, list) else data.get('posts', data.get('data', []))
            
            if not posts:
                break
            
            for post in posts:
                if 'id' in post:
                    all_posts[post['id']] = post
            
            stats["posts_fetched"] += len(posts)
            print(f"  Page {page+1}: {len(posts)} posts (total unique: {len(all_posts)})")
            
            if len(posts) < 100:
                break
            
            page += 1
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  Exception: {e}")
            stats["errors"] += 1
            break
    
    return len(all_posts)

def save_checkpoint():
    """Save current data to file."""
    output_file = DATA_DIR / "all_posts.json"
    with open(output_file, 'w') as f:
        json.dump({
            "fetched_at": datetime.now().isoformat(),
            "total_posts": len(all_posts),
            "stats": stats,
            "posts": list(all_posts.values())
        }, f, indent=2)
    print(f"\n✓ Checkpoint saved: {len(all_posts)} posts to {output_file}")

def main():
    print("=" * 60)
    print("MOLTBOOK DATA FETCHER - EDM Analysis")
    print(f"Output: {DATA_DIR}")
    print("=" * 60)
    
    # 1. Fetch by different sorts
    for sort in ['hot', 'new', 'top', 'rising']:
        print(f"\n[{sort.upper()}] Fetching posts sorted by {sort}...")
        fetch_posts('posts', {'sort': sort}, max_pages=20)
        save_checkpoint()
    
    # 2. Fetch from all submolts
    print("\n[SUBMOLTS] Fetching submolt list...")
    try:
        resp = requests.get(f"{BASE_URL}/submolts", headers=HEADERS, timeout=30)
        submolts = resp.json() if resp.status_code == 200 else []
        stats["api_calls"] += 1
        
        # Save submolts
        with open(DATA_DIR / "submolts.json", 'w') as f:
            json.dump(submolts, f, indent=2)
        
        submolt_names = [s.get('name', s.get('slug')) for s in submolts if isinstance(s, dict)]
        print(f"  Found {len(submolt_names)} submolts")
        
        for i, name in enumerate(submolt_names[:30]):  # Top 30 submolts
            if name:
                print(f"\n[SUBMOLT {i+1}/{min(len(submolt_names), 30)}] Fetching m/{name}...")
                fetch_posts(f'submolts/{name}/feed', {'sort': 'top'}, max_pages=10)
                fetch_posts(f'submolts/{name}/feed', {'sort': 'new'}, max_pages=10)
                save_checkpoint()
                
    except Exception as e:
        print(f"  Error fetching submolts: {e}")
        stats["errors"] += 1
    
    # 3. Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total unique posts: {len(all_posts)}")
    print(f"API calls made: {stats['api_calls']}")
    print(f"Errors: {stats['errors']}")
    save_checkpoint()
    
    # 4. Quick analysis preview
    if all_posts:
        posts = list(all_posts.values())
        total_comments = sum(p.get('commentCount', p.get('comment_count', 0)) for p in posts)
        total_upvotes = sum(p.get('upvotes', p.get('score', 0)) for p in posts)
        print(f"\nQuick stats:")
        print(f"  Total comments across posts: {total_comments:,}")
        print(f"  Total upvotes across posts: {total_upvotes:,}")
        print(f"  Avg comments per post: {total_comments/len(posts):.1f}")
        print(f"  Avg upvotes per post: {total_upvotes/len(posts):.1f}")

if __name__ == "__main__":
    main()
