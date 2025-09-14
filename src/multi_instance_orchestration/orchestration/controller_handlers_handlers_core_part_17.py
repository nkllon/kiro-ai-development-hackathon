from src.rm_ddd.core.health import ModuleHealth

class GetcompletedtasksClass:
    """Auto-generated class for functions."""

    def _get_completed_tasks(self, swarm: SwarmState) -> List[str]:
    """Get list of completed tasks ready for integration."""
    return [task_id for task_id, status in swarm.execution_status.items() if status == TaskStatus.COMPLETED]

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

