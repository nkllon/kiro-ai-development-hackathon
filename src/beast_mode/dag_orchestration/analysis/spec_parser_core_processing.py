"""
Spec Parser Core Processing

This module was extracted from spec_parser_core.py
as part of RM-DDD compliance refactoring.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..models.dag_models import SpecificationNode, TaskNode
from ..models.enums import TaskStatus
from src.rm_ddd.core.health import ModuleHealth


def parse_specification_directory(self, spec_directory: str) -> List[ParsedSpec]:
    """
        Parse all specifications in a directory.
        
        Args:
            spec_directory: Root directory containing specifications
            
        Returns:
            List[ParsedSpec]: All parsed specifications
        """
    parsed_specs = []
    spec_path = Path(spec_directory)
    if not spec_path.exists():
        raise FileNotFoundError(f'Specification directory not found: {spec_directory}')
    for spec_file in spec_path.rglob('*.md'):
        if self._is_spec_file(spec_file):
            try:
                parsed_spec = self.parse_specification_file(str(spec_file))
                parsed_specs.append(parsed_spec)
            except Exception as e:
                print(f'Warning: Failed to parse {spec_file}: {e}')
    return parsed_specs

def parse_specification_file(self, spec_file_path: str) -> ParsedSpec:
    """
        Parse a single specification file.
        
        Args:
            spec_file_path: Path to specification file
            
        Returns:
            ParsedSpec: Parsed specification data
        """
    spec_path = Path(spec_file_path)
    if not spec_path.exists():
        raise FileNotFoundError(f'Specification file not found: {spec_file_path}')
    with open(spec_path, 'r', encoding='utf-8') as f:
        content = f.read()
    spec_name = self._extract_spec_name(spec_path)
    requirements_count = self._count_requirements(content)
    tasks_count = self._count_tasks(content)
    completion_percentage = self._calculate_completion_percentage(content)
    dependencies = self._extract_spec_dependencies(content, spec_path)
    return ParsedSpec(spec_name=spec_name, spec_path=str(spec_path), requirements_count=requirements_count, tasks_count=tasks_count, completion_percentage=completion_percentage, dependencies=dependencies, raw_content=content)

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

