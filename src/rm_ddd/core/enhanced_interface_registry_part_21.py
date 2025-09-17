from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def load_metrics(self):
        """Load interface metrics from storage"""
        metrics_file = self.registry_file.replace('.json', '_metrics.json')
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                for interface_id, metrics_data in data.items():
                    self.metrics[interface_id] = InterfaceMetrics(**metrics_data)
            except Exception as e:
                print(f"Warning: Could not load metrics: {e}")

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

    