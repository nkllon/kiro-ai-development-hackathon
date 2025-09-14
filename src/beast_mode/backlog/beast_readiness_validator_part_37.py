from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _check_interface_registry_ready(self, registry_data: Any) -> bool:
        """Check if interface registry is ready"""
        return registry_data is not None and isinstance(registry_data, dict)
    