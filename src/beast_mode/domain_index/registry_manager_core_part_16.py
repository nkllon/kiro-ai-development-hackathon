from src.rm_ddd.core.health import ModuleHealth

def get_search_suggestions(self, partial_query: str) -> List[str]:
    """Get search query suggestions"""
    return self._index.suggest_completions(partial_query)
