from datetime import datetime
from typing import Dict, List, Any

    def load_health_checks(self):
        """Load interface health checks from storage"""
        health_file = self.registry_file.replace('.json', '_health.json')
        if os.path.exists(health_file):
            try:
                with open(health_file, 'r') as f:
                    data = json.load(f)
                for interface_id, health_data in data.items():
                    self.health_checks[interface_id] = InterfaceHealthCheck(**health_data)
            except Exception as e:
                print(f"Warning: Could not load health checks: {e}")

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

    