from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _build_dependency_graph(self, tasks: List[HackathonTask]) -> Dict[str, List[str]]:
        """Build dependency graph from tasks."""
        graph = {}
        for task in tasks:
            graph[task.task_id] = task.dependencies
        return graph
