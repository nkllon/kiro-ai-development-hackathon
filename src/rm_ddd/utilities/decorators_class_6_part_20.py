from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _add_creation_validation(cls: Type):
    """Add creation-time validation for value objects."""
    original_init = cls.__init__

    @functools.wraps(original_init)