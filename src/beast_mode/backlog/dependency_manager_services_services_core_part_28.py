from src.rm_ddd.core.health import ModuleHealth

class RecordoperationtimeClass:
    """Auto-generated class for functions."""

    def _record_operation_time(self, operation_time: float):
    """Record operation time for performance monitoring"""
    self._operation_times.append(operation_time * 1000)
    if len(self._operation_times) > self._max_operation_history:
    self._operation_times = self._operation_times[-self._max_operation_history:]

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

