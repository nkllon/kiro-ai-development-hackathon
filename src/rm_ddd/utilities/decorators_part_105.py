from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def decorator(cls: Type[T]) -> Type[T]:
    cls._ubiquitous_language_mapping = term_mapping
    cls._enforce_naming = enforce_naming
    cls._validate_consistency = validate_consistency
    cls._has_ubiquitous_language = True
    if enforce_naming:
        _validate_ubiquitous_language_naming(cls, term_mapping)
    if validate_consistency:
        _add_language_consistency_validation(cls, term_mapping)
    logger.debug(f'Applied @ubiquitous_language decorator to {cls.__name__}')
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

