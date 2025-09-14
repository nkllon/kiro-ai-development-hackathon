from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_supported_formats(self) -> List[str]:
        """Get list of all supported formats."""
        return list(self.processors.keys())
    