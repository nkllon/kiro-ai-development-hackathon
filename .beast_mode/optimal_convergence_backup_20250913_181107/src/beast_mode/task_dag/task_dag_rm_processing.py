"""
Task Dag Rm Processing

This module was extracted from task_dag_rm.py
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

def _parse_tasks_markdown(self, content: str) -> Dict[str, TaskNode]:
    """
        Parse tasks from markdown content
        
        Expected format:
        - [ ] 1. Task Name
          - Description
          - _Requirements: req1, req2_
        
        - [ ] 1.1 Subtask Name
          - Subtask description
          - _Requirements: req3_
        """
    tasks = {}
    current_task = None
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        task_match = re.match('^-\\s*\\[\\s*[x\\s]\\s*\\]\\s*(\\d+(?:\\.\\d+)*)\\s+(.+)$', line)
        if task_match:
            task_id = task_match.group(1)
            task_name = task_match.group(2)
            current_task = TaskNode(id=task_id, name=task_name, description='', dependencies=self._extract_dependencies(task_id), requirements=[], estimated_hours=4.0, priority=1)
            tasks[task_id] = current_task
            continue
        req_match = re.match('^_Requirements:\\s*(.+)_$', line)
        if req_match and current_task:
            reqs = [r.strip() for r in req_match.group(1).split(',')]
            current_task.requirements = reqs
            continue
        if current_task and line and (not line.startswith('-')) and (not line.startswith('_')):
            if current_task.description:
                current_task.description += ' ' + line
            else:
                current_task.description = line
    return tasks
