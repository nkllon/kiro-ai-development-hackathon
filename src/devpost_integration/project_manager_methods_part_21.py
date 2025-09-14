from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Pathfrom ..interfaces.projectstatus_interface import ProjectStatusfrom ..interfaces.devpostprojectmanager_interface import DevpostProjectManager
import logging

    def __post_init__(self):
        """__post_init__ - Enhanced for compliance"""
        if self.pending_changes is None:
            self.pending_changes = []
        if self.validation_errors is None:
            self.validation_errors = []

    # ReflectiveModule interface implementation