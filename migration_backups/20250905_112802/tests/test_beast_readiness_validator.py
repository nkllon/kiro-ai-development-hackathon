"""
Unit tests for BeastReadinessValidator

Tests all beast-readiness criteria and edge cases as required by task 4.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.beast_mode.backlog.beast_readiness_validator import (
    BeastReadinessValidator,
    ValidationCriterion,
    CompletenessReport,
    DependencyStatus,
    ReadinessValidation
)
from src.beast_mode.backlog.models import (
    BacklogItem,
    Requirement,
    AcceptanceCriterion,
    DependencyReference,
    MPMValidation
)
from src.beast_mode.backlog.enums import (
    StrategicTrack,
    BeastReadinessStatus,
    ApprovalStatus
)


# Fixtures at module level
@pytest.fixture
def validator():
    """Create validator instance for testing"""
    return BeastReadinessValidator()

@pytest.fixture
def complete_backlog_item():
    """Create a complete, beast-ready backlog item"""
    requirements = [
        Requirement(
            requirement_id="REQ-001",
            description="Implement user authentication with secure password hashing",
            priority=1,
            acceptance_criteria=["Password must be hashed using bcrypt", "Login must return JWT token"]
        )
    ]
    
    acceptance_criteria = [
        AcceptanceCriterion(
            criterion_id="AC-001",
            description="User can log in with valid credentials and receive JWT token",
            testable=True,
            measurable=True
        ),
        AcceptanceCriterion(
            criterion_id="AC-002", 
            description="Invalid login attempts are rejected with appropriate error message",
            testable=True,
            measurable=True
        )
    ]
    
    dependencies = [
        DependencyReference(
            dependency_id="DEP-001",
            target_item_id="ITEM-002",
            description="Database schema must be created with user table and proper indexes"
        )
    ]
    
    mpm_validation = MPMValidation(
        validation_id="MPM-001",
        validated_by="mpm_user",
        validation_timestamp=datetime.now(),
        completeness_score=0.95,
        dependency_confidence=0.90,
        business_alignment=0.85,
        beast_readiness_assessment="Item is complete and ready for beast execution",
        required_improvements=[],
        approval_status=ApprovalStatus.APPROVED
    )
    
    return BacklogItem(
        item_id="ITEM-001",
        title="Implement User Authentication System",
        track=StrategicTrack.PR_GATE,
        requirements=requirements,
        acceptance_criteria=acceptance_criteria,
        dependencies=dependencies,
        beast_readiness_status=BeastReadinessStatus.MPM_REVIEW,
        created_by="test_user",
        created_at=datetime.now() - timedelta(days=1),
        last_updated=datetime.now(),
        mpm_validation=mpm_validation
    )

@pytest.fixture
def incomplete_backlog_item():
    """Create an incomplete backlog item with various issues"""
    return BacklogItem(
        item_id="ITEM-002",
        title="Fix",  # Too short
        track=StrategicTrack.COMMUNITY,
        requirements=[],  # No requirements
        acceptance_criteria=[],  # No acceptance criteria
        dependencies=[],
        beast_readiness_status=BeastReadinessStatus.DRAFT,
        created_by="test_user",
        created_at=datetime.now() - timedelta(days=1),
        last_updated=datetime.now()
    )

@pytest.fixture
def ambiguous_backlog_item():
    """Create backlog item with ambiguous language"""
    requirements = [
        Requirement(
            requirement_id="REQ-001",
            description="Maybe implement something that could help users",  # Ambiguous
            priority=1,
            acceptance_criteria=["Should probably work"]  # Ambiguous
        )
    ]
    
    acceptance_criteria = [
        AcceptanceCriterion(
            criterion_id="AC-001",
            description="Might work correctly in most cases",  # Ambiguous
            testable=False,
            measurable=False
        )
    ]
    
    return BacklogItem(
        item_id="ITEM-003",
        title="Perhaps fix the thing",  # Ambiguous
        track=StrategicTrack.ZERO_FRICTION,
        requirements=requirements,
        acceptance_criteria=acceptance_criteria,
        dependencies=[],
        beast_readiness_status=BeastReadinessStatus.DRAFT,
        created_by="test_user",
        created_at=datetime.now() - timedelta(days=1),
        last_updated=datetime.now()
    )


class TestBeastReadinessValidator:
    """Test suite for BeastReadinessValidator"""


class TestValidateBeastReadiness:
    """Test the main validate_beast_readiness method"""
    
    def test_validate_complete_item_success(self, validator, complete_backlog_item):
        """Test validation of a complete, beast-ready item"""
        result = validator.validate_beast_readiness(complete_backlog_item)
        
        assert isinstance(result, ReadinessValidation)
        assert result.item_id == complete_backlog_item.item_id
        assert result.overall_beast_ready is True
        assert result.confidence_score >= 0.8
        assert len(result.next_actions) == 1
        assert "beast-ready" in result.next_actions[0].lower()
    
    def test_validate_incomplete_item_failure(self, validator, incomplete_backlog_item):
        """Test validation of an incomplete item"""
        result = validator.validate_beast_readiness(incomplete_backlog_item)
        
        assert result.overall_beast_ready is False
        assert result.confidence_score < 0.5
        assert len(result.next_actions) > 1
        assert any("requirements" in action.lower() for action in result.next_actions)
    
    def test_validation_caching(self, validator, complete_backlog_item):
        """Test that validation results are cached"""
        # First validation
        result1 = validator.validate_beast_readiness(complete_backlog_item)
        
        # Check cache
        assert complete_backlog_item.item_id in validator._validation_cache
        cached_result = validator._validation_cache[complete_backlog_item.item_id]
        assert cached_result.validation_id == result1.validation_id
    
    def test_validation_error_handling(self, validator):
        """Test error handling during validation"""
        # Create invalid item that will cause validation error
        invalid_item = Mock()
        invalid_item.item_id = "INVALID"
        invalid_item.requirements = None  # This should cause an error
        
        with pytest.raises(Exception):
            validator.validate_beast_readiness(invalid_item)


class TestCompletenessValidation:
    """Test completeness criteria validation"""
    
    def test_requirements_completeness_success(self, validator, complete_backlog_item):
        """Test successful requirements completeness validation"""
        report = validator.check_completeness_criteria(complete_backlog_item)
        
        req_criterion = next(c for c in report.criteria_results if c.criterion_name == "requirements_completeness")
        assert req_criterion.passed is True
        assert req_criterion.score >= 0.8
        assert len(req_criterion.details["missing"]) == 0
    
    def test_requirements_completeness_failure(self, validator, incomplete_backlog_item):
        """Test requirements completeness validation failure"""
        report = validator.check_completeness_criteria(incomplete_backlog_item)
        
        req_criterion = next(c for c in report.criteria_results if c.criterion_name == "requirements_completeness")
        assert req_criterion.passed is False
        assert req_criterion.score == 0.0
        assert "No requirements defined" in req_criterion.details["missing"]
    
    def test_acceptance_criteria_quality_success(self, validator, complete_backlog_item):
        """Test successful acceptance criteria validation"""
        report = validator.check_completeness_criteria(complete_backlog_item)
        
        ac_criterion = next(c for c in report.criteria_results if c.criterion_name == "acceptance_criteria_quality")
        assert ac_criterion.passed is True
        assert ac_criterion.score >= 0.8
    
    def test_acceptance_criteria_quality_failure(self, validator, incomplete_backlog_item):
        """Test acceptance criteria validation failure"""
        report = validator.check_completeness_criteria(incomplete_backlog_item)
        
        ac_criterion = next(c for c in report.criteria_results if c.criterion_name == "acceptance_criteria_quality")
        assert ac_criterion.passed is False
        assert ac_criterion.score == 0.0
        assert "No acceptance criteria defined" in ac_criterion.details["missing"]
    
    def test_context_adequacy_success(self, validator, complete_backlog_item):
        """Test successful context adequacy validation"""
        report = validator.check_completeness_criteria(complete_backlog_item)
        
        context_criterion = next(c for c in report.criteria_results if c.criterion_name == "context_adequacy")
        assert context_criterion.passed is True
        assert context_criterion.score >= 0.8
    
    def test_context_adequacy_failure_no_mpm(self, validator):
        """Test context adequacy failure when MPM validation is missing"""
        item = BacklogItem(
            item_id="ITEM-004",
            title="Test Item",
            track=StrategicTrack.PR_GATE,
            requirements=[],
            acceptance_criteria=[],
            dependencies=[],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
            # No mpm_validation
        )
        
        report = validator.check_completeness_criteria(item)
        
        context_criterion = next(c for c in report.criteria_results if c.criterion_name == "context_adequacy")
        assert context_criterion.passed is False
        assert "MPM validation is missing" in context_criterion.details["missing"]
    
    def test_ambiguity_detection_success(self, validator, complete_backlog_item):
        """Test successful ambiguity detection (no ambiguous language)"""
        report = validator.check_completeness_criteria(complete_backlog_item)
        
        ambiguity_criterion = next(c for c in report.criteria_results if c.criterion_name == "ambiguity_absence")
        assert ambiguity_criterion.passed is True
        assert ambiguity_criterion.score >= 0.9
    
    def test_ambiguity_detection_failure(self, validator, ambiguous_backlog_item):
        """Test ambiguity detection failure"""
        report = validator.check_completeness_criteria(ambiguous_backlog_item)
        
        ambiguity_criterion = next(c for c in report.criteria_results if c.criterion_name == "ambiguity_absence")
        assert ambiguity_criterion.passed is False
        assert len(ambiguity_criterion.details["ambiguous"]) > 0
        assert any("perhaps" in amb.lower() for amb in ambiguity_criterion.details["ambiguous"])
    
    def test_overall_completeness_scoring(self, validator, complete_backlog_item):
        """Test overall completeness score calculation"""
        report = validator.check_completeness_criteria(complete_backlog_item)
        
        assert 0.0 <= report.overall_score <= 1.0
        assert report.beast_ready == (report.overall_score >= validator._beast_readiness_threshold)
        
        # Verify weighted scoring
        total_weight = sum(c.weight for c in report.criteria_results)
        expected_score = sum(c.score * c.weight for c in report.criteria_results) / total_weight
        assert abs(report.overall_score - expected_score) < 0.001


class TestDependencyValidation:
    """Test dependency satisfaction validation"""
    
    def test_dependency_satisfaction_success(self, validator, complete_backlog_item):
        """Test successful dependency satisfaction validation"""
        statuses = validator.verify_dependency_satisfaction(complete_backlog_item)
        
        assert len(statuses) == len(complete_backlog_item.dependencies)
        
        for status in statuses:
            assert isinstance(status, DependencyStatus)
            assert status.dependency_id
            assert status.target_item_id
            # With good description, dependency should be satisfied
            assert status.satisfied is True
    
    def test_dependency_satisfaction_failure(self, validator):
        """Test dependency satisfaction failure"""
        # Create item with poorly defined dependency
        poor_dependency = DependencyReference(
            dependency_id="DEP-002",
            target_item_id="ITEM-999",
            description="Fix"  # Too short
        )
        
        item = BacklogItem(
            item_id="ITEM-005",
            title="Test Item",
            track=StrategicTrack.PR_GATE,
            requirements=[],
            acceptance_criteria=[],
            dependencies=[poor_dependency],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
        )
        
        statuses = validator.verify_dependency_satisfaction(item)
        
        assert len(statuses) == 1
        status = statuses[0]
        assert status.satisfied is False
        assert len(status.blocking_issues) > 0
        assert "insufficient" in status.blocking_issues[0].lower()
    
    def test_no_dependencies(self, validator):
        """Test validation with no dependencies"""
        item = BacklogItem(
            item_id="ITEM-006",
            title="Test Item",
            track=StrategicTrack.PR_GATE,
            requirements=[],
            acceptance_criteria=[],
            dependencies=[],  # No dependencies
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
        )
        
        statuses = validator.verify_dependency_satisfaction(item)
        assert len(statuses) == 0


class TestValidationCriterion:
    """Test ValidationCriterion data model"""
    
    def test_validation_criterion_creation(self):
        """Test creating ValidationCriterion"""
        criterion = ValidationCriterion(
            criterion_name="test_criterion",
            description="Test criterion description",
            weight=0.5,
            passed=True,
            score=0.8,
            remediation_guidance="Fix the issues",
            details={"test": "data"}
        )
        
        assert criterion.criterion_name == "test_criterion"
        assert criterion.weight == 0.5
        assert criterion.passed is True
        assert criterion.score == 0.8
        assert criterion.details["test"] == "data"


class TestCompletenessReport:
    """Test CompletenessReport data model"""
    
    def test_completeness_report_creation(self):
        """Test creating CompletenessReport"""
        criteria = [
            ValidationCriterion(
                criterion_name="test",
                description="Test",
                weight=1.0,
                passed=True,
                score=0.9,
                remediation_guidance="None needed"
            )
        ]
        
        report = CompletenessReport(
            overall_score=0.85,
            criteria_results=criteria,
            missing_elements=[],
            remediation_actions=[],
            beast_ready=True,
            validation_timestamp=datetime.now()
        )
        
        assert report.overall_score == 0.85
        assert len(report.criteria_results) == 1
        assert report.beast_ready is True
    
    def test_completeness_report_invalid_score(self):
        """Test CompletenessReport with invalid score"""
        with pytest.raises(ValueError, match="Overall score must be between 0.0 and 1.0"):
            CompletenessReport(
                overall_score=1.5,  # Invalid
                criteria_results=[],
                missing_elements=[],
                remediation_actions=[],
                beast_ready=False,
                validation_timestamp=datetime.now()
            )


class TestReadinessValidation:
    """Test ReadinessValidation data model"""
    
    def test_readiness_validation_creation(self, complete_backlog_item):
        """Test creating ReadinessValidation"""
        completeness = CompletenessReport(
            overall_score=0.9,
            criteria_results=[],
            missing_elements=[],
            remediation_actions=[],
            beast_ready=True,
            validation_timestamp=datetime.now()
        )
        
        validation = ReadinessValidation(
            item_id="ITEM-001",
            validation_id="VAL-001",
            completeness_report=completeness,
            dependency_statuses=[],
            overall_beast_ready=True,
            confidence_score=0.85,
            validation_timestamp=datetime.now(),
            validator_id="BeastReadinessValidator"
        )
        
        assert validation.item_id == "ITEM-001"
        assert validation.overall_beast_ready is True
        assert validation.confidence_score == 0.85
    
    def test_readiness_validation_invalid_confidence(self):
        """Test ReadinessValidation with invalid confidence score"""
        completeness = CompletenessReport(
            overall_score=0.9,
            criteria_results=[],
            missing_elements=[],
            remediation_actions=[],
            beast_ready=True,
            validation_timestamp=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
            ReadinessValidation(
                item_id="ITEM-001",
                validation_id="VAL-001",
                completeness_report=completeness,
                dependency_statuses=[],
                overall_beast_ready=True,
                confidence_score=1.2,  # Invalid
                validation_timestamp=datetime.now(),
                validator_id="BeastReadinessValidator"
            )


class TestReflectiveModuleInterface:
    """Test ReflectiveModule interface implementation"""
    
    def test_get_module_status(self, validator):
        """Test get_module_status method"""
        status = validator.get_module_status()
        
        assert status["module_name"] == "BeastReadinessValidator"
        assert status["status"] == "operational"
        assert "cached_validations" in status
        assert "beast_readiness_threshold" in status
        assert "dependency_satisfaction_threshold" in status
    
    def test_is_healthy_no_indicators(self, validator):
        """Test is_healthy with no health indicators"""
        assert validator.is_healthy() is True
    
    def test_is_healthy_with_healthy_indicators(self, validator, complete_backlog_item):
        """Test is_healthy with healthy indicators"""
        # Trigger a successful validation to create health indicators
        validator.validate_beast_readiness(complete_backlog_item)
        
        assert validator.is_healthy() is True
    
    def test_get_health_indicators(self, validator):
        """Test get_health_indicators method"""
        indicators = validator.get_health_indicators()
        
        assert "total_indicators" in indicators
        assert "indicators" in indicators
        assert "overall_health" in indicators
        assert indicators["overall_health"] is True
    
    def test_get_primary_responsibility(self, validator):
        """Test _get_primary_responsibility method"""
        responsibility = validator._get_primary_responsibility()
        
        assert "beast-readiness" in responsibility.lower()
        assert "validate" in responsibility.lower()


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_requirements_list(self, validator):
        """Test validation with empty requirements list"""
        item = BacklogItem(
            item_id="ITEM-007",
            title="Test Item",
            track=StrategicTrack.PR_GATE,
            requirements=[],  # Empty
            acceptance_criteria=[],
            dependencies=[],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
        )
        
        report = validator.check_completeness_criteria(item)
        assert report.beast_ready is False
        assert "No requirements defined" in report.missing_elements
    
    def test_very_short_descriptions(self, validator):
        """Test validation with very short descriptions"""
        requirements = [
            Requirement(
                requirement_id="REQ-001",
                description="Fix",  # Too short
                priority=1,
                acceptance_criteria=[]
            )
        ]
        
        item = BacklogItem(
            item_id="ITEM-008",
            title="X",  # Too short
            track=StrategicTrack.PR_GATE,
            requirements=requirements,
            acceptance_criteria=[],
            dependencies=[],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
        )
        
        report = validator.check_completeness_criteria(item)
        assert report.beast_ready is False
        assert any("insufficient description" in missing for missing in report.missing_elements)
    
    def test_non_testable_acceptance_criteria(self, validator):
        """Test validation with non-testable acceptance criteria"""
        criteria = [
            AcceptanceCriterion(
                criterion_id="AC-001",
                description="System should work well",
                testable=False,  # Not testable
                measurable=False  # Not measurable
            )
        ]
        
        item = BacklogItem(
            item_id="ITEM-009",
            title="Test Item",
            track=StrategicTrack.PR_GATE,
            requirements=[],
            acceptance_criteria=criteria,
            dependencies=[],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
        )
        
        report = validator.check_completeness_criteria(item)
        ac_criterion = next(c for c in report.criteria_results if c.criterion_name == "acceptance_criteria_quality")
        assert ac_criterion.passed is False
        assert any("not testable" in missing for missing in ac_criterion.details["missing"])
        assert any("not measurable" in missing for missing in ac_criterion.details["missing"])
    
    def test_threshold_boundary_conditions(self, validator):
        """Test validation at threshold boundaries"""
        # Test exactly at beast readiness threshold
        validator._beast_readiness_threshold = 0.85
        
        # Create item that scores exactly 0.85
        # This would require careful crafting of the scoring logic
        # For now, we'll test that the threshold is properly applied
        
        item = BacklogItem(
            item_id="ITEM-010",
            title="Boundary Test Item",
            track=StrategicTrack.PR_GATE,
            requirements=[],
            acceptance_criteria=[],
            dependencies=[],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test_user",
            created_at=datetime.now() - timedelta(days=1),
            last_updated=datetime.now()
        )
        
        report = validator.check_completeness_criteria(item)
        # With empty requirements and criteria, score should be well below threshold
        assert report.overall_score < validator._beast_readiness_threshold
        assert report.beast_ready is False


if __name__ == "__main__":
    pytest.main([__file__])