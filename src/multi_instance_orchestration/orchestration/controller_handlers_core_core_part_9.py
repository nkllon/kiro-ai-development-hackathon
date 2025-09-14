
def _calculate_optimal_instances(self, tasks: List[Task], parallel_groups: List[List[str]]) -> int:
    """Calculate optimal number of instances based on tasks and parallelism."""
    max_parallel = max((len(group) for group in parallel_groups)) if parallel_groups else 1
    optimal = min(max_parallel, self.config.instance_count, self.config.max_instances, len(tasks))
    return max(optimal, self.config.min_instances)
