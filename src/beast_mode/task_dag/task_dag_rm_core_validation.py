"""
Task Dag Rm Core Validation

This module was extracted from task_dag_rm_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
import random
import random
import random
from src.rm_ddd.core.health import ModuleHealth


def _validate_dag(self) -> bool:
    """Validate that the DAG has no cycles"""
    visited = set()
    rec_stack = set()

    def has_cycle(task_id: str) -> bool:
        if task_id in rec_stack:
            return True
        if task_id in visited:
            return False
        visited.add(task_id)
        rec_stack.add(task_id)
        if task_id in self.tasks:
            for dep_id in self.tasks[task_id].dependencies:
                if has_cycle(dep_id):
                    return True
        rec_stack.remove(task_id)
        return False
    for task_id in self.tasks:
        if task_id not in visited:
            if has_cycle(task_id):
                return False
    return True
