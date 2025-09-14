from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class AddtaskClass:
    """Auto-generated class for functions."""

    def add_task(self, task: HackathonTask) -> bool:
    """Add a task to the hackathon plan."""
    try:
    if any((t.task_id == task.task_id for t in self.tasks)):
    logger.warning(f'Task {task.task_id} already exists')
    return False
    self.tasks.append(task)
    logger.info(f'Task added: {task.task_id} - {task.title}')
    return True
    except Exception as e:
    logger.error(f'Failed to add task {task.task_id}: {e}')
    return False

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

