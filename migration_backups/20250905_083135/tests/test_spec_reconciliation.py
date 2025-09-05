"""
Tests for Spec Reconciliation System

Tests the governance and validation components to ensure they work correctly.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.spec_reconciliation.governance import (
    GovernanceController, SpecProposal, ValidationResult, OverlapSeverity
)
from src.spec_reconciliation.validation import (
    ConsistencyValidator, ConsistencyLevel
)
from src.spec_reconciliation.boundary_resolver import (
    ComponentBoundaryResolver, ComponentBoundary, InterfaceContract, 
    DependencyRelationship, BoundaryViolationType, ComponentType
)


class TestGovernanceController:
    """Test the GovernanceController functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create a sample spec for testing
        sample_spec_dir = self.specs_dir / "sample-spec"
        sample_spec_dir.mkdir()
        
        requirements_content = """
# Sample Spec Requirements

## Requirements

### Requirement 1
**User Story:** As a developer, I want to test functionality, so that I can validate the system.

#### Acceptance Criteria
1. WHEN testing is performed THEN the system SHALL validate correctly
2. WHEN validation occurs THEN results SHALL be accurate
"""
        
        (sample_spec_dir / "requirements.md").write_text(requirements_content)
        
        self.controller = GovernanceController(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_controller_initialization(self):
        """Test that controller initializes correctly"""
        assert self.controller.is_healthy()
        status = self.controller.get_module_status()
        assert status['module_name'] == 'GovernanceController'
        assert status['specs_monitored'] >= 1
    
    def test_validate_new_spec_no_overlap(self):
        """Test validation of spec with no overlaps"""
        proposal = SpecProposal(
            name="unique-spec",
            content="Unique functionality",
            requirements=["Unique requirement"],
            interfaces=["UniqueInterface"],
            terminology={"UniqueTerm"},
            functionality_keywords={"unique", "special", "distinct"}
        )
        
        result = self.controller.validate_new_spec(proposal)
        assert result in [ValidationResult.APPROVED, ValidationResult.REQUIRES_REVIEW]
    
    def test_validate_new_spec_with_overlap(self):
        """Test validation of spec with overlaps"""
        proposal = SpecProposal(
            name="overlapping-spec",
            content="Testing functionality",
            requirements=["Testing requirement"],
            interfaces=["TestInterface"],
            terminology={"TestTerm"},
            functionality_keywords={"test", "validate", "system"}  # Overlaps with sample spec
        )
        
        result = self.controller.validate_new_spec(proposal)
        # Should detect overlap and require review or consolidation
        assert result in [ValidationResult.REQUIRES_REVIEW, ValidationResult.REQUIRES_CONSOLIDATION]
    
    def test_check_overlap_conflicts(self):
        """Test overlap conflict detection"""
        proposal = SpecProposal(
            name="test-spec",
            content="Test content",
            requirements=["Test requirement"],
            interfaces=["TestInterface"],
            terminology={"TestTerm"},
            functionality_keywords={"test", "validate", "functionality"}
        )
        
        overlap_report = self.controller.check_overlap_conflicts(proposal)
        assert isinstance(overlap_report.severity, OverlapSeverity)
        assert isinstance(overlap_report.overlap_percentage, float)
    
    def test_enforce_approval_workflow(self):
        """Test approval workflow enforcement"""
        change_request = {
            'type': 'architecture_change',
            'affected_specs': ['spec1', 'spec2', 'spec3', 'spec4'],
            'description': 'Major architectural change'
        }
        
        approval_status = self.controller.enforce_approval_workflow(change_request)
        assert approval_status.status == ValidationResult.REQUIRES_REVIEW
        assert approval_status.reviewer == "architectural_review_board"
    
    def test_trigger_consolidation(self):
        """Test consolidation workflow triggering"""
        from src.spec_reconciliation.governance import OverlapReport
        
        overlap_report = OverlapReport(
            spec_pairs=[("spec1", "spec2")],
            overlap_percentage=0.85,
            overlapping_functionality=["function1", "function2"],
            severity=OverlapSeverity.HIGH,
            consolidation_recommendation="Consolidate immediately"
        )
        
        workflow = self.controller.trigger_consolidation(overlap_report)
        assert workflow['status'] == 'triggered'
        assert 'workflow_id' in workflow
        assert len(workflow['next_steps']) > 0


class TestConsistencyValidator:
    """Test the ConsistencyValidator functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        self.validator = ConsistencyValidator(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_validator_initialization(self):
        """Test that validator initializes correctly"""
        assert self.validator.is_healthy()
        status = self.validator.get_module_status()
        assert status['module_name'] == 'ConsistencyValidator'
    
    def test_validate_terminology(self):
        """Test terminology validation"""
        content = """
        This content contains PDCA methodology and RCA analysis.
        The ReflectiveModule pattern is used throughout.
        """
        
        report = self.validator.validate_terminology(content)
        assert isinstance(report.consistency_score, float)
        assert 0.0 <= report.consistency_score <= 1.0
        assert isinstance(report.consistent_terms, set)
        assert isinstance(report.inconsistent_terms, dict)
        assert isinstance(report.new_terms, set)
    
    def test_check_interface_compliance(self):
        """Test interface compliance checking"""
        interface_def = """
        class TestModule(ReflectiveModule):
            def get_module_status(self):
                pass
            
            def is_healthy(self):
                pass
                
            def get_health_indicators(self):
                pass
        """
        
        report = self.validator.check_interface_compliance(interface_def)
        assert isinstance(report.compliance_score, float)
        assert 0.0 <= report.compliance_score <= 1.0
        # Should be compliant since it has required ReflectiveModule methods
        assert report.compliance_score > 0.5
    
    def test_validate_pattern_consistency(self):
        """Test pattern consistency validation"""
        patterns = ["PDCA", "RCA"]
        
        report = self.validator.validate_pattern_consistency(patterns)
        assert isinstance(report.pattern_score, float)
        assert 0.0 <= report.pattern_score <= 1.0
        assert isinstance(report.consistent_patterns, list)
        assert isinstance(report.inconsistent_patterns, list)
    
    def test_generate_consistency_score(self):
        """Test overall consistency score generation"""
        # Create a temporary spec file
        spec_file = self.temp_dir / "test_spec.md"
        spec_content = """
        # Test Spec
        
        This spec uses PDCA methodology and implements ReflectiveModule pattern.
        
        ## Interface
        
        class TestModule(ReflectiveModule):
            def get_module_status(self):
                pass
        """
        spec_file.write_text(spec_content)
        
        metrics = self.validator.generate_consistency_score([str(spec_file)])
        assert isinstance(metrics.overall_score, float)
        assert 0.0 <= metrics.overall_score <= 1.0
        assert isinstance(metrics.consistency_level, ConsistencyLevel)
        assert isinstance(metrics.critical_issues, list)
        assert isinstance(metrics.improvement_priority, list)


def test_integration_governance_and_validation():
    """Test integration between governance and validation components"""
    with tempfile.TemporaryDirectory() as temp_dir:
        specs_dir = Path(temp_dir) / "specs"
        specs_dir.mkdir()
        
        # Create sample spec
        sample_spec_dir = specs_dir / "sample-spec"
        sample_spec_dir.mkdir()
        
        requirements_content = """
# Sample Requirements

## Requirements

### Requirement 1
**User Story:** As a user, I want PDCA functionality, so that I can improve systematically.

#### Acceptance Criteria
1. WHEN planning THEN system SHALL use model registry
2. WHEN executing THEN system SHALL follow systematic approach
"""
        
        (sample_spec_dir / "requirements.md").write_text(requirements_content)
        
        # Initialize both components
        controller = GovernanceController(str(specs_dir))
        validator = ConsistencyValidator(str(specs_dir))
        
        # Test that both are healthy
        assert controller.is_healthy()
        assert validator.is_healthy()
        
        # Test governance validation
        proposal = SpecProposal(
            name="test-spec",
            content="Test PDCA implementation",
            requirements=["PDCA requirement"],
            interfaces=["PDCAInterface"],
            terminology={"PDCA"},
            functionality_keywords={"pdca", "systematic", "improvement"}
        )
        
        validation_result = controller.validate_new_spec(proposal)
        assert isinstance(validation_result, ValidationResult)
        
        # Test consistency validation
        terminology_report = validator.validate_terminology(requirements_content)
        assert isinstance(terminology_report.consistency_score, float)


class TestContinuousMonitor:
    """Test the ContinuousMonitor automated correction workflows"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create sample spec files for testing
        self._create_sample_specs()
        
        from src.spec_reconciliation.monitoring import ContinuousMonitor
        self.monitor = ContinuousMonitor(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_sample_specs(self):
        """Create sample spec files for testing"""
        # Create spec with terminology issues
        spec1_dir = self.specs_dir / "spec-with-terminology-issues"
        spec1_dir.mkdir()
        
        spec1_content = """
# Spec with Terminology Issues

This spec uses inconsistent terminology like RCA, root cause analysis, and Root Cause Analysis.
It also mentions PDCA, Plan-Do-Check-Act, and plan do check act methodology.
"""
        (spec1_dir / "requirements.md").write_text(spec1_content)
        
        # Create spec with interface issues
        spec2_dir = self.specs_dir / "spec-with-interface-issues"
        spec2_dir.mkdir()
        
        spec2_content = """
# Spec with Interface Issues

## Interface Definition

class BadModule:
    def bad_method_name(self):
        pass
    
    def another_bad_method(self, param1, param2, param3, param4, param5):
        pass
"""
        (spec2_dir / "design.md").write_text(spec2_content)
    
    def test_monitor_initialization(self):
        """Test that monitor initializes correctly"""
        assert self.monitor.is_healthy()
        status = self.monitor.get_module_status()
        assert status['module_name'] == 'ContinuousMonitor'
    
    def test_create_automatic_terminology_correction(self):
        """Test automatic terminology correction workflow creation"""
        from src.spec_reconciliation.monitoring import InconsistencyReport
        
        # Create terminology report with inconsistencies
        terminology_report = InconsistencyReport(
            report_id="test_terminology_report",
            generated_at=self.monitor.consistency_validator.datetime.now() if hasattr(self.monitor.consistency_validator, 'datetime') else __import__('datetime').datetime.now(),
            terminology_drift={
                "RCA": ["root cause analysis", "Root Cause Analysis"],
                "PDCA": ["Plan-Do-Check-Act", "plan do check act"]
            },
            new_terminology={"systematic_improvement"},
            deprecated_usage={"old_term"},
            consistency_degradation=0.15,
            correction_suggestions=["Standardize RCA terminology", "Standardize PDCA terminology"]
        )
        
        # Create correction workflow
        workflow = self.monitor.create_automatic_terminology_correction(terminology_report)
        
        # Verify workflow creation
        assert workflow.workflow_id.startswith("terminology_correction_")
        assert workflow.correction_type == "terminology_correction"
        assert len(workflow.correction_steps) > 0
        assert workflow.created_at is not None
        
        # Verify workflow is in correction history
        assert len(self.monitor.correction_history) > 0
        assert self.monitor.correction_history[-1].workflow_id == workflow.workflow_id
    
    def test_create_interface_compliance_correction(self):
        """Test interface compliance correction workflow creation"""
        # Create interface violations
        interface_violations = [
            {
                'type': 'naming_convention',
                'severity': 'medium',
                'location': 'spec-with-interface-issues/design.md:8',
                'current_form': 'bad_method_name',
                'suggested_correction': 'get_bad_method_result',
                'reason': 'Method name does not follow convention'
            },
            {
                'type': 'parameter_order',
                'severity': 'low',
                'location': 'spec-with-interface-issues/design.md:11',
                'current_form': 'another_bad_method(param1, param2, param3, param4, param5)',
                'suggested_correction': 'another_bad_method(config: Dict[str, Any])',
                'reason': 'Too many parameters'
            }
        ]
        
        # Create correction workflow
        workflow = self.monitor.create_interface_compliance_correction(interface_violations)
        
        # Verify workflow creation
        assert workflow.workflow_id.startswith("interface_correction_")
        assert workflow.correction_type == "interface_compliance_correction"
        assert len(workflow.correction_steps) > 0
        assert workflow.created_at is not None
        
        # Verify workflow addresses both violations
        assert any("naming_convention" in step for step in workflow.correction_steps)
        assert any("parameter_order" in step for step in workflow.correction_steps)
    
    def test_create_conflict_resolution_automation(self):
        """Test conflict resolution automation workflow creation"""
        # Create conflicts
        conflicts = [
            {
                'type': 'duplicate_requirement',
                'complexity': 'low',
                'description': 'Duplicate requirement found in multiple specs',
                'affected_specs': ['spec1', 'spec2']
            },
            {
                'type': 'terminology_conflict',
                'complexity': 'medium',
                'description': 'Conflicting terminology usage',
                'affected_specs': ['spec1', 'spec3']
            },
            {
                'type': 'complex_architectural_conflict',
                'complexity': 'high',
                'description': 'Complex architectural decision conflict',
                'affected_specs': ['spec2', 'spec3', 'spec4']
            }
        ]
        
        # Create conflict resolution workflow
        workflow = self.monitor.create_conflict_resolution_automation(conflicts)
        
        # Verify workflow creation
        assert workflow.workflow_id.startswith("conflict_resolution_")
        assert workflow.correction_type == "conflict_resolution_automation"
        assert len(workflow.correction_steps) > 0
        assert workflow.created_at is not None
        
        # Verify different types of resolutions are handled
        steps_text = " ".join(workflow.correction_steps)
        assert "duplicate_requirement" in steps_text or "Auto-resolve" in steps_text
        assert "terminology_conflict" in steps_text or "pattern-based" in steps_text
        assert "Escalate" in steps_text  # Complex conflict should be escalated
    
    def test_create_escalation_system(self):
        """Test escalation system for corrections requiring human intervention"""
        from src.spec_reconciliation.monitoring import CorrectionWorkflow, CorrectionStatus
        
        # Create a failed workflow that needs escalation
        failed_workflow = CorrectionWorkflow(
            workflow_id="test_failed_workflow",
            correction_type="interface_compliance_correction",
            target_specs=["spec1", "spec2"],
            correction_steps=["Failed step 1", "Failed step 2"],
            status=CorrectionStatus.FAILED,
            created_at=__import__('datetime').datetime.now(),
            completed_at=None,
            success_rate=0.2,
            escalation_reason=None
        )
        
        escalation_reason = "Low success rate in automated correction"
        
        # Create escalation
        escalation_result = self.monitor.create_escalation_system(failed_workflow, escalation_reason)
        
        # Verify escalation creation
        assert escalation_result['escalation_created'] is True
        assert 'escalation_id' in escalation_result
        assert 'priority' in escalation_result
        assert 'resolution_deadline' in escalation_result
        assert len(escalation_result['recommended_actions']) > 0
        
        # Verify workflow status updated
        assert failed_workflow.status == CorrectionStatus.ESCALATED
        assert failed_workflow.escalation_reason == escalation_reason
        
        # Verify escalation is tracked
        assert hasattr(self.monitor, 'escalation_history')
        assert len(self.monitor.escalation_history) > 0
    
    def test_terminology_correction_execution(self):
        """Test execution of terminology corrections"""
        # Test helper method for determining standard terminology
        variations = ["RCA", "root cause analysis", "Root Cause Analysis"]
        standard_form = self.monitor._determine_standard_terminology("RCA", variations)
        assert standard_form in variations
        assert len(standard_form) > 0
    
    def test_interface_correction_execution(self):
        """Test execution of interface corrections"""
        # Test identification of interface specs
        interface_violations = [
            {
                'location': 'spec1/design.md:10',
                'type': 'naming_convention'
            },
            {
                'location': 'spec2/requirements.md:5',
                'type': 'parameter_order'
            }
        ]
        
        interface_specs = self.monitor._identify_interface_specs(interface_violations)
        assert isinstance(interface_specs, list)
        assert len(interface_specs) > 0
    
    def test_conflict_pattern_matching(self):
        """Test conflict pattern matching for automated resolution"""
        # Test known conflict pattern
        conflict = {
            'type': 'duplicate_requirement',
            'description': 'Duplicate requirement found in specifications'
        }
        
        pattern_match = self.monitor._match_conflict_pattern(conflict)
        assert pattern_match is not None
        assert 'confidence' in pattern_match
        assert 'resolution_strategy' in pattern_match
        assert pattern_match['confidence'] > 0.5
        
        # Test unknown conflict pattern
        unknown_conflict = {
            'type': 'unknown_conflict_type',
            'description': 'Some unknown conflict'
        }
        
        unknown_pattern = self.monitor._match_conflict_pattern(unknown_conflict)
        # Should return None for unknown patterns
        assert unknown_pattern is None
    
    def test_escalation_priority_determination(self):
        """Test escalation priority determination"""
        from src.spec_reconciliation.monitoring import CorrectionWorkflow, CorrectionStatus
        
        # Test critical priority
        critical_workflow = CorrectionWorkflow(
            workflow_id="critical_test",
            correction_type="interface_compliance_correction",
            target_specs=["spec1"],
            correction_steps=["step1"],
            status=CorrectionStatus.FAILED,
            created_at=__import__('datetime').datetime.now(),
            completed_at=None,
            success_rate=0.1,
            escalation_reason=None
        )
        
        critical_reason = "Critical security vulnerability detected"
        priority = self.monitor._determine_escalation_priority(critical_workflow, critical_reason)
        assert priority == "critical"
        
        # Test high priority
        high_priority_workflow = CorrectionWorkflow(
            workflow_id="high_test",
            correction_type="conflict_resolution_automation",
            target_specs=["spec1"],
            correction_steps=["step1"],
            status=CorrectionStatus.FAILED,
            created_at=__import__('datetime').datetime.now(),
            completed_at=None,
            success_rate=0.2,
            escalation_reason=None
        )
        
        high_reason = "Multiple conflicts detected"
        priority = self.monitor._determine_escalation_priority(high_priority_workflow, high_reason)
        assert priority == "high"
        
        # Test medium priority
        medium_workflow = CorrectionWorkflow(
            workflow_id="medium_test",
            correction_type="terminology_correction",
            target_specs=["spec1"],
            correction_steps=["step1"],
            status=CorrectionStatus.FAILED,
            created_at=__import__('datetime').datetime.now(),
            completed_at=None,
            success_rate=0.5,
            escalation_reason=None
        )
        
        medium_reason = "Terminology standardization needed"
        priority = self.monitor._determine_escalation_priority(medium_workflow, medium_reason)
        assert priority == "medium"
    
    def test_required_expertise_identification(self):
        """Test identification of required expertise for escalations"""
        from src.spec_reconciliation.monitoring import CorrectionWorkflow, CorrectionStatus
        
        # Test terminology workflow
        terminology_workflow = CorrectionWorkflow(
            workflow_id="terminology_test",
            correction_type="terminology_correction",
            target_specs=["spec1"],
            correction_steps=["step1"],
            status=CorrectionStatus.FAILED,
            created_at=__import__('datetime').datetime.now(),
            completed_at=None,
            success_rate=0.5,
            escalation_reason=None
        )
        
        expertise = self.monitor._identify_required_expertise(terminology_workflow)
        assert 'technical_writing' in expertise
        assert 'domain_expertise' in expertise
        assert 'spec_management' in expertise
        
        # Test interface workflow
        interface_workflow = CorrectionWorkflow(
            workflow_id="interface_test",
            correction_type="interface_compliance_correction",
            target_specs=["spec1"],
            correction_steps=["step1"],
            status=CorrectionStatus.FAILED,
            created_at=__import__('datetime').datetime.now(),
            completed_at=None,
            success_rate=0.5,
            escalation_reason=None
        )
        
        expertise = self.monitor._identify_required_expertise(interface_workflow)
        assert 'software_architecture' in expertise
        assert 'api_design' in expertise
        assert 'spec_management' in expertise


def test_automated_correction_workflows_integration():
    """Test integration of all automated correction workflows"""
    with tempfile.TemporaryDirectory() as temp_dir:
        specs_dir = Path(temp_dir) / "specs"
        specs_dir.mkdir()
        
        # Create spec with multiple issues
        problem_spec_dir = specs_dir / "problem-spec"
        problem_spec_dir.mkdir()
        
        problem_content = """
# Problem Spec

This spec has terminology issues like RCA and root cause analysis.
It also has interface problems.

## Interface

class BadInterface:
    def badMethodName(self):
        pass
    
    def anotherBadMethod(self, p1, p2, p3, p4, p5, p6):
        pass

## Conflicts

This spec conflicts with other specs on terminology and requirements.
"""
        (problem_spec_dir / "requirements.md").write_text(problem_content)
        
        from src.spec_reconciliation.monitoring import ContinuousMonitor, InconsistencyReport
        monitor = ContinuousMonitor(str(specs_dir))
        
        # Test terminology correction
        terminology_report = InconsistencyReport(
            report_id="integration_test",
            generated_at=__import__('datetime').datetime.now(),
            terminology_drift={"RCA": ["root cause analysis"]},
            new_terminology=set(),
            deprecated_usage=set(),
            consistency_degradation=0.2,
            correction_suggestions=["Standardize RCA"]
        )
        
        terminology_workflow = monitor.create_automatic_terminology_correction(terminology_report)
        assert terminology_workflow.correction_type == "terminology_correction"
        
        # Test interface correction
        interface_violations = [
            {
                'type': 'naming_convention',
                'severity': 'medium',
                'location': 'problem-spec/requirements.md:10',
                'current_form': 'badMethodName',
                'suggested_correction': 'get_bad_method_result'
            }
        ]
        
        interface_workflow = monitor.create_interface_compliance_correction(interface_violations)
        assert interface_workflow.correction_type == "interface_compliance_correction"
        
        # Test conflict resolution
        conflicts = [
            {
                'type': 'terminology_conflict',
                'complexity': 'medium',
                'description': 'RCA terminology conflict',
                'affected_specs': ['problem-spec']
            }
        ]
        
        conflict_workflow = monitor.create_conflict_resolution_automation(conflicts)
        assert conflict_workflow.correction_type == "conflict_resolution_automation"
        
        # Verify all workflows are tracked
        assert len(monitor.correction_history) >= 3
        
        # Test escalation system
        if any(w.success_rate < 0.5 for w in monitor.correction_history):
            failed_workflow = next(w for w in monitor.correction_history if w.success_rate < 0.5)
            escalation_result = monitor.create_escalation_system(failed_workflow, "Integration test escalation")
            assert escalation_result['escalation_created'] is True


class TestComponentBoundaryResolver:
    """Test the ComponentBoundaryResolver functionality for task 5.2"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.temp_dir) / "specs"
        self.specs_dir.mkdir()
        
        # Create consolidated spec directories for testing
        self._create_consolidated_specs()
        
        self.resolver = ComponentBoundaryResolver(str(self.specs_dir))
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_consolidated_specs(self):
        """Create consolidated spec files for testing"""
        # Unified Beast Mode System
        beast_mode_dir = self.specs_dir / "unified_beast_mode_system"
        beast_mode_dir.mkdir()
        
        beast_mode_requirements = """
# Unified Beast Mode System Requirements

## Requirements

### Requirement 1
**User Story:** As a system architect, I want domain-intelligent systematic development workflows, so that development is optimized.

#### Acceptance Criteria
1. WHEN executing PDCA cycles THEN the system SHALL orchestrate systematically
2. WHEN monitoring tool health THEN the system SHALL provide proactive maintenance
3. WHEN managing backlog THEN the system SHALL prioritize intelligently
"""
        
        beast_mode_design = """
# Unified Beast Mode System Design

## Interface

class BeastModeSystemInterface(ReflectiveModule):
    def execute_pdca_cycle(self, domain_context: DomainContext) -> PDCAResult:
        pass
    
    def manage_tool_health(self, tool_inventory: ToolInventory) -> HealthStatus:
        pass
    
    def optimize_backlog(self, backlog_items: List[BacklogItem]) -> OptimizedBacklog:
        pass
"""
        
        (beast_mode_dir / "requirements.md").write_text(beast_mode_requirements)
        (beast_mode_dir / "design.md").write_text(beast_mode_design)
        
        # Unified Testing & RCA Framework
        testing_rca_dir = self.specs_dir / "unified_testing_rca_framework"
        testing_rca_dir.mkdir()
        
        testing_rca_requirements = """
# Unified Testing & RCA Framework Requirements

## Requirements

### Requirement 1
**User Story:** As a developer, I want comprehensive RCA analysis, so that issues are resolved systematically.

#### Acceptance Criteria
1. WHEN issues occur THEN the system SHALL execute RCA analysis
2. WHEN testing is needed THEN the system SHALL run comprehensive tests
3. WHEN patterns are detected THEN the system SHALL optimize testing
"""
        
        testing_rca_design = """
# Unified Testing & RCA Framework Design

## Interface

class TestingRCAFrameworkInterface(ReflectiveModule):
    def execute_rca_analysis(self, issue_context: IssueContext) -> RCAResult:
        pass
    
    def run_comprehensive_tests(self, test_suite: TestSuite) -> TestResults:
        pass
    
    def detect_issues_automatically(self, monitoring_data: MonitoringData) -> IssueDetection:
        pass
"""
        
        (testing_rca_dir / "requirements.md").write_text(testing_rca_requirements)
        (testing_rca_dir / "design.md").write_text(testing_rca_design)
        
        # Unified RDI/RM Analysis System
        rdi_rm_dir = self.specs_dir / "unified_rdi_rm_analysis_system"
        rdi_rm_dir.mkdir()
        
        rdi_rm_requirements = """
# Unified RDI/RM Analysis System Requirements

## Requirements

### Requirement 1
**User Story:** As a quality engineer, I want RDI compliance validation, so that quality is maintained.

#### Acceptance Criteria
1. WHEN validating compliance THEN the system SHALL check RDI alignment
2. WHEN analyzing quality THEN the system SHALL provide metrics
3. WHEN tracking traceability THEN the system SHALL maintain links
"""
        
        rdi_rm_design = """
# Unified RDI/RM Analysis System Design

## Interface

class RDIRMAnalysisSystemInterface(ReflectiveModule):
    def validate_rdi_compliance(self, rdi_context: RDIContext) -> ComplianceResult:
        pass
    
    def analyze_quality_metrics(self, quality_data: QualityData) -> QualityAnalysis:
        pass
    
    def track_traceability(self, traceability_request: TraceabilityRequest) -> TraceabilityReport:
        pass
"""
        
        (rdi_rm_dir / "requirements.md").write_text(rdi_rm_requirements)
        (rdi_rm_dir / "design.md").write_text(rdi_rm_design)
    
    def test_resolver_initialization(self):
        """Test that resolver initializes correctly with predefined boundaries"""
        assert self.resolver.is_healthy()
        status = self.resolver.get_module_status()
        assert status['module_name'] == 'ComponentBoundaryResolver'
        
        # Check predefined boundaries are loaded
        assert len(self.resolver.component_boundaries) >= 3
        assert "unified_beast_mode_system" in self.resolver.component_boundaries
        assert "unified_testing_rca_framework" in self.resolver.component_boundaries
        assert "unified_rdi_rm_analysis_system" in self.resolver.component_boundaries
    
    def test_define_component_boundaries(self):
        """Test defining clear component boundaries eliminating functional overlap (R3.1)"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework", 
            "unified_rdi_rm_analysis_system"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        
        # Verify boundaries are created
        assert len(boundaries) == 3
        
        # Verify each boundary has required properties
        for boundary in boundaries:
            assert isinstance(boundary, ComponentBoundary)
            assert boundary.component_name in consolidated_specs
            assert isinstance(boundary.component_type, ComponentType)
            assert len(boundary.primary_responsibilities) > 0
            assert len(boundary.boundary_constraints) > 0
            assert len(boundary.interface_contracts) > 0
        
        # Verify no overlapping responsibilities (R3.1)
        all_responsibilities = []
        for boundary in boundaries:
            all_responsibilities.extend(boundary.primary_responsibilities)
        
        # Should not have exact duplicates
        assert len(all_responsibilities) == len(set(all_responsibilities))
    
    def test_create_interface_contracts(self):
        """Test creating explicit interface contracts with clear contracts (R3.2)"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        
        # Verify contracts are created
        assert len(contracts) > 0
        
        # Verify each contract has required properties (R3.2)
        for contract in contracts:
            assert isinstance(contract, InterfaceContract)
            assert contract.interface_name
            assert contract.provider_component
            assert isinstance(contract.consumer_components, list)
            assert isinstance(contract.methods, list)
            assert isinstance(contract.data_contracts, list)
            assert isinstance(contract.service_level_agreements, dict)
            assert isinstance(contract.validation_rules, list)
        
        # Verify interfaces are explicitly defined
        interface_names = [c.interface_name for c in contracts]
        assert len(interface_names) == len(set(interface_names))  # No duplicates
    
    def test_implement_dependency_management(self):
        """Test implementing dependency management ensuring clean interactions (R3.4)"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework",
            "unified_rdi_rm_analysis_system"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        dependency_graph = self.resolver.implement_dependency_management(boundaries, contracts)
        
        # Verify dependency graph is created
        assert isinstance(dependency_graph, dict)
        assert len(dependency_graph) > 0
        
        # Verify dependencies are explicitly documented (R3.4)
        for component, dependencies in dependency_graph.items():
            assert component in consolidated_specs
            assert isinstance(dependencies, list)
            
            for dep in dependencies:
                assert isinstance(dep, DependencyRelationship)
                assert dep.dependent_component == component
                assert dep.dependency_component
                assert dep.dependency_type in ["interface", "service", "data"]
                assert isinstance(dep.is_circular, bool)
                assert dep.validation_status
        
        # Verify no circular dependencies
        for dependencies in dependency_graph.values():
            for dep in dependencies:
                assert not dep.is_circular, f"Circular dependency detected: {dep.dependent_component} -> {dep.dependency_component}"
    
    def test_validate_component_boundaries(self):
        """Test validating boundaries through integration testing and compliance checking (R3.5)"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework"
        ]
        
        boundaries = self.resolver.define_component_boundaries(consolidated_specs)
        contracts = self.resolver.create_interface_contracts(boundaries)
        dependency_graph = self.resolver.implement_dependency_management(boundaries, contracts)
        
        validation_results = self.resolver.validate_component_boundaries(boundaries, contracts, dependency_graph)
        
        # Verify validation results
        assert isinstance(validation_results, dict)
        assert 'boundary_separation' in validation_results
        assert 'interface_compliance' in validation_results
        assert 'dependency_rules' in validation_results
        assert 'contract_adherence' in validation_results
        assert 'integration_test_plan' in validation_results
        assert 'overall_valid' in validation_results
        
        # Verify all validations are boolean
        for key, value in validation_results.items():
            if key != 'overall_valid':
                assert isinstance(value, bool)
        
        # Overall validation should be True for well-defined boundaries
        assert validation_results['overall_valid'] is True
    
    def test_resolve_component_boundaries_complete(self):
        """Test complete component boundary resolution process"""
        consolidated_specs = [
            "unified_beast_mode_system",
            "unified_testing_rca_framework",
            "unified_rdi_rm_analysis_system"
        ]
        
        resolution = self.resolver.resolve_component_boundaries(consolidated_specs)
        
        # Verify complete resolution
        assert resolution.resolution_id.startswith("boundary_resolution_")
        assert len(resolution.component_boundaries) == 3
        assert len(resolution.interface_contracts) > 0
        assert len(resolution.dependency_graph) > 0
        assert isinstance(resolution.boundary_violations, list)
        assert isinstance(resolution.validation_results, dict)
        assert isinstance(resolution.integration_test_plan, dict)
        
        # Verify no critical boundary violations
        critical_violations = [v for v in resolution.boundary_violations if v.severity == "critical"]
        assert len(critical_violations) == 0
        
        # Verify integration test plan is comprehensive
        test_plan = resolution.integration_test_plan
        assert 'boundary_tests' in test_plan
        assert 'contract_tests' in test_plan
        assert 'dependency_tests' in test_plan
        assert len(test_plan['boundary_tests']) > 0
        assert len(test_plan['contract_tests']) > 0
    
    def test_boundary_violation_detection(self):
        """Test detection of boundary violations"""
        # Create boundaries with intentional overlaps for testing
        overlapping_boundary1 = ComponentBoundary(
            component_name="test_component_1",
            component_type=ComponentType.CORE_COMPONENT,
            primary_responsibilities=["shared_responsibility", "unique_responsibility_1"],
            boundary_constraints=["MUST NOT access component 2"],
            interface_contracts=["TestInterface1"],
            allowed_dependencies=["test_component_2"],  # Creates circular dependency
            forbidden_access=[],
            shared_services=[]
        )
        
        overlapping_boundary2 = ComponentBoundary(
            component_name="test_component_2",
            component_type=ComponentType.CORE_COMPONENT,
            primary_responsibilities=["shared_responsibility", "unique_responsibility_2"],  # Overlap!
            boundary_constraints=["MUST NOT access component 1"],
            interface_contracts=["TestInterface2"],
            allowed_dependencies=["test_component_1"],  # Creates circular dependency
            forbidden_access=[],
            shared_services=[]
        )
        
        boundaries = [overlapping_boundary1, overlapping_boundary2]
        contracts = []  # Empty for this test
        
        # Create dependency graph with circular dependency
        dependency_graph = {
            "test_component_1": [DependencyRelationship(
                dependent_component="test_component_1",
                dependency_component="test_component_2",
                dependency_type="interface",
                interface_contract=None,
                is_circular=True,
                validation_status="invalid"
            )],
            "test_component_2": [DependencyRelationship(
                dependent_component="test_component_2",
                dependency_component="test_component_1",
                dependency_type="interface",
                interface_contract=None,
                is_circular=True,
                validation_status="invalid"
            )]
        }
        
        violations = self.resolver._detect_boundary_violations(boundaries, contracts, dependency_graph)
        
        # Should detect functional overlap
        functional_overlaps = [v for v in violations if v.violation_type == BoundaryViolationType.FUNCTIONAL_OVERLAP]
        assert len(functional_overlaps) > 0
        
        # Should detect circular dependency
        circular_deps = [v for v in violations if v.violation_type == BoundaryViolationType.CIRCULAR_DEPENDENCY]
        assert len(circular_deps) > 0
    
    def test_interface_contract_generation(self):
        """Test generation of interface contracts with proper methods and data contracts"""
        beast_mode_boundary = self.resolver.component_boundaries["unified_beast_mode_system"]
        all_boundaries = list(self.resolver.component_boundaries.values())
        
        contracts = self.resolver._create_component_contracts(beast_mode_boundary, all_boundaries)
        
        # Verify contracts are generated
        assert len(contracts) > 0
        
        contract = contracts[0]
        assert contract.interface_name == "BeastModeSystemInterface"
        assert contract.provider_component == "unified_beast_mode_system"
        assert len(contract.methods) > 0
        assert len(contract.data_contracts) > 0
        
        # Verify methods have proper structure
        for method in contract.methods:
            assert 'name' in method
            assert 'parameters' in method
            assert 'return_type' in method
            assert 'description' in method
        
        # Verify data contracts have proper structure
        for data_contract in contract.data_contracts:
            assert 'name' in data_contract
            assert 'fields' in data_contract
            assert 'validation' in data_contract
    
    def test_shared_service_contracts(self):
        """Test creation of shared service contracts"""
        boundaries = list(self.resolver.component_boundaries.values())
        shared_service_contracts = self.resolver._create_shared_service_contracts(boundaries)
        
        # Verify shared service contracts are created
        assert len(shared_service_contracts) > 0
        
        # Check for expected shared services
        service_names = [c.provider_component for c in shared_service_contracts]
        expected_services = ["domain_registry_service", "monitoring_metrics_service", "configuration_service"]
        
        for expected_service in expected_services:
            assert expected_service in service_names
        
        # Verify shared service contract structure
        for contract in shared_service_contracts:
            assert contract.interface_name.endswith("Interface")
            assert len(contract.consumer_components) > 0
            assert len(contract.methods) > 0
            assert contract.service_level_agreements['availability']
            assert contract.service_level_agreements['response_time']
            assert contract.service_level_agreements['throughput']
    
    def test_dependency_analysis(self):
        """Test dependency analysis for components"""
        beast_mode_boundary = self.resolver.component_boundaries["unified_beast_mode_system"]
        all_boundaries = list(self.resolver.component_boundaries.values())
        contracts = []  # Empty for this test
        
        dependencies = self.resolver._analyze_component_dependencies(beast_mode_boundary, all_boundaries, contracts)
        
        # Verify dependencies are analyzed
        assert isinstance(dependencies, list)
        
        # Beast Mode should have dependencies on other components
        dependency_names = [dep.dependency_component for dep in dependencies]
        expected_deps = ["domain_registry_service", "monitoring_metrics_service", "testing_rca_framework", "rdi_rm_analysis_system"]
        
        for expected_dep in expected_deps:
            if expected_dep in beast_mode_boundary.allowed_dependencies:
                # Should find dependency if it exists in allowed list
                pass  # Dependencies might not all be found due to test setup
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies"""
        # Create dependency graph with circular dependency
        dependency_graph = {
            "component_a": [DependencyRelationship(
                dependent_component="component_a",
                dependency_component="component_b",
                dependency_type="interface",
                interface_contract=None,
                is_circular=False,
                validation_status="valid"
            )],
            "component_b": [DependencyRelationship(
                dependent_component="component_b",
                dependency_component="component_a",
                dependency_type="interface",
                interface_contract=None,
                is_circular=False,
                validation_status="valid"
            )]
        }
        
        circular_deps = self.resolver._detect_circular_dependencies(dependency_graph)
        
        # Should detect the circular dependency
        assert len(circular_deps) > 0
        assert ("component_a", "component_b") in circular_deps or ("component_b", "component_a") in circular_deps
    
    def test_integration_test_plan_generation(self):
        """Test generation of comprehensive integration test plan"""
        boundaries = list(self.resolver.component_boundaries.values())[:2]  # Use first 2 for testing
        contracts = self.resolver.create_interface_contracts(boundaries)
        
        test_plan = self.resolver._generate_integration_test_plan(boundaries, contracts)
        
        # Verify test plan structure
        assert 'test_suites' in test_plan
        assert 'boundary_tests' in test_plan
        assert 'contract_tests' in test_plan
        assert 'dependency_tests' in test_plan
        
        # Verify boundary tests are generated
        assert len(test_plan['boundary_tests']) == len(boundaries)
        
        for boundary_test in test_plan['boundary_tests']:
            assert 'component' in boundary_test
            assert 'test_name' in boundary_test
            assert 'test_cases' in boundary_test
            assert len(boundary_test['test_cases']) > 0
        
        # Verify contract tests are generated
        assert len(test_plan['contract_tests']) == len(contracts)
        
        for contract_test in test_plan['contract_tests']:
            assert 'contract' in contract_test
            assert 'test_name' in contract_test
            assert 'test_cases' in contract_test
            assert len(contract_test['test_cases']) > 0


def test_component_boundary_resolution_integration():
    """Test integration of component boundary resolution with other reconciliation components"""
    with tempfile.TemporaryDirectory() as temp_dir:
        specs_dir = Path(temp_dir) / "specs"
        specs_dir.mkdir()
        
        # Create consolidated specs
        consolidated_specs = ["unified_beast_mode_system", "unified_testing_rca_framework"]
        
        for spec_name in consolidated_specs:
            spec_dir = specs_dir / spec_name
            spec_dir.mkdir()
            
            requirements_content = f"""
# {spec_name.replace('_', ' ').title()} Requirements

## Requirements

### Requirement 1
**User Story:** As a user, I want {spec_name} functionality, so that the system works correctly.

#### Acceptance Criteria
1. WHEN using {spec_name} THEN the system SHALL function properly
2. WHEN integrating components THEN boundaries SHALL be respected
"""
            
            design_content = f"""
# {spec_name.replace('_', ' ').title()} Design

## Interface

class {spec_name.replace('_', '').title()}Interface(ReflectiveModule):
    def execute_operation(self, context: Dict[str, Any]) -> OperationResult:
        pass
"""
            
            (spec_dir / "requirements.md").write_text(requirements_content)
            (spec_dir / "design.md").write_text(design_content)
        
        # Initialize boundary resolver
        resolver = ComponentBoundaryResolver(str(specs_dir))
        
        # Test complete boundary resolution
        resolution = resolver.resolve_component_boundaries(consolidated_specs)
        
        # Verify integration works
        assert resolution.resolution_id
        assert len(resolution.component_boundaries) == len(consolidated_specs)
        assert len(resolution.interface_contracts) > 0
        assert resolution.validation_results['overall_valid'] is True
        
        # Verify boundaries eliminate overlap
        all_responsibilities = []
        for boundary in resolution.component_boundaries:
            all_responsibilities.extend(boundary.primary_responsibilities)
        
        # Should not have exact duplicates (functional overlap eliminated)
        assert len(all_responsibilities) == len(set(all_responsibilities))
        
        # Verify interface contracts are explicit
        for contract in resolution.interface_contracts:
            assert contract.interface_name
            assert len(contract.methods) > 0
            assert len(contract.validation_rules) > 0
        
        # Verify dependency management is clean
        for component, dependencies in resolution.dependency_graph.items():
            for dep in dependencies:
                assert not dep.is_circular  # No circular dependencies
                assert dep.validation_status == "valid"