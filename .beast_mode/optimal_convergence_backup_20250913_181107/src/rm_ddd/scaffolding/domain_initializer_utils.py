"""
Domain Initializer Utils

This module was extracted from domain_initializer.py
as part of RM-DDD compliance refactoring.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException
from ..core.health import ModuleHealth
from ..models import ModuleStatus
from ..models import ModuleCapability
from ..models import DomainBoundaries

def _format_ubiquitous_language(self, language_mapping: Dict[str, str]) -> str:
    """Format ubiquitous language mapping for code generation."""
    if not language_mapping:
        return '                # TODO: Define ubiquitous language terms'
    formatted_items = []
    for term, definition in language_mapping.items():
        formatted_items.append(f'                "{term}": "{definition}"')
    return ',\n'.join(formatted_items)
