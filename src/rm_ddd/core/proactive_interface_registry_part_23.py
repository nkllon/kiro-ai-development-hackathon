from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, registry_file: str = "proactive_interface_registry.json"):
        super().__init__(registry_file)
        self.health_checks: Dict[str, InterfaceHealthCheck] = {}
        self.duplicate_rules: List[DuplicatePreventionRule] = []
        self.monitoring_enabled = True
        self.load_health_checks()
        self.setup_default_rules()

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

    