from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class BuilddependencygraphClass:
    """Auto-generated class for functions."""

    def _build_dependency_graph(self, tasks: List[HackathonTask]) -> Dict[str, List[str]]:
    """Build dependency graph from tasks."""
    graph = {}
    for task in tasks:
    graph[task.task_id] = task.dependencies
    return graph

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

