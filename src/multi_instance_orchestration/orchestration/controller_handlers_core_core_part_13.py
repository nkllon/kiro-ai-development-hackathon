from src.rm_ddd.core.health import ModuleHealth

class UpdateswarmmetricsClass:
    """Auto-generated class for functions."""

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

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

