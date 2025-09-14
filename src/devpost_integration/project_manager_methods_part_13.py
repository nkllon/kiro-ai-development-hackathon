from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Pathfrom ..interfaces.projectstatus_interface import ProjectStatusfrom ..interfaces.devpostprojectmanager_interface import DevpostProjectManager
import logging

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {
            'uptime': (datetime.now() - self._start_time).total_seconds(),
            'connected': self.status.connected,
            'project_id': self.status.project_id
        }
    