"""
Mpm Dashboard Core Utils

This module was extracted from mpm_dashboard_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from .models import BacklogItem, MPMValidation, DependencySpec
from .enums import StrategicTrack, BeastReadinessStatus, ApprovalStatus, StakeholderType, RiskLevel
from .dependency_manager import BacklogDependencyManager
from src.rm_ddd.core.health import ModuleHealth


def _calculate_resource_utilization(self, scenario_params: Dict[str, Any], constraints: ResourceConstraints) -> Dict[str, float]:
    """Calculate resource utilization for scenario"""
    return {'developers': min(1.0, scenario_params['efficiency']), 'time': scenario_params['efficiency'], 'budget': 0.8 if constraints.budget_constraints else 1.0}
