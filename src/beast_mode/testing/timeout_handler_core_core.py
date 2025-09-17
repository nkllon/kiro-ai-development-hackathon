import time
import signal
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .performance_monitor import PerformanceMetrics, PerformanceStatus
from .timeout_handler_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth


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

