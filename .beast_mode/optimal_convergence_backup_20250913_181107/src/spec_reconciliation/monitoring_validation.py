"""
Monitoring Validation

This module was extracted from monitoring.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from threading import Thread, Event
import schedule
from src.beast_mode.core.reflective_module import ReflectiveModule
from .validation import ConsistencyValidator, ConsistencyMetrics, TerminologyReport
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def validate_architectural_decisions(self, decision: ArchitecturalDecision) -> ValidationResult:
    """
        Validate architectural decisions against existing patterns and constraints
        
        Ensures new architectural decisions align with established patterns
        and don't violate existing constraints or create inconsistencies.
        """
    try:
        violations = []
        compliance_issues = []
        recommendations = []
        pattern_violations = self._validate_against_patterns(decision)
        violations.extend(pattern_violations)
        constraint_violations = self._check_constraint_violations(decision)
        violations.extend(constraint_violations)
        component_impact = self._analyze_component_impact(decision)
        if component_impact['has_conflicts']:
            compliance_issues.extend(component_impact['conflicts'])
        consistency_check = self._check_decision_consistency(decision)
        if not consistency_check['consistent']:
            compliance_issues.extend(consistency_check['issues'])
        total_checks = 10
        failed_checks = len(violations) + len(compliance_issues)
        validation_score = max(0.0, (total_checks - failed_checks) / total_checks)
        requires_review = validation_score < 0.7 or len(violations) > 0 or len(compliance_issues) > 2
        if violations:
            recommendations.append('Address architectural pattern violations')
        if compliance_issues:
            recommendations.append('Resolve compliance issues before implementation')
        if validation_score < 0.8:
            recommendations.append('Consider alternative approaches with higher compliance')
        validation_result = ValidationResult(decision_id=decision.decision_id, is_valid=len(violations) == 0 and validation_score >= 0.7, validation_score=validation_score, violations=violations, compliance_issues=compliance_issues, recommendations=recommendations, requires_review=requires_review)
        self.logger.info(f'Architectural decision {decision.decision_id} validated. Score: {validation_score:.3f}, Valid: {validation_result.is_valid}')
        return validation_result
    except Exception as e:
        self.logger.error(f'Error validating architectural decision: {e}')
        return ValidationResult(decision_id=decision.decision_id, is_valid=False, validation_score=0.0, violations=[f'Validation system error: {e}'], compliance_issues=[], recommendations=['Fix validation system before proceeding'], requires_review=True)

def _scheduled_drift_check(self):
    """Scheduled drift monitoring check"""
    try:
        self.monitor_spec_drift()
    except Exception as e:
        self.logger.error(f'Scheduled drift check failed: {e}')

def _scheduled_terminology_check(self):
    """Scheduled terminology consistency check"""
    try:
        self.detect_terminology_inconsistencies()
    except Exception as e:
        self.logger.error(f'Scheduled terminology check failed: {e}')

def _validate_against_patterns(self, decision: ArchitecturalDecision) -> List[str]:
    """Validate decision against established architectural patterns"""
    violations = []
    if any(('module' in comp.lower() for comp in decision.affected_components)):
        if 'ReflectiveModule' not in decision.description:
            violations.append('Components should follow ReflectiveModule pattern')
    if 'process' in decision.description.lower():
        pdca_keywords = ['plan', 'do', 'check', 'act']
        if not any((keyword in decision.description.lower() for keyword in pdca_keywords)):
            violations.append('Process decisions should follow PDCA pattern')
    return violations

def _check_constraint_violations(self, decision: ArchitecturalDecision) -> List[str]:
    """Check for constraint violations in architectural decision"""
    violations = []
    for constraint in decision.constraints:
        if 'performance' in constraint.lower() and 'benchmark' not in decision.description.lower():
            violations.append('Performance constraints require benchmarking approach')
        if 'security' in constraint.lower() and 'audit' not in decision.description.lower():
            violations.append('Security constraints require audit procedures')
    return violations

def _check_decision_consistency(self, decision: ArchitecturalDecision) -> Dict[str, Any]:
    """Check consistency with existing architectural decisions"""
    issues = []
    if not decision.rationale:
        issues.append('Decision lacks rationale')
    if not decision.alternatives_considered:
        issues.append('No alternatives considered')
    if len(decision.description) < 50:
        issues.append('Decision description too brief')
    return {'consistent': len(issues) == 0, 'issues': issues}

def _validate_against_patterns(self, decision: ArchitecturalDecision) -> List[str]:
    """Validate architectural decision against existing patterns"""
    violations = []
    if 'singleton' in decision.description.lower() and 'global state' in decision.description.lower():
        violations.append('Singleton pattern with global state may violate testability patterns')
    if 'direct database' in decision.description.lower() and 'repository' not in decision.description.lower():
        violations.append('Direct database access without repository pattern violates data access patterns')
    return violations

def _check_constraint_violations(self, decision: ArchitecturalDecision) -> List[str]:
    """Check for constraint violations in architectural decision"""
    violations = []
    for component in decision.affected_components:
        if component in ['database', 'storage'] and 'direct access' in decision.description.lower():
            violations.append(f'Direct access to {component} violates encapsulation constraints')
    return violations

def _check_decision_consistency(self, decision: ArchitecturalDecision) -> Dict[str, Any]:
    """Check consistency with existing architectural decisions"""
    issues = []
    if 'microservice' in decision.description.lower() and 'monolith' in decision.description.lower():
        issues.append('Decision mentions both microservice and monolith approaches')
    return {'consistent': len(issues) == 0, 'issues': issues}
