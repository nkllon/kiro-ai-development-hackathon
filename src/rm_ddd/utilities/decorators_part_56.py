from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def is_domain_entity(cls: Type) -> bool:
    """Check if a class has the @domain_entity decorator applied."""
    return getattr(cls, '_is_domain_entity', False)
