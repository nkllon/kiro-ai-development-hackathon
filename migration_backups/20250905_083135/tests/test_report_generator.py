"""
Unit tests for the ReportGenerator class.

Tests comprehensive compliance report generation including severity categorization,
issue details, remediation guidance, and Phase 3 readiness assessment.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.compliance.reporting.report_generator import (
    ReportGenerator,
    ComplianceReport,
    ComplianceSummary
)
from src.beast_mode.compliance.models import (
    ComplianceAnalysisResult,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity,
    RDIComplianceStatus,
    RMComplianceStatus,
    TestCoverageStatus,
    TaskReconciliationStatus,
    CommitInfo,
    RemediationStep
)


class TestReportGenerator:
    """Test suite for ReportGenerator class."""
    
    @pytest.fixture
    def report_generator(self):
        """Create a ReportGenerator instance for testing."""
        return ReportGenerator()
    
    @pytest.fixture
    def sample_compliance_issue(self):
        """Create a sample compliance issue for testing."""
        return ComplianceIssue(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            description="Missing requirement traceability for user authentication",
            affected_files=["src/auth/login.py", "src/auth/validator.py"],
            remediation_steps=[
                "Add requirement traceability comments",
                "Update design documentation"
            ],
            estimated_effort="medium",
            blocking_merge=True,
            metadata={"requirement_id": "REQ-001"}
        )
    
    @pytest.fixture
    def sample_analysis_result(self, sample_compliance_issue):
        """Create a sample compliance analysis result for testing."""
        commit = CommitInfo(
            commit_hash="abc123def456",
            author="test-author",
            timestamp=datetime.now(),
            message="Implement user authentication feature",
            modified_files=["src/auth/login.py"],
            added_files=["src/auth/validator.py"],
            deleted_files=[]
        )
        
        rdi_status = RDIComplianceStatus(
            requirements_traced=False,
            design_aligned=True,
            implementation_complete=True,
            test_coverage_adequate=False,
            compliance_score=65.0,
            issues=[sample_compliance_issue]
        )
        
        rm_status = RMComplianceStatus(
            interface_implemented=True,
            size_constraints_met=True,
            health_monitoring_present=False,
            registry_integrated=True,
            compliance_score=75.0,
            issues=[]
        )
        
        test_status = TestCoverageStatus(
            current_coverage=94.5,
            baseline_coverage=96.7,
            coverage_adequate=False,
            failing_tests=["test_auth_validation", "test_login_flow"],
            missing_tests=["test_password_reset"],
            issues=[]
        )
        
        task_status = TaskReconciliationStatus(
            claimed_complete_tasks=["Task 1", "Task 2"],
            actually_implemented_tasks=["Task 1"],
            missing_implementations=["Task 2"],
            reconciliation_score=50.0,
            issues=[]
        )
        
        return ComplianceAnalysisResult(
            analysis_timestamp=datetime.now(),
            commits_analyzed=[commit],
            rdi_compliance=rdi_status,
            rm_compliance=rm_status,
            test_coverage_status=test_status,
            task_completion_reconciliation=task_status,
            overall_compliance_score=68.5,
            critical_issues=[],
            recommendations=["Fix failing tests", "Improve test coverage"],
            phase3_ready=False
        )
    
    def test_report_generator_initialization(self, report_generator):
        """Test ReportGenerator initialization."""
        assert report_generator.report_format == "markdown"
        assert len(report_generator.severity_weights) == 4
        assert report_generator.severity_weights[IssueSeverity.CRITICAL] == 4.0
        assert report_generator.severity_weights[IssueSeverity.LOW] == 1.0
    
    def test_get_report_format(self, report_generator):
        """Test get_report_format method."""
        assert report_generator.get_report_format() == "markdown"
    
    def test_generate_report_basic_structure(self, report_generator, sample_analysis_result):
        """Test that generate_report produces a properly structured markdown report."""
        report = report_generator.generate_report(sample_analysis_result)
        
        # Check for main sections
        assert "# Beast Mode Framework Compliance Report" in report
        assert "## Executive Summary" in report
        assert "## Detailed Findings" in report
        assert "## Remediation Plan" in report
        assert "## Phase 3 Readiness Assessment" in report
        assert "## Appendix" in report
        
        # Check for key metrics
        assert "Overall Compliance Score:" in report
        assert "Phase 3 Readiness:" in report
        assert "68.5/100.0" in report
        assert "NOT READY" in report
    
    def test_generate_compliance_summary(self, report_generator, sample_analysis_result):
        """Test compliance summary generation."""
        summary = report_generator.generate_compliance_summary(sample_analysis_result)
        
        assert isinstance(summary, ComplianceSummary)
        assert summary.overall_score == 68.5
        assert summary.total_issues == 1  # One issue in sample data
        assert summary.critical_issues == 0
        assert summary.high_priority_issues == 1
        assert summary.phase3_ready is False
        # key_blockers should be empty since there are no critical issues in sample data
        assert len(summary.key_blockers) == 0
        assert len(summary.next_actions) > 0
    
    def test_executive_summary_generation(self, report_generator, sample_analysis_result):
        """Test executive summary generation."""
        summary = report_generator._generate_executive_summary(sample_analysis_result)
        
        assert "Overall Compliance Score:** 68.5/100.0" in summary
        assert "Phase 3 Readiness:** NOT READY" in summary
        assert "Total Issues Found: 1" in summary
        assert "Critical Issues: 0" in summary
        assert "High Priority Issues: 1" in summary
        assert "Test Coverage: 94.5%" in summary
        assert "RDI Compliance Score: 65.0/100.0" in summary
        assert "RM Compliance Score: 75.0/100.0" in summary
    
    def test_detailed_findings_generation(self, report_generator, sample_analysis_result):
        """Test detailed findings generation."""
        findings = report_generator._generate_detailed_findings(sample_analysis_result)
        
        assert "rdi_compliance" in findings
        assert "rm_compliance" in findings
        assert "test_coverage" in findings
        assert "task_reconciliation" in findings
        assert "commit_analysis" in findings
        
        # Check RDI findings
        rdi_findings = findings["rdi_compliance"]
        assert rdi_findings["compliance_score"] == 65.0
        assert rdi_findings["requirements_traced"] is False
        assert rdi_findings["design_aligned"] is True
        assert rdi_findings["issues_count"] == 1
        
        # Check test coverage findings
        test_findings = findings["test_coverage"]
        assert test_findings["current_coverage"] == 94.5
        assert test_findings["baseline_coverage"] == 96.7
        assert test_findings["coverage_adequate"] is False
        assert test_findings["failing_tests_count"] == 2
    
    def test_remediation_plan_generation(self, report_generator, sample_analysis_result):
        """Test remediation plan generation."""
        remediation_plan = report_generator._generate_remediation_plan(sample_analysis_result)
        
        assert len(remediation_plan) > 0
        
        # Check first remediation step
        step = remediation_plan[0]
        assert isinstance(step, RemediationStep)
        assert step.step_id.startswith("STEP-")
        assert step.priority == IssueSeverity.HIGH
        assert len(step.affected_components) > 0
        assert len(step.validation_criteria) > 0
    
    def test_phase3_readiness_assessment(self, report_generator, sample_analysis_result):
        """Test Phase 3 readiness assessment generation."""
        assessment = report_generator._generate_phase3_readiness_assessment(sample_analysis_result)
        
        assert "overall_readiness_score" in assessment
        assert "phase3_ready" in assessment
        assert "readiness_factors" in assessment
        assert "recommendations" in assessment
        assert "next_steps" in assessment
        
        # Check readiness factors
        factors = assessment["readiness_factors"]
        assert "rdi_compliance" in factors
        assert "rm_compliance" in factors
        assert "test_coverage" in factors
        assert "blocking_issues" in factors
        
        # Should not be ready due to low scores and issues
        assert assessment["phase3_ready"] is False
        assert assessment["overall_readiness_score"] < 80.0
    
    def test_issue_collection_and_deduplication(self, report_generator, sample_analysis_result):
        """Test that all issues are collected and deduplicated properly."""
        # Add duplicate issue to test deduplication
        duplicate_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            description="Missing requirement traceability for user authentication",
            affected_files=["src/auth/login.py", "src/auth/validator.py"],
            remediation_steps=["Add requirement traceability comments"],
            estimated_effort="medium",
            blocking_merge=True
        )
        sample_analysis_result.critical_issues.append(duplicate_issue)
        
        all_issues = report_generator._collect_all_issues(sample_analysis_result)
        
        # Should have only one issue due to deduplication
        assert len(all_issues) == 1
        assert all_issues[0].issue_type == ComplianceIssueType.RDI_VIOLATION
    
    def test_issue_grouping_by_type_and_severity(self, report_generator):
        """Test issue grouping functionality."""
        issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.CRITICAL,
                description="Critical RDI issue",
                affected_files=["file1.py"]
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.HIGH,
                description="High RM issue",
                affected_files=["file2.py"]
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.MEDIUM,
                description="Medium RDI issue",
                affected_files=["file3.py"]
            )
        ]
        
        groups = report_generator._group_issues_by_type_and_severity(issues)
        
        assert ComplianceIssueType.RDI_VIOLATION in groups
        assert ComplianceIssueType.RM_NON_COMPLIANCE in groups
        
        rdi_groups = groups[ComplianceIssueType.RDI_VIOLATION]
        assert len(rdi_groups[IssueSeverity.CRITICAL]) == 1
        assert len(rdi_groups[IssueSeverity.MEDIUM]) == 1
        assert len(rdi_groups[IssueSeverity.HIGH]) == 0
        
        rm_groups = groups[ComplianceIssueType.RM_NON_COMPLIANCE]
        assert len(rm_groups[IssueSeverity.HIGH]) == 1
    
    def test_remediation_description_generation(self, report_generator):
        """Test remediation description generation."""
        issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.CRITICAL,
                description="Test failure",
                affected_files=["test1.py"]
            )
        ]
        
        description = report_generator._generate_remediation_description(
            ComplianceIssueType.TEST_FAILURE, IssueSeverity.CRITICAL, issues
        )
        
        assert "Resolve test failures and coverage issues" in description
        assert "critical priority" in description
        assert "1 issues" in description
    
    def test_effort_estimation(self, report_generator):
        """Test effort estimation for remediation."""
        issues_minimal = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.LOW,
                description="Minor issue",
                estimated_effort="minimal"
            )
        ]
        
        issues_high = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.CRITICAL,
                description="Major issue",
                estimated_effort="high"
            )
        ]
        
        assert report_generator._estimate_remediation_effort(issues_minimal) == "minimal"
        assert report_generator._estimate_remediation_effort(issues_high) == "high"
        assert report_generator._estimate_remediation_effort([]) == "minimal"
    
    def test_affected_components_extraction(self, report_generator):
        """Test extraction of affected components."""
        issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.HIGH,
                description="Issue 1",
                affected_files=["file1.py", "file2.py"]
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.MEDIUM,
                description="Issue 2",
                affected_files=["file2.py", "file3.py"]
            )
        ]
        
        components = report_generator._extract_affected_components(issues)
        
        assert len(components) == 3
        assert "file1.py" in components
        assert "file2.py" in components
        assert "file3.py" in components
        assert components == sorted(components)  # Should be sorted
    
    def test_prerequisites_determination(self, report_generator):
        """Test prerequisite determination for different issue types."""
        rdi_prereqs = report_generator._determine_prerequisites(
            ComplianceIssueType.RDI_VIOLATION, IssueSeverity.CRITICAL
        )
        assert "Review requirements documentation" in rdi_prereqs
        assert "Coordinate with team lead before implementation" in rdi_prereqs
        
        rm_prereqs = report_generator._determine_prerequisites(
            ComplianceIssueType.RM_NON_COMPLIANCE, IssueSeverity.LOW
        )
        assert "Review RM interface specifications" in rm_prereqs
        assert "Coordinate with team lead before implementation" not in rm_prereqs
    
    def test_validation_criteria_generation(self, report_generator):
        """Test validation criteria generation."""
        test_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.HIGH,
                description="Test failure"
            )
        ]
        
        criteria = report_generator._generate_validation_criteria(
            ComplianceIssueType.TEST_FAILURE, test_issues
        )
        
        assert "All failing tests pass" in criteria
        assert "Test coverage meets or exceeds baseline" in criteria
        assert "No new test failures introduced" in criteria
    
    def test_next_actions_generation(self, report_generator, sample_analysis_result):
        """Test next actions generation."""
        actions = report_generator._generate_next_actions(sample_analysis_result)
        
        assert len(actions) > 0
        assert len(actions) <= 5  # Should limit to top 5
        
        # Should include actions for low compliance score and failing tests
        action_text = " ".join(actions)
        assert "critical compliance issues" in action_text or "test coverage" in action_text
    
    def test_readiness_recommendations(self, report_generator):
        """Test readiness recommendations generation."""
        readiness_factors = {
            "rdi_compliance": {"status": "FAIL"},
            "rm_compliance": {"status": "PASS"},
            "test_coverage": {"status": "FAIL"},
            "blocking_issues": {"status": "FAIL"}
        }
        
        recommendations = report_generator._generate_readiness_recommendations(readiness_factors)
        
        assert len(recommendations) > 0
        rec_text = " ".join(recommendations)
        assert "RDI compliance" in rec_text
        assert "test coverage" in rec_text
        assert "blocking issues" in rec_text
    
    def test_report_formatting_sections(self, report_generator, sample_analysis_result):
        """Test that all report sections are properly formatted."""
        report = report_generator.generate_report(sample_analysis_result)
        
        # Test markdown formatting
        assert report.count("# ") >= 1  # Main title
        assert report.count("## ") >= 4  # Main sections
        assert report.count("### ") >= 2  # Subsections
        assert "**Report ID:**" in report
        assert "**Generated:**" in report
        
        # Test that severity emojis are used in readiness assessment
        assert "✅" in report or "❌" in report
    
    def test_phase3_ready_scenario(self, report_generator):
        """Test report generation when system is Phase 3 ready."""
        # Create a "ready" analysis result
        ready_result = ComplianceAnalysisResult(
            analysis_timestamp=datetime.now(),
            commits_analyzed=[],
            rdi_compliance=RDIComplianceStatus(
                requirements_traced=True,
                design_aligned=True,
                implementation_complete=True,
                test_coverage_adequate=True,
                compliance_score=95.0,
                issues=[]
            ),
            rm_compliance=RMComplianceStatus(
                interface_implemented=True,
                size_constraints_met=True,
                health_monitoring_present=True,
                registry_integrated=True,
                compliance_score=90.0,
                issues=[]
            ),
            test_coverage_status=TestCoverageStatus(
                current_coverage=98.0,
                baseline_coverage=96.7,
                coverage_adequate=True,
                failing_tests=[],
                missing_tests=[],
                issues=[]
            ),
            task_completion_reconciliation=TaskReconciliationStatus(
                reconciliation_score=100.0,
                issues=[]
            ),
            overall_compliance_score=95.0,
            critical_issues=[],
            recommendations=[],
            phase3_ready=True
        )
        
        report = report_generator.generate_report(ready_result)
        
        assert "Phase 3 Readiness:** READY" in report
        assert "✅ YES" in report
        assert "Proceed with Phase 3 planning" in report
    
    def test_empty_analysis_result(self, report_generator):
        """Test report generation with minimal/empty analysis result."""
        empty_result = ComplianceAnalysisResult()
        
        report = report_generator.generate_report(empty_result)
        
        # Should still generate a valid report structure
        assert "# Beast Mode Framework Compliance Report" in report
        assert "## Executive Summary" in report
        assert "Overall Compliance Score:** 0.0/100.0" in report
        assert "Phase 3 Readiness:** NOT READY" in report
    
    @pytest.mark.parametrize("severity,expected_weight", [
        (IssueSeverity.CRITICAL, 4.0),
        (IssueSeverity.HIGH, 3.0),
        (IssueSeverity.MEDIUM, 2.0),
        (IssueSeverity.LOW, 1.0)
    ])
    def test_severity_weights(self, report_generator, severity, expected_weight):
        """Test that severity weights are correctly configured."""
        assert report_generator.severity_weights[severity] == expected_weight
    
    def test_report_generator_implements_interface(self, report_generator):
        """Test that ReportGenerator properly implements ComplianceReporter interface."""
        from src.beast_mode.compliance.interfaces import ComplianceReporter
        
        assert isinstance(report_generator, ComplianceReporter)
        
        # Test interface methods
        sample_result = ComplianceAnalysisResult()
        report = report_generator.generate_report(sample_result)
        assert isinstance(report, str)
        
        format_type = report_generator.get_report_format()
        assert isinstance(format_type, str)
        assert format_type == "markdown"