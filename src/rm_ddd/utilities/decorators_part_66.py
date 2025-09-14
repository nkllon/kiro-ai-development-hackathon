from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, AggregateRoot):
        raise TypeError(f'@aggregate_root can only be applied to AggregateRoot subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._max_aggregate_size = max_size
    cls._max_complexity = max_complexity
    cls._validate_boundaries = validate_boundaries
    cls._auto_register = auto_register
    cls._is_aggregate_root = True
    _wrap_aggregate_methods(cls, max_size)
    if validate_boundaries:
        _add_boundary_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    if auto_register:
        original_init = cls.__init__

        @functools.wraps(original_init)