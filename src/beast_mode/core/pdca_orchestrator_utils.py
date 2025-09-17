"""
Pdca Orchestrator Utils

This module was extracted from pdca_orchestrator.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from .reflective_module import ReflectiveModule, HealthStatus
from ..intelligence.registry_intelligence_engine import ProjectRegistryIntelligenceEngine, IntelligenceQuery
from ..tool_health.makefile_health_manager import MakefileHealthManager
from src.rm_ddd.core.health import ModuleHealth


def _identify_required_tools(self, task: DevelopmentTask) -> List[str]:
    """Identify tools required for task execution"""
    tools = ['registry_engine']
    if 'makefile' in task.task_name.lower():
        tools.append('makefile_manager')
    return tools

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

