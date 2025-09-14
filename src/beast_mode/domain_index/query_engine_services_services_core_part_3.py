from src.rm_ddd.core.health import ModuleHealth

class EnsureindexesbuiltClass:
    """Auto-generated class for functions."""

    def _ensure_indexes_built(self):
    """Ensure search indexes are built"""
    if not self._index_built and self.registry_manager:
    self._build_search_indexes()

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

