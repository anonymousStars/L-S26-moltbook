# L@S 2026: AI Agents as Informal Learners

Supplementary data and analysis scripts for:

> **AI Agents as Informal Learners: Characterizing an Emergent Learning Community at Scale**
> Submitted to Learning at Scale (L@S) 2026

## Dataset

Full datasets are available as [GitHub Release assets](https://github.com/anonymousStars/L-S26-moltbook/releases):

- **moltbook_combined.db.zst** (~129 MB) - 293,197 posts (236,104 surviving + 57,093 platform-deleted)
- **moltbook_comments_full.db.zst** (~281 MB) - 1,552,400 comments across 168,741 posts

### Download & Decompress

```bash
# Download from GitHub Releases
gh release download v1.0-data -R anonymousStars/L-S26-moltbook

# Decompress into data/ directory (where scripts expect them)
zstd -d moltbook_combined.db.zst -o data/moltbook_combined.db
zstd -d moltbook_comments_full.db.zst -o data/moltbook_comments_full.db

# Clean up
rm -f moltbook_combined.db.zst moltbook_comments_full.db.zst
```

See [SETUP.md](SETUP.md) for full setup instructions.

### Database Schema

**Posts** (`moltbook_combined.db`):
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Post UUID |
| title | TEXT | Post title |
| body | TEXT | Post content |
| author_id | TEXT | Author UUID |
| author_name | TEXT | Author display name |
| submolt | TEXT | Sub-community name |
| upvotes | INTEGER | Upvote count |
| downvotes | INTEGER | Downvote count |
| comment_count | INTEGER | Number of comments |
| created_at | TEXT | ISO timestamp |
| date | TEXT | Date (YYYY-MM-DD) |
| is_spam | INTEGER | Spam flag (keyword-based) |
| is_question | INTEGER | Question flag |
| body_length | INTEGER | Character count |
| deleted_by_platform | INTEGER | 1 if deleted between snapshots |
| source | TEXT | Data collection source |

**Comments** (`moltbook_comments_full.db`):
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Comment UUID |
| post_id | TEXT | Parent post UUID |
| content | TEXT | Comment text |
| parent_id | TEXT | Parent comment UUID (NULL if top-level) |
| upvotes | INTEGER | Upvote count |
| downvotes | INTEGER | Downvote count |
| created_at | TEXT | ISO timestamp |
| author_id | TEXT | Author UUID |
| author_name | TEXT | Author display name |
| author_karma | INTEGER | Author karma score |
| depth | INTEGER | Thread depth (0 = top-level) |

## Repository Structure

```
├── data/
│   ├── aggregate_statistics.csv    # Summary stats by knowledge/discourse type
│   └── submolt_statistics.csv      # Per-submolt statistics
├── scripts/
│   ├── fetch_all_data.py           # Data collection script
│   ├── fetch_data.sh               # Shell wrapper for fetching
│   ├── fetch_all_data.sh           # Bulk fetch script
│   ├── setup_db.py                 # Database setup
│   ├── analyze_full_data.py        # Main analysis script
│   ├── generate_figures.py         # Figure generation
│   └── classify_posts.py           # Post classification (spam, knowledge type, discourse type)
└── classification/
    ├── spam_filtering.md           # Spam detection methodology
    ├── knowledge_type.md           # Knowledge type taxonomy
    ├── discourse_type.md           # Discourse type classification
    └── comment_taxonomy.md         # Comment interaction patterns
```

## Key Statistics

| Metric | Value |
|--------|-------|
| Total posts | 293,197 |
| Surviving posts | 236,104 |
| Platform-deleted posts | 57,093 |
| Clean posts (non-spam) | 231,080 |
| Total comments | 1,552,400 |
| Unique post authors | 66,282 |
| Unique comment authors | 20,637 |
| Observation period | Jan 27 - Feb 16, 2026 |

## Three-Phase Analysis

| Phase | Period | Posts | Daily Avg | Key Event |
|-------|--------|-------|-----------|-----------|
| Phase 1 | Jan 27 - Feb 6 | 190,771 | 17,343 | Organic growth |
| Phase 2 | Feb 7 - 9 | 79,227 | 26,409 | Spam crisis (69.3% deleted) |
| Phase 3 | Feb 10 - 16 | 23,199 | 3,314 | Post-moderation |

## License

This dataset is collected from the publicly accessible Moltbook platform. Please cite our paper if you use this data.
