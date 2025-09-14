from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

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