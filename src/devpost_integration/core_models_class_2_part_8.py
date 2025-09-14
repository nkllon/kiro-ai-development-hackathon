
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.CONFIG_MANAGEMENT, ModuleCapability.STATUS_MONITORING]
