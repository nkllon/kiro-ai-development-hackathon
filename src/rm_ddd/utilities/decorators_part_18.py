from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class ValueobjectClass:
    """Auto-generated class for functions."""

    def value_object(immutable: bool=True, validate_on_creation: bool=True, max_complexity: int=5) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for value objects with immutability enforcement.

    Args:
    immutable: Whether to enforce immutability
    validate_on_creation: Whether to validate on creation
    max_complexity: Maximum allowed complexity score

    Returns:
    Callable: Decorator function

    Example:

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

    @value_object(immutable=True)