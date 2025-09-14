from src.rm_ddd.core.health import ModuleHealth

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.DATA_MANAGEMENT, ModuleCapability.VALIDATION, ModuleCapability.MONITORING]
