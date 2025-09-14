from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def domain_service(domain_context: str, stateless: bool=True, max_complexity: int=8, validate_purity: bool=True) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for domain services with statelessness validation.
    
    Args:
        domain_context: The bounded context this service belongs to
        stateless: Whether to enforce statelessness
        max_complexity: Maximum allowed complexity score
        validate_purity: Whether to validate domain purity
        
    Returns:
        Callable: Decorator function
        
    Example:
        @domain_service("order_management", stateless=True)