        class Order(Entity[str]):
            def __init__(self, order_id: str):
                super().__init__(order_id, "order_management")
                self.items = []
    """

    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, Entity):
            raise TypeError(f'@domain_entity can only be applied to Entity subclasses, got {cls}')
        cls._domain_context = domain_context
        cls._max_complexity = max_complexity
        cls._validate_invariants = validate_invariants
        cls._auto_register = auto_register
        cls._is_domain_entity = True
        original_init = cls.__init__

        @functools.wraps(original_init)
        def enhanced_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            if validate_invariants:
                try:
                    validation_result = self.validate_domain_invariants()
                    if not validation_result.is_valid:
                        raise InvariantViolationException('Domain invariant validation failed', current_state=self.__dict__, context={'errors': validation_result.errors})
                except AttributeError:
                    logger.warning(f"Entity {cls.__name__} doesn't implement validate_domain_invariants")
            if auto_register:
                _auto_register_entity(self, domain_context)
        cls.__init__ = enhanced_init
        _add_complexity_monitoring(cls, max_complexity)
        _add_validation_helpers(cls)
        logger.debug(f'Applied @domain_entity decorator to {cls.__name__}')
        return cls
    return decorator

def aggregate_root(domain_context: str, max_size: int=100, max_complexity: int=15, validate_boundaries: bool=True, auto_register: bool=True) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for aggregate roots with boundary enforcement and size limits.
    
    Args:
        domain_context: The bounded context this aggregate belongs to
        max_size: Maximum number of entities in the aggregate
        max_complexity: Maximum allowed complexity score
        validate_boundaries: Whether to validate aggregate boundaries
        auto_register: Whether to auto-register with bounded context
        
    Returns:
        Callable: Decorator function
        
    Example:
        @aggregate_root("order_management", max_size=50)