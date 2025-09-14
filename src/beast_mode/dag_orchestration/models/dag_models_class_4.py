from src.rm_ddd.core.registry import register_module
class SpecificationNode(ReflectiveModule):
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
    """Specification node in dependency graph."""
    spec_name: str
    spec_path: str
    completion_percentage: float
    task_count: int
    completed_tasks: int
    dependencies: List[str] = field(default_factory=list)  # spec names
    dependents: List[str] = field(default_factory=list)   # spec names
    layer: int = 0  # dependency layer (0 = no dependencies)
    
    def __post_init__(self) -> Any:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Validate specification node data."""
        if not (0 <= self.completion_percentage <= 100):
            raise ValueError("Completion percentage must be between 0 and 100")
        if self.completed_tasks > self.task_count:
            raise ValueError("Completed tasks cannot exceed total task count")


@dataclass
    def __init__(self):
        register_module('SpecificationNode', self)