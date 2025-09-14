"""
Phase3 Readiness Assessor Processing

This module was extracted from phase3_readiness_assessor.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType
from src.rm_ddd.core.health import ModuleHealth


class ConvertstatustoscoreClass:
    """Auto-generated class for functions."""

    def _convert_status_to_score(self, status: ReadinessStatus) -> float:
    """Convert readiness status to numeric score."""
    status_scores = {ReadinessStatus.READY: 100.0, ReadinessStatus.CONDITIONALLY_READY: 75.0, ReadinessStatus.NOT_READY: 25.0, ReadinessStatus.BLOCKED: 0.0}
    return status_scores.get(status, 0.0)

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

