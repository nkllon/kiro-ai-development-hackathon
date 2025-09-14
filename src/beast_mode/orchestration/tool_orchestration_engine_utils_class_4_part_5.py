
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
    """Result of tool execution"""
    tool_id: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int = 0
    exit_code: Optional[int] = None
    health_status: ToolStatus = ToolStatus.UNKNOWN
    repair_attempted: bool = False
    repair_successful: bool = False
    fallback_used: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
