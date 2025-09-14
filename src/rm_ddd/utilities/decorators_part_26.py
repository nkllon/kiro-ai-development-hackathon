from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def check_health(self):
        return {
            'status': self.ModuleStatus,
            'health': self.ModuleHealth
        }
    """
