from datetime import datetime
from typing import Dict, List, Any

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
