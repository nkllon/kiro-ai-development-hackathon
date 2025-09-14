from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_metadata(self, name: str) -> Optional[InterfaceMetadata]:
        """Get interface metadata"""
        return self.interfaces.get(name)
    