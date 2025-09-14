
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.SETTINGS_MANAGEMENT, ModuleCapability.TIMING_CONTROL, ModuleCapability.CHANNEL_MANAGEMENT, ModuleCapability.PREFERENCE_CONTROL]
