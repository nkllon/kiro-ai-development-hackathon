from datetime import datetime
from typing import Dict, List, Any

    def check_type(self, value: Any, expected_type: type) -> bool:
        """Support type checking and validation"""
        return isinstance(value, expected_type)
    