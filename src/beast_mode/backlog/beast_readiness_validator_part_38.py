from datetime import datetime
from typing import Dict, List, Any

    def _check_compliance_system_ready(self, compliance_data: Any) -> bool:
        """Check if compliance system is ready"""
        return compliance_data is not None and isinstance(compliance_data, dict)
    