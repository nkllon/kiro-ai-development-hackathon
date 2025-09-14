"""
Report Generator Core Validation

This module was extracted from report_generator_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json
from ..interfaces import ComplianceReporter
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType, RemediationStep, Phase2ValidationResult
from src.rm_ddd.core.health import ModuleHealth


class AnalyzetestcoveragefindingsClass:
    """Auto-generated class for functions."""

    def _analyze_test_coverage_findings(self, test_status) -> Dict[str, Any]:
    """Analyze test coverage findings."""
    return {'current_coverage': test_status.current_coverage, 'baseline_coverage': test_status.baseline_coverage, 'coverage_adequate': test_status.coverage_adequate, 'failing_tests_count': len(test_status.failing_tests), 'missing_tests_count': len(test_status.missing_tests), 'failing_tests': test_status.failing_tests[:10], 'issues_count': len(test_status.issues)}

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

