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
    """Fallback agent capabilities without Pydantic validation."""
    agent_id: str
    agent_name: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    availability: str = 'available'
    office_hours: Optional[Dict[str, str]] = None
    max_concurrent_tasks: int = 3
    current_load: int = 0
    trust_score: float = 0.5
    last_seen: datetime = field(default_factory=datetime.now)

@dataclass