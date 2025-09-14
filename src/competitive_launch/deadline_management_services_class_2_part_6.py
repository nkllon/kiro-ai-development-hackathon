from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs) -> bool:
        """Update task status and progress."""
        try:
            task = self._find_task(task_id)
            if not task:
                logger.error(f'Task {task_id} not found')
                return False
            old_status = task.status
            task.status = status
            if status == TaskStatus.IN_PROGRESS and (not task.started_at):
                task.started_at = datetime.now()
            elif status == TaskStatus.COMPLETED and (not task.completed_at):
                task.completed_at = datetime.now()
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            logger.info(f'Task {task_id} status updated: {old_status.value} -> {status.value}')
            return True
        except Exception as e:
            logger.error(f'Failed to update task {task_id}: {e}')
            return False
