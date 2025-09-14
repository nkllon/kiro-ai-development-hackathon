from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

            def __init__(self, order_id: str, customer_id: str):
                super().__init__(order_id)
                self.customer_id = customer_id
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE
