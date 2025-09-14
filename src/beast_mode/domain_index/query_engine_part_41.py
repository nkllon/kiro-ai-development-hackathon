from src.rm_ddd.core.health import ModuleHealth

def _generate_query_suggestions(self, query: str, keywords: List[str]) -> List[str]:
    """Generate query suggestions based on current query (legacy method)"""
    suggestions = []
    if len(keywords) == 1:
        suggestions.append(f'{query} in core category')
        suggestions.append(f'{query} with dependencies')
    suggestions.append(f"domains similar to {(keywords[0] if keywords else 'current')}")
    suggestions.append(f"dependencies of {(keywords[0] if keywords else 'domains')}")
    return suggestions[:self.suggestion_limit]
