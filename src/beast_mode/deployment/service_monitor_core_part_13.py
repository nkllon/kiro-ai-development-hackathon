from src.rm_ddd.core.health import ModuleHealth

class AddcallbackClass:
    """Auto-generated class for functions."""

    def add_callback(self, event: str, callback: Callable):
    """Add callback for service events"""
    if event in self.callbacks:
    self.callbacks[event].append(callback)

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

