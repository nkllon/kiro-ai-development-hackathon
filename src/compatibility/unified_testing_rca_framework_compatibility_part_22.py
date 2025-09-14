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
    """Interface metadata"""
    name: str
    type: InterfaceType
    status: InterfaceStatus
    file_path: str
    line_number: int
    methods: List[str]
    created_at: datetime
    compliance_score: float
