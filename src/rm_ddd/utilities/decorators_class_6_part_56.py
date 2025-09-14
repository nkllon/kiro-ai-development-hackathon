from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, DomainService):
        raise TypeError(f'@domain_service can only be applied to DomainService subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._is_stateless = stateless
    cls._max_complexity = max_complexity
    cls._validate_purity = validate_purity
    cls._is_domain_service = True
    if stateless:
        _enforce_statelessness(cls)
    if validate_purity:
        _add_purity_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    logger.debug(f'Applied @domain_service decorator to {cls.__name__}')
    return cls
