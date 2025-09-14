from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class AnalyzetaskdurationsClass:
    """Auto-generated class for functions."""

    def _analyze_task_durations(self, tasks: List[Dict[str, Any]], graph: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    """Analyze task durations and calculate slack."""
    analysis = {}
    for task in tasks:
    task_id = task.get('id', f'task_{len(analysis)}')
    duration = task.get('estimated_duration_days', 1)
    dependencies = task.get('dependencies', [])
    earliest_start = 0
    if dependencies:
    dependency_durations = []
    for dep in dependencies:
    if dep in analysis:
    dependency_durations.append(analysis[dep].get('earliest_finish', 0))
    else:
    dependency_durations.append(0)
    earliest_start = max(dependency_durations) if dependency_durations else 0
    earliest_finish = earliest_start + duration
    analysis[task_id] = {'duration_days': duration, 'earliest_start': earliest_start, 'earliest_finish': earliest_finish, 'dependencies': dependencies, 'priority': task.get('priority', 'medium'), 'competitive_impact': task.get('competitive_impact', 0.5)}
    return analysis

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

