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
    """Safety and resource usage metrics"""
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_io_operations: int
    network_operations: int
    analysis_duration_seconds: float
    safety_checks_passed: int
    safety_violations: List[str]

@dataclass(frozen=True)