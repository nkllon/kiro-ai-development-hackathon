from datetime import datetime
from typing import Dict, List, Any

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
    """Phase 3 readiness status levels."""
    READY = 'ready'
    CONDITIONALLY_READY = 'conditionally_ready'
    NOT_READY = 'not_ready'
    BLOCKED = 'blocked'
