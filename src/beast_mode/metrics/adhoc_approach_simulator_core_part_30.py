from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def list_interfaces(self) -> List[str]:
        """List all registered interfaces"""
        return list(self.interfaces.keys())
    