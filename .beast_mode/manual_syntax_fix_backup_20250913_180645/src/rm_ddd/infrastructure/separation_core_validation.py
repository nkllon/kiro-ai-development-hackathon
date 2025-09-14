"""
Separation Core Validation

This module was extracted from separation_core.py
as part of RM-DDD compliance refactoring.
"""

import ast
import inspect
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union
from datetime import datetime
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..models import DomainBoundaries
from ..domain.entities import Entity, AggregateRoot
from ..domain.services import DomainService
from ..domain.value_objects import ValueObject
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries

def validate_class_dependencies(self, cls: Type) -> ValidationResult:
    """
        Validate dependencies for a specific class.
        
        Args:
            cls: Class to validate
            
        Returns:
            ValidationResult: Validation results with any violations found
        """
    result = ValidationResult(is_valid=True)
    try:
        class_layer = self._determine_class_layer(cls)
        if class_layer is None:
            result.add_warning(f'Could not determine layer for class {cls.__name__}')
            return result
        dependencies = self._extract_class_dependencies(cls)
        for dep_class, dep_info in dependencies.items():
            dep_layer = self._determine_class_layer_by_name(dep_class)
            if dep_layer is None:
                continue
            if not self._is_dependency_allowed(class_layer, dep_layer):
                violation = LayerViolation(violating_class=cls.__name__, violating_method=dep_info.get('method'), dependency_class=dep_class, violation_type='invalid_layer_dependency', layer_from=class_layer, layer_to=dep_layer, message=f'{class_layer.value} layer class {cls.__name__} cannot depend on {dep_layer.value} layer class {dep_class}', file_path=dep_info.get('file_path'), line_number=dep_info.get('line_number'))
                self._violations.append(violation)
                result.add_error(violation.message)
    except Exception as e:
        logger.error(f'Error validating dependencies for {cls.__name__}: {e}')
        result.add_error(f'Validation error: {str(e)}')
    return result

def validate_module_dependencies(self, module_path: Union[str, Path]) -> ValidationResult:
    """
        Validate dependencies for an entire module.
        
        Args:
            module_path: Path to the module to validate
            
        Returns:
            ValidationResult: Validation results for the module
        """
    result = ValidationResult(is_valid=True)
    module_path = Path(module_path)
    if not module_path.exists():
        result.add_error(f'Module path does not exist: {module_path}')
        return result
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        tree = ast.parse(source_code, filename=str(module_path))
        module_analysis = self._analyze_module_ast(tree, str(module_path))
        for violation in module_analysis['violations']:
            self._violations.append(violation)
            result.add_error(violation.message)
        self._scanned_modules.add(str(module_path))
    except Exception as e:
        logger.error(f'Error validating module {module_path}: {e}')
        result.add_error(f'Module validation error: {str(e)}')
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    domain_violations = [v for v in self._violations if v.layer_from == LayerType.DOMAIN]
    if domain_violations:
        result.add_error(f'Found {len(domain_violations)} domain layer violations')
    return result

def validate_project(self, project_path: Union[str, Path]) -> ValidationResult:
    """
        Validate layer separation for an entire project.
        
        Args:
            project_path: Path to the project root
            
        Returns:
            ValidationResult: Comprehensive validation results
        """
    result = ValidationResult(is_valid=True)
    project_path = Path(project_path)
    python_files = list(project_path.rglob('*.py'))
    for py_file in python_files:
        if py_file.name.startswith('__'):
            continue
        module_result = self.validator.validate_module_dependencies(py_file)
        result.merge(module_result)
    return result
