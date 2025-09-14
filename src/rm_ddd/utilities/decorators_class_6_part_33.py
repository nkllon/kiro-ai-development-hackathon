from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def has_ubiquitous_language(cls: Type) -> bool:
    """Check if a class has the @ubiquitous_language decorator applied."""
    return getattr(cls, '_has_ubiquitous_language', False)
