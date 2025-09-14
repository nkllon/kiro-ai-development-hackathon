from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def _has_deadlock(self) -> bool:
        """Check for potential deadlock situation."""
        stats = self.task_manager.get_task_stats()
        return (stats[TaskStatus.IN_PROGRESS.value] == 0 and 
                stats[TaskStatus.NOT_STARTED.value] > 0)
    