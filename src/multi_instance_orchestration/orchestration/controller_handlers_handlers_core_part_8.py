
def _calculate_parallel_groups(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
    """Calculate parallel execution groups using topological sort."""
    groups = []
    remaining_tasks = set(dependency_graph.keys())
    while remaining_tasks:
        ready_tasks = [task_id for task_id in remaining_tasks if not any((dep in remaining_tasks for dep in dependency_graph[task_id]))]
        if not ready_tasks:
            ready_tasks = [next(iter(remaining_tasks))]
        groups.append(ready_tasks)
        remaining_tasks -= set(ready_tasks)
    return groups
