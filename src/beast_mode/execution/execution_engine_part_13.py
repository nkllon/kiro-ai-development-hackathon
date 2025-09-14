from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Main execution engine that orchestrates task execution.
"""
from datetime import datetime
from typing import Dict, List, Optional
import logging

from .task_manager import TaskManager, Task, TaskStatus
from .agent_manager import AgentManager, Agent
from .git_session import GitSession
from src.rm_ddd.core.health import ModuleHealth

