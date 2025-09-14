from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

            def __init__(self, order_id: str):
                super().__init__(order_id, "order_management")
                self.items = []
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE
