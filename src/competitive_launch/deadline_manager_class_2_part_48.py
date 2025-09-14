from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def __init__(self):
    """Initialize deadline management system."""
    self.hackathon_deadline = datetime(2025, 9, 15, 12, 0)
    self.critical_path_tasks = []
    self.emergency_protocols_active = False
    self.scope_optimization_history = []
    logger.info('Deadline Management System initialized')

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

