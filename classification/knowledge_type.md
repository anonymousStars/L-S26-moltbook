# Knowledge Type Classification

Posts are classified into three categories based on title keywords, following distinctions in learning science (Scardamalia & Bereiter, 2014).

## Categories

### Procedural
Posts about skills, how-to guides, and practical knowledge.

**Keywords (case-insensitive):**
- `skill`
- `build`, `built`
- `how to`, `how-to`
- `tutorial`
- `guide`
- `til:`, `til ` (Today I Learned)
- `learned`

### Conceptual
Posts about theories, understanding, and abstract knowledge.

**Keywords (case-insensitive):**
- `why ` (with space to avoid false positives)
- `understand`
- `theory`
- ` think ` (with spaces)
- `philosophy`
- `consciousness`
- `meaning`

### Other
Posts that do not match procedural or conceptual keywords.

## Implementation

```python
def classify_knowledge_type(title):
    title_lower = title.lower()
    
    # Procedural keywords
    procedural_keywords = [
        'skill', 'build', 'built', 'how to', 'how-to', 
        'tutorial', 'guide', 'til:', 'learned'
    ]
    
    # Conceptual keywords
    conceptual_keywords = [
        'why ', 'understand', 'theory', ' think ', 
        'philosophy', 'consciousness', 'meaning'
    ]
    
    for kw in procedural_keywords:
        if kw in title_lower:
            return 'Procedural'
    
    for kw in conceptual_keywords:
        if kw in title_lower:
            return 'Conceptual'
    
    return 'Other'
```

## Limitations

- Keyword-based classification is a rough proxy
- May miss posts with implicit procedural/conceptual content
- NLP-based classification would improve precision
