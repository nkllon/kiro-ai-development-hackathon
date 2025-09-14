from src.rm_ddd.core.health import ModuleHealth

class RemoveserviceClass:
    """Auto-generated class for functions."""

    def remove_service(self, service_name: str):
    """Remove a service from monitoring"""
    if service_name in self.services:
    service = self.services[service_name]
    if service.status == ServiceStatus.RUNNING:
    self.stop_service(service_name)
    del self.services[service_name]
    self.logger.info(f'Removed service from monitor: {service_name}')

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

