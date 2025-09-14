from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def is_value_object(cls: Type) -> bool:
    """Check if a class has the @value_object decorator applied."""
    return getattr(cls, '_is_value_object', False)
