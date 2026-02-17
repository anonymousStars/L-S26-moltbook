#!/usr/bin/env python3
"""
Comprehensive EDM analysis with the full dataset.
Includes statistical tests for stronger evidence.
"""

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import math

DATA_FILE = Path("data/moltbook_combined.db")

# Load data
with open(DATA_FILE) as f:
    data = json.load(f)

posts = data['posts']
print(f"Loaded {len(posts)} unique posts")
print(f"Fetched at: {data['fetched_at']}")
print()

# Helper functions
def get_upvotes(post):
    return post.get('upvotes', post.get('score', 0)) or 0

def get_comments(post):
    return post.get('commentCount', post.get('comment_count', 0)) or 0

def get_title(post):
    return post.get('title', '') or ''

def get_body(post):
    return post.get('body', post.get('content', '')) or ''

def get_created(post):
    ts = post.get('createdAt', post.get('created_at', post.get('timestamp')))
    if ts:
        try:
            if isinstance(ts, (int, float)):
                return datetime.fromtimestamp(ts)
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except:
            pass
    return None

def is_question(title):
    title_lower = title.lower()
    return '?' in title or any(title_lower.startswith(w) for w in ['what ', 'why ', 'how ', 'is ', 'are ', 'do ', 'does ', 'can ', 'should ', 'would ', 'could ', 'anyone ', 'who ', 'where ', 'when '])

def get_knowledge_type(title, body):
    text = (title + ' ' + body).lower()
    procedural_keywords = ['skill', 'build', 'built', 'how to', 'tutorial', 'guide', 'made', 'created', 'workflow', 'tool', 'script', 'code', 'implement', 'setup', 'configure']
    conceptual_keywords = ['understand', 'theory', 'why', 'philosophy', 'consciousness', 'meaning', 'think', 'believe', 'concept', 'idea', 'question', 'wonder', 'curious']
    
    proc_count = sum(1 for k in procedural_keywords if k in text)
    conc_count = sum(1 for k in conceptual_keywords if k in text)
    
    if proc_count > conc_count:
        return 'procedural'
    elif conc_count > proc_count:
        return 'conceptual'
    else:
        return 'other'

def gini_coefficient(values):
    if not values or all(v == 0 for v in values):
        return 0
    sorted_values = sorted(values)
    n = len(sorted_values)
    total = sum(sorted_values)
    if total == 0:
        return 0
    cumulative = 0
    for i, v in enumerate(sorted_values):
        cumulative += v
    gini_sum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(sorted_values))
    return gini_sum / (n * total)

def mean(values):
    return sum(values) / len(values) if values else 0

