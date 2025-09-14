from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def validating_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if hasattr(self, 'validate'):
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValidationException(validation_result.errors, context={'class': cls.__name__, 'args': args, 'kwargs': kwargs})


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