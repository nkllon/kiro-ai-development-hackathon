"""
Generators Core Core Validation

This module was extracted from generators_core_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
import re
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
import re
import re
from ..models import DomainBoundaries
import re
import re
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
import re
import re
import re
from ..models import DomainBoundaries
import re
import re
from ..models import DomainBoundaries
import re
import re
import re
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
import re
import re
import re

def validate_spec(self) -> ValidationResult:
    """Validate the generation specification."""
    result = ValidationResult(is_valid=True)
    if not self.name:
        result.add_error('Generation spec must have a name')
    if not self.domain_context:
        result.add_error('Generation spec must have a domain context')
    for attr in self.attributes:
        if 'name' not in attr:
            result.add_error('Attribute must have a name')
        if 'type' not in attr:
            result.add_error(f"Attribute {attr.get('name', 'unknown')} must have a type")
    return result

def validate_domain_invariants(self):
    """Validate domain invariants."""
    result = ValidationResult(is_valid=True)
    if not JINJA2_AVAILABLE:
        result.add_warning('Jinja2 not available - code generation capabilities limited')
    if not self._templates:
        result.add_error('No code templates available')
    return result

def validate_template(self, template_name: str) -> ValidationResult:
    """
        Validate a template for syntax and completeness.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            ValidationResult: Validation results
        """
    result = ValidationResult(is_valid=True)
    template = self._template_registry.get_template(template_name)
    if not template:
        result.add_error(f'Template {template_name} not found')
        return result
    try:
        test_context = {'name': 'TestEntity', 'domain_context': 'test', 'attributes': [], 'methods': [], 'constraints': [], 'generated_at': datetime.now().isoformat()}
        template.render(**test_context)
        logger.debug(f'Template {template_name} validation successful')
    except Exception as e:
        result.add_error(f'Template validation failed: {str(e)}')
    return result
