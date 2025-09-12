"""
Report Generator Core Core Validation

This module was extracted from report_generator_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import json
from ..interfaces import ComplianceReporter
from ..models import ComplianceAnalysisResult, ComplianceIssue, IssueSeverity, ComplianceIssueType, RemediationStep, Phase2ValidationResult

def _analyze_test_coverage_findings(self, test_status) -> Dict[str, Any]:
    """Analyze test coverage findings."""
    return {'current_coverage': test_status.current_coverage, 'baseline_coverage': test_status.baseline_coverage, 'coverage_adequate': test_status.coverage_adequate, 'failing_tests_count': len(test_status.failing_tests), 'missing_tests_count': len(test_status.missing_tests), 'failing_tests': test_status.failing_tests[:10], 'issues_count': len(test_status.issues)}
