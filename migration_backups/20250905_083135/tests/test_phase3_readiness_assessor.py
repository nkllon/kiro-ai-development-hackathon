"""
Unit tests for the Phase3ReadinessAssessor class.

Tests Phase 3 readiness scoring based on compliance analysis results,
blocking issues identification, and readiness assessment accuracy.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.compliance.reporting.phase3_readiness_assessor import (
    Phase3ReadinessAssessor,
    ReadinessStatus,
    ReadinessCriteria,
    ReadinessMetric,
    Phase3ReadinessReport
)
from src.beast_mode.compliance.models import (
    ComplianceAnalysisResult,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity,
    RDIComplianceStatus,
    RMComplianceStatus,
    TestCoverageStatus,
    TaskReconciliationStatus
)


class TestPhase3ReadinessAssessor:
    """Test suite for Phase3ReadinessAssessor class."""
    
    @pytest.fixture
    def readiness_assessor(self):
        """Create a Phase3ReadinessAssessor instance for testing."""
        return Phase3ReadinessAssessor()
    
    @pytest.fixture
    def ready_analysis_result(self):
        """Create an analysis result that should be ready for Phase 3."""
        return ComplianceAnalysisResult(
            analysis_timestamp=datetime.now(),
            commits_analyzed=[],
            rdi_compliance=RDIComplianceStatus(
                requirements_traced=True,
                design_aligned=True,
                implementation_complete=True,
                test_coverage_adequate=True,
                compliance_score=90.0,
                issues=[]
            ),
            rm_compliance=RMComplianceStatus(
                interface_implemented=True,
                size_constraints_met=True,
                health_monitoring_present=True,
                registry_integrated=True,
                compliance_score=85.0,
                issues=[]
            ),
            test_coverage_status=TestCoverageStatus(
                current_coverage=97.5,
                baseline_coverage=96.7,
                coverage_adequate=True,
                failing_tests=[],
                missing_tests=[],
                issues=[]
            ),
            task_completion_reconciliation=TaskReconciliationStatus(
                claimed_complete_tasks=["Task 1", "Task 2"],
                actually_implemented_tasks=["Task 1", "Task 2"],
                missing_implementations=[],
                reconciliation_score=100.0,
                issues=[]
            ),
            overall_compliance_score=90.0,
            critical_issues=[],
            recommendations=[],
            phase3_ready=True
        )
    
    @pytest.fixture
    def not_ready_analysis_result(self):
        """Create an analysis result that should not be ready for Phase 3."""
        blocking_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.CRITICAL,
            description="Critical RM interface missing",
            affected_files=["src/module.py"],
            blocking_merge=True
        )
        
        return ComplianceAnalysisResult(
            analysis_timestamp=datetime.now(),
            commits_analyzed=[],
            rdi_compliance=RDIComplianceStatus(
                requirements_traced=False,
                design_aligned=True,
                implementation_complete=False,
                test_coverage_adequate=False,
                compliance_score=45.0,
                issues=[]
            ),
            rm_compliance=RMComplianceStatus(
                interface_implemented=False,
                size_constraints_met=True,
                health_monitoring_present=False,
                registry_integrated=False,
                compliance_score=30.0,
                issues=[blocking_issue]
            ),
            test_coverage_status=TestCoverageStatus(
                current_coverage=85.0,
                baseline_coverage=96.7,
                coverage_adequate=False,
                failing_tests=["test_auth", "test_login", "test_validation"],
                missing_tests=["test_security"],
                issues=[]
            ),
            task_completion_reconciliation=TaskReconciliationStatus(
                claimed_complete_tasks=["Task 1", "Task 2", "Task 3"],
                actually_implemented_tasks=["Task 1"],
                missing_implementations=["Task 2", "Task 3"],
                reconciliation_score=33.0,
                issues=[]
            ),
            overall_compliance_score=40.0,
            critical_issues=[blocking_issue],
            recommendations=[],
            phase3_ready=False
        )
    
    @pytest.fixture
    def conditionally_ready_analysis_result(self):
        """Create an analysis result that should be conditionally ready for Phase 3."""
        return ComplianceAnalysisResult(
            analysis_timestamp=datetime.now(),
            commits_analyzed=[],
            rdi_compliance=RDIComplianceStatus(
                requirements_traced=True,
                design_aligned=True,
                implementation_complete=True,
                test_coverage_adequate=False,
                compliance_score=82.0,
                issues=[]
            ),
            rm_compliance=RMComplianceStatus(
                interface_implemented=True,
                size_constraints_met=True,
                health_monitoring_present=False,  # Minor issue
                registry_integrated=True,
                compliance_score=78.0,
                issues=[]
            ),
            test_coverage_status=TestCoverageStatus(
                current_coverage=95.0,  # Slightly below baseline
                baseline_coverage=96.7,
                coverage_adequate=False,
                failing_tests=["test_minor_issue"],
                missing_tests=[],
                issues=[]
            ),
            task_completion_reconciliation=TaskReconciliationStatus(
                reconciliation_score=92.0,
                issues=[]
            ),
            overall_compliance_score=82.0,
            critical_issues=[],
            recommendations=[],
            phase3_ready=False
        )
    
    def test_assessor_initialization(self, readiness_assessor):
        """Test Phase3ReadinessAssessor initialization."""
        assert len(readiness_assessor.readiness_thresholds) == 6
        assert len(readiness_assessor.criteria_weights) == 6
        assert len(readiness_assessor.blocking_issue_types) > 0
        
        # Check threshold values
        assert readiness_assessor.readiness_thresholds[ReadinessCriteria.RDI_COMPLIANCE] == 80.0
        assert readiness_assessor.readiness_thresholds[ReadinessCriteria.RM_COMPLIANCE] == 80.0
        assert readiness_assessor.readiness_thresholds[ReadinessCriteria.TEST_COVERAGE] == 96.7
        
        # Check weights sum to 1.0
        total_weight = sum(readiness_assessor.criteria_weights.values())
        assert abs(total_weight - 1.0) < 0.01
    
    def test_assess_phase3_readiness_ready_scenario(self, readiness_assessor, ready_analysis_result):
        """Test Phase 3 readiness assessment for ready scenario."""
        report = readiness_assessor.assess_phase3_readiness(ready_analysis_result)
        
        assert isinstance(report, Phase3ReadinessReport)
        assert report.overall_readiness_status == ReadinessStatus.READY
        assert report.overall_readiness_score >= 85.0
        assert len(report.blocking_issues) == 0
        assert report.go_no_go_decision["decision"] == "GO"
        assert "Ready now" in report.estimated_time_to_ready or "now" in report.estimated_time_to_ready.lower()
    
    def test_assess_phase3_readiness_not_ready_scenario(self, readiness_assessor, not_ready_analysis_result):
        """Test Phase 3 readiness assessment for not ready scenario."""
        report = readiness_assessor.assess_phase3_readiness(not_ready_analysis_result)
        
        assert isinstance(report, Phase3ReadinessReport)
        assert report.overall_readiness_status in [ReadinessStatus.NOT_READY, ReadinessStatus.BLOCKED]
        assert report.overall_readiness_score < 80.0
        assert len(report.blocking_issues) > 0
        assert report.go_no_go_decision["decision"] == "NO GO"
        assert "days" in report.estimated_time_to_ready or "weeks" in report.estimated_time_to_ready
    
    def test_assess_phase3_readiness_conditional_scenario(self, readiness_assessor, conditionally_ready_analysis_result):
        """Test Phase 3 readiness assessment for conditionally ready scenario."""
        report = readiness_assessor.assess_phase3_readiness(conditionally_ready_analysis_result)
        
        assert isinstance(report, Phase3ReadinessReport)
        assert report.overall_readiness_status in [ReadinessStatus.CONDITIONALLY_READY, ReadinessStatus.READY]
        assert len(report.conditional_requirements) > 0
        assert report.go_no_go_decision["decision"] in ["CONDITIONAL GO", "GO"]
    
    def test_get_readiness_summary(self, readiness_assessor, ready_analysis_result):
        """Test readiness summary generation."""
        summary = readiness_assessor.get_readiness_summary(ready_analysis_result)
        
        expected_keys = [
            "readiness_status", "readiness_score", "blocking_issues_count",
            "critical_blockers", "ready_for_phase3", "key_metrics"
        ]
        
        for key in expected_keys:
            assert key in summary
        
        assert summary["readiness_status"] == ReadinessStatus.READY.value
        assert summary["ready_for_phase3"] is True
        assert summary["blocking_issues_count"] == 0
        assert len(summary["key_metrics"]) == 6
    
    def test_evaluate_rdi_compliance_metric_ready(self, readiness_assessor):
        """Test RDI compliance metric evaluation for ready status."""
        rdi_status = RDIComplianceStatus(
            requirements_traced=True,
            design_aligned=True,
            implementation_complete=True,
            test_coverage_adequate=True,
            compliance_score=85.0,
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_rdi_compliance_metric(rdi_status)
        
        assert isinstance(metric, ReadinessMetric)
        assert metric.criteria == ReadinessCriteria.RDI_COMPLIANCE
        assert metric.status == ReadinessStatus.READY
        assert metric.current_value == 85.0
        assert metric.required_value == 80.0
        assert len(metric.blocking_issues) == 0
    
    def test_evaluate_rdi_compliance_metric_not_ready(self, readiness_assessor):
        """Test RDI compliance metric evaluation for not ready status."""
        rdi_status = RDIComplianceStatus(
            requirements_traced=False,
            design_aligned=False,
            implementation_complete=False,
            test_coverage_adequate=False,
            compliance_score=45.0,
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_rdi_compliance_metric(rdi_status)
        
        assert metric.status == ReadinessStatus.NOT_READY
        assert metric.current_value == 45.0
        assert len(metric.blocking_issues) > 0
        assert len(metric.recommendations) > 0
        
        # Check specific blocking issues
        blocking_text = " ".join(metric.blocking_issues).lower()
        assert "traceability" in blocking_text
        assert "alignment" in blocking_text
        assert "implementation" in blocking_text
    
    def test_evaluate_rm_compliance_metric_ready(self, readiness_assessor):
        """Test RM compliance metric evaluation for ready status."""
        rm_status = RMComplianceStatus(
            interface_implemented=True,
            size_constraints_met=True,
            health_monitoring_present=True,
            registry_integrated=True,
            compliance_score=85.0,
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_rm_compliance_metric(rm_status)
        
        assert metric.criteria == ReadinessCriteria.RM_COMPLIANCE
        assert metric.status == ReadinessStatus.READY
        assert len(metric.blocking_issues) == 0
    
    def test_evaluate_rm_compliance_metric_not_ready(self, readiness_assessor):
        """Test RM compliance metric evaluation for not ready status."""
        rm_status = RMComplianceStatus(
            interface_implemented=False,
            size_constraints_met=False,
            health_monitoring_present=False,
            registry_integrated=False,
            compliance_score=30.0,
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_rm_compliance_metric(rm_status)
        
        assert metric.status == ReadinessStatus.NOT_READY
        assert len(metric.blocking_issues) == 4  # All RM aspects failing
        assert len(metric.recommendations) == 4
        
        blocking_text = " ".join(metric.blocking_issues).lower()
        assert "interface" in blocking_text
        assert "size" in blocking_text
        assert "health" in blocking_text
        assert "registry" in blocking_text
    
    def test_evaluate_test_coverage_metric_ready(self, readiness_assessor):
        """Test test coverage metric evaluation for ready status."""
        test_status = TestCoverageStatus(
            current_coverage=98.0,
            baseline_coverage=96.7,
            coverage_adequate=True,
            failing_tests=[],
            missing_tests=[],
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_test_coverage_metric(test_status)
        
        assert metric.criteria == ReadinessCriteria.TEST_COVERAGE
        assert metric.status == ReadinessStatus.READY
        assert metric.current_value == 98.0
        assert metric.required_value == 96.7
        assert len(metric.blocking_issues) == 0
    
    def test_evaluate_test_coverage_metric_not_ready(self, readiness_assessor):
        """Test test coverage metric evaluation for not ready status."""
        test_status = TestCoverageStatus(
            current_coverage=85.0,
            baseline_coverage=96.7,
            coverage_adequate=False,
            failing_tests=["test1", "test2", "test3"],
            missing_tests=["test4"],
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_test_coverage_metric(test_status)
        
        assert metric.status == ReadinessStatus.NOT_READY
        assert len(metric.blocking_issues) >= 2  # Failing tests and coverage
        assert len(metric.recommendations) >= 2
        
        blocking_text = " ".join(metric.blocking_issues).lower()
        assert "failing tests" in blocking_text
        assert "coverage" in blocking_text
    
    def test_evaluate_blocking_issues_metric_ready(self, readiness_assessor):
        """Test blocking issues metric evaluation for ready status."""
        analysis_result = ComplianceAnalysisResult(
            rdi_compliance=RDIComplianceStatus(issues=[]),
            rm_compliance=RMComplianceStatus(issues=[]),
            test_coverage_status=TestCoverageStatus(issues=[]),
            task_completion_reconciliation=TaskReconciliationStatus(issues=[]),
            critical_issues=[]
        )
        
        metric = readiness_assessor._evaluate_blocking_issues_metric(analysis_result)
        
        assert metric.criteria == ReadinessCriteria.BLOCKING_ISSUES
        assert metric.status == ReadinessStatus.READY
        assert metric.current_value == 0
        assert metric.required_value == 0
    
    def test_evaluate_blocking_issues_metric_blocked(self, readiness_assessor):
        """Test blocking issues metric evaluation for blocked status."""
        blocking_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.CRITICAL,
                description="Critical issue 1",
                blocking_merge=True
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.CRITICAL,
                description="Critical issue 2",
                blocking_merge=True
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.HIGH,
                description="High issue",
                blocking_merge=True
            )
        ]
        
        analysis_result = ComplianceAnalysisResult(
            rdi_compliance=RDIComplianceStatus(issues=[]),
            rm_compliance=RMComplianceStatus(issues=[blocking_issues[0]]),
            test_coverage_status=TestCoverageStatus(issues=[blocking_issues[1]]),
            task_completion_reconciliation=TaskReconciliationStatus(issues=[]),
            critical_issues=[blocking_issues[2]]
        )
        
        metric = readiness_assessor._evaluate_blocking_issues_metric(analysis_result)
        
        assert metric.status == ReadinessStatus.BLOCKED
        assert metric.current_value == 3
        assert len(metric.blocking_issues) > 0
    
    def test_evaluate_task_completion_metric(self, readiness_assessor):
        """Test task completion metric evaluation."""
        # Ready scenario
        ready_task_status = TaskReconciliationStatus(
            claimed_complete_tasks=["Task 1", "Task 2"],
            actually_implemented_tasks=["Task 1", "Task 2"],
            missing_implementations=[],
            reconciliation_score=100.0,
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_task_completion_metric(ready_task_status)
        assert metric.status == ReadinessStatus.READY
        assert len(metric.blocking_issues) == 0
        
        # Not ready scenario
        not_ready_task_status = TaskReconciliationStatus(
            claimed_complete_tasks=["Task 1", "Task 2", "Task 3"],
            actually_implemented_tasks=["Task 1"],
            missing_implementations=["Task 2", "Task 3"],
            reconciliation_score=33.0,
            issues=[]
        )
        
        metric = readiness_assessor._evaluate_task_completion_metric(not_ready_task_status)
        assert metric.status == ReadinessStatus.NOT_READY
        assert len(metric.blocking_issues) > 0
        assert "incomplete tasks" in " ".join(metric.blocking_issues).lower()
    
    def test_evaluate_overall_score_metric(self, readiness_assessor):
        """Test overall score metric evaluation."""
        # Ready scenario
        metric = readiness_assessor._evaluate_overall_score_metric(90.0)
        assert metric.criteria == ReadinessCriteria.OVERALL_SCORE
        assert metric.status == ReadinessStatus.READY
        assert metric.current_value == 90.0
        
        # Not ready scenario
        metric = readiness_assessor._evaluate_overall_score_metric(60.0)
        assert metric.status == ReadinessStatus.NOT_READY
        assert len(metric.recommendations) > 0
    
    def test_calculate_overall_readiness_score(self, readiness_assessor):
        """Test overall readiness score calculation."""
        metrics = [
            ReadinessMetric(
                criteria=ReadinessCriteria.RDI_COMPLIANCE,
                current_value=85.0,
                required_value=80.0,
                weight=0.25,
                status=ReadinessStatus.READY,
                description="Test metric"
            ),
            ReadinessMetric(
                criteria=ReadinessCriteria.RM_COMPLIANCE,
                current_value=75.0,
                required_value=80.0,
                weight=0.25,
                status=ReadinessStatus.CONDITIONALLY_READY,
                description="Test metric"
            ),
            ReadinessMetric(
                criteria=ReadinessCriteria.TEST_COVERAGE,
                current_value=95.0,
                required_value=96.7,
                weight=0.20,
                status=ReadinessStatus.CONDITIONALLY_READY,
                description="Test metric"
            ),
            ReadinessMetric(
                criteria=ReadinessCriteria.BLOCKING_ISSUES,
                current_value=0.0,
                required_value=0.0,
                weight=0.15,
                status=ReadinessStatus.READY,
                description="Test metric"
            ),
            ReadinessMetric(
                criteria=ReadinessCriteria.TASK_COMPLETION,
                current_value=90.0,
                required_value=90.0,
                weight=0.10,
                status=ReadinessStatus.READY,
                description="Test metric"
            ),
            ReadinessMetric(
                criteria=ReadinessCriteria.OVERALL_SCORE,
                current_value=85.0,
                required_value=85.0,
                weight=0.05,
                status=ReadinessStatus.READY,
                description="Test metric"
            )
        ]
        
        score = readiness_assessor._calculate_overall_readiness_score(metrics)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0
        assert score > 70.0  # Should be reasonably high given the metrics
    
    def test_determine_overall_readiness_status(self, readiness_assessor):
        """Test overall readiness status determination."""
        # Ready scenario - all metrics ready
        ready_metrics = [
            ReadinessMetric(ReadinessCriteria.RDI_COMPLIANCE, 85.0, 80.0, 0.25, ReadinessStatus.READY, ""),
            ReadinessMetric(ReadinessCriteria.RM_COMPLIANCE, 85.0, 80.0, 0.25, ReadinessStatus.READY, ""),
            ReadinessMetric(ReadinessCriteria.TEST_COVERAGE, 97.0, 96.7, 0.20, ReadinessStatus.READY, ""),
            ReadinessMetric(ReadinessCriteria.BLOCKING_ISSUES, 0.0, 0.0, 0.15, ReadinessStatus.READY, ""),
            ReadinessMetric(ReadinessCriteria.TASK_COMPLETION, 95.0, 90.0, 0.10, ReadinessStatus.READY, ""),
            ReadinessMetric(ReadinessCriteria.OVERALL_SCORE, 90.0, 85.0, 0.05, ReadinessStatus.READY, "")
        ]
        
        status = readiness_assessor._determine_overall_readiness_status(ready_metrics, 90.0)
        assert status == ReadinessStatus.READY
        
        # Blocked scenario - one metric blocked
        blocked_metrics = ready_metrics.copy()
        blocked_metrics[0] = ReadinessMetric(ReadinessCriteria.RDI_COMPLIANCE, 30.0, 80.0, 0.25, ReadinessStatus.BLOCKED, "")
        
        status = readiness_assessor._determine_overall_readiness_status(blocked_metrics, 60.0)
        assert status == ReadinessStatus.BLOCKED
        
        # Not ready scenario - critical metric not ready
        not_ready_metrics = ready_metrics.copy()
        not_ready_metrics[0] = ReadinessMetric(ReadinessCriteria.RDI_COMPLIANCE, 50.0, 80.0, 0.25, ReadinessStatus.NOT_READY, "")
        
        status = readiness_assessor._determine_overall_readiness_status(not_ready_metrics, 70.0)
        assert status == ReadinessStatus.NOT_READY
    
    def test_identify_blocking_issues(self, readiness_assessor, not_ready_analysis_result):
        """Test identification of blocking issues."""
        blocking_issues = readiness_assessor._identify_blocking_issues(not_ready_analysis_result)
        
        assert len(blocking_issues) > 0
        
        # Should include critical issues
        critical_issues = [i for i in blocking_issues if i.severity == IssueSeverity.CRITICAL]
        assert len(critical_issues) > 0
        
        # Should include issues marked as blocking merge
        merge_blocking = [i for i in blocking_issues if i.blocking_merge]
        assert len(merge_blocking) > 0
        
        # Should be sorted by severity (critical first)
        if len(blocking_issues) > 1:
            for i in range(len(blocking_issues) - 1):
                current_weight = readiness_assessor._get_severity_weight(blocking_issues[i].severity)
                next_weight = readiness_assessor._get_severity_weight(blocking_issues[i + 1].severity)
                assert current_weight >= next_weight
    
    def test_generate_conditional_requirements(self, readiness_assessor):
        """Test generation of conditional requirements."""
        metrics = [
            ReadinessMetric(
                ReadinessCriteria.RDI_COMPLIANCE, 82.0, 80.0, 0.25, 
                ReadinessStatus.CONDITIONALLY_READY, "",
                blocking_issues=["Minor traceability gap"]
            ),
            ReadinessMetric(
                ReadinessCriteria.TEST_COVERAGE, 95.0, 96.7, 0.20,
                ReadinessStatus.CONDITIONALLY_READY, "",
                blocking_issues=["Coverage slightly below baseline"]
            )
        ]
        
        blocking_issues = []
        
        requirements = readiness_assessor._generate_conditional_requirements(metrics, blocking_issues)
        
        assert len(requirements) > 0
        req_text = " ".join(requirements).lower()
        assert "monitor" in req_text
        assert "rdi_compliance" in req_text or "test_coverage" in req_text
    
    def test_generate_readiness_recommendations(self, readiness_assessor):
        """Test generation of readiness recommendations."""
        metrics = [
            ReadinessMetric(
                ReadinessCriteria.RDI_COMPLIANCE, 60.0, 80.0, 0.25,
                ReadinessStatus.NOT_READY, "",
                recommendations=["Complete requirement traceability"]
            ),
            ReadinessMetric(
                ReadinessCriteria.RM_COMPLIANCE, 85.0, 80.0, 0.25,
                ReadinessStatus.READY, "",
                recommendations=[]
            )
        ]
        
        blocking_issues = []
        
        recommendations = readiness_assessor._generate_readiness_recommendations(metrics, blocking_issues)
        
        assert len(recommendations) > 0
        assert len(recommendations) <= 10  # Should limit to top 10
        
        # Should include priority recommendation for highest weight not-ready metric
        assert any("Priority" in rec and "rdi_compliance" in rec for rec in recommendations)
        
        # Should include general recommendations
        rec_text = " ".join(recommendations).lower()
        assert "compliance analysis" in rec_text or "daily" in rec_text
    
    def test_generate_next_steps(self, readiness_assessor):
        """Test generation of next steps."""
        # Ready scenario
        ready_steps = readiness_assessor._generate_next_steps(ReadinessStatus.READY, [])
        assert len(ready_steps) > 0
        steps_text = " ".join(ready_steps).lower()
        assert "phase 3" in steps_text
        assert "proceed" in steps_text or "planning" in steps_text
        
        # Not ready scenario
        not_ready_steps = readiness_assessor._generate_next_steps(ReadinessStatus.NOT_READY, [])
        assert len(not_ready_steps) > 0
        steps_text = " ".join(not_ready_steps).lower()
        assert "remediation" in steps_text or "execute" in steps_text
        
        # Blocked scenario
        blocked_steps = readiness_assessor._generate_next_steps(ReadinessStatus.BLOCKED, [])
        assert len(blocked_steps) > 0
        steps_text = " ".join(blocked_steps).lower()
        assert "stop" in steps_text or "do not proceed" in steps_text
    
    def test_estimate_time_to_ready(self, readiness_assessor):
        """Test estimation of time to ready."""
        # Ready scenario
        ready_metrics = [
            ReadinessMetric(ReadinessCriteria.RDI_COMPLIANCE, 85.0, 80.0, 0.25, ReadinessStatus.READY, "")
        ]
        time_estimate = readiness_assessor._estimate_time_to_ready(ready_metrics, [])
        assert "Ready now" in time_estimate or "now" in time_estimate.lower()
        
        # Not ready scenario with multiple issues
        not_ready_metrics = [
            ReadinessMetric(ReadinessCriteria.RDI_COMPLIANCE, 50.0, 80.0, 0.25, ReadinessStatus.NOT_READY, ""),
            ReadinessMetric(ReadinessCriteria.RM_COMPLIANCE, 40.0, 80.0, 0.25, ReadinessStatus.NOT_READY, "")
        ]
        
        blocking_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.CRITICAL,
                description="Critical issue"
            )
        ]
        
        time_estimate = readiness_assessor._estimate_time_to_ready(not_ready_metrics, blocking_issues)
        assert any(unit in time_estimate for unit in ["days", "weeks", "months"])
    
    def test_perform_risk_assessment(self, readiness_assessor, not_ready_analysis_result):
        """Test risk assessment performance."""
        metrics = [
            ReadinessMetric(ReadinessCriteria.RDI_COMPLIANCE, 50.0, 80.0, 0.25, ReadinessStatus.NOT_READY, "")
        ]
        
        risk_assessment = readiness_assessor._perform_risk_assessment(not_ready_analysis_result, metrics)
        
        expected_keys = ["risk_level", "identified_risks", "mitigation_strategies", "contingency_plans"]
        for key in expected_keys:
            assert key in risk_assessment
        
        assert risk_assessment["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert len(risk_assessment["identified_risks"]) > 0
        assert len(risk_assessment["mitigation_strategies"]) > 0
        assert len(risk_assessment["contingency_plans"]) > 0
    
    def test_make_go_no_go_decision(self, readiness_assessor):
        """Test go/no-go decision making."""
        # GO scenario
        go_decision = readiness_assessor._make_go_no_go_decision(
            ReadinessStatus.READY, [], {"risk_level": "LOW"}
        )
        assert go_decision["decision"] == "GO"
        assert go_decision["confidence"] == "HIGH"
        
        # NO GO scenario
        blocking_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.CRITICAL,
            description="Critical blocker"
        )
        
        no_go_decision = readiness_assessor._make_go_no_go_decision(
            ReadinessStatus.BLOCKED, [blocking_issue], {"risk_level": "HIGH"}
        )
        assert no_go_decision["decision"] == "NO GO"
        assert no_go_decision["confidence"] == "HIGH"
        
        # CONDITIONAL GO scenario
        conditional_decision = readiness_assessor._make_go_no_go_decision(
            ReadinessStatus.CONDITIONALLY_READY, [], {"risk_level": "MEDIUM"}
        )
        assert conditional_decision["decision"] == "CONDITIONAL GO"
        
        # Check decision structure
        expected_keys = ["decision", "confidence", "rationale", "conditions", "review_date"]
        for key in expected_keys:
            assert key in conditional_decision
    
    def test_convert_status_to_score(self, readiness_assessor):
        """Test conversion of readiness status to numeric score."""
        assert readiness_assessor._convert_status_to_score(ReadinessStatus.READY) == 100.0
        assert readiness_assessor._convert_status_to_score(ReadinessStatus.CONDITIONALLY_READY) == 75.0
        assert readiness_assessor._convert_status_to_score(ReadinessStatus.NOT_READY) == 25.0
        assert readiness_assessor._convert_status_to_score(ReadinessStatus.BLOCKED) == 0.0
    
    def test_severity_weight_calculation(self, readiness_assessor):
        """Test severity weight calculation."""
        assert readiness_assessor._get_severity_weight(IssueSeverity.CRITICAL) == 4
        assert readiness_assessor._get_severity_weight(IssueSeverity.HIGH) == 3
        assert readiness_assessor._get_severity_weight(IssueSeverity.MEDIUM) == 2
        assert readiness_assessor._get_severity_weight(IssueSeverity.LOW) == 1
    
    def test_issue_deduplication(self, readiness_assessor):
        """Test that duplicate issues are properly handled."""
        duplicate_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.HIGH,
                description="Same issue",
                affected_files=["file1.py", "file2.py"]
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.HIGH,
                description="Same issue",
                affected_files=["file2.py", "file1.py"]  # Same files, different order
            )
        ]
        
        analysis_result = ComplianceAnalysisResult(
            rdi_compliance=RDIComplianceStatus(issues=duplicate_issues),
            rm_compliance=RMComplianceStatus(issues=[]),
            test_coverage_status=TestCoverageStatus(issues=[]),
            task_completion_reconciliation=TaskReconciliationStatus(issues=[]),
            critical_issues=[]
        )
        
        unique_issues = readiness_assessor._collect_all_issues(analysis_result)
        assert len(unique_issues) == 1  # Duplicates should be removed
    
    @pytest.mark.parametrize("status,expected_decision", [
        (ReadinessStatus.READY, "GO"),
        (ReadinessStatus.CONDITIONALLY_READY, "CONDITIONAL GO"),
        (ReadinessStatus.NOT_READY, "NO GO"),
        (ReadinessStatus.BLOCKED, "NO GO")
    ])
    def test_decision_mapping(self, readiness_assessor, status, expected_decision):
        """Test that readiness status maps to correct go/no-go decision."""
        decision = readiness_assessor._make_go_no_go_decision(status, [], {"risk_level": "LOW"})
        assert expected_decision in decision["decision"]
    
    def test_comprehensive_assessment_flow(self, readiness_assessor, ready_analysis_result):
        """Test the complete assessment flow from analysis to report."""
        report = readiness_assessor.assess_phase3_readiness(ready_analysis_result)
        
        # Verify report completeness
        assert report.assessment_timestamp is not None
        assert report.overall_readiness_status is not None
        assert report.overall_readiness_score >= 0.0
        assert len(report.readiness_metrics) == 6  # All criteria evaluated
        assert report.blocking_issues is not None
        assert report.conditional_requirements is not None
        assert report.recommendations is not None
        assert report.next_steps is not None
        assert report.estimated_time_to_ready is not None
        assert report.risk_assessment is not None
        assert report.go_no_go_decision is not None
        
        # Verify metric completeness
        criteria_covered = {metric.criteria for metric in report.readiness_metrics}
        expected_criteria = set(ReadinessCriteria)
        assert criteria_covered == expected_criteria