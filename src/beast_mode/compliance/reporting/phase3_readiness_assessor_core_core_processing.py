"""
Phase3 Readiness Assessor Core Core Processing

This module was extracted from phase3_readiness_assessor_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType
from src.rm_ddd.core.health import ModuleHealth


def _convert_status_to_score(self, status: ReadinessStatus) -> float:
    """Convert readiness status to numeric score."""
    status_scores = {ReadinessStatus.READY: 100.0, ReadinessStatus.CONDITIONALLY_READY: 75.0, ReadinessStatus.NOT_READY: 25.0, ReadinessStatus.BLOCKED: 0.0}
    return status_scores.get(status, 0.0)
