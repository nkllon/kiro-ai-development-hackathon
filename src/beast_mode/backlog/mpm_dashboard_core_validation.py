"""
Mpm Dashboard Core Validation

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

def _invalidate_cache(self) -> None:
    """Invalidate cached portfolio status"""
    self._cached_portfolio_status = None
    self._cache_timestamp = None
