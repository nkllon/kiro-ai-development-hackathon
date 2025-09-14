
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.VALIDATION,
            ModuleCapability.ERROR_HANDLING,
            ModuleCapability.MONITORING,
            ModuleCapability.REPORTING
        ]
    