from src.rm_ddd.core.health import ModuleHealth

class ValidateaggregatesizeClass:
    """Auto-generated class for functions."""

    def _validate_aggregate_size(self, aggregate: AggregateRoot) -> ValidationResult:
    """Validate aggregate size limits."""
    result = ValidationResult(is_valid=True)
    max_size = getattr(aggregate.__class__, '_max_aggregate_size', 100)
    current_size = self._count_aggregate_members(aggregate)
    if current_size > max_size:
    result.add_warning(f'Aggregate size ({current_size}) exceeds recommended limit ({max_size})')
    return result

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

