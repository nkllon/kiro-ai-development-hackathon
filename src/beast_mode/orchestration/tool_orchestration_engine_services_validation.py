"""
Tool Orchestration Engine Services Validation

This module was extracted from tool_orchestration_engine_services.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..intelligence.model_driven_intelligence_engine import ModelDrivenIntelligenceEngine
from ..analysis.rca_engine import RCAEngine
from ..ghostbusters.multi_perspective_validator import MultiPerspectiveValidator as MultiStakeholderPerspectiveEngine
from collections import Counter
from ..analysis.rca_engine import Failure, FailureCategory
from ..analysis.rca_engine import RCAEngine
from collections import Counter
from ..analysis.rca_engine import Failure, FailureCategory
from ..analysis.rca_engine import RCAEngine

def _check_tool_health(self, tool_id: str) -> Dict[str, Any]:
    """
        Check health of a specific tool
        """
    if tool_id not in self.tools_registry:
        return {'status': ToolStatus.UNKNOWN, 'error': 'Tool not registered'}
    tool_def = self.tools_registry[tool_id]
    if tool_def.health_check_command:
        try:
            result = subprocess.run(tool_def.health_check_command.split(), capture_output=True, text=True, timeout=30, cwd=self.project_root)
            if result.returncode == 0:
                status = ToolStatus.HEALTHY
            else:
                status = ToolStatus.FAILED
        except Exception:
            status = ToolStatus.FAILED
    else:
        try:
            result = subprocess.run(['which', tool_def.command.split()[0]], capture_output=True, text=True, timeout=10)
            status = ToolStatus.HEALTHY if result.returncode == 0 else ToolStatus.FAILED
        except Exception:
            status = ToolStatus.FAILED
    self.tool_health_cache[tool_id] = status
    return {'status': status, 'tool_id': tool_id, 'timestamp': datetime.now()}

def _validate_tool_definition(self, tool_def: ToolDefinition) -> bool:
    """
        Validate tool definition
        """
    if not tool_def.tool_id or not tool_def.name:
        return False
    if not tool_def.command:
        return False
    if tool_def.timeout_seconds <= 0:
        return False
    return True

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

