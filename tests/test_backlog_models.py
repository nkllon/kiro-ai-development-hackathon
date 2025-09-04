"""Unit tests for OpenFlow Backlog Management data models

This module provides comprehensive testing for all data models,
enums, validation logic, and serialization behavior.
"""

import pytest
from datetime import datetime, timedelta
from dataclasses import asdict
from src.beast_mode.backlog.models import (
    BacklogItem,
    DependencySpec,
    MPMValidation,
    Requirement,
    AcceptanceCriterion,
    DependencyReference,
    GhostbustersValidation,
)
from src.beast_mode.backlog.enums import (
    StrategicTrack,
    DependencyType,
    RiskLevel,
    BeastReadinessStatus,
    ApprovalStatus,
    StakeholderType,
)


class TestEnums:
    """Test all enum values and behavior"""
    
    def test_strategic_track_values(self):
        """Test StrategicTrack enum has correct values"""
        assert StrategicTrack.PR_GATE.value == "pr_gate"
        assert StrategicTrack.ZERO_FRICTION.value == "zero_friction"
        assert StrategicTrack.COMMUNITY.value == "community"
        assert StrategicTrack.PROOF_ENGINE.value == "proof_engine"
    
    def test_dependency_type_values(self):
        """Test DependencyType enum has correct values"""
        assert DependencyType.BLOCKING.value == "blocking"
        assert DependencyType.INFORMATIONAL.value == "informational"
        assert DependencyType.RESOURCE_SHARED.value == "resource_shared"
    
    def test_risk_level_values(self):
        """Test RiskLevel enum has correct values"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
    
    def test_beast_readiness_status_values(self):
        """Test BeastReadinessStatus enum has correct values"""
        assert BeastReadinessStatus.DRAFT.value == "draft"
        assert BeastReadinessStatus.MPM_REVIEW.value == "mpm_review"
        assert BeastReadinessStatus.GHOSTBUSTERS_VALIDATION.value == "ghostbusters_validation"
        assert BeastReadinessStatus.BEAST_READY.value == "beast_ready"
        assert BeastReadinessStatus.IN_EXECUTION.value == "in_execution"
        assert BeastReadinessStatus.COMPLETED.value == "completed"
        assert BeastReadinessStatus.BLOCKED.value == "blocked"

class TestRequirement:
    """Test Requirement data model"""
    
    def test_valid_requirement_creation(self):
        """Test creating a valid requirement"""
        req = Requirement(
            requirement_id="REQ-001",
            description="Test requirement",
            priority=1,
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        assert req.requirement_id == "REQ-001"
        assert req.description == "Test requirement"
        assert req.priority == 1
        assert len(req.acceptance_criteria) == 2
    
    def test_requirement_immutability(self):
        """Test that requirement is immutable"""
        req = Requirement(
            requirement_id="REQ-001",
            description="Test requirement",
            priority=1
        )
        with pytest.raises(AttributeError):
            req.requirement_id = "REQ-002"
    
    def test_empty_requirement_id_validation(self):
        """Test validation for empty requirement ID"""
        with pytest.raises(ValueError, match="Requirement ID cannot be empty"):
            Requirement(
                requirement_id="",
                description="Test requirement",
                priority=1
            )
    
    def test_empty_description_validation(self):
        """Test validation for empty description"""
        with pytest.raises(ValueError, match="Requirement description cannot be empty"):
            Requirement(
                requirement_id="REQ-001",
                description="",
                priority=1
            )
    
    def test_invalid_priority_validation(self):
        """Test validation for invalid priority"""
        with pytest.raises(ValueError, match="Priority must be positive"):
            Requirement(
                requirement_id="REQ-001",
                description="Test requirement",
                priority=0
            )


class TestAcceptanceCriterion:
    """Test AcceptanceCriterion data model"""
    
    def test_valid_criterion_creation(self):
        """Test creating a valid acceptance criterion"""
        criterion = AcceptanceCriterion(
            criterion_id="AC-001",
            description="Test criterion",
            testable=True,
            measurable=True
        )
        assert criterion.criterion_id == "AC-001"
        assert criterion.description == "Test criterion"
        assert criterion.testable is True
        assert criterion.measurable is True
    
    def test_criterion_defaults(self):
        """Test default values for criterion"""
        criterion = AcceptanceCriterion(
            criterion_id="AC-001",
            description="Test criterion"
        )
        assert criterion.testable is True
        assert criterion.measurable is True
    
    def test_empty_criterion_id_validation(self):
        """Test validation for empty criterion ID"""
        with pytest.raises(ValueError, match="Criterion ID cannot be empty"):
            AcceptanceCriterion(
                criterion_id="",
                description="Test criterion"
            )
    
    def test_empty_description_validation(self):
        """Test validation for empty description"""
        with pytest.raises(ValueError, match="Criterion description cannot be empty"):
            AcceptanceCriterion(
                criterion_id="AC-001",
                description=""
            )


class TestDependencyReference:
    """Test DependencyReference data model"""
    
    def test_valid_dependency_reference_creation(self):
        """Test creating a valid dependency reference"""
        dep_ref = DependencyReference(
            dependency_id="DEP-001",
            target_item_id="ITEM-002",
            description="Depends on item 2"
        )
        assert dep_ref.dependency_id == "DEP-001"
        assert dep_ref.target_item_id == "ITEM-002"
        assert dep_ref.description == "Depends on item 2"
    
    def test_empty_dependency_id_validation(self):
        """Test validation for empty dependency ID"""
        with pytest.raises(ValueError, match="Dependency ID cannot be empty"):
            DependencyReference(
                dependency_id="",
                target_item_id="ITEM-002",
                description="Test dependency"
            )
    
    def test_empty_target_item_id_validation(self):
        """Test validation for empty target item ID"""
        with pytest.raises(ValueError, match="Target item ID cannot be empty"):
            DependencyReference(
                dependency_id="DEP-001",
                target_item_id="",
                description="Test dependency"
            )


class TestGhostbustersValidation:
    """Test GhostbustersValidation data model"""
    
    def test_valid_ghostbusters_validation_creation(self):
        """Test creating a valid ghostbusters validation"""
        validation = GhostbustersValidation(
            validation_id="GB-001",
            validated_by="ghostbusters-system",
            validation_timestamp=datetime.now(),
            perspectives_validated=[StakeholderType.DEVELOPER, StakeholderType.OPERATIONS],
            gaps_found=["Missing security perspective"],
            recommendations=["Add security review"],
            overall_score=0.8,
            passed=True
        )
        assert validation.validation_id == "GB-001"
        assert validation.validated_by == "ghostbusters-system"
        assert len(validation.perspectives_validated) == 2
        assert validation.overall_score == 0.8
        assert validation.passed is True
    
    def test_empty_validation_id_validation(self):
        """Test validation for empty validation ID"""
        with pytest.raises(ValueError, match="Validation ID cannot be empty"):
            GhostbustersValidation(
                validation_id="",
                validated_by="ghostbusters-system",
                validation_timestamp=datetime.now(),
                perspectives_validated=[StakeholderType.DEVELOPER]
            )
    
    def test_invalid_overall_score_validation(self):
        """Test validation for invalid overall score"""
        with pytest.raises(ValueError, match="Overall score must be between 0.0 and 1.0"):
            GhostbustersValidation(
                validation_id="GB-001",
                validated_by="ghostbusters-system",
                validation_timestamp=datetime.now(),
                perspectives_validated=[StakeholderType.DEVELOPER],
                overall_score=1.5
            )


class TestMPMValidation:
    """Test MPMValidation data model"""
    
    def test_valid_mpm_validation_creation(self):
        """Test creating a valid MPM validation"""
        validation = MPMValidation(
            validation_id="MPM-001",
            validated_by="mpm-user",
            validation_timestamp=datetime.now(),
            completeness_score=0.9,
            dependency_confidence=0.8,
            business_alignment=0.95,
            beast_readiness_assessment="Ready for beast execution",
            required_improvements=["Add more test cases"],
            approval_status=ApprovalStatus.APPROVED
        )
        assert validation.validation_id == "MPM-001"
        assert validation.completeness_score == 0.9
        assert validation.approval_status == ApprovalStatus.APPROVED
    
    def test_mpm_validation_defaults(self):
        """Test default values for MPM validation"""
        validation = MPMValidation(
            validation_id="MPM-001",
            validated_by="mpm-user",
            validation_timestamp=datetime.now(),
            completeness_score=0.9,
            dependency_confidence=0.8,
            business_alignment=0.95,
            beast_readiness_assessment="Ready"
        )
        assert validation.approval_status == ApprovalStatus.PENDING
        assert len(validation.required_improvements) == 0
    
    def test_invalid_completeness_score_validation(self):
        """Test validation for invalid completeness score"""
        with pytest.raises(ValueError, match="Completeness score must be between 0.0 and 1.0"):
            MPMValidation(
                validation_id="MPM-001",
                validated_by="mpm-user",
                validation_timestamp=datetime.now(),
                completeness_score=1.5,
                dependency_confidence=0.8,
                business_alignment=0.95,
                beast_readiness_assessment="Ready"
            )


class TestDependencySpec:
    """Test DependencySpec data model"""
    
    def test_valid_dependency_spec_creation(self):
        """Test creating a valid dependency spec"""
        dep_spec = DependencySpec(
            dependency_id="DEP-001",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="ITEM-002",
            target_track=StrategicTrack.PR_GATE,
            satisfaction_criteria="Item must be completed",
            estimated_completion=datetime.now() + timedelta(days=7),
            risk_level=RiskLevel.MEDIUM,
            mitigation_strategy="Parallel development"
        )
        assert dep_spec.dependency_id == "DEP-001"
        assert dep_spec.dependency_type == DependencyType.BLOCKING
        assert dep_spec.target_track == StrategicTrack.PR_GATE
        assert dep_spec.risk_level == RiskLevel.MEDIUM
    
    def test_dependency_spec_optional_fields(self):
        """Test dependency spec with optional fields"""
        dep_spec = DependencySpec(
            dependency_id="DEP-001",
            dependency_type=DependencyType.INFORMATIONAL,
            target_item_id="ITEM-002",
            target_track=None,
            satisfaction_criteria="Item must be completed",
            estimated_completion=None,
            risk_level=RiskLevel.LOW
        )
        assert dep_spec.target_track is None
        assert dep_spec.estimated_completion is None
        assert dep_spec.mitigation_strategy is None
    
    def test_empty_dependency_id_validation(self):
        """Test validation for empty dependency ID"""
        with pytest.raises(ValueError, match="Dependency ID cannot be empty"):
            DependencySpec(
                dependency_id="",
                dependency_type=DependencyType.BLOCKING,
                target_item_id="ITEM-002",
                target_track=None,
                satisfaction_criteria="Item must be completed",
                estimated_completion=None,
                risk_level=RiskLevel.LOW
            )


class TestBacklogItem:
    """Test BacklogItem data model"""
    
    def create_sample_backlog_item(self):
        """Helper method to create a sample backlog item"""
        now = datetime.now()
        return BacklogItem(
            item_id="ITEM-001",
            title="Sample backlog item",
            track=StrategicTrack.PR_GATE,
            requirements=[
                Requirement(
                    requirement_id="REQ-001",
                    description="Test requirement",
                    priority=1
                )
            ],
            acceptance_criteria=[
                AcceptanceCriterion(
                    criterion_id="AC-001",
                    description="Test criterion"
                )
            ],
            dependencies=[
                DependencyReference(
                    dependency_id="DEP-001",
                    target_item_id="ITEM-002",
                    description="Depends on item 2"
                )
            ],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test-user",
            created_at=now,
            last_updated=now
        )
    
    def test_valid_backlog_item_creation(self):
        """Test creating a valid backlog item"""
        item = self.create_sample_backlog_item()
        assert item.item_id == "ITEM-001"
        assert item.title == "Sample backlog item"
        assert item.track == StrategicTrack.PR_GATE
        assert len(item.requirements) == 1
        assert len(item.acceptance_criteria) == 1
        assert len(item.dependencies) == 1
        assert item.beast_readiness_status == BeastReadinessStatus.DRAFT
    
    def test_backlog_item_immutability(self):
        """Test that backlog item is immutable"""
        item = self.create_sample_backlog_item()
        with pytest.raises(AttributeError):
            item.title = "Modified title"
    
    def test_empty_item_id_validation(self):
        """Test validation for empty item ID"""
        now = datetime.now()
        with pytest.raises(ValueError, match="Item ID cannot be empty"):
            BacklogItem(
                item_id="",
                title="Sample item",
                track=StrategicTrack.PR_GATE,
                requirements=[],
                acceptance_criteria=[],
                dependencies=[],
                beast_readiness_status=BeastReadinessStatus.DRAFT,
                created_by="test-user",
                created_at=now,
                last_updated=now
            )
    
    def test_future_created_at_validation(self):
        """Test validation for future created_at date"""
        future_date = datetime.now() + timedelta(days=1)
        with pytest.raises(ValueError, match="Created at cannot be in the future"):
            BacklogItem(
                item_id="ITEM-001",
                title="Sample item",
                track=StrategicTrack.PR_GATE,
                requirements=[],
                acceptance_criteria=[],
                dependencies=[],
                beast_readiness_status=BeastReadinessStatus.DRAFT,
                created_by="test-user",
                created_at=future_date,
                last_updated=future_date
            )


class TestSerialization:
    """Test serialization and deserialization of data models"""
    
    def test_backlog_item_serialization(self):
        """Test that backlog item can be serialized to dict"""
        now = datetime.now()
        item = BacklogItem(
            item_id="ITEM-001",
            title="Sample item",
            track=StrategicTrack.PR_GATE,
            requirements=[],
            acceptance_criteria=[],
            dependencies=[],
            beast_readiness_status=BeastReadinessStatus.DRAFT,
            created_by="test-user",
            created_at=now,
            last_updated=now
        )
        
        item_dict = asdict(item)
        assert item_dict["item_id"] == "ITEM-001"
        assert item_dict["title"] == "Sample item"
        assert item_dict["track"] == StrategicTrack.PR_GATE
        assert item_dict["beast_readiness_status"] == BeastReadinessStatus.DRAFT
    
    def test_dependency_spec_serialization(self):
        """Test that dependency spec can be serialized to dict"""
        dep_spec = DependencySpec(
            dependency_id="DEP-001",
            dependency_type=DependencyType.BLOCKING,
            target_item_id="ITEM-002",
            target_track=StrategicTrack.COMMUNITY,
            satisfaction_criteria="Must be completed",
            estimated_completion=None,
            risk_level=RiskLevel.HIGH
        )
        
        dep_dict = asdict(dep_spec)
        assert dep_dict["dependency_id"] == "DEP-001"
        assert dep_dict["dependency_type"] == DependencyType.BLOCKING
        assert dep_dict["target_track"] == StrategicTrack.COMMUNITY
        assert dep_dict["risk_level"] == RiskLevel.HIGH
    
    def test_mpm_validation_serialization(self):
        """Test that MPM validation can be serialized to dict"""
        validation = MPMValidation(
            validation_id="MPM-001",
            validated_by="mpm-user",
            validation_timestamp=datetime.now(),
            completeness_score=0.9,
            dependency_confidence=0.8,
            business_alignment=0.95,
            beast_readiness_assessment="Ready"
        )
        
        validation_dict = asdict(validation)
        assert validation_dict["validation_id"] == "MPM-001"
        assert validation_dict["completeness_score"] == 0.9
        assert validation_dict["approval_status"] == ApprovalStatus.PENDING