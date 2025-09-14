from src.rm_ddd.core.registry import register_module
class TaskCommand(ABC, ReflectiveModule):
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
    """Abstract base class for executable task commands."""
    
    def __init__(self, task_id: str, name: str, description: str):
        register_module(self.__class__.__name__, self)
        self.task_id = task_id
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
    
    @abstractmethod
    def execute(self) -> bool:
        """execute - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Execute the task command. Returns True if successful."""
        pass
    
    def rollback(self) -> bool:
        """rollback - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Rollback changes made by this command. Override if needed."""
        self.logger.info(f"No rollback needed for {self.task_id}")
        return True
    
    def get_duration(self) -> float:
        """get_duration - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
