from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _create_error_summary(self, execution_start: datetime, error: str) -> Dict:
        """Create error summary."""
        return {
            "error": error,
            "execution_start": execution_start.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "success": False
        }
    