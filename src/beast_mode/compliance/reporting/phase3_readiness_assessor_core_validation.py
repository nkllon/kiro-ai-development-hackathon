"""
Phase3 Readiness Assessor Core Validation

This module was extracted from phase3_readiness_assessor_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType
from src.rm_ddd.core.health import ModuleHealth


class EvaluatetestcoveragemetricClass:
    """Auto-generated class for functions."""

    def _evaluate_test_coverage_metric(self, test_status) -> ReadinessMetric:
    """Evaluate test coverage readiness metric."""
    current_coverage = test_status.current_coverage
    required_coverage = self.readiness_thresholds[ReadinessCriteria.TEST_COVERAGE]
    if current_coverage >= required_coverage:
    status = ReadinessStatus.READY
    elif current_coverage >= required_coverage * 0.95:
    status = ReadinessStatus.CONDITIONALLY_READY
    else:
    status = ReadinessStatus.NOT_READY
    blocking_issues = []
    recommendations = []
    if len(test_status.failing_tests) > 0:
    blocking_issues.append(f'{len(test_status.failing_tests)} failing tests')
    recommendations.append('Fix all failing tests before Phase 3')
    if not test_status.coverage_adequate:
    blocking_issues.append('Test coverage below baseline')
    recommendations.append(f'Increase test coverage to {required_coverage}%')
    if len(test_status.missing_tests) > 0:
    recommendations.append('Add missing test cases for complete coverage')
    return ReadinessMetric(criteria=ReadinessCriteria.TEST_COVERAGE, current_value=current_coverage, required_value=required_coverage, weight=self.criteria_weights[ReadinessCriteria.TEST_COVERAGE], status=status, description=f'Test coverage: {current_coverage:.1f}% (required: {required_coverage:.1f}%)', blocking_issues=blocking_issues, recommendations=recommendations)

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

