from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def is_aggregate_root(cls: Type) -> bool:
    """Check if a class has the @aggregate_root decorator applied."""
    return getattr(cls, '_is_aggregate_root', False)
