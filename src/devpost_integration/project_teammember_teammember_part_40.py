
def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.MEMBER_MANAGEMENT, ModuleCapability.ROLE_MANAGEMENT, ModuleCapability.PERMISSION_CONTROL]
