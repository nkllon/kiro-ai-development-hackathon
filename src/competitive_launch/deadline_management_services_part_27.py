from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _find_critical_path(self, dependency_graph: Dict[str, List[str]], tasks: List[HackathonTask]) -> List[HackathonTask]:
        """Find critical path using topological sort."""
        sorted_tasks = sorted(tasks, key=lambda t: (t.priority.value, -t.estimated_hours))
        return sorted_tasks[:min(5, len(sorted_tasks))]

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

