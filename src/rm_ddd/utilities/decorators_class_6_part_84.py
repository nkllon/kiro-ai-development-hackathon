from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if validate_invariants:
        try:
            validation_result = self.validate_domain_invariants()
            if not validation_result.is_valid:
                raise InvariantViolationException('Domain invariant validation failed', current_state=self.__dict__, context={'errors': validation_result.errors})
        except AttributeError:
            logger.warning(f"Entity {cls.__name__} doesn't implement validate_domain_invariants")
    if auto_register:
        _auto_register_entity(self, domain_context)


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

@functools.wraps(original_init)