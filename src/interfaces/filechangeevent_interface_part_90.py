from src.rm_ddd.core.health import ModuleHealth

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.EVENT_TRACKING, ModuleCapability.CHANGE_DETECTION, ModuleCapability.METADATA_MANAGEMENT]
