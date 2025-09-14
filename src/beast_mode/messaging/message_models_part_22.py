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
    """Agent capabilities model with validation."""
    agent_id: str = Field(..., description='Unique agent identifier')
    agent_name: str = Field(..., description='Human-readable agent name')
    capabilities: List[AgentCapability] = Field(default_factory=list, description='List of agent capabilities')
    specializations: List[str] = Field(default_factory=list, description='Specialized skills or domains')
    availability: str = Field(default='available', description='Current availability status')
    office_hours: Optional[Dict[str, str]] = Field(None, description='Office hours schedule')
    max_concurrent_tasks: int = Field(default=3, description='Maximum concurrent tasks')
    current_load: int = Field(default=0, description='Current task load')
    trust_score: float = Field(default=0.5, ge=0.0, le=1.0, description='Trust score based on past performance')
    last_seen: datetime = Field(default_factory=datetime.now, description='Last activity timestamp')

    @validator('capabilities')