from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def is_domain_service(cls: Type) -> bool:
    """Check if a class has the @domain_service decorator applied."""
    return getattr(cls, '_is_domain_service', False)
