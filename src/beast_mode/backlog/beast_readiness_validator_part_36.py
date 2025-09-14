from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _check_beast_mode_ready(self, system_data: Any) -> bool:
        """Check if Beast Mode system is ready"""
        return system_data is not None and isinstance(system_data, dict)
    