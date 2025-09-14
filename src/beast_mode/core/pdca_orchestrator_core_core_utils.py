"""
Pdca Orchestrator Core Core Utils

This module was extracted from pdca_orchestrator_core_core.py
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
