class TaskNode(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
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
    """Task node in dependency graph."""
    task_id: str
    spec_name: str
    task_name: str
    description: str
    estimated_effort: int  # hours
    completion_status: TaskStatus
    dependencies: List[str] = field(default_factory=list)  # task IDs
    dependents: List[str] = field(default_factory=list)   # task IDs
    requirements_traced: List[str] = field(default_factory=list)
    priority: int = 1  # 1=highest, 5=lowest
    complexity: float = 1.0  # 1.0=simple, 5.0=very complex
    
    def __post_init__(self) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate task node data."""
        if self.estimated_effort < 0:
            raise ValueError("Estimated effort cannot be negative")
        if not (1 <= self.priority <= 5):
            raise ValueError("Priority must be between 1 and 5")


@dataclass