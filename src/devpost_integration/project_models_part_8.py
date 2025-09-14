from src.rm_ddd.core.health import ModuleHealth

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.PROJECT_MANAGEMENT, ModuleCapability.TEAM_MANAGEMENT, ModuleCapability.SUBMISSION_TRACKING, ModuleCapability.DEADLINE_MANAGEMENT]
