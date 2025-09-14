from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

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