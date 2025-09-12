"""
Handler Validation

This module was extracted from handler.py
as part of RM-DDD compliance refactoring.
"""

import re
from datetime import datetime
from typing import Callable, Optional
from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import ActionResult, CommandPattern, StructuredAction, ValidationResult

def validate_command(self, action: StructuredAction) -> ValidationResult:
    """Validate command syntax and permissions."""
    key = f'{action.verb}_{action.noun}'
    if key in self.command_patterns:
        pattern = self.command_patterns[key]
        return pattern.validate_action(action)
    else:
        return ValidationResult(is_valid=False, errors=[f'Unknown command pattern: {action.verb} {action.noun}'], suggestions=[f"Available patterns: {', '.join(self.command_patterns.keys())}"])
