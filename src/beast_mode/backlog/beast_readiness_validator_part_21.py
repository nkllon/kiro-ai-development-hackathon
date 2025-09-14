from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def validate(self, value: Any) -> bool:
        """Validate value against rule"""
        try:
            return bool(self.validator(value))
        except Exception:
            return False
