"""
Remediation Guide Core Core Processing

This module was extracted from remediation_guide_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from ..models import ComplianceAnalysisResult, ComplianceIssue, ComplianceIssueType, IssueSeverity, RemediationStep
from src.rm_ddd.core.health import ModuleHealth


class ConvertefforttodurationClass:
    """Auto-generated class for functions."""

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

