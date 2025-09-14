from src.rm_ddd.core.health import ModuleHealth

class ValidatevalueobjectimmutabilityClass:
    """Auto-generated class for functions."""

    def _validate_value_object_immutability(self, value_object: ValueObject) -> ValidationResult:
    """Validate value object immutability."""
    result = ValidationResult(is_valid=True)
    is_immutable = getattr(value_object.__class__, '_is_immutable', None)
    if is_immutable is False:
    result.add_warning('Value object is not marked as immutable')
    setter_methods = [method for method in dir(value_object) if method.startswith('set_') and callable(getattr(value_object, method))]
    if setter_methods:
    result.add_warning(f'Value object has setter methods that may violate immutability: {setter_methods}')
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

