from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _enforce_statelessness(cls: Type):
    """Enforce statelessness for domain services."""
    original_setattr = cls.__setattr__
