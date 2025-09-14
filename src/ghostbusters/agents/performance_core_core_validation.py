"""
Performance Core Core Validation

This module was extracted from performance_core_core.py
as part of RM-DDD compliance refactoring.
"""

import ast
import re
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from ..core.interfaces import GhostbustersExpertAgent
from ..core.models import AnalysisResult, AnalysisContext, Finding, Recommendation, FindingType, Severity, CodeLocation
from src.rm_ddd.core.health import ModuleHealth


def validate_confidence(self, result: AnalysisResult) -> bool:
    """Validate confidence score accuracy"""
    if not 0.0 <= result.confidence <= 1.0:
        return False
    if result.confidence > 0.8:
        return 'performance_issues_detected' in result.metadata
    return True

def _check_performance_patterns(self, content: str, file_path: Path) -> List[Finding]:
    """Check for performance anti-patterns using regex"""
    findings = []
    lines = content.splitlines()
    all_patterns = {**self.inefficient_patterns, **self.db_patterns, **self.memory_patterns, **self.io_patterns, **self.concurrency_patterns}
    for issue_type, patterns in all_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                severity = self._get_issue_severity(issue_type)
                confidence = self._get_issue_confidence(issue_type)
                findings.append(Finding(type=FindingType.PERFORMANCE_ISSUE, severity=severity, location=CodeLocation(str(file_path), line_num), description=self._get_issue_description(issue_type), confidence=confidence, evidence={'issue': issue_type, 'pattern': pattern}))
    return findings
