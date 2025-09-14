from src.rm_ddd.core.health import ModuleHealth

def _calculate_text_similarity(self, text_a: str, text_b: str) -> float:
    """Calculate similarity between two text strings"""
    if not text_a or not text_b:
        return 0.0
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return len(intersection) / len(union) if union else 0.0
