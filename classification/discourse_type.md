# Discourse Type Classification

Posts are classified as Questions (help-seeking) or Statements (knowledge-sharing).

## Classification Rule

A post is classified as a **Question** if its title contains a question mark (`?`).

All other posts are classified as **Statements**.

## Implementation

```python
def classify_discourse_type(title):
    if '?' in title:
        return 'Question'
    return 'Statement'
```

## Rationale

- Question marks reliably indicate help-seeking behavior
- This simple heuristic achieves high precision
- More sophisticated NLP could detect implicit questions

## Results in Our Dataset

| Type | Count | Percentage |
|------|-------|------------|
| Statements | 26,378 | 92.0% |
| Questions | 2,305 | 8.0% |

**Statement-to-Question Ratio:** 11.4:1

This ratio is notably higher than typical human learning communities (usually <5:1), suggesting AI agents are optimized for knowledge broadcasting rather than help-seeking.
