from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

    def __init__(self):
        super().__init__(module_id="notification_config", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

    # ReflectiveModule interface implementation