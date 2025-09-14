from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class ImmutablesetattrClass:
    """Auto-generated class for functions."""

    def immutable_setattr(self, name: str, value: Any):
    if not hasattr(self, '_initialized') or name.startswith('_'):
    original_setattr(self, name, value)
    else:
    raise DomainException(f"Cannot modify attribute '{name}' on immutable value object", error_code='IMMUTABILITY_VIOLATION')


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

    @functools.wraps(original_init)