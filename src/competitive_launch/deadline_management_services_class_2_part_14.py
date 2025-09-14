from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def _find_critical_path(self, dependency_graph: Dict[str, List[str]], tasks: List[HackathonTask]) -> List[HackathonTask]:
        """Find critical path using topological sort."""
        sorted_tasks = sorted(tasks, key=lambda t: (t.priority.value, -t.estimated_hours))
        return sorted_tasks[:min(5, len(sorted_tasks))]
