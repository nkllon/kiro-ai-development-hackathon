from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_capabilities(self) -> List[str]:
        """Return list of security analysis capabilities"""
        return self._capabilities.copy()
