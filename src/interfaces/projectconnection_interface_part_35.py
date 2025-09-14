
def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.METADATA_MANAGEMENT, ModuleCapability.VALIDATION, ModuleCapability.EXPORT_IMPORT]
