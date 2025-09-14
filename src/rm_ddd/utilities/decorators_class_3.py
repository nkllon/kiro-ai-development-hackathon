from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
        class OrderCalculationService(DomainService):
            def calculate_total(self, order: Order) -> Money:
                return sum(item.price * item.quantity for item in order.items)
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE

    def check_health(self):
        return {
            'status': self.ModuleStatus,
            'health': self.ModuleHealth
        }
    """

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
    return decorator

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
        @value_object(immutable=True)