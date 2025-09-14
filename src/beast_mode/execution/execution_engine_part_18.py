from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def add_task(self, task: Task) -> None:
        """Add a task to the execution queue."""
        self.task_manager.add_task(task)
    