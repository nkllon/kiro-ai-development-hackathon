"""
Handler Utils

This module was extracted from handler.py
as part of RM-DDD compliance refactoring.
"""

import re
from datetime import datetime
from typing import Callable, Optional
from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import ActionResult, CommandPattern, StructuredAction, ValidationResult
from src.rm_ddd.core.health import ModuleHealth


def format_response(self, result: ActionResult) -> str:
    """Format result as human-readable text."""
    return result.to_response_string()
