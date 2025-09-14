from src.rm_ddd.core.health import ModuleHealth

class RecordsuccessfuloperationClass:
    """Auto-generated class for functions."""

    def _record_successful_operation(self, component: str, operation: str, duration: float) -> None:
    """Record successful operation for health monitoring"""
    self.monitor_component_health(component, True, duration * 1000)

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

