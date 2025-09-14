"""
Error Handler Models

This module was extracted from error_handler.py
as part of RM-DDD compliance refactoring.
"""

import time
import traceback
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import contextmanager
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import RCAEngine, Failure, RCAResult
from typing import TYPE_CHECKING
from .rca_integration import TestFailureData, TestRCAReportData, TestRCASummaryData
from .rca_integration import TestRCAReportData, TestRCASummaryData
from .rca_integration import TestRCASummaryData
from .rca_integration import TestRCAReportData

@dataclass
class FallbackReportData:
    """Fallback report when RCA analysis fails"""
    error_summary: str
    basic_failure_info: List[Dict[str, Any]]
    suggested_actions: List[str]
    health_status: Dict[str, Any]
    timestamp: datetime
    degradation_level: DegradationLevel
