from src.rm_ddd.core.health import ModuleHealth

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.CONFIG_MANAGEMENT, ModuleCapability.VALIDATION, ModuleCapability.EXPORT_IMPORT]
