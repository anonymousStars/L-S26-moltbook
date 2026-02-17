# Spam Filtering Methodology

We filtered automated content (primarily token minting spam) that constituted 58% of raw posts.

## Spam Patterns

Posts were classified as spam if their title (case-insensitive) contained:

| Pattern | Description | Example |
|---------|-------------|---------|
| `mint` | Token minting posts | "mint $CLAW 02" |
| `claw` | CLAW token related | "Mint CLAW #1770643665" |
| `mbc` | MBC-20 token standard | "MBC-20 MINT" |

## Implementation

```python
def is_spam(title):
    title_lower = title.lower()
    spam_patterns = ['mint', 'claw', 'mbc']
    
    for pattern in spam_patterns:
        if pattern in title_lower:
            return True
    return False

def filter_spam(posts):
    return [p for p in posts if not is_spam(p['title'])]
```

## Filtering Results

| Category | Count | Percentage |
|----------|-------|------------|
| Raw posts collected | 68,228 | 100% |
| Spam (filtered) | 39,545 | 58% |
| **Substantive posts** | **28,683** | **42%** |

## Notes

- Token minting was a platform feature that generated automated posts
- These posts contain no learning content
- Filtering improves signal-to-noise ratio for learning analysis
- Conservative filtering (may retain some spam that doesn't match patterns)
