from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def domain_entity(domain_context: str, max_complexity: int=10, validate_invariants: bool=True, auto_register: bool=True) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for domain entities with automatic validation and compliance.
    
    Args:
        domain_context: The bounded context this entity belongs to
        max_complexity: Maximum allowed complexity score
        validate_invariants: Whether to validate invariants automatically
        auto_register: Whether to auto-register with bounded context
        
    Returns:
        Callable: Decorator function
        
    Example:
        @domain_entity("order_management")