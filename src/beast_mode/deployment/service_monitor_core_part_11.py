from src.rm_ddd.core.health import ModuleHealth

class GetservicestatusClass:
    """Auto-generated class for functions."""

    def get_service_status(self, service_name: str) -> Optional[MonitoredService]:
    """Get status of a specific service"""
    return self.services.get(service_name)

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

