from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

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

