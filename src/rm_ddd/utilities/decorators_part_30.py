from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class CheckhealthClass:
    """Auto-generated class for functions."""

    def check_health(self):
    return {
    'status': self.ModuleStatus,
    'health': self.ModuleHealth
    }
    """

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

