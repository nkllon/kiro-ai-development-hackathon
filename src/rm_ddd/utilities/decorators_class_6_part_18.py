from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def immutable_setattr(self, name: str, value: Any):
        if not hasattr(self, '_initialized') or name.startswith('_'):
            original_setattr(self, name, value)
        else:
            raise DomainException(f"Cannot modify attribute '{name}' on immutable value object", error_code='IMMUTABILITY_VIOLATION')
    cls.__setattr__ = immutable_setattr
    original_init = cls.__init__

    @functools.wraps(original_init)