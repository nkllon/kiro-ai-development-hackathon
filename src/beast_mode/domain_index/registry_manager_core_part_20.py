from src.rm_ddd.core.health import ModuleHealth

class GetcacheinfoClass:
    """Auto-generated class for functions."""

    def get_cache_info(self, key: str) -> Optional[Dict[str, Any]]:
    """Get detailed cache information for a key"""
    return self._cache.get_entry_info(key)

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

