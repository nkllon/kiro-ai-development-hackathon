from src.rm_ddd.core.health import ModuleHealth

    def get_health_status(self) -> HealthStatus:
        """Get health status for RM pattern compliance"""
        return self.health_status
