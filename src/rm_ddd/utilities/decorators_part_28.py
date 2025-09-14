from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

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