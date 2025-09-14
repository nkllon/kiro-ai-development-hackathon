from src.rm_ddd.core.health import ModuleHealth, ModuleStatus
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule


def is_aggregate_root(cls: Type) -> bool:
    """Check if a class has the @aggregate_root decorator applied."""
    return getattr(cls, '_is_aggregate_root', False)

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

