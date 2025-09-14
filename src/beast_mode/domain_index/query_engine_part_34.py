from src.rm_ddd.core.health import ModuleHealth

class DeterminequerytypeClass:
    """Auto-generated class for functions."""

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

