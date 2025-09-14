from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Pathfrom ..interfaces.projectstatus_interface import ProjectStatusfrom ..interfaces.devpostprojectmanager_interface import DevpostProjectManager
import logging

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    