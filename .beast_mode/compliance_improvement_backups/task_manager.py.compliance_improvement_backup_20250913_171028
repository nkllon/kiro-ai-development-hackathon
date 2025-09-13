"""
Task management and lifecycle operations.
"""
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import logging

from .commands import TaskCommand

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class Task:
    def __init__(self, task_id: str, description: str, command: TaskCommand, dependencies: List[str] = None):
        self.id = task_id
        self.description = description
        self.command = command
        self.dependencies = dependencies or []
        self.status = TaskStatus.NOT_STARTED
        self.assigned_agent = None
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None
    
    def execute(self) -> bool:
        """Execute the task's command."""
        self.start_time = datetime.now()
        success = self.command.execute()
        self.end_time = datetime.now()
        
        if success:
            self.result = self.command.result
        else:
            self.error = self.command.error
        
        return success

class TaskManager:
    """Manages task lifecycle and dependencies."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the manager."""
        self.tasks[task.id] = task
        self.logger.info(f"Added task: {task.id}")
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready for execution."""
        ready_tasks = []
        for task in self.tasks.values():
            if task.status == TaskStatus.NOT_STARTED:
                if self._are_dependencies_met(task):
                    ready_tasks.append(task)
        return ready_tasks
    
    def _are_dependencies_met(self, task: Task) -> bool:
        """Check if all dependencies for a task are completed."""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    def start_task(self, task_id: str, agent_id: str) -> bool:
        """Mark a task as started."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent = agent_id
        task.start_time = datetime.now()
        self.logger.info(f"Started task {task_id} with agent {agent_id}")
        return True
    
    def execute_task(self, task_id: str) -> bool:
        """Execute a task and update its status."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        success = task.execute()
        
        if success:
            task.status = TaskStatus.COMPLETED
            self.logger.info(f"Completed task {task_id}")
        else:
            task.status = TaskStatus.FAILED
            self.logger.error(f"Failed task {task_id}: {task.error}")
        
        return success
    
    def complete_task(self, task_id: str, result: any = None) -> bool:
        """Mark a task as completed (for backward compatibility)."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.end_time = datetime.now()
        task.result = result
        self.logger.info(f"Completed task {task_id}")
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.end_time = datetime.now()
        task.error = error
        self.logger.error(f"Failed task {task_id}: {error}")
        return True
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get statistics about task statuses."""
        stats = {status.value: 0 for status in TaskStatus}
        for task in self.tasks.values():
            stats[task.status.value] += 1
        return stats