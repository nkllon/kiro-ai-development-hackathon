from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class DecoratorClass:
    """Auto-generated class for functions."""

    def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, ValueObject):
    raise TypeError(f'@value_object can only be applied to ValueObject subclasses, got {cls}')
    cls._is_immutable = immutable
    cls._validate_on_creation = validate_on_creation
    cls._max_complexity = max_complexity
    cls._is_value_object = True
    if immutable:
    _enforce_immutability(cls)
    if validate_on_creation:
    _add_creation_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @value_object decorator to {cls.__name__}')
    return cls

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

