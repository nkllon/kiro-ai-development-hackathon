        class OrderCreated(DomainEvent):
            def __init__(self, order_id: str, customer_id: str):
                super().__init__(order_id)
                self.customer_id = customer_id
    """

    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, DomainEvent):
            raise TypeError(f'@domain_event can only be applied to DomainEvent subclasses, got {cls}')
        cls._event_version = event_version
        cls._validate_significance = validate_significance
        cls._auto_timestamp = auto_timestamp
        cls._is_domain_event = True
        if validate_significance:
            _add_significance_validation(cls)
        if auto_timestamp:
            _add_auto_timestamping(cls)
        logger.debug(f'Applied @domain_event decorator to {cls.__name__}')
        return cls
    return decorator

def ubiquitous_language(term_mapping: Dict[str, str], enforce_naming: bool=True, validate_consistency: bool=True) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to enforce ubiquitous language consistency.
    
    Args:
        term_mapping: Mapping of domain terms to their definitions
        enforce_naming: Whether to enforce naming conventions
        validate_consistency: Whether to validate language consistency
        
    Returns:
        Callable: Decorator function
        
    Example:
        @ubiquitous_language({
            "Order": "A customer request for products",
            "OrderItem": "A line item within an order"
        })