def median(values):
    if not values:
        return 0
    sorted_v = sorted(values)
    n = len(sorted_v)
    if n % 2:
        return sorted_v[n // 2]
    return (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2

def std(values):
    if len(values) < 2:
        return 0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

def mann_whitney_u(group1, group2):
    """Simple Mann-Whitney U test implementation."""
    if not group1 or not group2:
        return None, None
    
    # Combine and rank
    combined = [(v, 0) for v in group1] + [(v, 1) for v in group2]
    combined.sort(key=lambda x: x[0])
    
    # Assign ranks (handle ties by averaging)
    ranks = []
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2
        for k in range(i, j):
            ranks.append((avg_rank, combined[k][1]))
        i = j
    
    # Sum ranks for group 0
    r1 = sum(r for r, g in ranks if g == 0)
    n1, n2 = len(group1), len(group2)
    
    # U statistic
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    
    # Effect size (rank-biserial correlation)
    effect = 1 - (2 * u) / (n1 * n2)
    
    return u, effect

print("=" * 70)
print("COMPREHENSIVE EDM ANALYSIS")
print("=" * 70)

# 1. Basic Stats
upvotes = [get_upvotes(p) for p in posts]
comments = [get_comments(p) for p in posts]

print("\n1. BASIC STATISTICS")
print("-" * 40)
print(f"Total posts: {len(posts)}")
print(f"Total comments: {sum(comments):,}")
print(f"Total upvotes: {sum(upvotes):,}")
print(f"Mean comments: {mean(comments):.1f} (SD={std(comments):.1f})")
print(f"Mean upvotes: {mean(upvotes):.1f} (SD={std(upvotes):.1f})")
print(f"Median comments: {median(comments):.0f}")
print(f"Median upvotes: {median(upvotes):.0f}")

# 2. Questions vs Statements
print("\n2. QUESTIONS vs STATEMENTS")
print("-" * 40)

questions = [(get_upvotes(p), get_comments(p)) for p in posts if is_question(get_title(p))]
statements = [(get_upvotes(p), get_comments(p)) for p in posts if not is_question(get_title(p))]

q_upvotes = [u for u, c in questions]
q_comments = [c for u, c in questions]
s_upvotes = [u for u, c in statements]
s_comments = [c for u, c in statements]

print(f"Questions: {len(questions)} posts")
print(f"  Mean upvotes: {mean(q_upvotes):.1f} (SD={std(q_upvotes):.1f})")
print(f"  Mean comments: {mean(q_comments):.1f} (SD={std(q_comments):.1f})")
print(f"Statements: {len(statements)} posts")
print(f"  Mean upvotes: {mean(s_upvotes):.1f} (SD={std(s_upvotes):.1f})")
print(f"  Mean comments: {mean(s_comments):.1f} (SD={std(s_comments):.1f})")
print(f"Ratio: {len(statements)/len(questions):.1f}:1 (statements:questions)")

# Statistical test
u, effect = mann_whitney_u(s_upvotes, q_upvotes)
print(f"\nMann-Whitney U (upvotes): U={u:.0f}, effect size r={effect:.3f}")
u, effect = mann_whitney_u(s_comments, q_comments)
print(f"Mann-Whitney U (comments): U={u:.0f}, effect size r={effect:.3f}")

# 3. Knowledge Type Analysis
print("\n3. KNOWLEDGE TYPE ANALYSIS")
print("-" * 40)

knowledge_types = defaultdict(list)
for p in posts:
    kt = get_knowledge_type(get_title(p), get_body(p))
    knowledge_types[kt].append((get_upvotes(p), get_comments(p)))

for kt in ['procedural', 'conceptual', 'other']:
    data_kt = knowledge_types[kt]
    if data_kt:
        up = [u for u, c in data_kt]
        co = [c for u, c in data_kt]
        print(f"{kt.capitalize()}: {len(data_kt)} posts")
        print(f"  Mean upvotes: {mean(up):.1f} (SD={std(up):.1f})")
        print(f"  Mean comments: {mean(co):.1f} (SD={std(co):.1f})")

# Statistical test between procedural and conceptual
if knowledge_types['procedural'] and knowledge_types['conceptual']:
    proc_up = [u for u, c in knowledge_types['procedural']]
    conc_up = [u for u, c in knowledge_types['conceptual']]
    u, effect = mann_whitney_u(proc_up, conc_up)
    print(f"\nMann-Whitney U (procedural vs conceptual upvotes): U={u:.0f}, r={effect:.3f}")

# 4. Post Length Analysis
print("\n4. POST LENGTH ANALYSIS")
print("-" * 40)

short = [(get_upvotes(p), get_comments(p)) for p in posts if len(get_body(p)) < 500]
medium = [(get_upvotes(p), get_comments(p)) for p in posts if 500 <= len(get_body(p)) < 2000]
long_posts = [(get_upvotes(p), get_comments(p)) for p in posts if len(get_body(p)) >= 2000]

for name, data_len in [('Short (<500)', short), ('Medium (500-2000)', medium), ('Long (>2000)', long_posts)]:
    if data_len:
        up = [u for u, c in data_len]
        co = [c for u, c in data_len]
        print(f"{name}: {len(data_len)} posts, mean upvotes={mean(up):.1f}, mean comments={mean(co):.1f}")

# Statistical test
if short and long_posts:
    u, effect = mann_whitney_u([u for u, c in long_posts], [u for u, c in short])
    print(f"\nMann-Whitney U (long vs short upvotes): U={u:.0f}, r={effect:.3f}")

# 5. Participation Inequality
print("\n5. PARTICIPATION INEQUALITY")
print("-" * 40)

gini_upvotes = gini_coefficient(upvotes)
gini_comments = gini_coefficient(comments)

print(f"Gini coefficient (upvotes): {gini_upvotes:.3f}")
print(f"Gini coefficient (comments): {gini_comments:.3f}")
print(f"Human MOOC baseline: 0.55-0.65")
print(f"Difference from upper human baseline: +{gini_upvotes - 0.65:.3f}")

# 6. Temporal Analysis
print("\n6. TEMPORAL ANALYSIS")
print("-" * 40)

hourly_counts = defaultdict(int)
for p in posts:
    created = get_created(p)
    if created:
        hourly_counts[created.hour] += 1

if hourly_counts:
    total = sum(hourly_counts.values())
    peak_hour = max(hourly_counts.keys(), key=lambda h: hourly_counts[h])
    peak_pct = hourly_counts[peak_hour] / total * 100
    
    print(f"Peak hour: {peak_hour}:00 UTC")
    print(f"Posts at peak hour: {hourly_counts[peak_hour]} ({peak_pct:.1f}%)")
    print(f"Expected if uniform: {100/24:.1f}%")
    print(f"Clustering factor: {peak_pct / (100/24):.1f}x")
    
    # Check for scheduling signature (>15% at any single hour)
    if peak_pct > 15:
        print(f"⚠️ SCHEDULING SIGNATURE DETECTED (>{15}% threshold)")

# 7. Top Learning Posts
print("\n7. TOP LEARNING-RELATED POSTS")
print("-" * 40)

learning_keywords = ['learn', 'skill', 'built', 'tutorial', 'how to', 'guide', 'discovered', 'figured out']
learning_posts = []
for p in posts:
    title = get_title(p).lower()
    if any(k in title for k in learning_keywords):
        learning_posts.append((get_comments(p), get_upvotes(p), get_title(p)[:60]))

learning_posts.sort(reverse=True)
for i, (comments, upvotes, title) in enumerate(learning_posts[:10]):
    print(f"{i+1}. [{comments:,} comments, {upvotes} upvotes] {title}...")

# 8. Summary Statistics for Paper
print("\n" + "=" * 70)
print("SUMMARY FOR PAPER")
print("=" * 70)

print(f"""
Dataset: {len(posts):,} unique posts from Moltbook
Total engagement: {sum(comments):,} comments, {sum(upvotes):,} upvotes

Key Findings:
1. Questions vs Statements: {len(statements):,} statements, {len(questions):,} questions
   Ratio: {len(statements)/len(questions):.0f}:1
   Statements get {mean(s_comments)/mean(q_comments):.1f}x more comments

2. Knowledge Types:
   Procedural: {len(knowledge_types['procedural'])} posts
   Conceptual: {len(knowledge_types['conceptual'])} posts
   
3. Participation Inequality:
   Gini (upvotes): {gini_upvotes:.2f}
   Gini (comments): {gini_comments:.2f}
   
4. Temporal Clustering:
   Peak hour: {peak_hour}:00 UTC ({peak_pct:.1f}% of posts)
""")

# Save results for paper
results = {
    'total_posts': len(posts),
    'total_comments': sum(comments),
    'total_upvotes': sum(upvotes),
    'questions': len(questions),
    'statements': len(statements),
    'q_mean_upvotes': mean(q_upvotes),
    'q_mean_comments': mean(q_comments),
    's_mean_upvotes': mean(s_upvotes),
    's_mean_comments': mean(s_comments),
    'procedural_posts': len(knowledge_types['procedural']),
    'conceptual_posts': len(knowledge_types['conceptual']),
    'gini_upvotes': gini_upvotes,
    'gini_comments': gini_comments,
    'peak_hour': peak_hour,
    'peak_pct': peak_pct,
}

with open(DATA_FILE.parent / 'analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {DATA_FILE.parent / 'analysis_results.json'}")
