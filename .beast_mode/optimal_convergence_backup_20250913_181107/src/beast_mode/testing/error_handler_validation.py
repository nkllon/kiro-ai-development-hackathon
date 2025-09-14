"""
Error Handler Validation

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

def _check_component_health(self, component: str) -> None:
    """Check health of specific component"""
    if component in self.component_health:
        metrics = self.component_health[component]
        if not metrics.is_healthy:
            self.logger.warning(f'Component {component} is unhealthy')
