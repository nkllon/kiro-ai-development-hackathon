from datetime import datetime
from typing import Dict, List, Any

    def _build_dependency_graph(self, tasks: List[HackathonTask]) -> Dict[str, List[str]]:
        """Build dependency graph from tasks."""
        graph = {}
        for task in tasks:
            graph[task.task_id] = task.dependencies
        return graph
