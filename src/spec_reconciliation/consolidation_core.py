import ast
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import hashlib
import re
from datetime import datetime
from src.beast_mode.core.reflective_module import ReflectiveModule
from .governance import GovernanceController
from .models import OverlapSeverity, OverlapReport
import time
import time
import time
import time
import time
import time
from .consolidation_core_validation import *
from .consolidation_core_core import *
from .consolidation_core_processing import *
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

