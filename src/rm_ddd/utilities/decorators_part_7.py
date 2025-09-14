from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

        @aggregate_root("order_management", max_size=50)