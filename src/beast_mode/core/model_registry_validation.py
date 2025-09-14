"""
Model Registry Validation

This module was extracted from model_registry.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from .pdca_models import ModelIntelligence, Requirement, Pattern, Tool, ValidationLevel, ReflectiveModule
from src.rm_ddd.core.health import ModuleHealth


def validate_systematic_compliance(self) -> ValidationLevel:
    """Validate systematic compliance of model registry"""
    if len(self.intelligence_cache) > 0 and self.cache_hits > 0:
        return ValidationLevel.HIGH
    if len(self.intelligence_cache) > 0 or self.query_count > 0:
        return ValidationLevel.MEDIUM
    return ValidationLevel.LOW
