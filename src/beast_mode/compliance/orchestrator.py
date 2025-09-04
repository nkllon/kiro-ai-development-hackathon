"""
ComplianceOrchestrator - Main orchestrator for RDI-RM compliance checking.

This module implements the central orchestrator that coordinates all compliance
checking activities for the Beast Mode Framework, ensuring systematic validation
of commits ahead of main against RDI methodology and RM architectural standards.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.reflective_module import ReflectiveModule
from .interfaces import ComplianceValidator, ComplianceAnalyzer, ValidationContext
from .models import (
    ComplianceAnalysisResult,
    Phase2ValidationResult,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity,
    CommitInfo,
    RDIComplianceStatus,
    RMComplianceStatus,
    TestCoverageStatus,
    TaskReconciliationStatus
)


class ComplianceOrchestrator(ReflectiveModule):
    """
    Main orchestrator for RDI-RM compliance checking.
    
    Implements systematic validation of commits ahead of main to ensure
    all components meet Beast Mode Framework standards before integration.
    """
    
    def __init__(self, repository_path: str = "."):
        """
        Initialize the compliance orchestrator.
        
        Args:
            repository_path: Path to the git repository to analyze
        """
        super().__init__("ComplianceOrchestrator")
        self.repository_path = Path(repository_path)
        self.logger = logging.getLogger(__name__)
        
        # Registry of validators and analyzers
        self._validators: Dict[str, ComplianceValidator] = {}
        self._analyzers: Dict[str, ComplianceAnalyzer] = {}
        
        # Configuration
        self._config = {
            "target_branch": "main",
            "base_branch": "origin/master",
            "test_coverage_baseline": 96.7,
            "max_module_size": 200,
            "phase2_expected_failing_tests": 7
        }
        
        self.logger.info(f"ComplianceOrchestrator initialized for repository: {self.repository_path}")
    
    def register_validator(self, validator: ComplianceValidator) -> None:
        """
        Register a compliance validator.
        
        Args:
            validator: The validator to register
        """
        name = validator.get_validator_name()
        self._validators[name] = validator
        self.logger.debug(f"Registered validator: {name}")
    
    def register_analyzer(self, analyzer: ComplianceAnalyzer) -> None:
        """
        Register a compliance analyzer.
        
        Args:
            analyzer: The analyzer to register
        """
        name = analyzer.get_analyzer_name()
        self._analyzers[name] = analyzer
        self.logger.debug(f"Registered analyzer: {name}")
    
    def analyze_commits_ahead_of_main(self) -> ComplianceAnalysisResult:
        """
        Analyze the commits ahead of main for compliance.
        
        This method orchestrates the complete compliance analysis workflow,
        including RDI validation, RM compliance checking, and test coverage analysis.
        
        Returns:
            Comprehensive compliance analysis result
        """
        self.logger.info("Starting compliance analysis of commits ahead of main")
        
        try:
            # Create validation context
            context = ValidationContext(
                repository_path=str(self.repository_path),
                target_branch=self._config["target_branch"],
                base_branch=self._config["base_branch"]
            )
            
            # Initialize result structure
            result = ComplianceAnalysisResult()
            
            # Step 1: Identify commits ahead of main
            result.commits_analyzed = self._get_commits_ahead_of_main()
            self.logger.info(f"Found {len(result.commits_analyzed)} commits ahead of main")
            
            # Step 2: Run RDI compliance validation
            result.rdi_compliance = self._validate_rdi_compliance(context)
            
            # Step 3: Run RM architectural compliance validation
            result.rm_compliance = self._validate_rm_compliance(context)
            
            # Step 4: Validate test coverage
            result.test_coverage_status = self._validate_test_coverage(context)
            
            # Step 5: Reconcile task completion status
            result.task_completion_reconciliation = self._reconcile_task_completion(context)
            
            # Step 6: Calculate overall compliance score
            result.overall_compliance_score = self._calculate_overall_compliance_score(result)
            
            # Step 7: Identify critical issues
            result.critical_issues = self._identify_critical_issues(result)
            
            # Step 8: Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            # Step 9: Determine Phase 3 readiness
            result.phase3_ready = self._assess_phase3_readiness(result)
            
            self.logger.info(f"Compliance analysis completed. Overall score: {result.overall_compliance_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during compliance analysis: {str(e)}")
            # Return a result with critical error
            result = ComplianceAnalysisResult()
            result.critical_issues.append(
                ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.CRITICAL,
                    description=f"Compliance analysis failed: {str(e)}",
                    blocking_merge=True
                )
            )
            return result
    
    def validate_phase2_completion(self) -> Phase2ValidationResult:
        """
        Validate Phase 2 completion against task list.
        
        Returns:
            Phase 2 validation result with readiness assessment
        """
        self.logger.info("Starting Phase 2 completion validation")
        
        result = Phase2ValidationResult()
        
        try:
            # This is a placeholder implementation - will be expanded in later tasks
            result.claimed_complete_tasks = self._get_claimed_complete_tasks()
            result.actually_implemented_tasks = self._get_actually_implemented_tasks()
            result.missing_implementations = list(
                set(result.claimed_complete_tasks) - set(result.actually_implemented_tasks)
            )
            
            # Calculate Phase 3 readiness score
            if result.claimed_complete_tasks:
                implementation_ratio = len(result.actually_implemented_tasks) / len(result.claimed_complete_tasks)
                result.phase3_readiness_score = implementation_ratio * 100
            
            # Check for expected failing tests
            result.test_failures_count = self._config["phase2_expected_failing_tests"]
            
            self.logger.info(f"Phase 2 validation completed. Readiness score: {result.phase3_readiness_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during Phase 2 validation: {str(e)}")
            result.blocking_issues.append(
                ComplianceIssue(
                    issue_type=ComplianceIssueType.ARCHITECTURAL_VIOLATION,
                    severity=IssueSeverity.CRITICAL,
                    description=f"Phase 2 validation failed: {str(e)}",
                    blocking_merge=True
                )
            )
            return result
    
    def generate_compliance_report(self) -> str:
        """
        Generate comprehensive compliance report with remediation steps.
        
        Returns:
            Formatted compliance report
        """
        analysis_result = self.analyze_commits_ahead_of_main()
        
        report_lines = [
            "# Beast Mode Framework Compliance Report",
            f"Generated: {analysis_result.analysis_timestamp}",
            "",
            f"## Overall Compliance Score: {analysis_result.overall_compliance_score:.2f}/100",
            "",
            f"## Analysis Summary",
            f"- Commits analyzed: {len(analysis_result.commits_analyzed)}",
            f"- RDI compliance score: {analysis_result.rdi_compliance.compliance_score:.2f}",
            f"- RM compliance score: {analysis_result.rm_compliance.compliance_score:.2f}",
            f"- Test coverage: {analysis_result.test_coverage_status.current_coverage:.1f}%",
            f"- Phase 3 ready: {'Yes' if analysis_result.phase3_ready else 'No'}",
            "",
        ]
        
        if analysis_result.critical_issues:
            report_lines.extend([
                "## Critical Issues",
                ""
            ])
            for issue in analysis_result.critical_issues:
                report_lines.extend([
                    f"### {issue.issue_type.value.replace('_', ' ').title()}",
                    f"**Severity:** {issue.severity.value.upper()}",
                    f"**Description:** {issue.description}",
                    f"**Blocking merge:** {'Yes' if issue.blocking_merge else 'No'}",
                    ""
                ])
        
        if analysis_result.recommendations:
            report_lines.extend([
                "## Recommendations",
                ""
            ])
            for i, recommendation in enumerate(analysis_result.recommendations, 1):
                report_lines.append(f"{i}. {recommendation}")
        
        return "\n".join(report_lines)
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, Any]:
        """Get the current status of the compliance orchestrator."""
        return {
            "module_name": "ComplianceOrchestrator",
            "repository_path": str(self.repository_path),
            "registered_validators": len(self._validators),
            "registered_analyzers": len(self._analyzers),
            "configuration": self._config,
            "is_healthy": self.is_healthy()
        }
    
    def is_healthy(self) -> bool:
        """Check if the compliance orchestrator is healthy."""
        try:
            # Basic health checks
            return (
                self.repository_path.exists() and
                self.repository_path.is_dir() and
                (self.repository_path / ".git").exists()
            )
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health metrics for operational visibility."""
        indicators = {}
        
        try:
            # Repository health
            repo_exists = self.repository_path.exists()
            git_exists = (self.repository_path / ".git").exists() if repo_exists else False
            
            indicators["repository_accessible"] = {
                "status": "healthy" if repo_exists else "unhealthy",
                "value": repo_exists,
                "message": f"Repository at {self.repository_path} {'exists' if repo_exists else 'not found'}"
            }
            
            indicators["git_repository"] = {
                "status": "healthy" if git_exists else "unhealthy", 
                "value": git_exists,
                "message": "Git repository detected" if git_exists else "Not a git repository"
            }
            
            # Component health
            indicators["validators_registered"] = {
                "status": "healthy" if self._validators else "degraded",
                "value": len(self._validators),
                "message": f"{len(self._validators)} validators registered"
            }
            
            indicators["analyzers_registered"] = {
                "status": "healthy" if self._analyzers else "degraded",
                "value": len(self._analyzers),
                "message": f"{len(self._analyzers)} analyzers registered"
            }
            
        except Exception as e:
            indicators["error"] = {
                "status": "unhealthy",
                "value": str(e),
                "message": f"Error getting health indicators: {str(e)}"
            }
        
        return indicators
    
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module."""
        return "Orchestrate comprehensive compliance checking for RDI methodology and RM architectural standards"
    
    # Private helper methods (placeholder implementations)
    def _get_commits_ahead_of_main(self) -> List[CommitInfo]:
        """Get commits ahead of main branch."""
        # Placeholder - will be implemented in GitAnalyzer task
        return []
    
    def _validate_rdi_compliance(self, context: ValidationContext) -> RDIComplianceStatus:
        """Validate RDI methodology compliance."""
        # Placeholder - will be implemented in RDI validation tasks
        return RDIComplianceStatus()
    
    def _validate_rm_compliance(self, context: ValidationContext) -> RMComplianceStatus:
        """Validate RM architectural compliance."""
        # Placeholder - will be implemented in RM validation tasks
        return RMComplianceStatus()
    
    def _validate_test_coverage(self, context: ValidationContext) -> TestCoverageStatus:
        """Validate test coverage against baseline."""
        # Placeholder - will be implemented in test coverage validation task
        return TestCoverageStatus()
    
    def _reconcile_task_completion(self, context: ValidationContext) -> TaskReconciliationStatus:
        """Reconcile task completion claims with actual implementation."""
        # Placeholder - will be implemented in task reconciliation task
        return TaskReconciliationStatus()
    
    def _calculate_overall_compliance_score(self, result: ComplianceAnalysisResult) -> float:
        """Calculate overall compliance score from individual components."""
        scores = [
            result.rdi_compliance.compliance_score,
            result.rm_compliance.compliance_score,
            result.test_coverage_status.current_coverage,
            result.task_completion_reconciliation.reconciliation_score
        ]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _identify_critical_issues(self, result: ComplianceAnalysisResult) -> List[ComplianceIssue]:
        """Identify critical issues from analysis results."""
        critical_issues = []
        
        # Collect critical issues from all components
        for component_status in [
            result.rdi_compliance,
            result.rm_compliance,
            result.test_coverage_status,
            result.task_completion_reconciliation
        ]:
            if hasattr(component_status, 'issues'):
                critical_issues.extend([
                    issue for issue in component_status.issues
                    if issue.severity == IssueSeverity.CRITICAL
                ])
        
        return critical_issues
    
    def _generate_recommendations(self, result: ComplianceAnalysisResult) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        if result.overall_compliance_score < 80:
            recommendations.append("Overall compliance score is below acceptable threshold (80%)")
        
        if not result.rdi_compliance.requirements_traced:
            recommendations.append("Ensure all implementations trace back to valid requirements")
        
        if not result.rm_compliance.interface_implemented:
            recommendations.append("Implement ReflectiveModule interface for all new components")
        
        if result.test_coverage_status.current_coverage < result.test_coverage_status.baseline_coverage:
            recommendations.append(f"Improve test coverage to meet baseline of {result.test_coverage_status.baseline_coverage}%")
        
        return recommendations
    
    def _assess_phase3_readiness(self, result: ComplianceAnalysisResult) -> bool:
        """Assess if the system is ready for Phase 3."""
        return (
            result.overall_compliance_score >= 80 and
            len(result.critical_issues) == 0 and
            result.test_coverage_status.current_coverage >= result.test_coverage_status.baseline_coverage * 0.95
        )
    
    def _get_claimed_complete_tasks(self) -> List[str]:
        """Get list of tasks claimed as complete."""
        # Placeholder - will be implemented in task analysis
        return []
    
    def _get_actually_implemented_tasks(self) -> List[str]:
        """Get list of tasks actually implemented."""
        # Placeholder - will be implemented in task analysis
        return []