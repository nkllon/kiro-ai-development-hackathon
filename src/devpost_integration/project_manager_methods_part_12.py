from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Pathfrom ..interfaces.projectstatus_interface import ProjectStatusfrom ..interfaces.devpostprojectmanager_interface import DevpostProjectManager
import logging

    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        if config.project_path:
            self.status.local_path = config.project_path
        if config.connected is not None:
            self.status.connected = config.connected
        return True
    