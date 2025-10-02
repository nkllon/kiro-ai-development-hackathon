"""
CI/CD Pipeline Integration for Technical Debt Patch Annotation System

This module provides comprehensive integration with CI/CD pipelines, including patch annotation
validation, debt threshold checking, merge blocking, and pull request reporting capabilities.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import PatchAnnotation, DebtLevel, BypassType, ValidationResult
from ..discovery.patch_scanner import PatchScanner, ScanConfiguration, ScanResult
from ..classification.debt_classifier import DebtClassifier


class MergeBlockReason(Enum):
    """Reasons for blocking merge operations."""
    INVALID_ANNOTATIONS = "invalid_annotations"
    DEBT_THRESHOLD_EXCEEDED = "debt_threshold_exceeded"
    MISSING_ANNOTATIONS = "missing_annotations"
    CRITICAL_PATCHES_ADDED = "critical_patches_added"
    VALIDATION_FAILED = "validation_failed"


class CIPipelineStage(Enum):
    """CI/CD pipeline stages where patch validation occurs."""
    PRE_COMMIT = "pre_commit"
    BUILD = "build"
    TEST = "test"
    PRE_MERGE = "pre_merge"
    POST_MERGE = "post_merge"
    DEPLOYMENT = "deployment"


@dataclass
class ThresholdConfiguration:
    """Configuration for technical debt thresholds."""
    
    # Component-level thresholds
    max_patches_per_component: int = 10
    max_critical_patches_per_component: int = 2
    max_high_patches_per_component: int = 5
    
    # Repository-level thresholds
    max_total_patches: int = 50
    max_total_critical_patches: int = 5
    max_total_high_patches: int = 15
    
    # Age-based thresholds
    max_patch_age_days: int = 90
    critical_patch_max_age_days: int = 30
    
    # Component debt score thresholds (0-100 scale)
    component_debt_warning_threshold: float = 70.0
    component_debt_blocking_threshold: float = 85.0
    
    # Custom thresholds by component
    component_specific_thresholds: Dict[str, Dict[str, int]] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    """Represents a validation issue found during CI/CD checks."""
    
    severity: str  # "error", "warning", "info"
    category: str  # "annotation", "threshold", "validation", "policy"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    patch_id: Optional[str] = None
    component: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class PatchImpactReport:
    """Report on patch impact for pull requests."""
    
    # Summary statistics
    patches_added: int = 0
    patches_modified: int = 0
    patches_removed: int = 0
    net_patch_change: int = 0
    
    # Debt level breakdown
    patches_by_debt_level: Dict[str, int] = field(default_factory=dict)
    
    # Component impact
    affected_components: Set[str] = field(default_factory=set)
    component_debt_changes: Dict[str, float] = field(default_factory=dict)
    
    # Validation issues
    validation_issues: List[ValidationIssue] = field(default_factory=list)
    
    # Threshold violations
    threshold_violations: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Merge decision
    should_block_merge: bool = False
    block_reasons: List[MergeBlockReason] = field(default_factory=list)


@dataclass
class CIPipelineResult:
    """Result of CI/CD pipeline patch validation."""
    
    stage: CIPipelineStage
    success: bool
    execution_time_seconds: float
    
    # Validation results
    patches_validated: int = 0
    validation_issues: List[ValidationIssue] = field(default_factory=list)
    
    # Impact assessment
    impact_report: Optional[PatchImpactReport] = None
    
    # Threshold checks
    threshold_violations: List[str] = field(default_factory=list)
    
    # Merge decision
    should_block_merge: bool = False
    block_reasons: List[MergeBlockReason] = field(default_factory=list)
    
    # Metadata
    repository_path: str = ""
    commit_hash: Optional[str] = None
    pull_request_id: Optional[str] = None
    branch_name: Optional[str] = None


class CICDIntegration(ReflectiveModule):
    """
    CI/CD Pipeline Integration for Technical Debt Patch Management.
    
    This class provides comprehensive integration with CI/CD pipelines, including:
    - Patch annotation validation in build pipelines
    - Debt threshold checking with automated merge blocking
    - Pull request reporting for patch impact assessment
    - Integration with popular CI/CD platforms (GitHub Actions, GitLab CI, Jenkins)
    """
    
    def __init__(self, 
                 threshold_config: Optional[ThresholdConfiguration] = None,
                 scanner_config: Optional[ScanConfiguration] = None):
        """
        Initialize CI/CD integration.
        
        Args:
            threshold_config: Configuration for debt thresholds
            scanner_config: Configuration for patch scanning
        """
        super().__init__()
        self.threshold_config = threshold_config or ThresholdConfiguration()
        self.scanner_config = scanner_config or ScanConfiguration()
        self.scanner = PatchScanner(self.scanner_config)
        self.debt_classifier = DebtClassifier()
        self.logger = logging.getLogger(__name__)
        
        # Initialize metrics
        self._register_metrics()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for ReflectiveModule interface."""
        return {
            "module_name": "CICDIntegration",
            "version": "1.0.0",
            "description": "CI/CD Pipeline Integration for Technical Debt Patch Management",
            "capabilities": [
                "patch_validation",
                "threshold_checking",
                "merge_blocking",
                "pull_request_reporting",
                "pipeline_integration",
                "automated_quality_gates"
            ]
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of CI/CD integration capabilities."""
        return [
            "patch_validation",
            "threshold_checking", 
            "merge_blocking",
            "pull_request_reporting",
            "pipeline_integration",
            "automated_quality_gates"
        ]
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation when errors occur."""
        self.logger.error(f"CICDIntegration error: {str(error)}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_validation_only",
            "available_operations": ["validate_patch_annotations", "basic_threshold_check"]
        }
    
    def _register_metrics(self):
        """Register Prometheus metrics for CI/CD operations."""
        try:
            from prometheus_client import Counter, Histogram, Gauge
            
            self.pipeline_runs_total = Counter(
                'cicd_integration_pipeline_runs_total',
                'Total number of CI/CD pipeline runs',
                ['stage', 'result']
            )
            
            self.patches_validated_total = Counter(
                'cicd_integration_patches_validated_total',
                'Total number of patches validated in CI/CD',
                ['validation_result']
            )
            
            self.merge_blocks_total = Counter(
                'cicd_integration_merge_blocks_total',
                'Total number of merges blocked due to patch issues',
                ['block_reason']
            )
            
            self.validation_duration_seconds = Histogram(
                'cicd_integration_validation_duration_seconds',
                'Time spent validating patches in CI/CD'
            )
            
            self.current_debt_score = Gauge(
                'cicd_integration_current_debt_score',
                'Current technical debt score',
                ['component']
            )
            
        except ImportError:
            self.logger.warning("Prometheus client not available, metrics disabled")
    
    def validate_patch_annotations(self, 
                                 repository_path: str,
                                 changed_files: Optional[List[str]] = None) -> CIPipelineResult:
        """
        Validate patch annotations in build pipelines.
        
        This method scans for patch annotations and validates their format,
        completeness, and compliance with annotation standards.
        
        Args:
            repository_path: Path to the repository being validated
            changed_files: Optional list of changed files to focus validation on
            
        Returns:
            CIPipelineResult with validation results and recommendations
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Starting patch annotation validation for: {repository_path}")
        
        result = CIPipelineResult(
            stage=CIPipelineStage.BUILD,
            success=True,
            execution_time_seconds=0.0,
            repository_path=repository_path
        )
        
        try:
            # Scan for patches (focus on changed files if provided)
            if changed_files:
                scan_result = self._scan_changed_files(repository_path, changed_files)
            else:
                scan_result = self.scanner.scan_directory(repository_path)
            
            result.patches_validated = len(scan_result.get_all_patches())
            
            # Validate each patch annotation
            validation_issues = []
            for patch in scan_result.get_all_patches():
                patch_validation = patch.validate()
                
                if not patch_validation.is_valid:
                    for error in patch_validation.errors:
                        validation_issues.append(ValidationIssue(
                            severity="error",
                            category="annotation",
                            message=error,
                            file_path=patch.file_path,
                            line_number=patch.line_start,
                            patch_id=patch.patch_id,
                            component=patch.component,
                            suggestion="Fix annotation format according to standards"
                        ))
                
                for warning in patch_validation.warnings:
                    validation_issues.append(ValidationIssue(
                        severity="warning",
                        category="annotation",
                        message=warning,
                        file_path=patch.file_path,
                        line_number=patch.line_start,
                        patch_id=patch.patch_id,
                        component=patch.component
                    ))
            
            result.validation_issues = validation_issues
            
            # Check for critical validation failures
            error_count = len([issue for issue in validation_issues if issue.severity == "error"])
            if error_count > 0:
                result.success = False
                result.should_block_merge = True
                result.block_reasons.append(MergeBlockReason.INVALID_ANNOTATIONS)
            
            # Update metrics
            if hasattr(self, 'patches_validated_total'):
                self.patches_validated_total.labels(
                    validation_result="success" if result.success else "failure"
                ).inc(result.patches_validated)
            
            self.logger.info(
                f"Patch validation completed: {result.patches_validated} patches validated, "
                f"{error_count} errors, {len(validation_issues) - error_count} warnings"
            )
            
        except Exception as e:
            self.logger.error(f"Patch validation failed: {str(e)}")
            result.success = False
            result.validation_issues.append(ValidationIssue(
                severity="error",
                category="validation",
                message=f"Validation process failed: {str(e)}",
                suggestion="Check CI/CD configuration and repository access"
            ))
        
        finally:
            result.execution_time_seconds = time.time() - start_time
            
            if hasattr(self, 'validation_duration_seconds'):
                self.validation_duration_seconds.observe(result.execution_time_seconds)
            
            if hasattr(self, 'pipeline_runs_total'):
                self.pipeline_runs_total.labels(
                    stage=result.stage.value,
                    result="success" if result.success else "failure"
                ).inc()
        
        return result
    
    def check_debt_thresholds(self, 
                            repository_path: str,
                            component_filter: Optional[List[str]] = None) -> CIPipelineResult:
        """
        Check debt threshold compliance with automated merge blocking.
        
        This method analyzes current technical debt levels against configured
        thresholds and determines if merge should be blocked.
        
        Args:
            repository_path: Path to the repository to analyze
            component_filter: Optional list of components to focus on
            
        Returns:
            CIPipelineResult with threshold analysis and merge decision
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Starting debt threshold check for: {repository_path}")
        
        result = CIPipelineResult(
            stage=CIPipelineStage.PRE_MERGE,
            success=True,
            execution_time_seconds=0.0,
            repository_path=repository_path
        )
        
        try:
            # Scan repository for patches
            scan_result = self.scanner.scan_directory(repository_path)
            all_patches = scan_result.get_all_patches()
            
            # Filter by components if specified
            if component_filter:
                all_patches = [p for p in all_patches if p.component in component_filter]
            
            result.patches_validated = len(all_patches)
            
            # Check repository-level thresholds
            threshold_violations = []
            
            # Total patch count
            if len(all_patches) > self.threshold_config.max_total_patches:
                threshold_violations.append(
                    f"Total patches ({len(all_patches)}) exceeds limit ({self.threshold_config.max_total_patches})"
                )
            
            # Critical patch count
            critical_patches = [p for p in all_patches if p.debt_level == DebtLevel.CRITICAL]
            if len(critical_patches) > self.threshold_config.max_total_critical_patches:
                threshold_violations.append(
                    f"Critical patches ({len(critical_patches)}) exceeds limit ({self.threshold_config.max_total_critical_patches})"
                )
            
            # High patch count
            high_patches = [p for p in all_patches if p.debt_level == DebtLevel.HIGH]
            if len(high_patches) > self.threshold_config.max_total_high_patches:
                threshold_violations.append(
                    f"High-priority patches ({len(high_patches)}) exceeds limit ({self.threshold_config.max_total_high_patches})"
                )
            
            # Check component-level thresholds
            patches_by_component = {}
            for patch in all_patches:
                component = patch.component or "unknown"
                if component not in patches_by_component:
                    patches_by_component[component] = []
                patches_by_component[component].append(patch)
            
            for component, component_patches in patches_by_component.items():
                # Component patch count
                if len(component_patches) > self.threshold_config.max_patches_per_component:
                    threshold_violations.append(
                        f"Component '{component}' has {len(component_patches)} patches, "
                        f"exceeds limit ({self.threshold_config.max_patches_per_component})"
                    )
                
                # Component critical patches
                component_critical = [p for p in component_patches if p.debt_level == DebtLevel.CRITICAL]
                if len(component_critical) > self.threshold_config.max_critical_patches_per_component:
                    threshold_violations.append(
                        f"Component '{component}' has {len(component_critical)} critical patches, "
                        f"exceeds limit ({self.threshold_config.max_critical_patches_per_component})"
                    )
                
                # Component high patches
                component_high = [p for p in component_patches if p.debt_level == DebtLevel.HIGH]
                if len(component_high) > self.threshold_config.max_high_patches_per_component:
                    threshold_violations.append(
                        f"Component '{component}' has {len(component_high)} high-priority patches, "
                        f"exceeds limit ({self.threshold_config.max_high_patches_per_component})"
                    )
                
                # Component debt score
                try:
                    debt_assessment = self.debt_classifier._impact_engine.assess_component_impact(component, component_patches)
                    debt_score = debt_assessment.total_debt_score
                    
                    if debt_score >= self.threshold_config.component_debt_blocking_threshold:
                        threshold_violations.append(
                            f"Component '{component}' debt score ({debt_score:.1f}) exceeds blocking threshold "
                            f"({self.threshold_config.component_debt_blocking_threshold})"
                        )
                        result.should_block_merge = True
                        result.block_reasons.append(MergeBlockReason.DEBT_THRESHOLD_EXCEEDED)
                    
                    elif debt_score >= self.threshold_config.component_debt_warning_threshold:
                        result.validation_issues.append(ValidationIssue(
                            severity="warning",
                            category="threshold",
                            message=f"Component '{component}' debt score ({debt_score:.1f}) exceeds warning threshold",
                            component=component,
                            suggestion="Consider prioritizing cleanup for this component"
                        ))
                    
                    # Update debt score metric
                    if hasattr(self, 'current_debt_score'):
                        self.current_debt_score.labels(component=component).set(debt_score)
                
                except Exception as e:
                    self.logger.warning(f"Failed to assess debt for component '{component}': {str(e)}")
            
            # Check patch age thresholds
            current_time = datetime.now()
            for patch in all_patches:
                patch_age = current_time - patch.created_date
                
                if patch.debt_level == DebtLevel.CRITICAL:
                    max_age = timedelta(days=self.threshold_config.critical_patch_max_age_days)
                    if patch_age > max_age:
                        threshold_violations.append(
                            f"Critical patch {patch.patch_id} is {patch_age.days} days old, "
                            f"exceeds limit ({self.threshold_config.critical_patch_max_age_days} days)"
                        )
                
                max_age = timedelta(days=self.threshold_config.max_patch_age_days)
                if patch_age > max_age:
                    result.validation_issues.append(ValidationIssue(
                        severity="warning",
                        category="threshold",
                        message=f"Patch {patch.patch_id} is {patch_age.days} days old, consider cleanup",
                        patch_id=patch.patch_id,
                        component=patch.component,
                        suggestion="Schedule patch cleanup or update expected resolution date"
                    ))
            
            result.threshold_violations = threshold_violations
            
            # Determine if merge should be blocked
            if threshold_violations:
                blocking_violations = [v for v in threshold_violations if "exceeds limit" in v or "blocking threshold" in v]
                if blocking_violations:
                    result.should_block_merge = True
                    result.block_reasons.append(MergeBlockReason.DEBT_THRESHOLD_EXCEEDED)
                    result.success = False
            
            # Update metrics
            if hasattr(self, 'merge_blocks_total') and result.should_block_merge:
                for reason in result.block_reasons:
                    self.merge_blocks_total.labels(block_reason=reason.value).inc()
            
            self.logger.info(
                f"Debt threshold check completed: {len(threshold_violations)} violations, "
                f"merge blocked: {result.should_block_merge}"
            )
            
        except Exception as e:
            self.logger.error(f"Debt threshold check failed: {str(e)}")
            result.success = False
            result.validation_issues.append(ValidationIssue(
                severity="error",
                category="threshold",
                message=f"Threshold check failed: {str(e)}",
                suggestion="Check CI/CD configuration and repository access"
            ))
        
        finally:
            result.execution_time_seconds = time.time() - start_time
            
            if hasattr(self, 'validation_duration_seconds'):
                self.validation_duration_seconds.observe(result.execution_time_seconds)
            
            if hasattr(self, 'pipeline_runs_total'):
                self.pipeline_runs_total.labels(
                    stage=result.stage.value,
                    result="success" if result.success else "failure"
                ).inc()
        
        return result
    
    def generate_pull_request_report(self, 
                                   repository_path: str,
                                   base_branch: str = "main",
                                   head_branch: Optional[str] = None,
                                   pull_request_id: Optional[str] = None) -> PatchImpactReport:
        """
        Generate pull request reporting for patch impact assessment.
        
        This method analyzes the impact of changes in a pull request on
        technical debt patches and provides recommendations.
        
        Args:
            repository_path: Path to the repository
            base_branch: Base branch for comparison (default: "main")
            head_branch: Head branch for comparison (current branch if None)
            pull_request_id: Optional pull request identifier
            
        Returns:
            PatchImpactReport with detailed impact analysis
        """
        self.logger.info(f"Generating pull request patch impact report")
        
        report = PatchImpactReport()
        
        try:
            # Get changed files from git
            changed_files = self._get_changed_files(repository_path, base_branch, head_branch)
            
            if not changed_files:
                self.logger.info("No changed files detected")
                return report
            
            # Scan current state
            current_scan = self._scan_changed_files(repository_path, changed_files)
            current_patches = current_scan.get_all_patches()
            
            # Try to get base branch state for comparison
            base_patches = []
            try:
                # Temporarily checkout base branch to scan
                original_branch = self._get_current_branch(repository_path)
                self._checkout_branch(repository_path, base_branch)
                
                base_scan = self._scan_changed_files(repository_path, changed_files)
                base_patches = base_scan.get_all_patches()
                
                # Return to original branch
                self._checkout_branch(repository_path, original_branch)
                
            except Exception as e:
                self.logger.warning(f"Could not analyze base branch: {str(e)}")
            
            # Analyze patch changes
            current_patch_ids = {p.patch_id for p in current_patches}
            base_patch_ids = {p.patch_id for p in base_patches}
            
            report.patches_added = len(current_patch_ids - base_patch_ids)
            report.patches_removed = len(base_patch_ids - current_patch_ids)
            report.patches_modified = len(current_patch_ids & base_patch_ids)  # Simplified
            report.net_patch_change = report.patches_added - report.patches_removed
            
            # Analyze debt level distribution
            for patch in current_patches:
                debt_level = patch.debt_level.value
                report.patches_by_debt_level[debt_level] = report.patches_by_debt_level.get(debt_level, 0) + 1
            
            # Analyze component impact
            report.affected_components = {p.component for p in current_patches if p.component}
            
            for component in report.affected_components:
                component_patches = [p for p in current_patches if p.component == component]
                try:
                    debt_assessment = self.debt_classifier._impact_engine.assess_component_impact(component, component_patches)
                    report.component_debt_changes[component] = debt_assessment.total_debt_score
                except Exception as e:
                    self.logger.warning(f"Could not assess debt for component '{component}': {str(e)}")
            
            # Validate patches and check for issues
            validation_issues = []
            for patch in current_patches:
                patch_validation = patch.validate()
                
                if not patch_validation.is_valid:
                    for error in patch_validation.errors:
                        validation_issues.append(ValidationIssue(
                            severity="error",
                            category="annotation",
                            message=error,
                            file_path=patch.file_path,
                            patch_id=patch.patch_id,
                            component=patch.component
                        ))
                
                # Check for critical patches being added
                if patch.patch_id in (current_patch_ids - base_patch_ids) and patch.debt_level == DebtLevel.CRITICAL:
                    validation_issues.append(ValidationIssue(
                        severity="error",
                        category="policy",
                        message=f"Critical patch {patch.patch_id} added in pull request",
                        patch_id=patch.patch_id,
                        component=patch.component,
                        suggestion="Critical patches require special approval process"
                    ))
                    report.should_block_merge = True
                    report.block_reasons.append(MergeBlockReason.CRITICAL_PATCHES_ADDED)
            
            report.validation_issues = validation_issues
            
            # Run threshold checks
            threshold_result = self.check_debt_thresholds(repository_path)
            report.threshold_violations = threshold_result.threshold_violations
            
            if threshold_result.should_block_merge:
                report.should_block_merge = True
                report.block_reasons.extend(threshold_result.block_reasons)
            
            # Generate recommendations
            recommendations = []
            
            if report.patches_added > 0:
                recommendations.append(f"Added {report.patches_added} new patches - consider cleanup planning")
            
            if report.patches_by_debt_level.get("Critical", 0) > 0:
                recommendations.append("Critical patches detected - prioritize immediate resolution")
            
            if report.net_patch_change > 5:
                recommendations.append("Significant increase in technical debt - consider refactoring approach")
            
            for component, debt_score in report.component_debt_changes.items():
                if debt_score > self.threshold_config.component_debt_warning_threshold:
                    recommendations.append(f"Component '{component}' has high debt score ({debt_score:.1f}) - schedule cleanup")
            
            if not recommendations:
                recommendations.append("No significant patch impact detected")
            
            report.recommendations = recommendations
            
            self.logger.info(
                f"Pull request impact analysis completed: {report.patches_added} added, "
                f"{report.patches_removed} removed, {len(report.validation_issues)} issues"
            )
            
        except Exception as e:
            self.logger.error(f"Pull request report generation failed: {str(e)}")
            report.validation_issues.append(ValidationIssue(
                severity="error",
                category="validation",
                message=f"Report generation failed: {str(e)}",
                suggestion="Check repository state and CI/CD configuration"
            ))
        
        return report
    
    def _scan_changed_files(self, repository_path: str, changed_files: List[str]) -> ScanResult:
        """
        Scan only the changed files for patches.
        
        Args:
            repository_path: Path to the repository
            changed_files: List of changed file paths
            
        Returns:
            ScanResult containing patches from changed files
        """
        scan_result = ScanResult(root_path=repository_path)
        
        for file_path in changed_files:
            full_path = Path(repository_path) / file_path
            if full_path.exists() and full_path.is_file():
                extraction_result = self.scanner.scan_file(str(full_path))
                scan_result.file_results[str(full_path)] = extraction_result
                scan_result.files_scanned += 1
                
                if extraction_result.errors:
                    scan_result.scan_errors.extend(extraction_result.errors)
        
        scan_result.total_patches_found = len(scan_result.get_all_patches())
        return scan_result
    
    def _get_changed_files(self, repository_path: str, base_branch: str, head_branch: Optional[str] = None) -> List[str]:
        """
        Get list of changed files between branches using git.
        
        Args:
            repository_path: Path to the repository
            base_branch: Base branch for comparison
            head_branch: Head branch for comparison (current if None)
            
        Returns:
            List of changed file paths
        """
        try:
            if head_branch:
                compare_ref = f"{base_branch}...{head_branch}"
            else:
                compare_ref = base_branch
            
            result = subprocess.run(
                ["git", "diff", "--name-only", compare_ref],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            return changed_files
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get changed files: {str(e)}")
            return []
    
    def _get_current_branch(self, repository_path: str) -> str:
        """Get the current git branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"  # Fallback
    
    def _checkout_branch(self, repository_path: str, branch_name: str):
        """Checkout a git branch."""
        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repository_path,
            capture_output=True,
            check=True
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status for the CI/CD integration.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            "service": "cicd_integration",
            "status": "healthy",
            "configuration": {
                "max_total_patches": self.threshold_config.max_total_patches,
                "max_critical_patches": self.threshold_config.max_total_critical_patches,
                "component_debt_blocking_threshold": self.threshold_config.component_debt_blocking_threshold,
                "max_patch_age_days": self.threshold_config.max_patch_age_days
            },
            "capabilities": [
                "patch_validation",
                "threshold_checking",
                "merge_blocking", 
                "pull_request_reporting",
                "pipeline_integration",
                "automated_quality_gates"
            ]
        }


def create_github_actions_workflow() -> str:
    """
    Generate a GitHub Actions workflow for patch validation.
    
    Returns:
        YAML content for GitHub Actions workflow
    """
    return """
name: Technical Debt Patch Validation

on:
  pull_request:
    branches: [ main, develop ]
  push:
    branches: [ main, develop ]

jobs:
  patch-validation:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Fetch full history for comparison
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Validate patch annotations
      run: |
        python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
    
    - name: Check debt thresholds
      run: |
        python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .
    
    - name: Generate PR impact report
      if: github.event_name == 'pull_request'
      run: |
        python -m technical_debt_patch_annotation.integration.cicd_integration pr-report . --base-branch ${{ github.base_ref }} --head-branch ${{ github.head_ref }}
    
    - name: Comment PR with report
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          if (fs.existsSync('patch_impact_report.md')) {
            const report = fs.readFileSync('patch_impact_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
          }
"""


def create_gitlab_ci_config() -> str:
    """
    Generate a GitLab CI configuration for patch validation.
    
    Returns:
        YAML content for GitLab CI configuration
    """
    return """
stages:
  - validate
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

patch-validation:
  stage: validate
  image: python:3.9
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install -r requirements.txt
  script:
    - python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
    - python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .
  artifacts:
    reports:
      junit: patch_validation_report.xml
    paths:
      - patch_validation_report.json
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

patch-impact-report:
  stage: report
  image: python:3.9
  dependencies:
    - patch-validation
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install -r requirements.txt
  script:
    - python -m technical_debt_patch_annotation.integration.cicd_integration pr-report . --base-branch $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --head-branch $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
  artifacts:
    paths:
      - patch_impact_report.md
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
"""


def create_jenkins_pipeline() -> str:
    """
    Generate a Jenkins pipeline for patch validation.
    
    Returns:
        Groovy content for Jenkins pipeline
    """
    return """
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python${PYTHON_VERSION} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Validate Patch Annotations') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m technical_debt_patch_annotation.integration.cicd_integration validate-annotations .
                '''
            }
        }
        
        stage('Check Debt Thresholds') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m technical_debt_patch_annotation.integration.cicd_integration check-thresholds .
                '''
            }
        }
        
        stage('Generate PR Report') {
            when {
                changeRequest()
            }
            steps {
                sh '''
                    . venv/bin/activate
                    python -m technical_debt_patch_annotation.integration.cicd_integration pr-report . --base-branch ${CHANGE_TARGET} --head-branch ${CHANGE_BRANCH}
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'patch_*.json,patch_*.md', allowEmptyArchive: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'patch_impact_report.html',
                reportName: 'Patch Impact Report'
            ])
        }
        failure {
            emailext (
                subject: "Patch Validation Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Patch validation failed. Check the build logs for details.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
"""


# CLI interface for CI/CD integration
if __name__ == "__main__":
    import argparse
    import sys
    
    def main():
        parser = argparse.ArgumentParser(description="CI/CD Integration for Technical Debt Patch Management")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Validate annotations command
        validate_parser = subparsers.add_parser("validate-annotations", help="Validate patch annotations")
        validate_parser.add_argument("repository_path", help="Path to repository")
        validate_parser.add_argument("--changed-files", nargs="*", help="List of changed files to focus on")
        
        # Check thresholds command
        threshold_parser = subparsers.add_parser("check-thresholds", help="Check debt thresholds")
        threshold_parser.add_argument("repository_path", help="Path to repository")
        threshold_parser.add_argument("--components", nargs="*", help="Components to focus on")
        
        # PR report command
        pr_parser = subparsers.add_parser("pr-report", help="Generate pull request impact report")
        pr_parser.add_argument("repository_path", help="Path to repository")
        pr_parser.add_argument("--base-branch", default="main", help="Base branch for comparison")
        pr_parser.add_argument("--head-branch", help="Head branch for comparison")
        pr_parser.add_argument("--pr-id", help="Pull request ID")
        
        # Generate workflow configs
        workflow_parser = subparsers.add_parser("generate-workflows", help="Generate CI/CD workflow configurations")
        workflow_parser.add_argument("--platform", choices=["github", "gitlab", "jenkins"], required=True)
        workflow_parser.add_argument("--output", help="Output file path")
        
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return 1
        
        # Initialize CI/CD integration
        cicd = CICDIntegration()
        
        try:
            if args.command == "validate-annotations":
                result = cicd.validate_patch_annotations(args.repository_path, args.changed_files)
                
                print(f"Validation completed: {result.patches_validated} patches validated")
                print(f"Success: {result.success}")
                print(f"Execution time: {result.execution_time_seconds:.2f}s")
                
                if result.validation_issues:
                    print(f"\nValidation Issues ({len(result.validation_issues)}):")
                    for issue in result.validation_issues:
                        print(f"  {issue.severity.upper()}: {issue.message}")
                        if issue.file_path:
                            print(f"    File: {issue.file_path}:{issue.line_number or 'N/A'}")
                
                if result.should_block_merge:
                    print(f"\n❌ MERGE BLOCKED - Reasons: {[r.value for r in result.block_reasons]}")
                    return 1
                else:
                    print("\n✅ Validation passed")
                    return 0
            
            elif args.command == "check-thresholds":
                result = cicd.check_debt_thresholds(args.repository_path, args.components)
                
                print(f"Threshold check completed: {result.patches_validated} patches analyzed")
                print(f"Success: {result.success}")
                print(f"Execution time: {result.execution_time_seconds:.2f}s")
                
                if result.threshold_violations:
                    print(f"\nThreshold Violations ({len(result.threshold_violations)}):")
                    for violation in result.threshold_violations:
                        print(f"  ⚠️  {violation}")
                
                if result.should_block_merge:
                    print(f"\n❌ MERGE BLOCKED - Reasons: {[r.value for r in result.block_reasons]}")
                    return 1
                else:
                    print("\n✅ Thresholds satisfied")
                    return 0
            
            elif args.command == "pr-report":
                report = cicd.generate_pull_request_report(
                    args.repository_path, 
                    args.base_branch, 
                    args.head_branch,
                    args.pr_id
                )
                
                # Generate markdown report
                markdown_report = f"""# Technical Debt Patch Impact Report

## Summary
- **Patches Added**: {report.patches_added}
- **Patches Removed**: {report.patches_removed}
- **Patches Modified**: {report.patches_modified}
- **Net Change**: {report.net_patch_change:+d}

## Debt Level Distribution
"""
                for level, count in report.patches_by_debt_level.items():
                    markdown_report += f"- **{level}**: {count}\n"
                
                markdown_report += f"""
## Affected Components
{', '.join(report.affected_components) if report.affected_components else 'None'}

## Component Debt Scores
"""
                for component, score in report.component_debt_changes.items():
                    markdown_report += f"- **{component}**: {score:.1f}\n"
                
                if report.validation_issues:
                    markdown_report += f"\n## Validation Issues ({len(report.validation_issues)})\n"
                    for issue in report.validation_issues:
                        markdown_report += f"- **{issue.severity.upper()}**: {issue.message}\n"
                
                if report.threshold_violations:
                    markdown_report += f"\n## Threshold Violations ({len(report.threshold_violations)})\n"
                    for violation in report.threshold_violations:
                        markdown_report += f"- ⚠️ {violation}\n"
                
                markdown_report += f"\n## Recommendations\n"
                for rec in report.recommendations:
                    markdown_report += f"- {rec}\n"
                
                if report.should_block_merge:
                    markdown_report += f"\n## ❌ MERGE BLOCKED\n**Reasons**: {', '.join([r.value for r in report.block_reasons])}\n"
                else:
                    markdown_report += f"\n## ✅ MERGE APPROVED\nNo blocking issues detected.\n"
                
                # Save report
                with open("patch_impact_report.md", "w") as f:
                    f.write(markdown_report)
                
                print("Pull request impact report generated: patch_impact_report.md")
                
                if report.should_block_merge:
                    return 1
                else:
                    return 0
            
            elif args.command == "generate-workflows":
                if args.platform == "github":
                    content = create_github_actions_workflow()
                    default_file = ".github/workflows/patch-validation.yml"
                elif args.platform == "gitlab":
                    content = create_gitlab_ci_config()
                    default_file = ".gitlab-ci.yml"
                elif args.platform == "jenkins":
                    content = create_jenkins_pipeline()
                    default_file = "Jenkinsfile"
                
                output_file = args.output or default_file
                
                # Create directory if needed
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                with open(output_file, "w") as f:
                    f.write(content)
                
                print(f"Generated {args.platform} workflow configuration: {output_file}")
                return 0
        
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    sys.exit(main())