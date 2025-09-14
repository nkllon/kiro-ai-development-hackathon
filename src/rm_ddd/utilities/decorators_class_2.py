from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
from src.rm_ddd.core.registry import register_module
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

class Order(AggregateRoot[str], ReflectiveModule):
def __init__(self, order_id: str):
    self.module_id = self.__class__.__name__
    self.health_status = "healthy"
    self.registry_metadata = {}
    register_module(self.__class__.__name__, self)
    super().__init__(order_id, "order_management")
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE

class InitClass:
    """Auto-generated class for functions."""

    def check_health(self):
    return {
    'status': self.ModuleStatus,
    'health': self.ModuleHealth
    }
    """

    def decorator(cls: Type[T]) -> Type[T]:
    if not issubclass(cls, AggregateRoot):
    raise TypeError(f'@aggregate_root can only be applied to AggregateRoot subclasses, got {cls}')
    cls._domain_context = domain_context
    cls._max_aggregate_size = max_size
    cls._max_complexity = max_complexity
    cls._validate_boundaries = validate_boundaries
    cls._auto_register = auto_register
    cls._is_aggregate_root = True
    _wrap_aggregate_methods(cls, max_size)
    if validate_boundaries:
    _add_boundary_validation(cls)
    _add_complexity_monitoring(cls, max_complexity)
    if auto_register:
    original_init = cls.__init__

    @functools.wraps(original_init)
    def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)
    cls.__init__ = enhanced_init
    logger.debug(f'Applied @aggregate_root decorator to {cls.__name__}')
    return cls
    return decorator

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

    @domain_service("order_management", stateless=True)