from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class StatelesssetattrClass:
    """Auto-generated class for functions."""

    def stateless_setattr(self, name: str, value: Any):
    if hasattr(self, '_initializing') or name.startswith('_'):
    original_setattr(self, name, value)
    else:
    raise DomainException(f"Cannot modify attribute '{name}' on stateless domain service", error_code='STATELESS_VIOLATION')
    cls.__setattr__ = stateless_setattr
    original_init = cls.__init__


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