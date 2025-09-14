"""
Design Validator Core Core Processing

This module was extracted from design_validator_core_core.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule


def _parse_design_file(self, file_path: Path) -> Dict[str, DesignComponent]:
    """
        Parse a design document to extract component definitions.
        
        Args:
            file_path: Path to the design file
            
        Returns:
            Dictionary of design components
        """
    components = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception:
        return components
    current_component = None
    in_code_block = False
    code_block_content = []
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if line_stripped.startswith('```'):
            if in_code_block:
                if code_block_content:
                    parsed_components = self._parse_code_block(code_block_content, file_path, line_num)
                    if current_component and current_component.name in parsed_components:
                        code_component = parsed_components[current_component.name]
                        current_component.methods = code_component.methods
                        current_component.attributes = code_component.attributes
                        current_component.metadata.update(code_component.metadata)
                    else:
                        components.update(parsed_components)
                code_block_content = []
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_block_content.append(line)
            continue
        component_match = self._match_component_header(line_stripped)
        if component_match:
            if current_component:
                components[current_component.name] = current_component
            component_name, component_type = component_match
            current_component = DesignComponent(name=component_name, component_type=component_type, description='', methods=[], attributes=[], file_path=str(file_path), line_number=line_num, metadata={})
        elif current_component and line_stripped:
            if line_stripped.startswith('**Purpose**:') or line_stripped.startswith('Purpose:'):
                current_component.description = line_stripped
    if current_component:
        components[current_component.name] = current_component
    return components

def _parse_code_block(self, code_lines: List[str], file_path: Path, line_num: int) -> Dict[str, DesignComponent]:
    """
        Parse code blocks in design documents to extract component definitions.
        
        Args:
            code_lines: Lines of code from the code block
            file_path: Path to the design file
            line_num: Line number where the code block ends
            
        Returns:
            Dictionary of design components found in the code block
        """
    components = {}
    code_content = '\n'.join(code_lines)
    class_matches = re.finditer('class\\s+(\\w+)(?:\\([^)]*\\))?:', code_content, re.MULTILINE)
    for match in class_matches:
        class_name = match.group(1)
        methods = []
        class_start = match.end()
        lines_after_class = code_content[class_start:].split('\n')
        class_content_lines = []
        for line in lines_after_class:
            if line.strip() == '':
                class_content_lines.append(line)
                continue
            elif line.startswith('    ') or line.startswith('\t'):
                class_content_lines.append(line)
            else:
                break
        class_content = '\n'.join(class_content_lines)
        method_matches = re.findall('\\n\\s+def\\s+(\\w+)', class_content)
        methods.extend(method_matches)
        components[class_name] = DesignComponent(name=class_name, component_type=ComponentType.CLASS, description=f'Class defined in design document', methods=methods, attributes=[], file_path=str(file_path), line_number=line_num, metadata={'from_code_block': True})
    lines = code_content.split('\n')
    in_class = False
    class_indent_level = 0
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if line.strip():
            indent_level = len(line) - len(line.lstrip())
        else:
            continue
        if stripped_line.startswith('class '):
            in_class = True
            class_indent_level = indent_level
            continue
        elif in_class and indent_level <= class_indent_level and stripped_line:
            in_class = False
        if stripped_line.startswith('def ') and (not in_class):
            func_match = re.search('def\\s+(\\w+)', stripped_line)
            if func_match:
                function_name = func_match.group(1)
                if not any((function_name in comp.methods for comp in components.values())):
                    components[function_name] = DesignComponent(name=function_name, component_type=ComponentType.FUNCTION, description=f'Function defined in design document', methods=[], attributes=[], file_path=str(file_path), line_number=line_num, metadata={'from_code_block': True})
    return components

def _parse_implementation_file(self, file_path: Path) -> Dict[str, ImplementationComponent]:
    """
        Parse a Python implementation file to extract components.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary of implementation components
        """
    components = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception:
        return components
    class_matches = re.finditer('^class\\s+(\\w+)(?:\\([^)]*\\))?:', content, re.MULTILINE)
    for match in class_matches:
        class_name = match.group(1)
        class_line = content[:match.start()].count('\n') + 1
        methods, attributes = self._extract_class_members(content, match.start())
        docstring = self._extract_docstring(content, match.end())
        components[class_name] = ImplementationComponent(name=class_name, component_type=ComponentType.CLASS, methods=methods, attributes=attributes, file_path=str(file_path), line_number=class_line, docstring=docstring, metadata={})
    function_matches = re.finditer('^def\\s+(\\w+)', content, re.MULTILINE)
    for match in function_matches:
        function_name = match.group(1)
        function_line = content[:match.start()].count('\n') + 1
        if self._is_method_in_class(content, match.start()):
            continue
        docstring = self._extract_docstring(content, match.end())
        components[function_name] = ImplementationComponent(name=function_name, component_type=ComponentType.FUNCTION, methods=[], attributes=[], file_path=str(file_path), line_number=function_line, docstring=docstring, metadata={})
    return components

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

