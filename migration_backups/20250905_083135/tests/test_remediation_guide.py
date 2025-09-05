"""
Unit tests for the RemediationGuide class.

Tests specific remediation step generation for identified compliance issues,
including specialized guidance for the 7 failing tests from Phase 2.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.compliance.reporting.remediation_guide import (
    RemediationGuide,
    RemediationTemplate,
    RemediationCategory,
    FailingTestRemediation
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
    RemediationStep
)


class TestRemediationGuide:
    """Test suite for RemediationGuide class."""
    
    @pytest.fixture
    def remediation_guide(self):
        """Create a RemediationGuide instance for testing."""
        return RemediationGuide()
    
    @pytest.fixture
    def sample_rdi_issue(self):
        """Create a sample RDI compliance issue."""
        return ComplianceIssue(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            description="Missing requirement traceability for authentication module",
            affected_files=["src/auth/login.py", "src/auth/validator.py"],
            remediation_steps=[],
            estimated_effort="medium",
            blocking_merge=True
        )
    
    @pytest.fixture
    def sample_rm_issue(self):
        """Create a sample RM compliance issue."""
        return ComplianceIssue(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.CRITICAL,
            description="Missing RM interface implementation",
            affected_files=["src/modules/user_manager.py"],
            remediation_steps=[],
            estimated_effort="high",
            blocking_merge=True
        )
    
    @pytest.fixture
    def sample_test_issue(self):
        """Create a sample test failure issue."""
        return ComplianceIssue(
            issue_type=ComplianceIssueType.TEST_FAILURE,
            severity=IssueSeverity.HIGH,
            description="Test failure in authentication validation",
            affected_files=["tests/test_auth.py"],
            remediation_steps=[],
            estimated_effort="medium",
            blocking_merge=False
        )
    
    @pytest.fixture
    def sample_analysis_result(self, sample_rdi_issue, sample_rm_issue, sample_test_issue):
        """Create a sample compliance analysis result."""
        rdi_status = RDIComplianceStatus(
            requirements_traced=False,
            design_aligned=True,
            implementation_complete=True,
            test_coverage_adequate=False,
            compliance_score=65.0,
            issues=[sample_rdi_issue]
        )
        
        rm_status = RMComplianceStatus(
            interface_implemented=False,
            size_constraints_met=True,
            health_monitoring_present=False,
            registry_integrated=False,
            compliance_score=45.0,
            issues=[sample_rm_issue]
        )
        
        test_status = TestCoverageStatus(
            current_coverage=94.5,
            baseline_coverage=96.7,
            coverage_adequate=False,
            failing_tests=["test_auth_validation", "test_login_flow"],
            missing_tests=["test_password_reset"],
            issues=[sample_test_issue]
        )
        
        task_status = TaskReconciliationStatus(
            reconciliation_score=75.0,
            issues=[]
        )
        
        return ComplianceAnalysisResult(
            analysis_timestamp=datetime.now(),
            commits_analyzed=[],
            rdi_compliance=rdi_status,
            rm_compliance=rm_status,
            test_coverage_status=test_status,
            task_completion_reconciliation=task_status,
            overall_compliance_score=58.5,
            critical_issues=[],
            recommendations=[],
            phase3_ready=False
        )
    
    def test_remediation_guide_initialization(self, remediation_guide):
        """Test RemediationGuide initialization."""
        assert len(remediation_guide.remediation_templates) > 0
        assert len(remediation_guide.phase2_failing_tests) == 7  # 7 known failing tests
        assert len(remediation_guide.common_patterns) > 0
        
        # Check that all expected templates are present
        expected_templates = [
            "rdi_missing_traceability",
            "rdi_design_misalignment", 
            "rm_interface_missing",
            "rm_size_violation",
            "test_failure_generic"
        ]
        
        for template_name in expected_templates:
            assert template_name in remediation_guide.remediation_templates
    
    def test_phase2_failing_tests_initialization(self, remediation_guide):
        """Test that Phase 2 failing tests are properly initialized."""
        expected_tests = [
            "test_auth_validation",
            "test_login_flow", 
            "test_data_validation",
            "test_rm_interface",
            "test_coverage_calculation",
            "test_dependency_resolution",
            "test_health_monitoring"
        ]
        
        for test_name in expected_tests:
            assert test_name in remediation_guide.phase2_failing_tests
            
        # Check structure of a specific test remediation
        auth_test = remediation_guide.phase2_failing_tests["test_auth_validation"]
        assert isinstance(auth_test, FailingTestRemediation)
        assert auth_test.test_name == "test_auth_validation"
        assert len(auth_test.remediation_steps) > 0
        assert len(auth_test.affected_components) > 0
        assert auth_test.priority in [IssueSeverity.CRITICAL, IssueSeverity.HIGH, IssueSeverity.MEDIUM]
    
    def test_generate_remediation_guide_structure(self, remediation_guide, sample_analysis_result):
        """Test that generate_remediation_guide returns proper structure."""
        guide = remediation_guide.generate_remediation_guide(sample_analysis_result)
        
        # Check all expected sections are present
        expected_sections = [
            "summary",
            "categorized_issues",
            "remediation_steps",
            "test_failure_remediations",
            "implementation_roadmap",
            "effort_analysis",
            "success_criteria",
            "monitoring_plan"
        ]
        
        for section in expected_sections:
            assert section in guide
        
        # Check summary structure
        summary = guide["summary"]
        assert "total_issues" in summary
        assert "total_remediation_steps" in summary
        assert "estimated_completion" in summary
        
        # Check roadmap structure
        roadmap = guide["implementation_roadmap"]
        assert "phase_1_critical" in roadmap
        assert "phase_2_high_priority" in roadmap
        assert "phase_3_medium_priority" in roadmap
        assert "phase_4_low_priority" in roadmap
    
    def test_generate_specific_remediation_rdi_issue(self, remediation_guide, sample_rdi_issue):
        """Test specific remediation generation for RDI issues."""
        remediation = remediation_guide.generate_specific_remediation(sample_rdi_issue)
        
        assert isinstance(remediation, RemediationStep)
        assert remediation.priority == sample_rdi_issue.severity
        assert len(remediation.affected_components) > 0
        assert len(remediation.validation_criteria) > 0
        assert "traceability" in remediation.description.lower()
    
    def test_generate_specific_remediation_rm_issue(self, remediation_guide, sample_rm_issue):
        """Test specific remediation generation for RM issues."""
        remediation = remediation_guide.generate_specific_remediation(sample_rm_issue)
        
        assert isinstance(remediation, RemediationStep)
        assert remediation.priority == sample_rm_issue.severity
        assert "interface" in remediation.description.lower()
        assert "get_module_status" in " ".join(remediation.validation_criteria).lower() or \
               "interface" in " ".join(remediation.validation_criteria).lower()
    
    def test_generate_specific_remediation_test_issue(self, remediation_guide, sample_test_issue):
        """Test specific remediation generation for test issues."""
        remediation = remediation_guide.generate_specific_remediation(sample_test_issue)
        
        assert isinstance(remediation, RemediationStep)
        assert remediation.priority == sample_test_issue.severity
        assert "test" in remediation.description.lower()
    
    def test_get_phase2_test_remediations(self, remediation_guide):
        """Test retrieval of Phase 2 test remediations."""
        remediations = remediation_guide.get_phase2_test_remediations()
        
        assert len(remediations) == 7
        assert all(isinstance(r, FailingTestRemediation) for r in remediations)
        
        # Check that critical tests are included
        test_names = [r.test_name for r in remediations]
        assert "test_auth_validation" in test_names
        assert "test_login_flow" in test_names
        assert "test_rm_interface" in test_names
    
    def test_issue_categorization(self, remediation_guide):
        """Test issue categorization by remediation type."""
        issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.TEST_FAILURE,
                severity=IssueSeverity.HIGH,
                description="Test failure",
                affected_files=["test.py"]
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.CRITICAL,
                description="Missing interface implementation",
                affected_files=["module.py"]
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.MEDIUM,
                description="Missing traceability documentation",
                affected_files=["component.py"]
            )
        ]
        
        categorized = remediation_guide._categorize_issues(issues)
        
        assert RemediationCategory.TESTING in categorized
        assert RemediationCategory.ARCHITECTURE in categorized
        assert RemediationCategory.DOCUMENTATION in categorized
        
        assert len(categorized[RemediationCategory.TESTING]) == 1
        assert len(categorized[RemediationCategory.ARCHITECTURE]) == 1
        assert len(categorized[RemediationCategory.DOCUMENTATION]) == 1
    
    def test_remediation_category_determination(self, remediation_guide):
        """Test determination of remediation categories."""
        test_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.TEST_FAILURE,
            severity=IssueSeverity.HIGH,
            description="Test failure",
            affected_files=[]
        )
        assert remediation_guide._determine_remediation_category(test_issue) == RemediationCategory.TESTING
        
        rm_interface_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.CRITICAL,
            description="Missing interface implementation",
            affected_files=[]
        )
        assert remediation_guide._determine_remediation_category(rm_interface_issue) == RemediationCategory.ARCHITECTURE
        
        rm_size_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.MEDIUM,
            description="Module size exceeds limit",
            affected_files=[]
        )
        assert remediation_guide._determine_remediation_category(rm_size_issue) == RemediationCategory.REFACTORING
        
        rdi_traceability_issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            description="Missing requirement traceability",
            affected_files=[]
        )
        assert remediation_guide._determine_remediation_category(rdi_traceability_issue) == RemediationCategory.DOCUMENTATION
    
    def test_test_failure_remediations_generation(self, remediation_guide):
        """Test generation of test failure remediations."""
        failing_tests = ["test_auth_validation", "test_unknown_test", "test_login_flow"]
        
        remediations = remediation_guide._generate_test_failure_remediations(failing_tests)
        
        assert len(remediations) == 3
        
        # Check known tests have specific remediations
        auth_remediation = next(r for r in remediations if r.test_name == "test_auth_validation")
        assert "Authentication validation logic" in auth_remediation.failure_reason
        assert len(auth_remediation.remediation_steps) > 0
        
        # Check unknown test has generic remediation
        unknown_remediation = next(r for r in remediations if r.test_name == "test_unknown_test")
        assert "requires investigation" in unknown_remediation.failure_reason
        assert len(unknown_remediation.remediation_steps) > 0
    
    def test_implementation_roadmap_creation(self, remediation_guide):
        """Test creation of implementation roadmap."""
        remediation_steps = [
            RemediationStep(
                step_id="REM-001",
                description="Critical fix",
                priority=IssueSeverity.CRITICAL,
                estimated_effort="high",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            ),
            RemediationStep(
                step_id="REM-002", 
                description="High priority fix",
                priority=IssueSeverity.HIGH,
                estimated_effort="medium",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            ),
            RemediationStep(
                step_id="REM-003",
                description="Medium priority fix", 
                priority=IssueSeverity.MEDIUM,
                estimated_effort="low",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            )
        ]
        
        test_remediations = [
            FailingTestRemediation(
                test_name="test_critical",
                failure_reason="Critical failure",
                remediation_steps=[],
                affected_components=[],
                estimated_effort="high",
                priority=IssueSeverity.CRITICAL
            )
        ]
        
        roadmap = remediation_guide._create_implementation_roadmap(remediation_steps, test_remediations)
        
        assert "phase_1_critical" in roadmap
        assert "phase_2_high_priority" in roadmap
        assert "phase_3_medium_priority" in roadmap
        assert "phase_4_low_priority" in roadmap
        
        # Check critical phase has critical items
        phase1 = roadmap["phase_1_critical"]
        assert len(phase1["remediation_steps"]) == 1
        assert len(phase1["test_remediations"]) == 1
        assert phase1["remediation_steps"][0].priority == IssueSeverity.CRITICAL
    
    def test_effort_analysis(self, remediation_guide):
        """Test effort analysis for remediation."""
        remediation_steps = [
            RemediationStep(
                step_id="REM-001",
                description="High effort task",
                priority=IssueSeverity.HIGH,
                estimated_effort="high",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            ),
            RemediationStep(
                step_id="REM-002",
                description="Medium effort task",
                priority=IssueSeverity.MEDIUM,
                estimated_effort="medium",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            )
        ]
        
        test_remediations = [
            FailingTestRemediation(
                test_name="test_1",
                failure_reason="Test failure",
                remediation_steps=[],
                affected_components=[],
                estimated_effort="medium",
                priority=IssueSeverity.HIGH
            )
        ]
        
        effort_analysis = remediation_guide._analyze_remediation_effort(remediation_steps, test_remediations)
        
        assert "total_effort_points" in effort_analysis
        assert "estimated_duration" in effort_analysis
        assert "effort_by_category" in effort_analysis
        assert "test_remediation_effort" in effort_analysis
        assert "resource_requirements" in effort_analysis
        assert "risk_factors" in effort_analysis
        
        # Check that effort points are calculated correctly
        # high=8, medium=4, medium=4 = 16 total
        assert effort_analysis["total_effort_points"] == 16
    
    def test_success_criteria_definition(self, remediation_guide, sample_analysis_result):
        """Test definition of success criteria."""
        criteria = remediation_guide._define_success_criteria(sample_analysis_result)
        
        assert len(criteria) > 0
        assert any("compliance score" in c.lower() for c in criteria)
        assert any("test coverage" in c.lower() for c in criteria)
        assert any("failing tests" in c.lower() for c in criteria)
        assert any("phase 3 readiness" in c.lower() for c in criteria)
    
    def test_monitoring_plan_creation(self, remediation_guide, sample_analysis_result):
        """Test creation of monitoring plan."""
        monitoring_plan = remediation_guide._create_monitoring_plan(sample_analysis_result)
        
        expected_sections = ["daily_checks", "weekly_reviews", "success_metrics", "escalation_triggers"]
        for section in expected_sections:
            assert section in monitoring_plan
            assert len(monitoring_plan[section]) > 0
        
        # Check that monitoring includes key metrics
        metrics = monitoring_plan["success_metrics"]
        assert any("compliance score" in m.lower() for m in metrics)
        assert any("test coverage" in m.lower() for m in metrics)
    
    def test_template_application(self, remediation_guide):
        """Test application of remediation templates."""
        template = RemediationTemplate(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            category=RemediationCategory.DOCUMENTATION,
            title_template="Fix {component} traceability",
            description_template="Add traceability for {component}",
            steps_template=["Step 1", "Step 2"],
            prerequisites=["Prereq 1"],
            validation_criteria=["Criteria 1"],
            estimated_effort="medium"
        )
        
        issue = ComplianceIssue(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            description="Missing traceability",
            affected_files=["src/auth/login.py"]
        )
        
        remediation = remediation_guide._apply_template(template, issue)
        
        assert isinstance(remediation, RemediationStep)
        assert "login" in remediation.description
        assert remediation.priority == IssueSeverity.HIGH
        assert remediation.estimated_effort == "medium"
        assert len(remediation.prerequisites) > 0
        assert len(remediation.validation_criteria) > 0
    
    def test_component_name_extraction(self, remediation_guide):
        """Test extraction of component names from file paths."""
        # Test with full path
        assert remediation_guide._extract_component_name(["src/auth/login.py"]) == "login"
        
        # Test with simple filename
        assert remediation_guide._extract_component_name(["validator.py"]) == "validator"
        
        # Test with empty list
        assert remediation_guide._extract_component_name([]) == "component"
        
        # Test with multiple files (should use first)
        assert remediation_guide._extract_component_name(["src/auth/login.py", "src/auth/validator.py"]) == "login"
    
    def test_severity_weight_calculation(self, remediation_guide):
        """Test severity weight calculation."""
        assert remediation_guide._get_severity_weight(IssueSeverity.CRITICAL) == 4
        assert remediation_guide._get_severity_weight(IssueSeverity.HIGH) == 3
        assert remediation_guide._get_severity_weight(IssueSeverity.MEDIUM) == 2
        assert remediation_guide._get_severity_weight(IssueSeverity.LOW) == 1
    
    def test_effort_to_duration_conversion(self, remediation_guide):
        """Test conversion of effort points to duration estimates."""
        assert "1-2 days" in remediation_guide._convert_effort_to_duration(8)
        assert "3-5 days" in remediation_guide._convert_effort_to_duration(16)
        assert "1-2 weeks" in remediation_guide._convert_effort_to_duration(32)
        assert "2-4 weeks" in remediation_guide._convert_effort_to_duration(64)
        assert "1-2 months" in remediation_guide._convert_effort_to_duration(128)
    
    def test_resource_requirements_estimation(self, remediation_guide):
        """Test estimation of resource requirements."""
        # Small effort
        small_resources = remediation_guide._estimate_resource_requirements(8)
        assert "1-2 developers" in small_resources["team_size"]
        
        # Medium effort
        medium_resources = remediation_guide._estimate_resource_requirements(24)
        assert "2-3 developers" in medium_resources["team_size"]
        
        # Large effort
        large_resources = remediation_guide._estimate_resource_requirements(64)
        assert "3-4 developers" in large_resources["team_size"]
    
    def test_risk_factor_identification(self, remediation_guide):
        """Test identification of risk factors."""
        # Create scenario with many critical issues
        critical_steps = [
            RemediationStep(
                step_id=f"REM-{i:03d}",
                description=f"Critical step {i}",
                priority=IssueSeverity.CRITICAL,
                estimated_effort="high",
                affected_components=[f"component{i}.py"],
                prerequisites=[],
                validation_criteria=[]
            )
            for i in range(6)  # More than 5 critical issues
        ]
        
        test_remediations = [
            FailingTestRemediation(
                test_name=f"test_{i}",
                failure_reason="Test failure",
                remediation_steps=[],
                affected_components=[],
                estimated_effort="medium",
                priority=IssueSeverity.HIGH
            )
            for i in range(6)  # More than 5 failing tests
        ]
        
        risks = remediation_guide._identify_risk_factors(critical_steps, test_remediations)
        
        assert len(risks) > 0
        risk_text = " ".join(risks).lower()
        assert "critical issues" in risk_text or "failing tests" in risk_text
    
    def test_success_probability_estimation(self, remediation_guide):
        """Test estimation of success probability."""
        # High probability scenario (no critical issues, few high-effort steps)
        low_risk_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.MEDIUM,
                description="Minor issue",
                affected_files=[]
            )
        ]
        
        low_risk_steps = [
            RemediationStep(
                step_id="REM-001",
                description="Easy fix",
                priority=IssueSeverity.MEDIUM,
                estimated_effort="low",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            )
        ]
        
        probability = remediation_guide._estimate_success_probability(low_risk_issues, low_risk_steps)
        assert "High" in probability
        
        # Low probability scenario (many critical issues, many high-effort steps)
        high_risk_issues = [
            ComplianceIssue(
                issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
                severity=IssueSeverity.CRITICAL,
                description="Critical issue",
                affected_files=[]
            )
            for _ in range(6)
        ]
        
        high_risk_steps = [
            RemediationStep(
                step_id=f"REM-{i:03d}",
                description="Hard fix",
                priority=IssueSeverity.CRITICAL,
                estimated_effort="high",
                affected_components=[],
                prerequisites=[],
                validation_criteria=[]
            )
            for i in range(12)
        ]
        
        probability = remediation_guide._estimate_success_probability(high_risk_issues, high_risk_steps)
        assert "Low" in probability or "Medium" in probability
    
    def test_issue_deduplication(self, remediation_guide):
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
            ),
            ComplianceIssue(
                issue_type=ComplianceIssueType.RDI_VIOLATION,
                severity=IssueSeverity.HIGH,
                description="Different issue",
                affected_files=["file1.py"]
            )
        ]
        
        # Create analysis result with duplicate issues
        analysis_result = ComplianceAnalysisResult(
            rdi_compliance=RDIComplianceStatus(issues=duplicate_issues),
            rm_compliance=RMComplianceStatus(issues=[]),
            test_coverage_status=TestCoverageStatus(issues=[]),
            task_completion_reconciliation=TaskReconciliationStatus(issues=[]),
            critical_issues=[]
        )
        
        unique_issues = remediation_guide._collect_all_issues(analysis_result)
        
        # Should have 2 unique issues (duplicates removed)
        assert len(unique_issues) == 2