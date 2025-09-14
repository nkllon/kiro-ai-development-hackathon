from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

            def calculate_total(self, order: Order) -> Money:
                return sum(item.price * item.quantity for item in order.items)
    ModuleHealth = ModuleHealth.HEALTHY
    ModuleStatus = ModuleStatus.ACTIVE

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

