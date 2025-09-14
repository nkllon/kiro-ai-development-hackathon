
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
    """Represents an AI agent with specialized capabilities"""
    agent_id: str
    agent_type: AgentType
    name: str
    capabilities: List[str]
    expertise_level: float
    collaboration_score: float
    created_at: datetime

@dataclass