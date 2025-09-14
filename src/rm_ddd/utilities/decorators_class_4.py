from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
from src.rm_ddd.core.registry import register_module
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

class Money(ValueObject, ReflectiveModule):
def __init__(self, amount: Decimal, currency: str):
    self.module_id = self.__class__.__name__
    self.health_status = "healthy"
    self.registry_metadata = {}
    register_module(self.__class__.__name__, self)
    self.amount = amount
    self.currency = currency
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

    @domain_event(event_version=1)