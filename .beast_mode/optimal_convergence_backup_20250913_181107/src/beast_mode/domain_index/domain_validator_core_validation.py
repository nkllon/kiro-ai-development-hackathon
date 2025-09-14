"""
Domain Validator Core Validation

This module was extracted from domain_validator_core.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from .base import DomainSystemComponent
from .models import Domain, DomainCollection, ValidationResult, HealthIssue, IssueSeverity, IssueCategory, DependencyGraph
from .exceptions import DomainValidationError
import glob
import jsonschema
import glob
import glob

def validate(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    """Execute validation rule"""
    try:
        return self.validator_func(domain, context) or []
    except Exception as e:
        return [HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Validation rule '{self.name}' failed: {str(e)}", suggested_fix='Check validation rule implementation')]

def check(self, domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    """Execute consistency check"""
    try:
        return self.checker_func(domains, context) or []
    except Exception as e:
        return [HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Consistency check '{self.name}' failed: {str(e)}", suggested_fix='Check consistency check implementation')]

def validate_domain(self, domain: Domain, context: Optional[Dict[str, Any]]=None) -> ValidationResult:
    """Validate a single domain against all rules"""
    with self._time_operation('validate_domain'):
        self.validations_performed += 1
        context = context or {}
        context['validator'] = self
        all_issues = []
        for rule in self._validation_rules:
            try:
                issues = rule.validate(domain, context)
                all_issues.extend(issues)
            except Exception as e:
                self.logger.error(f"Validation rule '{rule.name}' failed: {e}")
                all_issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f'Validation rule error: {str(e)}', suggested_fix='Check validation rule implementation'))
        errors = [issue for issue in all_issues if issue.severity == IssueSeverity.CRITICAL]
        warnings = [issue for issue in all_issues if issue.severity == IssueSeverity.WARNING]
        suggestions = [issue.suggested_fix for issue in all_issues if issue.severity == IssueSeverity.INFO]
        self.issues_found += len(all_issues)
        return ValidationResult(is_valid=len(errors) == 0, errors=[issue.description for issue in errors], warnings=[issue.description for issue in warnings], suggestions=suggestions)

def validate_domain_collection(self, domains: DomainCollection) -> Dict[str, ValidationResult]:
    """Validate all domains in a collection"""
    with self._time_operation('validate_domain_collection'):
        results = {}
        for domain_name, domain in domains.items():
            context = {'all_domains': domains}
            results[domain_name] = self.validate_domain(domain, context)
        return results

def check_consistency(self, domains: DomainCollection) -> List[HealthIssue]:
    """Check cross-domain consistency"""
    with self._time_operation('check_consistency'):
        self.consistency_checks_performed += 1
        context = {'validator': self}
        all_issues = []
        for check in self._consistency_checks:
            try:
                issues = check.check(domains, context)
                all_issues.extend(issues)
            except Exception as e:
                self.logger.error(f"Consistency check '{check.name}' failed: {e}")
                all_issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f'Consistency check error: {str(e)}', suggested_fix='Check consistency check implementation'))
        self.issues_found += len(all_issues)
        return all_issues

def validate_dependencies(self, domains: DomainCollection) -> List[HealthIssue]:
    """Validate all domain dependencies"""
    with self._time_operation('validate_dependencies'):
        issues = []
        for domain_name, domain in domains.items():
            for dep in domain.dependencies:
                if dep not in domains:
                    issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.DEPENDENCY, description=f"Domain '{domain_name}' depends on non-existent domain '{dep}'", suggested_fix=f"Either create domain '{dep}' or remove dependency", affected_files=[domain_name]))
        circular_deps = self.detect_circular_dependencies(domains)
        for cycle in circular_deps:
            cycle_str = ' -> '.join(cycle)
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f'Circular dependency detected: {cycle_str}', suggested_fix='Refactor to remove circular dependency', affected_files=cycle[:-1]))
        return issues

def validate_file_patterns(self, domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    """Validate domain file patterns"""
    issues = []
    if not domain.patterns:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.PATTERN, description=f"Domain '{domain.name}' has no file patterns", suggested_fix='Add at least one file pattern to define domain scope'))
        return issues
    for pattern in domain.patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.PATTERN, description=f"Invalid pattern in domain '{domain.name}': {pattern}", suggested_fix='Ensure all patterns are non-empty strings'))
            continue
        if pattern.startswith('/'):
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' starts with '/' (absolute path)", suggested_fix='Use relative paths for better portability'))
        if '\\' in pattern:
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' uses backslashes", suggested_fix='Use forward slashes for cross-platform compatibility'))
        if self.check_filesystem:
            if not self._pattern_has_matches(pattern):
                issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' matches no files", suggested_fix='Verify pattern is correct or files exist'))
    return issues

def add_consistency_check(self, check: ConsistencyCheck) -> None:
    """Add custom consistency check"""
    self._consistency_checks.append(check)
    self.logger.info(f'Added consistency check: {check.name}')

def _initialize_builtin_consistency_checks(self) -> None:
    """Initialize built-in consistency checks"""

    def check_dependency_consistency(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        return self.validate_dependencies(domains)
    self._consistency_checks.append(ConsistencyCheck(name='dependency_consistency', description='Check domain dependency consistency', severity=IssueSeverity.CRITICAL, checker_func=check_dependency_consistency))

    def check_pattern_overlaps(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        issues = []
        domain_patterns = {}
        for domain_name, domain in domains.items():
            domain_patterns[domain_name] = domain.patterns
        for domain1, patterns1 in domain_patterns.items():
            for domain2, patterns2 in domain_patterns.items():
                if domain1 >= domain2:
                    continue
                for pattern1 in patterns1:
                    for pattern2 in patterns2:
                        if self._patterns_overlap(pattern1, pattern2):
                            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern overlap between '{domain1}' and '{domain2}': '{pattern1}' vs '{pattern2}'", suggested_fix='Review domain boundaries to avoid pattern conflicts', affected_files=[domain1, domain2]))
        return issues
    self._consistency_checks.append(ConsistencyCheck(name='pattern_overlaps', description='Check for overlapping file patterns between domains', severity=IssueSeverity.WARNING, checker_func=check_pattern_overlaps))

    def check_orphaned_dependencies(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
        issues = []
        all_dependencies = set()
        domain_names = set(domains.keys())
        for domain in domains.values():
            all_dependencies.update(domain.dependencies)
        orphaned = all_dependencies - domain_names
        for orphan in orphaned:
            issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f"Dependency '{orphan}' is referenced but no domain exists", suggested_fix=f"Create domain '{orphan}' or remove references to it"))
        return issues
    self._consistency_checks.append(ConsistencyCheck(name='orphaned_dependencies', description="Check for dependencies that don't correspond to existing domains", severity=IssueSeverity.WARNING, checker_func=check_orphaned_dependencies))

def validate_required_fields(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    for field in self.required_fields:
        if not hasattr(domain, field) or not getattr(domain, field):
            issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' missing required field: {field}", suggested_fix=f'Add {field} to domain definition'))
    return issues

def validate_domain_name(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    if not domain.name:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description='Domain name is empty', suggested_fix='Provide a valid domain name'))
        return issues
    if not re.match('^[a-z][a-z0-9_]*$', domain.name):
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain name '{domain.name}' doesn't follow naming convention", suggested_fix='Use lowercase letters, numbers, and underscores only'))
    reserved_names = {'test', 'temp', 'tmp', 'debug', 'admin'}
    if domain.name.lower() in reserved_names:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain name '{domain.name}' is reserved", suggested_fix='Choose a more descriptive domain name'))
    return issues

def validate_tools(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    if not domain.tools:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no tools configuration", suggested_fix='Add tools configuration for linting, formatting, etc.'))
        return issues
    if not domain.tools.linter:
        issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no linter configured", suggested_fix='Configure a linter for code quality'))
    if not domain.tools.formatter:
        issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no formatter configured", suggested_fix='Configure a formatter for consistent code style'))
    return issues

def validate_required_fields(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    for field in self.required_fields:
        if not hasattr(domain, field) or not getattr(domain, field):
            issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' missing required field: {field}", suggested_fix=f'Add {field} to domain definition'))
    return issues

def validate_domain_name(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    if not domain.name:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.VALIDATION, description='Domain name is empty', suggested_fix='Provide a valid domain name'))
        return issues
    if not re.match('^[a-z][a-z0-9_]*$', domain.name):
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain name '{domain.name}' doesn't follow naming convention", suggested_fix='Use lowercase letters, numbers, and underscores only'))
    reserved_names = {'test', 'temp', 'tmp', 'debug', 'admin'}
    if domain.name.lower() in reserved_names:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain name '{domain.name}' is reserved", suggested_fix='Choose a more descriptive domain name'))
    return issues

def validate_tools(domain: Domain, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    if not domain.tools:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no tools configuration", suggested_fix='Add tools configuration for linting, formatting, etc.'))
        return issues
    if not domain.tools.linter:
        issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no linter configured", suggested_fix='Configure a linter for code quality'))
    if not domain.tools.formatter:
        issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Domain '{domain.name}' has no formatter configured", suggested_fix='Configure a formatter for consistent code style'))
    return issues

def check_dependency_consistency(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    return self.validate_dependencies(domains)

def check_pattern_overlaps(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    domain_patterns = {}
    for domain_name, domain in domains.items():
        domain_patterns[domain_name] = domain.patterns
    for domain1, patterns1 in domain_patterns.items():
        for domain2, patterns2 in domain_patterns.items():
            if domain1 >= domain2:
                continue
            for pattern1 in patterns1:
                for pattern2 in patterns2:
                    if self._patterns_overlap(pattern1, pattern2):
                        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern overlap between '{domain1}' and '{domain2}': '{pattern1}' vs '{pattern2}'", suggested_fix='Review domain boundaries to avoid pattern conflicts', affected_files=[domain1, domain2]))
    return issues

def check_orphaned_dependencies(domains: DomainCollection, context: Dict[str, Any]) -> List[HealthIssue]:
    issues = []
    all_dependencies = set()
    domain_names = set(domains.keys())
    for domain in domains.values():
        all_dependencies.update(domain.dependencies)
    orphaned = all_dependencies - domain_names
    for orphan in orphaned:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f"Dependency '{orphan}' is referenced but no domain exists", suggested_fix=f"Create domain '{orphan}' or remove references to it"))
    return issues
