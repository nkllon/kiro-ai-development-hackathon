from src.rm_ddd.core.health import ModuleHealth

def _get_cached_graph(self) -> DependencyGraph:
    """Get cached dependency graph or build new one if cache is stale"""
    current_time = time.time()
    if self._graph_cache is None or current_time - self._cache_timestamp > self._cache_ttl:
        self._graph_cache = self._build_dependency_graph()
        self._cache_timestamp = current_time
    return self._graph_cache

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

