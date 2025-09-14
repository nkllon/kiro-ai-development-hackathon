from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _add_auto_timestamping(cls: Type):
    """Add automatic timestamping for domain events."""
    original_init = cls.__init__

    @functools.wraps(original_init)