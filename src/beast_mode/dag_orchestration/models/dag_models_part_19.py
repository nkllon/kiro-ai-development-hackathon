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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    