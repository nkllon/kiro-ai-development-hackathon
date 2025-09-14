from src.rm_ddd.core.health import ModuleHealth

class PatternmatchesClass:
    """Auto-generated class for functions."""

    def _pattern_matches(self, search_pattern: str, indexed_pattern: str) -> bool:
    """Check if search pattern matches indexed pattern"""
    if '*' in search_pattern:
    regex_pattern = search_pattern.replace('*', '.*')
    return bool(re.search(regex_pattern, indexed_pattern))
    return search_pattern in indexed_pattern

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

