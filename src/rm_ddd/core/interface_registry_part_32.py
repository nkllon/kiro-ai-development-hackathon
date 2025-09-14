from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def load_registry(self):
        """Load registry from persistent storage"""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                for interface_id, interface_data in data.get('interfaces', {}).items():
                    self.interfaces[interface_id] = InterfaceMetadata(**interface_data)
                self.domain_index = data.get('domain_index', {})
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
    