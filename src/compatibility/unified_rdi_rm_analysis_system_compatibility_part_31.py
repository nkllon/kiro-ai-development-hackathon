from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def save_registry(self):
        """Save registry to file"""
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w') as f:
                json.dump(self._serialize_registry(), f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    