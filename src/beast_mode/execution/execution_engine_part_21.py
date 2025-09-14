from datetime import datetime
from typing import Dict, List, Any

    def _all_tasks_completed(self) -> bool:
        """Check if all tasks are completed."""
        stats = self.task_manager.get_task_stats()
        total_tasks = sum(stats.values())
        return stats[TaskStatus.COMPLETED.value] == total_tasks
    