from src.rm_ddd.core.health import ModuleHealth

class DetermineintentClass:
    """Auto-generated class for functions."""

    def _determine_intent(self, query: str) -> str:
    """Determine the intent of the natural language query"""
    if any((word in query for word in ['pattern', 'file', 'path', '*.py', 'src/'])):
    return 'pattern_search'
    elif any((word in query for word in ['contains', 'content', 'indicator', 'includes'])):
    return 'content_search'
    elif any((word in query for word in ['tool', 'capability', 'can', 'does', 'supports', 'run'])):
    return 'capability_search'
    else:
    return 'general_search'

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

