from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Types of timing constraints."""
    HARD_LIMIT = 'hard_limit'
    SOFT_LIMIT = 'soft_limit'
    MINIMUM_TIME = 'minimum_time'
    BUFFER_TIME = 'buffer_time'

@dataclass