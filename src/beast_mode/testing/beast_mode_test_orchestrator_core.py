import logging
import time
import traceback
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import pytest
from contextlib import contextmanager
from ..core.reflective_module import ReflectiveModule
from ..analysis.rca_engine import RCAEngine
from .rca_integration import TestRCAIntegrationEngine
import psutil
import threading
import psutil
import psutil
import psutil
import threading
import psutil
from .beast_mode_test_orchestrator_core_core import *
from .beast_mode_test_orchestrator_core_validation import *
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

