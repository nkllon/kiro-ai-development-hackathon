
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.RESULT_TRACKING, ModuleCapability.ERROR_HANDLING, ModuleCapability.METRICS_COLLECTION, ModuleCapability.REPORTING]
