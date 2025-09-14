from src.rm_ddd.core.health import ModuleHealth

class GeneratequerysuggestionsClass:
    """Auto-generated class for functions."""

    def _generate_query_suggestions(self, query: str, keywords: List[str]) -> List[str]:
    """Generate query suggestions based on current query (legacy method)"""
    suggestions = []
    if len(keywords) == 1:
    suggestions.append(f'{query} in core category')
    suggestions.append(f'{query} with dependencies')
    suggestions.append(f"domains similar to {(keywords[0] if keywords else 'current')}")
    suggestions.append(f"dependencies of {(keywords[0] if keywords else 'domains')}")
    return suggestions[:self.suggestion_limit]

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

