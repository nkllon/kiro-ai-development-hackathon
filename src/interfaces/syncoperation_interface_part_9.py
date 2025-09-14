
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.SYNC_OPERATIONS, ModuleCapability.PROGRESS_TRACKING, ModuleCapability.ERROR_HANDLING, ModuleCapability.STATUS_MONITORING]
