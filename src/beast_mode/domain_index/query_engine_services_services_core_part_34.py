from src.rm_ddd.core.health import ModuleHealth

def _determine_query_type(self, query: str) -> str:
    """Determine the type of query being asked"""
    relationship_patterns = ['\\b(depend\\w*\\s+on|depends?\\s+on)\\b', '\\b(similar\\s+to|like)\\b', '\\b(related\\s+to|connected\\s+to)\\b', '\\b(circular\\s+depend|cycle)\\b', '\\b(coupling|coupled)\\b', '\\b(extract\\w*\\s+impact|extraction)\\b']
    for pattern in relationship_patterns:
        if re.search(pattern, query):
            return 'relationship'
    analysis_patterns = ['\\b(analy[sz]e|analysis)\\b', '\\b(metrics?|statistics?|stats)\\b', '\\b(health|status|report)\\b', '\\b(complexity|coupling|quality)\\b']
    for pattern in analysis_patterns:
        if re.search(pattern, query):
            return 'analysis'
    comparison_patterns = ['\\b(compare|comparison|versus|vs)\\b', '\\b(difference|different|differ)\\b', '\\b(better|worse|best|worst)\\b']
    for pattern in comparison_patterns:
        if re.search(pattern, query):
            return 'comparison'
    return 'search'
