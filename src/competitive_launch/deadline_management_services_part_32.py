from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class LoaddefaulttasksClass:
    """Auto-generated class for functions."""

    def _load_default_tasks(self):
    """Load default hackathon tasks."""
    default_tasks = [HackathonTask(task_id='devpost_integration', title='DevPost Integration Complete', description='Complete DevPost platform integration with API client, authentication, and project management', priority=TaskPriority.CRITICAL, status=TaskStatus.COMPLETED, estimated_hours=16.0, actual_hours=16.0, competitive_impact=0.9, technical_debt_risk=0.0, completed_at=datetime.now()), HackathonTask(task_id='competitive_intelligence', title='Competitive Intelligence System', description='Implement real-time competitor monitoring and response automation', priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS, estimated_hours=12.0, competitive_impact=0.8, technical_debt_risk=0.2), HackathonTask(task_id='deadline_management', title='Deadline Management System', description='Deploy hackathon deadline orchestration with critical path analysis', priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS, estimated_hours=8.0, competitive_impact=0.7, technical_debt_risk=0.1), HackathonTask(task_id='demo_preparation', title='Demo and Presentation Preparation', description='Prepare comprehensive demo and presentation materials', priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED, estimated_hours=6.0, competitive_impact=0.6, technical_debt_risk=0.0), HackathonTask(task_id='documentation', title='Documentation and README', description='Create comprehensive documentation and README files', priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED, estimated_hours=4.0, competitive_impact=0.4, technical_debt_risk=0.0)]
    for task in default_tasks:
    self.tasks.append(task)

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

