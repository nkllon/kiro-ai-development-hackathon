from src.rm_ddd.core.health import ModuleHealth

class StopmonitoringClass:
    """Auto-generated class for functions."""

    def stop_monitoring(self):
    """Stop the monitoring thread"""
    if not self.running:
    return
    self.running = False
    if self.monitoring_thread:
    self.monitoring_thread.join(timeout=5)
    self.logger.info('Service monitoring stopped')

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

