from src.rm_ddd.core.health import ModuleHealth

def _extract_keywords(self, query: str) -> List[str]:
    """Extract keywords from natural language query"""
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = re.findall('\\b\\w+\\b', query.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords
