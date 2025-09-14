from datetime import datetime
from typing import Dict, List, Any

    def validate(self, value: Any) -> bool:
        """Validate value against rule"""
        try:
            return bool(self.validator(value))
        except Exception:
            return False
