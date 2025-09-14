from src.rm_ddd.core.health import ModuleHealth

def _get_cached_graph(self) -> DependencyGraph:
    """Get cached dependency graph or build new one if cache is stale"""
    current_time = time.time()
    if self._graph_cache is None or current_time - self._cache_timestamp > self._cache_ttl:
        self._graph_cache = self._build_dependency_graph()
        self._cache_timestamp = current_time
    return self._graph_cache
