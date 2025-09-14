from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def stateless_setattr(self, name: str, value: Any):
    if hasattr(self, '_initializing') or name.startswith('_'):
        original_setattr(self, name, value)
    else:
        raise DomainException(f"Cannot modify attribute '{name}' on stateless domain service", error_code='STATELESS_VIOLATION')

@functools.wraps(original_init)