from datetime import datetime
from typing import Dict, List, Any

    def _find_task(self, task_id: str) -> Optional[HackathonTask]:
        """Find task by ID."""
        return next((t for t in self.tasks if t.task_id == task_id), None)
