from datetime import datetime
from typing import Dict, List, Any

    def _build_dependency_graph(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build dependency graph from tasks."""
        graph = {}
        for task in tasks:
            task_id = task.get('id', f'task_{len(graph)}')
            dependencies = task.get('dependencies', [])
            graph[task_id] = dependencies
        return graph
