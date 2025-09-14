from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

            def calculate_total(self, order: Order) -> Money:
                return sum(item.price * item.quantity for item in order.items)
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE
