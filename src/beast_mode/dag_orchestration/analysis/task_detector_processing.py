"""
Task Detector Processing

This module was extracted from task_detector.py
as part of RM-DDD compliance refactoring.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from ..models.dag_models import TaskNode, DependencyEdge
from ..models.enums import TaskStatus
from .spec_parser import ParsedSpec
from src.rm_ddd.core.health import ModuleHealth


def _parse_task_line(self, line: str, line_index: int, lines: List[str]) -> Optional[Tuple[str, str, TaskStatus, str, List[str], List[str]]]:
    """Parse a single line to extract task information."""
    line = line.strip()
    if not line:
        return None
    checkbox_match = re.match('^\\s*-\\s*\\[\\s*([x\\s\\-!F])\\s*\\]\\s*(.+)$', line, re.IGNORECASE)
    if checkbox_match:
        status_char = checkbox_match.group(1).strip().lower()
        task_text = checkbox_match.group(2).strip()
        if status_char == 'x':
            status = TaskStatus.COMPLETED
        elif status_char == '-':
            status = TaskStatus.IN_PROGRESS
        elif status_char == '!':
            status = TaskStatus.BLOCKED
        elif status_char == 'f':
            status = TaskStatus.FAILED
        else:
            status = TaskStatus.NOT_STARTED
        task_id, task_name = self._extract_task_id_and_name(task_text)
        description, requirements, dependencies = self._extract_task_details(line_index, lines)
        return (task_id, task_name, status, description, requirements, dependencies)
    numbered_match = re.match('^\\s*(\\d+(?:\\.\\d+)*)\\.\\s*(.+)$', line)
    if numbered_match:
        task_id = numbered_match.group(1)
        task_text = numbered_match.group(2).strip()
        status = self._determine_status_from_text(task_text)
        task_name = self._clean_task_name(task_text)
        description, requirements, dependencies = self._extract_task_details(line_index, lines)
        return (task_id, task_name, status, description, requirements, dependencies)
    return None

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

