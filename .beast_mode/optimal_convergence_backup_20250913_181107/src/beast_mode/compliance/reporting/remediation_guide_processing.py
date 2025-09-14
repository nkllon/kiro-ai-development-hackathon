"""
Remediation Guide Processing

This module was extracted from remediation_guide.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from ..models import ComplianceAnalysisResult, ComplianceIssue, ComplianceIssueType, IssueSeverity, RemediationStep

def _convert_effort_to_duration(self, effort_points: int) -> str:
    """Convert effort points to estimated duration."""
    if effort_points <= 8:
        return '1-2 days'
    elif effort_points <= 16:
        return '3-5 days'
    elif effort_points <= 32:
        return '1-2 weeks'
    elif effort_points <= 64:
        return '2-4 weeks'
    else:
        return '1-2 months'
