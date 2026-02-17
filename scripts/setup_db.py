#!/usr/bin/env python3
"""
Set up SQLite database for Moltbook data.
Better organization and querying capability.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("data/edm-full/all_posts_combined.json")
DB_FILE = Path("data/moltbook.db")

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            body TEXT,
            author_id TEXT,
            author_name TEXT,
            submolt TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            fetched_at TIMESTAMP,
            is_question BOOLEAN,
            knowledge_type TEXT,
            body_length INTEGER
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS fetch_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TIMESTAMP,
            source TEXT,
            post_count INTEGER
        )
    ''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_posts_submolt ON posts(submolt)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_posts_upvotes ON posts(upvotes)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_posts_comments ON posts(comment_count)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_posts_knowledge ON posts(knowledge_type)')
    
    conn.commit()
    return conn

def is_question(title):
    if not title:
        return False
    title_lower = title.lower()
    return '?' in title or any(title_lower.startswith(w) for w in 
        ['what ', 'why ', 'how ', 'is ', 'are ', 'do ', 'does ', 'can ', 
         'should ', 'would ', 'could ', 'anyone ', 'who ', 'where ', 'when '])

def get_knowledge_type(title, body):
    text = ((title or '') + ' ' + (body or '')).lower()
    procedural = ['skill', 'build', 'built', 'how to', 'tutorial', 'guide', 
                  'made', 'created', 'workflow', 'tool', 'script', 'code']
    conceptual = ['understand', 'theory', 'why', 'philosophy', 'consciousness',
                  'meaning', 'think', 'believe', 'concept', 'idea', 'wonder']
    
    proc_count = sum(1 for k in procedural if k in text)
    conc_count = sum(1 for k in conceptual if k in text)
    
    if proc_count > conc_count:
        return 'procedural'
    elif conc_count > proc_count:
        return 'conceptual'
    return 'other'

def parse_timestamp(ts):
    if not ts:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts).isoformat()
        return datetime.fromisoformat(ts.replace('Z', '+00:00')).isoformat()
    except:
        return None

def import_posts(conn, data_file):
    c = conn.cursor()
    
    with open(data_file) as f:
        data = json.load(f)
    
    posts = data['posts']
    fetched_at = data.get('fetched_at', datetime.now().isoformat())
    
    print(f"Importing {len(posts)} posts...")
    
    imported = 0
    for p in posts:
        post_id = p.get('id')
        if not post_id:
            continue
        
        title = p.get('title', '')
        body = p.get('body', p.get('content', ''))
        
        author = p.get('author', {})
        if isinstance(author, dict):
            author_id = author.get('id', '')
            author_name = author.get('username', author.get('name', ''))
        else:
            author_id = ''
            author_name = str(author) if author else ''
        
        submolt = p.get('submolt', {})
        if isinstance(submolt, dict):
            submolt_name = submolt.get('name', submolt.get('slug', ''))
        else:
            submolt_name = str(submolt) if submolt else ''
        
        upvotes = p.get('upvotes', p.get('score', 0)) or 0
        downvotes = p.get('downvotes', 0) or 0
        comment_count = p.get('commentCount', p.get('comment_count', 0)) or 0
        created_at = parse_timestamp(p.get('createdAt', p.get('created_at', p.get('timestamp'))))
        
        try:
            c.execute('''
                INSERT OR REPLACE INTO posts 
                (id, title, body, author_id, author_name, submolt, upvotes, downvotes,
                 comment_count, created_at, fetched_at, is_question, knowledge_type, body_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_id, title, body, author_id, author_name, submolt_name,
                upvotes, downvotes, comment_count, created_at, fetched_at,
                is_question(title), get_knowledge_type(title, body), len(body or '')
            ))
            imported += 1
        except Exception as e:
            print(f"Error importing post {post_id}: {e}")
    
    # Log the import
    c.execute('''
        INSERT INTO fetch_logs (fetched_at, source, post_count)
        VALUES (?, ?, ?)
    ''', (fetched_at, str(data_file), imported))
    
    conn.commit()
    print(f"Imported {imported} posts")
    return imported

def print_stats(conn):
    c = conn.cursor()
    
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    c.execute("SELECT COUNT(*) FROM posts")
    print(f"Total posts: {c.fetchone()[0]}")
    
    c.execute("SELECT SUM(comment_count), SUM(upvotes) FROM posts")
    row = c.fetchone()
    print(f"Total comments: {row[0]:,}")
    print(f"Total upvotes: {row[1]:,}")
    
    print("\nBy knowledge type:")
    c.execute("""
        SELECT knowledge_type, COUNT(*), AVG(upvotes), AVG(comment_count)
        FROM posts GROUP BY knowledge_type ORDER BY COUNT(*) DESC
    """)
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]} posts, avg {row[2]:.1f} upvotes, {row[3]:.1f} comments")
    
    print("\nTop 10 submolts:")
    c.execute("""
        SELECT submolt, COUNT(*), SUM(comment_count)
        FROM posts WHERE submolt != ''
        GROUP BY submolt ORDER BY COUNT(*) DESC LIMIT 10
    """)
    for row in c.fetchall():
        print(f"  m/{row[0]}: {row[1]} posts, {row[2]:,} comments")
    
    print("\nQuestions vs Statements:")
    c.execute("""
        SELECT is_question, COUNT(*), AVG(upvotes), AVG(comment_count)
        FROM posts GROUP BY is_question
    """)
    for row in c.fetchall():
        label = "Questions" if row[0] else "Statements"
        print(f"  {label}: {row[1]} posts, avg {row[2]:.1f} upvotes, {row[3]:.1f} comments")
    
    print("\nHourly distribution (top 5):")
    c.execute("""
        SELECT strftime('%H', created_at) as hour, COUNT(*) as cnt
        FROM posts WHERE created_at IS NOT NULL
        GROUP BY hour ORDER BY cnt DESC LIMIT 5
    """)
    for row in c.fetchall():
        print(f"  {row[0]}:00 UTC: {row[1]} posts")

if __name__ == "__main__":
    print(f"Setting up database: {DB_FILE}")
    conn = setup_database()
    
    if DATA_FILE.exists():
        import_posts(conn, DATA_FILE)
    
    print_stats(conn)
    conn.close()
    print(f"\nDatabase saved to: {DB_FILE}")
