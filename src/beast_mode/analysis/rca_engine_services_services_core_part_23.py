from src.rm_ddd.core.health import ModuleHealth

class AddpatterntolibraryClass:
    """Auto-generated class for functions."""

    def _add_pattern_to_library(self, pattern: PreventionPattern):
    """Add pattern to library with hash-based indexing for fast lookup"""
    self.pattern_library[pattern.pattern_id] = pattern
    if pattern.pattern_hash not in self.pattern_index:
    self.pattern_index[pattern.pattern_hash] = []
    self.pattern_index[pattern.pattern_hash].append(pattern.pattern_id)
    self._save_pattern_library()

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

