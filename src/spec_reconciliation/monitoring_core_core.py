import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from threading import Thread, Event
import schedule
from src.beast_mode.core.reflective_module import ReflectiveModule
from .validation import ConsistencyValidator, ConsistencyMetrics, TerminologyReport
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .monitoring_core_core_validation import *
from .monitoring_core_core_handlers import *
from .monitoring_core_core_core import *
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

