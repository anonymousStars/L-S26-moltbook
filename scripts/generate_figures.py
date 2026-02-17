#!/usr/bin/env python3
"""Generate figures for EDM paper"""
import json
import os
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

DATA_DIR = "data"
OUTPUT_DIR = "edm-paper/EDM-template2024"

def load_all_posts():
    """Load all unique posts"""
    all_posts = {}
    for fname in os.listdir(DATA_DIR):
        if fname.startswith("posts-") or fname.startswith("submolt-"):
            path = os.path.join(DATA_DIR, fname)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                try:
                    with open(path) as f:
                        data = json.load(f)
                    if "posts" in data:
                        for p in data["posts"]:
                            all_posts[p["id"]] = p
                except:
                    pass
    return list(all_posts.values())

def generate_hourly_distribution():
    """Generate hourly distribution figure"""
    posts = load_all_posts()
    
    hours = []
    for p in posts:
        if "created_at" in p:
            try:
                ts = p["created_at"].replace("+00:00", "").replace("Z", "")
                if "." in ts:
                    ts = ts.split(".")[0]
                dt = datetime.fromisoformat(ts)
                hours.append(dt.hour)
            except:
                pass
    
    hour_counts = Counter(hours)
    x = list(range(24))
    y = [hour_counts.get(h, 0) for h in x]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(x, y, color='#2E86AB', edgecolor='white', linewidth=0.5)
    
    # Highlight the peak hour
    max_idx = y.index(max(y))
    bars[max_idx].set_color('#E63946')
    
    ax.set_xlabel('Hour (UTC)', fontsize=11)
    ax.set_ylabel('Number of Posts', fontsize=11)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], rotation=45, ha='right')
    
    # Add annotation for peak
    ax.annotate(f'Peak: {max(y)} posts', 
                xy=(max_idx, max(y)), 
                xytext=(max_idx + 2, max(y) - 10),
                fontsize=9,
                arrowprops=dict(arrowstyle='->', color='gray'))
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save as PDF and PNG
    plt.savefig(os.path.join(OUTPUT_DIR, 'hourly_distribution.pdf'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'hourly_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"Saved hourly_distribution.pdf and .png to {OUTPUT_DIR}")

def generate_engagement_distribution():
    """Generate engagement distribution figure"""
    posts = load_all_posts()
    
    upvotes = [p.get("upvotes", 0) for p in posts]
    
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Use log bins for better visualization of power-law
    import numpy as np
    bins = np.logspace(0, np.log10(max(upvotes)+1), 30)
    
    ax.hist(upvotes, bins=bins, color='#2E86AB', edgecolor='white', linewidth=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('Upvotes (log scale)', fontsize=11)
    ax.set_ylabel('Number of Posts', fontsize=11)
    
    # Add mean and median lines
    mean_val = sum(upvotes) / len(upvotes)
    median_val = sorted(upvotes)[len(upvotes)//2]
    
    ax.axvline(mean_val, color='#E63946', linestyle='--', label=f'Mean: {mean_val:.1f}')
    ax.axvline(median_val, color='#2A9D8F', linestyle=':', label=f'Median: {median_val:.0f}')
    ax.legend(fontsize=9)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    plt.savefig(os.path.join(OUTPUT_DIR, 'engagement_distribution.pdf'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'engagement_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"Saved engagement_distribution.pdf and .png to {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_hourly_distribution()
    generate_engagement_distribution()
    print("Done!")
