from src.rm_ddd.core.health import ModuleHealth

class GetmodulestatusClass:
    """Auto-generated class for functions."""

    def get_module_status(self) -> Dict[str, Any]:
    """Operational visibility for external systems"""
    return {'module_name': self.module_name, 'dependencies_count': len(self._dependencies), 'graph_cached': self._graph_cache is not None, 'cache_age_seconds': time.time() - self._cache_timestamp, 'avg_operation_time_ms': self._get_avg_operation_time(), 'is_healthy': self.is_healthy(), 'performance_within_limits': self._is_performance_healthy()}

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

