from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class WrapaggregatemethodsClass:
    """Auto-generated class for functions."""

    def _wrap_aggregate_methods(cls: Type, max_size: int):
    """Wrap aggregate methods to enforce size limits."""

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

