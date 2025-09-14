
def _create_distribution_plan(self, tasks: List[Task], instance_count: int, parallel_groups: List[List[str]]) -> DistributionPlan:
    """Create distribution plan based on strategy."""
    task_assignments = {f'instance-{i}': [] for i in range(instance_count)}
    for i, task in enumerate(tasks):
        instance_id = f'instance-{i % instance_count}'
        task_assignments[instance_id].append(task.id)
    max_tasks_per_instance = max((len(task_list) for task_list in task_assignments.values())) if task_assignments else 0
    avg_task_duration = sum((task.estimated_duration.total_seconds() for task in tasks)) / len(tasks) if tasks else 0
    estimated_completion_time = timedelta(seconds=max_tasks_per_instance * avg_task_duration)
    plan = DistributionPlan(total_tasks=len(tasks), strategy_used=self.config.task_distribution_strategy, parallel_execution_groups=parallel_groups, instance_assignments=task_assignments, estimated_completion_time=estimated_completion_time)
    return plan
