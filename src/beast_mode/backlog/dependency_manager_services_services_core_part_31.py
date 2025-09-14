from src.rm_ddd.core.health import ModuleHealth

def _calculate_cache_hit_ratio(self) -> float:
    """Calculate cache hit ratio for performance metrics"""
    if self._graph_cache is not None:
        cache_age = time.time() - self._cache_timestamp
        if cache_age < self._cache_ttl:
            return 0.8
    return 0.0

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

