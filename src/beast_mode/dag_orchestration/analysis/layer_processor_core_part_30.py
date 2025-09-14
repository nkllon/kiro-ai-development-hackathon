from datetime import datetime
from typing import Dict, List, Any

def _group_parallel_tasks(self, task_ids: List[str], constraint_graph: ConstraintGraph) -> List[List[str]]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Group tasks that can run in parallel within a layer."""
    if len(task_ids) <= 1:
        return [task_ids] if task_ids else []
    groups = []
    remaining_tasks = task_ids.copy()
    while remaining_tasks:
        current_group = [remaining_tasks.pop(0)]
        current_effort = constraint_graph.nodes[current_group[0]].estimated_effort
        i = 0
        while i < len(remaining_tasks):
            task_id = remaining_tasks[i]
            task_effort = constraint_graph.nodes[task_id].estimated_effort
            if abs(task_effort - current_effort) / max(current_effort, 1) <= 0.5:
                current_group.append(remaining_tasks.pop(i))
            else:
                i += 1
        groups.append(current_group)
    return groups
