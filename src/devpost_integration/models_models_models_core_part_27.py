from src.rm_ddd.core.health import ModuleHealth

class ResetmetricsClass:
    """Auto-generated class for functions."""

    def reset_metrics(self) -> None:
    """Reset module metrics"""
    self._metrics = {'operations_count': 0, 'last_operation_time': None, 'error_count': 0, 'success_rate': 1.0, 'previews_generated': 0, 'preview_errors': 0}
    self._logger.info('Metrics reset successfully')

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

