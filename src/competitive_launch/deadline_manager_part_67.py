from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _identify_critical_path(self, analysis: Dict[str, Dict[str, Any]], graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """Identify critical path through task analysis."""
    critical_tasks = []
    for task_id, task_data in analysis.items():
        latest_start = task_data['earliest_start']
        slack = latest_start - task_data['earliest_start']
        if slack <= 0:
            critical_tasks.append({'id': task_id, 'duration_days': task_data['duration_days'], 'slack_days': slack, 'priority': task_data['priority'], 'competitive_impact': task_data['competitive_impact']})
    critical_tasks.sort(key=lambda x: analysis[x['id']]['earliest_start'])
    return critical_tasks

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

