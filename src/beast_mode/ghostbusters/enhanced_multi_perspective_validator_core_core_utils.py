"""
Enhanced Multi Perspective Validator Core Core Utils

This module was extracted from enhanced_multi_perspective_validator_core_core.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ..core.reflective_module import ReflectiveModule, HealthStatus
from src.rm_ddd.core.health import ModuleHealth


def _assess_resource_utilization(self, decision_context: DecisionContext) -> float:
    return 0.6
