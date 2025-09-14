from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _check_validation_framework_ready(self, validation_data: Any) -> bool:
        """Check if validation framework is ready"""
        return validation_data is not None and isinstance(validation_data, dict)
    