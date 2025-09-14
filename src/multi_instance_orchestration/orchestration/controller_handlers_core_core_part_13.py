from src.rm_ddd.core.health import ModuleHealth

def _update_swarm_metrics(self, swarm: SwarmState) -> None:
    """Update performance metrics for swarm."""
    metrics = swarm.performance_metrics
    completed_count = sum((1 for status in swarm.execution_status.values() if status == TaskStatus.COMPLETED))
    failed_count = sum((1 for status in swarm.execution_status.values() if status == TaskStatus.FAILED))
    metrics.completed_tasks = completed_count
    metrics.failed_tasks = failed_count
    metrics.active_instances = len([i for i in swarm.instances.values() if i.status == 'active'])
    total_finished = completed_count + failed_count
    metrics.error_rate = failed_count / total_finished if total_finished > 0 else 0.0
    metrics.last_updated = datetime.now()
