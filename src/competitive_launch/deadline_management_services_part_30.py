from datetime import datetime
from typing import Dict, List, Any

    def _update_priorities_for_acceleration(self):
        """Update task priorities for emergency acceleration."""
        for task in self.tasks:
            if task.status == TaskStatus.COMPLETED:
                continue
            if task.competitive_impact > 0.8:
                task.priority = TaskPriority.CRITICAL
            elif task.competitive_impact < 0.3:
                task.priority = TaskPriority.LOW
