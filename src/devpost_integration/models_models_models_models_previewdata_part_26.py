from src.rm_ddd.core.health import ModuleHealth

class UpdatemetricsClass:
    """Auto-generated class for functions."""

    def _update_metrics(self, operation: str) -> None:
    """Update performance metrics"""
    self._metrics['operations_count'] += 1
    self._metrics['last_operation_time'] = datetime.now()
    total_ops = self._metrics['operations_count']
    errors = self._metrics['error_count']
    self._metrics['success_rate'] = (total_ops - errors) / total_ops if total_ops > 0 else 1.0

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

