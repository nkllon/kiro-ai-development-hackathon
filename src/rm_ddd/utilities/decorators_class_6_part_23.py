from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class ValidatesignificanceClass:
    """Auto-generated class for functions."""

    def validate_significance(self) -> ValidationResult:
    """Validate that event represents significant business occurrence."""
    result = ValidationResult(is_valid=True)
    try:
    event_data = self.get_event_data()
    if not event_data:
    result.add_warning('Event has no data - may not be significant')
    except Exception as e:
    result.add_error(f'Cannot validate event significance: {str(e)}')
    return result
    cls._validate_significance = validate_significance

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

