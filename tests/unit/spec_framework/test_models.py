"""
Unit tests for Spec Mode Framework core models.
"""

import pytest
from datetime import datetime
from src.spec_framework.core.models import (
    Specification,
    Requirement,
    UserStory,
    AcceptanceCriterion,
    EARSStatement,
    ValidationMethod,
    TraceabilityMatrix,
    SpecificationStatus,
    RequirementStatus,
    Priority
)


class TestSpecification:
    """Test cases for Specification model."""
    
    def test_specification_creation(self):
        """Test basic specification creation."""
        spec = Specification(
            name="Test Specification",
            description="A test specification",
            created_by="test_user"
        )
        
        assert spec.name == "Test Specification"
        assert spec.description == "A test specification"
        assert spec.created_by == "test_user"
        assert spec.status == SpecificationStatus.DRAFT
        assert len(spec.requirements) == 0
        assert spec.id is not None
    
    def test_add_requirement(self):
        """Test adding requirement to specification."""
        spec = Specification(name="Test Spec")
        
        user_story = UserStory(
            role="developer",
            feature="create specifications",
            benefit="systematic development"
        )
        
        requirement = Requirement(
            user_story=user_story,
            business_value="Improved development quality"
        )
        
        spec.add_requirement(requirement)
        
        assert len(spec.requirements) == 1
        assert spec.requirements[0] == requirement
        assert len(spec.audit_trail.changes) == 1
        assert spec.audit_trail.changes[0].change_type == "requirement_added"
    
    def test_get_requirements_by_status(self):
        """Test filtering requirements by status."""
        spec = Specification(name="Test Spec")
        
        req1 = Requirement(status=RequirementStatus.DRAFT)
        req2 = Requirement(status=RequirementStatus.DEFINED)
        req3 = Requirement(status=RequirementStatus.DRAFT)
        
        spec.add_requirement(req1)
        spec.add_requirement(req2)
        spec.add_requirement(req3)
        
        draft_reqs = spec.get_requirements_by_status(RequirementStatus.DRAFT)
        defined_reqs = spec.get_requirements_by_status(RequirementStatus.DEFINED)
        
        assert len(draft_reqs) == 2
        assert len(defined_reqs) == 1
        assert req2 in defined_reqs
    
    def test_completion_percentage(self):
        """Test completion percentage calculation."""
        spec = Specification(name="Test Spec")
        
        req1 = Requirement(status=RequirementStatus.VALIDATED)
        req2 = Requirement(status=RequirementStatus.DRAFT)
        req3 = Requirement(status=RequirementStatus.VALIDATED)
        
        spec.add_requirement(req1)
        spec.add_requirement(req2)
        spec.add_requirement(req3)
        
        completion = spec.get_completion_percentage()
        assert completion == pytest.approx(66.67, rel=1e-2)


class TestRequirement:
    """Test cases for Requirement model."""
    
    def test_requirement_creation(self):
        """Test basic requirement creation."""
        user_story = UserStory(
            role="developer",
            feature="write tests",
            benefit="code quality"
        )
        
        requirement = Requirement(
            user_story=user_story,
            business_value="Higher quality code",
            priority=Priority.HIGH
        )
        
        assert requirement.user_story == user_story
        assert requirement.business_value == "Higher quality code"
        assert requirement.priority == Priority.HIGH
        assert requirement.status == RequirementStatus.DRAFT
        assert len(requirement.acceptance_criteria) == 0
    
    def test_add_acceptance_criterion(self):
        """Test adding acceptance criterion to requirement."""
        requirement = Requirement()
        
        ears_statement = EARSStatement(
            condition="user submits valid data",
            system="the system",
            response="process the data successfully"
        )
        
        criterion = AcceptanceCriterion(
            ears_format=ears_statement,
            testable=True
        )
        
        requirement.add_acceptance_criterion(criterion)
        
        assert len(requirement.acceptance_criteria) == 1
        assert requirement.acceptance_criteria[0] == criterion
    
    def test_requirement_completeness(self):
        """Test requirement completeness validation."""
        # Incomplete requirement
        incomplete_req = Requirement()
        assert not incomplete_req.is_complete()
        
        # Complete requirement
        user_story = UserStory(
            role="user",
            feature="login",
            benefit="access system"
        )
        
        ears_statement = EARSStatement(
            condition="user provides valid credentials",
            system="the system",
            response="grant access"
        )
        
        criterion = AcceptanceCriterion(
            ears_format=ears_statement,
            testable=True
        )
        
        complete_req = Requirement(user_story=user_story)
        complete_req.add_acceptance_criterion(criterion)
        
        assert complete_req.is_complete()


class TestEARSStatement:
    """Test cases for EARS statement model."""
    
    def test_ears_statement_creation(self):
        """Test EARS statement creation."""
        ears = EARSStatement(
            condition="user clicks button",
            system="the application",
            response="navigate to next page",
            statement_type="WHEN"
        )
        
        assert ears.condition == "user clicks button"
        assert ears.system == "the application"
        assert ears.response == "navigate to next page"
        assert ears.statement_type == "WHEN"
    
    def test_ears_statement_string_representation(self):
        """Test EARS statement string formatting."""
        ears = EARSStatement(
            condition="user submits form",
            system="the system",
            response="validate input",
            statement_type="WHEN"
        )
        
        expected = "WHEN user submits form THEN the system SHALL validate input"
        assert str(ears) == expected


class TestTraceabilityMatrix:
    """Test cases for TraceabilityMatrix model."""
    
    def test_traceability_matrix_creation(self):
        """Test traceability matrix creation."""
        matrix = TraceabilityMatrix()
        
        assert len(matrix.requirement_to_design) == 0
        assert len(matrix.design_to_tasks) == 0
        assert len(matrix.task_to_implementation) == 0
        assert len(matrix.implementation_to_tests) == 0
    
    def test_add_requirement_design_link(self):
        """Test adding requirement to design link."""
        matrix = TraceabilityMatrix()
        
        matrix.add_requirement_design_link("req1", "design1")
        matrix.add_requirement_design_link("req1", "design2")
        matrix.add_requirement_design_link("req2", "design1")
        
        assert len(matrix.requirement_to_design) == 2
        assert "design1" in matrix.requirement_to_design["req1"]
        assert "design2" in matrix.requirement_to_design["req1"]
        assert "design1" in matrix.requirement_to_design["req2"]
    
    def test_requirement_coverage_calculation(self):
        """Test requirement coverage calculation."""
        matrix = TraceabilityMatrix()
        
        # No requirements
        assert matrix.get_requirement_coverage() == 0.0
        
        # Add some links
        matrix.add_requirement_design_link("req1", "design1")
        matrix.add_requirement_design_link("req2", "design2")
        matrix.requirement_to_design["req3"] = []  # Requirement with no design links
        
        coverage = matrix.get_requirement_coverage()
        assert coverage == pytest.approx(66.67, rel=1e-2)


class TestUserStory:
    """Test cases for UserStory model."""
    
    def test_user_story_creation(self):
        """Test user story creation."""
        story = UserStory(
            role="administrator",
            feature="manage users",
            benefit="system security"
        )
        
        assert story.role == "administrator"
        assert story.feature == "manage users"
        assert story.benefit == "system security"
    
    def test_user_story_string_representation(self):
        """Test user story string formatting."""
        story = UserStory(
            role="developer",
            feature="write clean code",
            benefit="maintainability"
        )
        
        expected = "As a developer, I want write clean code, so that maintainability"
        assert str(story) == expected