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
    """Agent: - Enhanced for compliance"""
    id: str
    name: str
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: int = 0
    is_available: bool = True
