from src.rm_ddd.core.health import ModuleHealth

class CleanupClass:
    """Auto-generated class for functions."""

    def cleanup(self):
    """Cleanup resources and stop all services"""
    self.stop_monitoring()
    for service_name in list(self.services.keys()):
    self.stop_service(service_name)
    self.logger.info('Service monitor cleanup completed')

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

