from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class CheckaggregatesizeClass:
    """Auto-generated class for functions."""

    def check_aggregate_size(self):
    """Check aggregate size limits."""
    current_size = getattr(self, '_aggregate_size', 0)
    if current_size > max_size:
    raise DomainException(f'Aggregate size ({current_size}) exceeds limit ({max_size})', error_code='AGGREGATE_SIZE_EXCEEDED')
    return current_size
    cls._check_aggregate_size = check_aggregate_size

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

