from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def get_domain_context(cls: Type) -> Optional[str]:
    """Get the domain context for a decorated class."""
    return getattr(cls, '_domain_context', None)
