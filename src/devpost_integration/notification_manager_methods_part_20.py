from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

    def __init__(self):
        """Initialize notification manager"""
        super().__init__(module_id="notificationmanager", version="1.0.0")
        register_module(self)
    