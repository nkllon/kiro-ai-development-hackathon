"""
Phase Optimizer Core Processing

This module was extracted from phase_optimizer_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import math
from ..models.dag_models import MVPPhase, TaskNode, ParallelGroup, ResourceRequirements, MVPRoute, RiskFactor
from ..models.enums import TaskStatus, RiskType, RiskImpact

def process_task(task: TaskNode):
    if task.task_id in processed:
        return
    for dep_id in task.dependencies:
        if dep_id in task_lookup and dep_id not in processed:
            process_task(task_lookup[dep_id])
    sorted_tasks.append(task)
    processed.add(task.task_id)

def process_task(task: TaskNode):
    if task.task_id in processed:
        return
    for dep_id in task.dependencies:
        if dep_id in task_lookup and dep_id not in processed:
            process_task(task_lookup[dep_id])
    sorted_tasks.append(task)
    processed.add(task.task_id)
