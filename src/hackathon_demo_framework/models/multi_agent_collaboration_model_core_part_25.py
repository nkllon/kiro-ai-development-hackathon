
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
    """Represents a task for agent collaboration"""
    task_id: str
    description: str
    complexity: float
    required_agents: List[AgentType]
    human_input: Optional[str]
    created_at: datetime

@dataclass