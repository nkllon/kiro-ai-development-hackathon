
def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.MESSAGE_MANAGEMENT, ModuleCapability.DELIVERY_TRACKING, ModuleCapability.RECIPIENT_MANAGEMENT]
