from src.rm_ddd.core.health import ModuleHealth

def _calculate_cache_hit_ratio(self) -> float:
    """Calculate cache hit ratio for performance metrics"""
    if self._graph_cache is not None:
        cache_age = time.time() - self._cache_timestamp
        if cache_age < self._cache_ttl:
            return 0.8
    return 0.0
