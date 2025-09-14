from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

class DomaineventClass:
    """Auto-generated class for functions."""

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

    @domain_event(event_version=1)