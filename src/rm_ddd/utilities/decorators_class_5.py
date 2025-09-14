from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
from src.rm_ddd.core.registry import register_module
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

        class OrderCreated(DomainEvent, ReflectiveModule):
            def __init__(self, order_id: str, customer_id: str):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        register_module(self.__class__.__name__, self)
                super().__init__(order_id)
                self.customer_id = customer_id
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE

    def check_health(self):
        return {
            'status': self.ModuleStatus,
            'health': self.ModuleHealth
        }
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

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        })