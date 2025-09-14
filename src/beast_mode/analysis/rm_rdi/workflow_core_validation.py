"""
Workflow Core Validation

This module was extracted from workflow_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from .data_models import AnalysisResult, AnalysisStatus
from .safety import get_safety_manager
from src.rm_ddd.core.health import ModuleHealth


def _validate_dependencies(self, steps: List[WorkflowStep]) -> None:
    """Validate step dependencies are valid"""
    step_ids = {step.step_id for step in steps}
    for step in steps:
        for dep in step.dependencies:
            if dep not in step_ids:
                raise ValueError(f'Invalid dependency {dep} for step {step.step_id}')
    self._check_circular_dependencies(steps)

def _check_circular_dependencies(self, steps: List[WorkflowStep]) -> None:
    """Check for circular dependencies in workflow steps"""
    visited = set()
    rec_stack = set()

    def has_cycle(step_id: str, step_map: Dict[str, WorkflowStep]) -> bool:
        visited.add(step_id)
        rec_stack.add(step_id)
        step = step_map[step_id]
        for dep in step.dependencies:
            if dep not in visited:
                if has_cycle(dep, step_map):
                    return True
            elif dep in rec_stack:
                return True
        rec_stack.remove(step_id)
        return False
    step_map = {step.step_id: step for step in steps}
    for step in steps:
        if step.step_id not in visited:
            if has_cycle(step.step_id, step_map):
                raise ValueError(f'Circular dependency detected involving step {step.step_id}')

def _validate_result_safety(self, result: AggregatedResult) -> bool:
    """Validate that aggregated result is safe"""
    if not result.safety_validated or not result.emergency_shutdown_available:
        return False
    for step_result in result.step_results.values():
        if step_result.result and (not step_result.result.safety_validated):
            return False
    return True
