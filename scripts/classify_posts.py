"""
Post Classification Script
Classifies Moltbook posts by knowledge type and discourse type.
"""

def classify_knowledge_type(title: str) -> str:
    """
    Classify post by knowledge type based on title keywords.
    
    Returns: 'Procedural', 'Conceptual', or 'Other'
    """
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


def classify_discourse_type(title: str) -> str:
    """
    Classify post as Question or Statement.
    
    Returns: 'Question' or 'Statement'
    """
    if '?' in title:
        return 'Question'
    return 'Statement'


def is_spam(title: str) -> bool:
    """
    Check if post is likely spam (token minting).
    
    Returns: True if spam, False otherwise
    """
    title_lower = title.lower()
    spam_patterns = ['mint', 'claw', 'mbc']
    
    for pattern in spam_patterns:
        if pattern in title_lower:
            return True
    return False


def classify_length(body_length: int) -> str:
    """
    Classify post by content length.
    
    Returns: 'Short', 'Medium', or 'Long'
    """
    if body_length < 500:
        return 'Short'
    elif body_length <= 2000:
        return 'Medium'
    else:
        return 'Long'


# Example usage
if __name__ == "__main__":
    test_titles = [
        "Built an email-to-podcast skill today",
        "Why do agents prefer statements over questions?",
        "mint $CLAW 02",
        "Hello Moltbook community!",
        "TIL: Memory decay makes retrieval BETTER"
    ]
    
    for title in test_titles:
        if not is_spam(title):
            kt = classify_knowledge_type(title)
            dt = classify_discourse_type(title)
            print(f"{title[:50]:50} | {kt:12} | {dt}")
