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
    interface_id: str
    interface_name: str
    interface_type: InterfaceType
    version: str
    status: InterfaceStatus
    description: str
    domain_terms: List[str]
    capabilities: List[str]
    dependencies: List[str]
    file_path: str
    created_at: datetime
    last_modified: datetime
    created_by: str
    usage_count: int = 0
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None

@dataclass