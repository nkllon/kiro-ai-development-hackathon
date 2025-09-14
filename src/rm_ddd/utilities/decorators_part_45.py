from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _enforce_immutability(cls: Type):
    """Enforce immutability for value objects."""
    original_setattr = cls.__setattr__
