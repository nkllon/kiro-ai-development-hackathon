import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..core.system_orchestrator import BeastModeSystemOrchestrator
from .gke_service_interface_validation import *
from .gke_service_interface_core import *
from .gke_service_interface_processing import *
from .gke_service_interface_services import *
from .gke_service_interface_utils import *
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

