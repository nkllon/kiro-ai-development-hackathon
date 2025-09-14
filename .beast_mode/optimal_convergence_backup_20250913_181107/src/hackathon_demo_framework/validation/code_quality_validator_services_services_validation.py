"""
Code Quality Validator Services Services Validation

This module was extracted from code_quality_validator_services_services.py
as part of RM-DDD compliance refactoring.
"""

import logging
import ast
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from ..models import ValidationResult, TechnicalAssessment

def validate_code_quality(self, min_score: float=80.0) -> ValidationResult:
    """
        Validate code quality against minimum standards.
        
        Args:
            min_score: Minimum acceptable quality score
            
        Returns:
            Validation result with quality assessment
        """
    report = self.assess_code_quality()
    issues = []
    recommendations = []
    if report.overall_score < min_score:
        issues.append(f'Code quality score too low: {report.overall_score:.1f} < {min_score}')
    if report.critical_issues > 0:
        issues.append(f'Critical code quality issues found: {report.critical_issues}')
        recommendations.append('Fix all critical code quality issues immediately')
    if report.major_issues > 5:
        issues.append(f'Too many major code quality issues: {report.major_issues}')
        recommendations.append('Reduce major code quality issues to improve maintainability')
    recommendations.extend(report.recommendations[:3])
    return ValidationResult(is_valid=len(issues) == 0, score=report.overall_score, issues=issues, recommendations=recommendations)
