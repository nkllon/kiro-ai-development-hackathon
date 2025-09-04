"""
Domain Health Monitoring System

This module provides comprehensive health monitoring for all domains,
including dependency validation, file pattern checking, and health reporting.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import DomainSystemComponent
from .interfaces import HealthMonitorInterface
from .models import (
    Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics,
    IssueSeverity, IssueCategory, HealthStatusCollection
)
from .exceptions import HealthMonitorError, HealthCheckFailedError
from .config import get_config


class DomainHealthMonitor(DomainSystemComponent, HealthMonitorInterface):
    """
    Comprehensive health monitoring for all domains
    
    Provides health checking capabilities including:
    - File pattern validation against filesystem
    - Dependency existence and accessibility validation
    - Health status aggregation and reporting
    - Automated health check scheduling
    - Issue detection and resolution suggestions
    """
    
    def __init__(self, registry_manager=None, config: Optional[Dict[str, Any]] = None):
        super().__init__("domain_health_monitor", config)
        
        # Configuration
        self.config_obj = get_config()
        self.check_interval = self.config_obj.get("health_check_interval_minutes", 15)
        self.check_timeout = self.config_obj.get("health_check_timeout_seconds", 10)
        self.max_issues_per_domain = self.config_obj.get("max_health_issues_per_domain", 50)
        self.parallel_checks = self.config_obj.get("parallel_processing_enabled", True)
        self.max_workers = self.config_obj.get("max_worker_threads", 4)
        
        # Registry manager (will be injected)
        self.registry_manager = registry_manager
        
        # Health check state
        self._health_cache = {}
        self._last_full_check = None
        self._scheduled_checks = {}
        
        # Statistics
        self.total_checks = 0
        self.failed_checks = 0
        self.issues_detected = 0
        self.issues_resolved = 0
        
        # Project root for file validation
        self.project_root = Path.cwd()
        
        self.logger.info("Initialized DomainHealthMonitor")
    
    def set_registry_manager(self, registry_manager):
        """Set the registry manager (dependency injection)"""
        self.registry_manager = registry_manager
    
    def set_project_root(self, project_root: str):
        """Set the project root directory for file validation"""
        self.project_root = Path(project_root)
        self.logger.info(f"Set project root to: {self.project_root}")
    
    def check_domain_health(self, domain_name: str) -> HealthStatus:
        """Check health of a specific domain"""
        with self._time_operation("check_domain_health"):
            self.total_checks += 1
            
            try:
                if not self.registry_manager:
                    raise HealthMonitorError("Registry manager not set")
                
                domain = self.registry_manager.get_domain(domain_name)
                return self._perform_health_check(domain)
                
            except Exception as e:
                self.failed_checks += 1
                self._handle_error(e, "check_domain_health")
                raise HealthCheckFailedError(domain_name, "full_check", str(e))
    
    def check_all_domains(self) -> HealthStatusCollection:
        """Check health of all domains"""
        with self._time_operation("check_all_domains"):
            try:
                if not self.registry_manager:
                    raise HealthMonitorError("Registry manager not set")
                
                all_domains = self.registry_manager.get_all_domains()
                health_statuses = {}
                
                if self.parallel_checks and len(all_domains) > 1:
                    # Parallel health checks
                    health_statuses = self._parallel_health_checks(all_domains)
                else:
                    # Sequential health checks
                    for domain_name, domain in all_domains.items():
                        try:
                            health_statuses[domain_name] = self._perform_health_check(domain)
                        except Exception as e:
                            self.failed_checks += 1
                            self.logger.error(f"Health check failed for {domain_name}: {e}")
                            health_statuses[domain_name] = self._create_failed_health_status(str(e))
                
                # Update cache and timestamp
                self._health_cache.update(health_statuses)
                self._last_full_check = datetime.now()
                
                self.logger.info(f"Completed health checks for {len(health_statuses)} domains")
                return health_statuses
                
            except Exception as e:
                self._handle_error(e, "check_all_domains")
                return {}
    
    def _parallel_health_checks(self, domains: Dict[str, Domain]) -> HealthStatusCollection:
        """Perform health checks in parallel"""
        health_statuses = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all health check tasks
            future_to_domain = {
                executor.submit(self._perform_health_check, domain): domain_name
                for domain_name, domain in domains.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_domain, timeout=self.check_timeout * len(domains)):
                domain_name = future_to_domain[future]
                try:
                    health_status = future.result()
                    health_statuses[domain_name] = health_status
                except Exception as e:
                    self.failed_checks += 1
                    self.logger.error(f"Parallel health check failed for {domain_name}: {e}")
                    health_statuses[domain_name] = self._create_failed_health_status(str(e))
        
        return health_statuses
    
    def _perform_health_check(self, domain: Domain) -> HealthStatus:
        """Perform comprehensive health check for a domain"""
        start_time = time.time()
        issues = []
        
        # File pattern validation
        pattern_issues = self._check_file_patterns(domain)
        issues.extend(pattern_issues)
        
        # Dependency validation
        dependency_issues = self._check_dependencies(domain)
        issues.extend(dependency_issues)
        
        # Content indicator validation
        content_issues = self._check_content_indicators(domain)
        issues.extend(content_issues)
        
        # Tool validation
        tool_issues = self._check_domain_tools(domain)
        issues.extend(tool_issues)
        
        # Limit issues to prevent overwhelming output
        if len(issues) > self.max_issues_per_domain:
            issues = issues[:self.max_issues_per_domain]
            issues.append(HealthIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.VALIDATION,
                description=f"Too many issues detected (showing first {self.max_issues_per_domain})",
                suggested_fix="Review domain configuration and resolve critical issues first"
            ))
        
        # Calculate health metrics
        metrics = self._calculate_health_metrics(domain, issues)
        
        # Determine overall health status
        status_type = self._determine_health_status_type(issues, metrics)
        
        # Update statistics
        self.issues_detected += len(issues)
        
        check_duration = int((time.time() - start_time) * 1000)
        
        return HealthStatus(
            status=status_type,
            last_check=datetime.now(),
            issues=issues,
            metrics=metrics,
            check_duration_ms=check_duration,
            next_check=datetime.now() + timedelta(minutes=self.check_interval)
        )
    
    def _check_file_patterns(self, domain: Domain) -> List[HealthIssue]:
        """Check if domain file patterns match actual files"""
        issues = []
        
        try:
            for pattern in domain.patterns:
                # Convert glob pattern to pathlib pattern
                pattern_path = self.project_root / pattern.replace("**", "*")
                
                # Check if pattern matches any files
                matching_files = list(self.project_root.glob(pattern))
                
                if not matching_files:
                    issues.append(HealthIssue(
                        severity=IssueSeverity.WARNING,
                        category=IssueCategory.PATTERN,
                        description=f"Pattern '{pattern}' matches no files",
                        suggested_fix=f"Verify pattern is correct or remove if no longer needed",
                        affected_files=[pattern]
                    ))
                else:
                    # Check if files are accessible
                    inaccessible_files = []
                    for file_path in matching_files[:10]:  # Limit to first 10 files
                        if not file_path.exists() or not os.access(file_path, os.R_OK):
                            inaccessible_files.append(str(file_path))
                    
                    if inaccessible_files:
                        issues.append(HealthIssue(
                            severity=IssueSeverity.CRITICAL,
                            category=IssueCategory.FILE,
                            description=f"Files matching '{pattern}' are not accessible",
                            suggested_fix="Check file permissions and existence",
                            affected_files=inaccessible_files
                        ))
        
        except Exception as e:
            issues.append(HealthIssue(
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.PATTERN,
                description=f"Failed to validate patterns: {str(e)}",
                suggested_fix="Check pattern syntax and file system access"
            ))
        
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
                    issues.append(HealthIssue(
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.DEPENDENCY,
                        description=f"Dependency '{dependency}' not found in registry",
                        suggested_fix=f"Add '{dependency}' to registry or remove from dependencies"
                    ))
                else:
                    # Check if dependency is healthy (recursive check with depth limit)
                    dep_domain = all_domains[dependency]
                    if hasattr(dep_domain, 'health_status') and dep_domain.health_status:
                        if dep_domain.health_status.status == HealthStatusType.FAILED:
                            issues.append(HealthIssue(
                                severity=IssueSeverity.WARNING,
                                category=IssueCategory.DEPENDENCY,
                                description=f"Dependency '{dependency}' has failed health status",
                                suggested_fix=f"Resolve health issues in '{dependency}' domain"
                            ))
        
        except Exception as e:
            issues.append(HealthIssue(
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.DEPENDENCY,
                description=f"Failed to validate dependencies: {str(e)}",
                suggested_fix="Check registry accessibility and dependency configuration"
            ))
        
        return issues
    
    def _check_content_indicators(self, domain: Domain) -> List[HealthIssue]:
        """Check if content indicators are found in domain files"""
        issues = []
        
        try:
            # Get files matching domain patterns
            domain_files = []
            for pattern in domain.patterns:
                matching_files = list(self.project_root.glob(pattern))
                domain_files.extend(matching_files)
            
            if not domain_files:
                return issues  # No files to check
            
            # Check a sample of files for content indicators
            sample_files = domain_files[:5]  # Check first 5 files
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
                        continue  # Skip files that can't be read
            
            # Check if any indicators were found
            missing_indicators = set(domain.content_indicators) - indicators_found
            if missing_indicators and len(domain.content_indicators) > 0:
                issues.append(HealthIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.VALIDATION,
                    description=f"Content indicators not found in sample files: {', '.join(missing_indicators)}",
                    suggested_fix="Verify content indicators are correct or update them"
                ))
        
        except Exception as e:
            issues.append(HealthIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.VALIDATION,
                description=f"Failed to validate content indicators: {str(e)}",
                suggested_fix="Check file accessibility and content indicator configuration"
            ))
        
        return issues
    
    def _check_domain_tools(self, domain: Domain) -> List[HealthIssue]:
        """Check if domain tools are available and configured correctly"""
        issues = []
        
        try:
            tools_to_check = [
                ("linter", domain.tools.linter),
                ("formatter", domain.tools.formatter),
                ("validator", domain.tools.validator)
            ]
            
            for tool_type, tool_name in tools_to_check:
                if tool_name:
                    # Basic check - just verify tool name is reasonable
                    if not isinstance(tool_name, str) or not tool_name.strip():
                        issues.append(HealthIssue(
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.VALIDATION,
                            description=f"Invalid {tool_type} configuration: '{tool_name}'",
                            suggested_fix=f"Set a valid {tool_type} tool name"
                        ))
        
        except Exception as e:
            issues.append(HealthIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.VALIDATION,
                description=f"Failed to validate domain tools: {str(e)}",
                suggested_fix="Check domain tools configuration"
            ))
        
        return issues
    
    def _calculate_health_metrics(self, domain: Domain, issues: List[HealthIssue]) -> HealthMetrics:
        """Calculate health metrics based on issues found"""
        # Count issues by severity
        critical_count = sum(1 for issue in issues if issue.severity == IssueSeverity.CRITICAL)
        warning_count = sum(1 for issue in issues if issue.severity == IssueSeverity.WARNING)
        info_count = sum(1 for issue in issues if issue.severity == IssueSeverity.INFO)
        
        # Calculate component scores (1.0 = perfect, 0.0 = completely broken)
        dependency_score = max(0.0, 1.0 - (critical_count * 0.3) - (warning_count * 0.1))
        pattern_score = max(0.0, 1.0 - (critical_count * 0.2) - (warning_count * 0.05))
        file_score = max(0.0, 1.0 - (critical_count * 0.4) - (warning_count * 0.1))
        makefile_score = 0.8  # Default score, will be updated when makefile integration is available
        
        # Overall health score
        overall_score = (dependency_score + pattern_score + file_score + makefile_score) / 4.0
        
        return HealthMetrics(
            dependency_health_score=dependency_score,
            pattern_coverage_score=pattern_score,
            file_accessibility_score=file_score,
            makefile_integration_score=makefile_score,
            overall_health_score=overall_score
        )
    
    def _determine_health_status_type(self, issues: List[HealthIssue], metrics: HealthMetrics) -> HealthStatusType:
        """Determine overall health status type"""
        critical_issues = sum(1 for issue in issues if issue.severity == IssueSeverity.CRITICAL)
        
        if critical_issues > 0:
            return HealthStatusType.FAILED
        elif metrics.overall_health_score < 0.7:
            return HealthStatusType.DEGRADED
        else:
            return HealthStatusType.HEALTHY
    
    def _create_failed_health_status(self, error_message: str) -> HealthStatus:
        """Create a failed health status for error cases"""
        issue = HealthIssue(
            severity=IssueSeverity.CRITICAL,
            category=IssueCategory.VALIDATION,
            description=f"Health check failed: {error_message}",
            suggested_fix="Check system configuration and try again"
        )
        
        metrics = HealthMetrics(
            dependency_health_score=0.0,
            pattern_coverage_score=0.0,
            file_accessibility_score=0.0,
            makefile_integration_score=0.0,
            overall_health_score=0.0
        )
        
        return HealthStatus(
            status=HealthStatusType.FAILED,
            last_check=datetime.now(),
            issues=[issue],
            metrics=metrics
        )
    
    def validate_dependencies(self, domain_name: Optional[str] = None) -> List[str]:
        """Validate domain dependencies"""
        with self._time_operation("validate_dependencies"):
            try:
                if not self.registry_manager:
                    return ["Registry manager not available"]
                
                issues = []
                
                if domain_name:
                    # Validate specific domain
                    domain = self.registry_manager.get_domain(domain_name)
                    dependency_issues = self._check_dependencies(domain)
                    issues.extend([issue.description for issue in dependency_issues])
                else:
                    # Validate all domains
                    all_domains = self.registry_manager.get_all_domains()
                    for domain in all_domains.values():
                        dependency_issues = self._check_dependencies(domain)
                        issues.extend([f"{domain.name}: {issue.description}" for issue in dependency_issues])
                
                return issues
                
            except Exception as e:
                self._handle_error(e, "validate_dependencies")
                return [f"Dependency validation failed: {str(e)}"]
    
    def detect_orphaned_files(self) -> List[str]:
        """Find files not covered by any domain"""
        with self._time_operation("detect_orphaned_files"):
            try:
                if not self.registry_manager:
                    return []
                
                # Get all domain patterns
                all_domains = self.registry_manager.get_all_domains()
                covered_patterns = set()
                
                for domain in all_domains.values():
                    for pattern in domain.patterns:
                        covered_patterns.add(pattern)
                
                # Find all Python files in the project
                all_py_files = list(self.project_root.glob("**/*.py"))
                
                # Check which files are not covered by any pattern
                orphaned_files = []
                for file_path in all_py_files:
                    relative_path = file_path.relative_to(self.project_root)
                    is_covered = False
                    
                    for pattern in covered_patterns:
                        # Simple pattern matching (could be enhanced)
                        if self._file_matches_pattern(str(relative_path), pattern):
                            is_covered = True
                            break
                    
                    if not is_covered:
                        orphaned_files.append(str(relative_path))
                
                return orphaned_files
                
            except Exception as e:
                self._handle_error(e, "detect_orphaned_files")
                return []
    
    def _file_matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a domain pattern"""
        # Simple pattern matching - could be enhanced with proper glob matching
        if "**" in pattern:
            # Recursive pattern
            pattern_parts = pattern.split("**")
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                return file_path.startswith(prefix.rstrip("/")) and file_path.endswith(suffix.lstrip("/"))
        
        return pattern in file_path
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains"""
        with self._time_operation("detect_circular_dependencies"):
            try:
                if not self.registry_manager:
                    return []
                
                all_domains = self.registry_manager.get_all_domains()
                circular_deps = []
                
                # Use depth-first search to detect cycles
                visited = set()
                rec_stack = set()
                
                def dfs(domain_name: str, path: List[str]) -> None:
                    if domain_name in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(domain_name)
                        cycle = path[cycle_start:] + [domain_name]
                        circular_deps.append(cycle)
                        return
                    
                    if domain_name in visited:
                        return
                    
                    visited.add(domain_name)
                    rec_stack.add(domain_name)
                    
                    if domain_name in all_domains:
                        domain = all_domains[domain_name]
                        for dep in domain.dependencies:
                            dfs(dep, path + [domain_name])
                    
                    rec_stack.remove(domain_name)
                
                # Check each domain for cycles
                for domain_name in all_domains:
                    if domain_name not in visited:
                        dfs(domain_name, [])
                
                return circular_deps
                
            except Exception as e:
                self._handle_error(e, "detect_circular_dependencies")
                return []
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        try:
            if not self._health_cache:
                # Perform health checks if cache is empty
                self.check_all_domains()
            
            total_domains = len(self._health_cache)
            healthy_count = sum(1 for status in self._health_cache.values() 
                              if status.status == HealthStatusType.HEALTHY)
            degraded_count = sum(1 for status in self._health_cache.values() 
                               if status.status == HealthStatusType.DEGRADED)
            failed_count = sum(1 for status in self._health_cache.values() 
                             if status.status == HealthStatusType.FAILED)
            
            total_issues = sum(len(status.issues) for status in self._health_cache.values())
            critical_issues = sum(
                sum(1 for issue in status.issues if issue.severity == IssueSeverity.CRITICAL)
                for status in self._health_cache.values()
            )
            
            return {
                "total_domains": total_domains,
                "healthy_domains": healthy_count,
                "degraded_domains": degraded_count,
                "failed_domains": failed_count,
                "overall_health_percentage": (healthy_count / max(total_domains, 1)) * 100,
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "last_full_check": self._last_full_check.isoformat() if self._last_full_check else None,
                "check_statistics": {
                    "total_checks": self.total_checks,
                    "failed_checks": self.failed_checks,
                    "issues_detected": self.issues_detected,
                    "issues_resolved": self.issues_resolved
                }
            }
            
        except Exception as e:
            self._handle_error(e, "get_health_summary")
            return {"error": str(e)}
    
    def schedule_health_check(self, domain_name: str, interval_minutes: int) -> bool:
        """Schedule periodic health checks"""
        try:
            next_check = datetime.now() + timedelta(minutes=interval_minutes)
            self._scheduled_checks[domain_name] = {
                "interval_minutes": interval_minutes,
                "next_check": next_check
            }
            
            self.logger.info(f"Scheduled health check for {domain_name} every {interval_minutes} minutes")
            return True
            
        except Exception as e:
            self._handle_error(e, "schedule_health_check")
            return False
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """Get health monitor statistics"""
        return {
            "total_checks_performed": self.total_checks,
            "failed_checks": self.failed_checks,
            "success_rate": (self.total_checks - self.failed_checks) / max(self.total_checks, 1),
            "issues_detected": self.issues_detected,
            "issues_resolved": self.issues_resolved,
            "last_full_check": self._last_full_check.isoformat() if self._last_full_check else None,
            "cached_health_statuses": len(self._health_cache),
            "scheduled_checks": len(self._scheduled_checks),
            "parallel_checks_enabled": self.parallel_checks,
            "max_workers": self.max_workers,
            "performance_metrics": self.performance_metrics
        }