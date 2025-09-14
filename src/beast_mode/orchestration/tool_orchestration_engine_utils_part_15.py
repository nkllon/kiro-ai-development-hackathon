
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
    """Definition of a tool in the orchestration system"""
    tool_id: str
    name: str
    description: str
    command: str
    health_check_command: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    priority: ToolPriority = ToolPriority.MEDIUM
    timeout_seconds: int = 300
    retry_attempts: int = 3
    fallback_tools: List[str] = field(default_factory=list)
    repair_procedures: List[str] = field(default_factory=list)

@dataclass