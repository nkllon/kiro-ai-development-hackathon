
def _find_common_text_patterns(self, texts: List[str]) -> Dict[str, int]:
    """Find common patterns in a list of texts"""
    pattern_counts = {}
    for text in texts:
        words = text.lower().split()
        for word in words:
            if len(word) > 3:
                pattern_counts[word] = pattern_counts.get(word, 0) + 1
    return {pattern: count for pattern, count in pattern_counts.items() if count > 1}
