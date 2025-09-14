import time
import threading
import logging
import psutil
import subprocess
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from .config_manager import DeploymentConfig
from .service_monitor_services_validation import *
from .service_monitor_services_services import *
from .service_monitor_services_core import *
from src.rm_ddd.core.health import ModuleHealth


class RegistermoduleClass:
    """Auto-generated class for functions."""

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

