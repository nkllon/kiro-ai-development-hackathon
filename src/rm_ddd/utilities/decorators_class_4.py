        class Money(ValueObject):
            def __init__(self, amount: Decimal, currency: str):
                self.amount = amount
                self.currency = currency
    """

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
    return decorator

def domain_event(event_version: int=1, validate_significance: bool=True, auto_timestamp: bool=True) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for domain events with validation and metadata.
    
    Args:
        event_version: Version of the event schema
        validate_significance: Whether to validate business significance
        auto_timestamp: Whether to automatically add timestamps
        
    Returns:
        Callable: Decorator function
        
    Example:
        @domain_event(event_version=1)