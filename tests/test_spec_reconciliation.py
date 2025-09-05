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