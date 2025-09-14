
def _get_completed_tasks(self, swarm: SwarmState) -> List[str]:
    """Get list of completed tasks ready for integration."""
    return [task_id for task_id, status in swarm.execution_status.items() if status == TaskStatus.COMPLETED]
