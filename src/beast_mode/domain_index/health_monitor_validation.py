"""
Health Monitor Validation

This module was extracted from health_monitor.py
as part of RM-DDD compliance refactoring.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import DomainSystemComponent
from .interfaces import HealthMonitorInterface
from .models import Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory, HealthStatusCollection
from .exceptions import HealthMonitorError, HealthCheckFailedError
from .config import get_config
from .health_reporter import HealthReportGenerator
from ..utils.path_normalizer import safe_relative_to

def check_domain_health(self, domain_name: str) -> HealthStatus:
    """Check health of a specific domain"""
    with self._time_operation('check_domain_health'):
        self.total_checks += 1
        try:
            if not self.registry_manager:
                raise HealthMonitorError('Registry manager not set')
            domain = self.registry_manager.get_domain(domain_name)
            return self._perform_health_check(domain)
        except Exception as e:
            self.failed_checks += 1
            self._handle_error(e, 'check_domain_health')
            raise HealthCheckFailedError(domain_name, 'full_check', str(e))

def check_all_domains(self) -> HealthStatusCollection:
    """Check health of all domains"""
    with self._time_operation('check_all_domains'):
        try:
            if not self.registry_manager:
                raise HealthMonitorError('Registry manager not set')
            all_domains = self.registry_manager.get_all_domains()
            health_statuses = {}
            if self.parallel_checks and len(all_domains) > 1:
                health_statuses = self._parallel_health_checks(all_domains)
            else:
                for domain_name, domain in all_domains.items():
                    try:
                        health_statuses[domain_name] = self._perform_health_check(domain)
                    except Exception as e:
                        self.failed_checks += 1
                        self.logger.error(f'Health check failed for {domain_name}: {e}')
                        health_statuses[domain_name] = self._create_failed_health_status(str(e))
            self._health_cache.update(health_statuses)
            self._last_full_check = datetime.now()
            self.logger.info(f'Completed health checks for {len(health_statuses)} domains')
            return health_statuses
        except Exception as e:
            self._handle_error(e, 'check_all_domains')
            return {}

def _parallel_health_checks(self, domains: Dict[str, Domain]) -> HealthStatusCollection:
    """Perform health checks in parallel"""
    health_statuses = {}
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        future_to_domain = {executor.submit(self._perform_health_check, domain): domain_name for domain_name, domain in domains.items()}
        for future in as_completed(future_to_domain, timeout=self.check_timeout * len(domains)):
            domain_name = future_to_domain[future]
            try:
                health_status = future.result()
                health_statuses[domain_name] = health_status
            except Exception as e:
                self.failed_checks += 1
                self.logger.error(f'Parallel health check failed for {domain_name}: {e}')
                health_statuses[domain_name] = self._create_failed_health_status(str(e))
    return health_statuses

def _perform_health_check(self, domain: Domain) -> HealthStatus:
    """Perform comprehensive health check for a domain"""
    start_time = time.time()
    issues = []
    pattern_issues = self._check_file_patterns(domain)
    issues.extend(pattern_issues)
    dependency_issues = self._check_dependencies(domain)
    issues.extend(dependency_issues)
    content_issues = self._check_content_indicators(domain)
    issues.extend(content_issues)
    tool_issues = self._check_domain_tools(domain)
    issues.extend(tool_issues)
    if len(issues) > self.max_issues_per_domain:
        issues = issues[:self.max_issues_per_domain]
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f'Too many issues detected (showing first {self.max_issues_per_domain})', suggested_fix='Review domain configuration and resolve critical issues first'))
    metrics = self._calculate_health_metrics(domain, issues)
    status_type = self._determine_health_status_type(issues, metrics)
    self.issues_detected += len(issues)
    check_duration = int((time.time() - start_time) * 1000)
    return HealthStatus(status=status_type, last_check=datetime.now(), issues=issues, metrics=metrics, check_duration_ms=check_duration, next_check=datetime.now() + timedelta(minutes=self.check_interval))

def _check_file_patterns(self, domain: Domain) -> List[HealthIssue]:
    """Check if domain file patterns match actual files"""
    issues = []
    try:
        for pattern in domain.patterns:
            pattern_path = self.project_root / pattern.replace('**', '*')
            matching_files = list(self.project_root.glob(pattern))
            if not matching_files:
                issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.PATTERN, description=f"Pattern '{pattern}' matches no files", suggested_fix=f'Verify pattern is correct or remove if no longer needed', affected_files=[pattern]))
            else:
                inaccessible_files = []
                for file_path in matching_files[:10]:
                    if not file_path.exists() or not os.access(file_path, os.R_OK):
                        inaccessible_files.append(str(file_path))
                if inaccessible_files:
                    issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.FILE, description=f"Files matching '{pattern}' are not accessible", suggested_fix='Check file permissions and existence', affected_files=inaccessible_files))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.PATTERN, description=f'Failed to validate patterns: {str(e)}', suggested_fix='Check pattern syntax and file system access'))
    return issues

def _check_dependencies(self, domain: Domain) -> List[HealthIssue]:
    """Check if domain dependencies exist and are accessible"""
    issues = []
    if not self.registry_manager:
        return issues
    try:
        all_domains = self.registry_manager.get_all_domains()
        for dependency in domain.dependencies:
            if dependency not in all_domains:
                issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.DEPENDENCY, description=f"Dependency '{dependency}' not found in registry", suggested_fix=f"Add '{dependency}' to registry or remove from dependencies"))
            else:
                dep_domain = all_domains[dependency]
                if hasattr(dep_domain, 'health_status') and dep_domain.health_status:
                    if dep_domain.health_status.status == HealthStatusType.FAILED:
                        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.DEPENDENCY, description=f"Dependency '{dependency}' has failed health status", suggested_fix=f"Resolve health issues in '{dependency}' domain"))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.CRITICAL, category=IssueCategory.DEPENDENCY, description=f'Failed to validate dependencies: {str(e)}', suggested_fix='Check registry accessibility and dependency configuration'))
    return issues

def _check_content_indicators(self, domain: Domain) -> List[HealthIssue]:
    """Check if content indicators are found in domain files"""
    issues = []
    try:
        domain_files = []
        for pattern in domain.patterns:
            matching_files = list(self.project_root.glob(pattern))
            domain_files.extend(matching_files)
        if not domain_files:
            return issues
        sample_files = domain_files[:5]
        indicators_found = set()
        for file_path in sample_files:
            if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        for indicator in domain.content_indicators:
                            if indicator.lower() in content:
                                indicators_found.add(indicator)
                except Exception:
                    continue
        missing_indicators = set(domain.content_indicators) - indicators_found
        if missing_indicators and len(domain.content_indicators) > 0:
            issues.append(HealthIssue(severity=IssueSeverity.INFO, category=IssueCategory.VALIDATION, description=f"Content indicators not found in sample files: {', '.join(missing_indicators)}", suggested_fix='Verify content indicators are correct or update them'))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f'Failed to validate content indicators: {str(e)}', suggested_fix='Check file accessibility and content indicator configuration'))
    return issues

def _check_domain_tools(self, domain: Domain) -> List[HealthIssue]:
    """Check if domain tools are available and configured correctly"""
    issues = []
    try:
        tools_to_check = [('linter', domain.tools.linter), ('formatter', domain.tools.formatter), ('validator', domain.tools.validator)]
        for tool_type, tool_name in tools_to_check:
            if tool_name:
                if not isinstance(tool_name, str) or not tool_name.strip():
                    issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f"Invalid {tool_type} configuration: '{tool_name}'", suggested_fix=f'Set a valid {tool_type} tool name'))
    except Exception as e:
        issues.append(HealthIssue(severity=IssueSeverity.WARNING, category=IssueCategory.VALIDATION, description=f'Failed to validate domain tools: {str(e)}', suggested_fix='Check domain tools configuration'))
    return issues

def validate_dependencies(self, domain_name: Optional[str]=None) -> List[str]:
    """Validate domain dependencies"""
    with self._time_operation('validate_dependencies'):
        try:
            if not self.registry_manager:
                return ['Registry manager not available']
            issues = []
            if domain_name:
                domain = self.registry_manager.get_domain(domain_name)
                dependency_issues = self._check_dependencies(domain)
                issues.extend([issue.description for issue in dependency_issues])
            else:
                all_domains = self.registry_manager.get_all_domains()
                for domain in all_domains.values():
                    dependency_issues = self._check_dependencies(domain)
                    issues.extend([f'{domain.name}: {issue.description}' for issue in dependency_issues])
            return issues
        except Exception as e:
            self._handle_error(e, 'validate_dependencies')
            return [f'Dependency validation failed: {str(e)}']

def schedule_health_check(self, domain_name: str, interval_minutes: int) -> bool:
    """Schedule periodic health checks"""
    try:
        next_check = datetime.now() + timedelta(minutes=interval_minutes)
        self._scheduled_checks[domain_name] = {'interval_minutes': interval_minutes, 'next_check': next_check}
        self.logger.info(f'Scheduled health check for {domain_name} every {interval_minutes} minutes')
        return True
    except Exception as e:
        self._handle_error(e, 'schedule_health_check')
        return False
