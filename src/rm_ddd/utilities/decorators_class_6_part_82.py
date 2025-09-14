from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def validating_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    if hasattr(self, 'validate'):
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValidationException(validation_result.errors, context={'class': cls.__name__, 'args': args, 'kwargs': kwargs})

@functools.wraps(original_init)