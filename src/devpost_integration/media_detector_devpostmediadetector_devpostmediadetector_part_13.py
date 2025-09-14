
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.HEALTH_MONITORING,
            ModuleCapability.CONFIGURATION,
            ModuleCapability.LOGGING,
            ModuleCapability.METRICS,
            ModuleCapability.PERSISTENCE
        ]
    