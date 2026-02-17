# Setup Guide

## 1. Download and decompress data

```bash
# Download from GitHub Releases
gh release download v1.0-data -R anonymousStars/L-S26-moltbook

# Decompress into data/ directory
zstd -d moltbook_combined.db.zst -o data/moltbook_combined.db
zstd -d moltbook_comments_full.db.zst -o data/moltbook_comments_full.db

# Clean up compressed files
rm -f moltbook_combined.db.zst moltbook_comments_full.db.zst
```

## 2. Verify

```bash
sqlite3 data/moltbook_combined.db 'SELECT count(*) FROM posts'
# Expected: 293197

sqlite3 data/moltbook_comments_full.db 'SELECT count(*) FROM comments'
# Expected: 1552400
```

## 3. Run analysis

```bash
python scripts/analyze_full_data.py
```

## Directory structure after setup

```
data/
├── moltbook_combined.db        # 293,197 posts (369 MB)
├── moltbook_comments_full.db   # 1,552,400 comments (1.0 GB)
├── aggregate_statistics.csv
└── submolt_statistics.csv
```
