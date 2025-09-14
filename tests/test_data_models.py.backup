"""
Unit tests for spec reconciliation data models

Tests all data model classes for validation, serialization, and functionality.
"""

import json
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.spec_reconciliation.models import (
    # Enums
    ValidationResult, OverlapSeverity, ConsolidationStatus, ConflictResolutionStrategy,
    DriftSeverity, CorrectionStatus, ConsistencyLevel, PreventionType,
    
    # Core Analysis Models
    SpecAnalysis, ConsolidationPlan, PreventionControl,
    
    # Overlap and Conflict Models
    OverlapAnalysis, ConsolidationOpportunity, ConflictReport, TerminologyIssue,
    InterfaceIssue, PreventionRecommendation,
    
    # Change and Migration Models
    InterfaceChange, TerminologyChange, MigrationStep, ValidationCriterion,
    
    # Traceability Models
    TraceabilityLink, TraceabilityMap,
    
    # Monitoring and Drift Models
    DriftDetection, DriftReport,
    
    # Control and Workflow Models
    TriggerCondition, ValidationRule, EnforcementAction, EscalationStep,
    MonitoringMetric,
    
    # Consistency and Validation Models
    TerminologyReport, ComplianceReport, PatternReport, ConsistencyMetrics,
    
    # Governance Models
    SpecProposal, OverlapReport, ApprovalStatus,
    
    # Workflow Models
    CorrectionWorkflow, ArchitecturalDecision,
    
    # Additional Models
    RequirementAnalysis, InconsistencyReport,
    
    # Utility functions
    get_model_class, create_model_instance, validate_all_models
)


class TestDataModelValidation:
    """Test data model validation functionality"""
    
    def test_spec_analysis_validation(self):
        """Test SpecAnalysis data model validation"""
        # Valid instance
        spec_analysis = SpecAnalysis(
            spec_id="test-spec-001",
            overlapping_specs=["spec-a", "spec-b"],
            conflicting_requirements=[],
            terminology_issues=[],
            interface_inconsistencies=[],
            consolidation_opportunities=[],
            prevention_recommendations=[]
        )
        
        assert spec_analysis.validate() is True
        assert spec_analysis.get_overlap_count() == 2
        assert spec_analysis.get_critical_issues_count() == 0
        
        # Test serialization
        data_dict = spec_analysis.to_dict()
        assert data_dict["spec_id"] == "test-spec-001"
        assert len(data_dict["overlapping_specs"]) == 2
        
        json_str = spec_analysis.to_json()
        assert "test-spec-001" in json_str
    
    def test_consolidation_plan_validation(self):
        """Test ConsolidationPlan data model validation"""
        plan = ConsolidationPlan(
            target_specs=["spec-1", "spec-2"],
            unified_spec_name="unified-spec",
            requirement_mapping={"req-1": "unified-req-1"},
            estimated_effort=40
        )
        
        assert plan.validate() is True
        assert plan.get_total_migration_steps() == 0
        assert plan.get_estimated_duration_days() == 5.0  # 40 hours / 8 hours per day
        
        # Test with migration steps
        plan.migration_steps = [
            MigrationStep(step_id="step-1", description="Test step", estimated_effort=8),
            MigrationStep(step_id="step-2", description="Test step 2", estimated_effort=16)
        ]
        assert plan.get_total_migration_steps() == 2
    
    def test_prevention_control_validation(self):
        """Test PreventionControl data model validation"""
        trigger_condition = TriggerCondition(
            condition_type="threshold",
            condition_expression="overlap_percentage > 0.5",
            parameters={"metric": "overlap_percentage", "threshold": 0.5, "operator": ">"}
        )
        
        control = PreventionControl(
            control_type=PreventionType.GOVERNANCE,
            trigger_conditions=[trigger_condition],
            name="Overlap Prevention Control",
            description="Prevents spec overlap above threshold"
        )
        
        assert control.validate() is True
        
        # Test trigger evaluation
        context = {"overlap_percentage": 0.7}
        assert control.is_triggered(context) is True
        
        context = {"overlap_percentage": 0.3}
        assert control.is_triggered(context) is False


class TestOverlapAnalysisModels:
    """Test overlap analysis related models"""
    
    def test_overlap_analysis_data_model(self):
        """Test OverlapAnalysis data structure and attributes"""
        overlap_analysis = OverlapAnalysis(
            spec_pairs=[("spec-a", "spec-b"), ("spec-b", "spec-c")],
            functional_overlaps={"authentication": ["spec-a", "spec-b"]},
            terminology_conflicts={"user": ["spec-a", "spec-c"]},
            interface_conflicts={"UserService": ["spec-a", "spec-b"]},
            dependency_relationships={"spec-a": ["spec-b"]},
            risk_assessment={"spec-a-spec-b": 0.8, "spec-b-spec-c": 0.3},
            effort_estimates={"spec-a-spec-b": 24, "spec-b-spec-c": 8},
            total_specs_analyzed=3
        )
        
        assert overlap_analysis.validate() is True
        assert len(overlap_analysis.spec_pairs) == 2
        assert overlap_analysis.total_specs_analyzed == 3
        
        # Test highest risk pairs
        highest_risk = overlap_analysis.get_highest_risk_pairs()
        assert highest_risk[0] == ("spec-a", "spec-b")  # Highest risk first
        
        # Test serialization
        data_dict = overlap_analysis.to_dict()
        assert "spec_pairs" in data_dict
        assert "functional_overlaps" in data_dict
    
    def test_consolidation_opportunity_model(self):
        """Test ConsolidationOpportunity model functionality"""
        opportunity = ConsolidationOpportunity(
            target_specs=["spec-1", "spec-2"],
            overlap_percentage=0.75,
            consolidation_type="merge",
            effort_estimate=32,
            risk_level="medium",
            benefits=["Reduced duplication", "Clearer interfaces"],
            challenges=["Complex migration", "Stakeholder alignment"],
            recommended_strategy=ConflictResolutionStrategy.MERGE_COMPATIBLE
        )
        
        assert opportunity.validate() is True
        
        # Test priority score calculation
        priority_score = opportunity.calculate_priority_score()
        assert 0.0 <= priority_score <= 1.0
        assert opportunity.priority_score == priority_score
        
        # Test serialization
        json_str = opportunity.to_json()
        parsed = json.loads(json_str)
        assert parsed["overlap_percentage"] == 0.75
        assert parsed["consolidation_type"] == "merge"


class TestConflictAndIssueModels:
    """Test conflict and issue tracking models"""
    
    def test_conflict_report_model(self):
        """Test ConflictReport model"""
        conflict = ConflictReport(
            conflicting_specs=["spec-a", "spec-b"],
            conflict_type="interface_mismatch",
            severity=OverlapSeverity.HIGH,
            description="Conflicting interface definitions for UserService",
            suggested_resolution="Standardize on spec-a interface definition",
            affected_requirements=["REQ-001", "REQ-002"]
        )
        
        assert conflict.validate() is True
        assert conflict.severity == OverlapSeverity.HIGH
        assert len(conflict.affected_requirements) == 2
        assert conflict.resolution_status == "open"
    
    def test_terminology_issue_model(self):
        """Test TerminologyIssue model"""
        issue = TerminologyIssue(
            term="user_account",
            conflicting_definitions={
                "spec-a": "A registered user with authentication credentials",
                "spec-b": "An account holder with billing information"
            },
            severity=DriftSeverity.MEDIUM,
            affected_specs=["spec-a", "spec-b"],
            recommended_unified_definition="A registered user with authentication and account management capabilities"
        )
        
        assert issue.validate() is True
        assert len(issue.conflicting_definitions) == 2
        assert issue.severity == DriftSeverity.MEDIUM
    
    def test_interface_issue_model(self):
        """Test InterfaceIssue model"""
        issue = InterfaceIssue(
            interface_name="UserRepository",
            conflicting_definitions={
                "spec-a": "interface UserRepository { findById(id: string): User }",
                "spec-b": "interface UserRepository { getUser(userId: number): UserEntity }"
            },
            severity=DriftSeverity.HIGH,
            affected_specs=["spec-a", "spec-b"],
            recommended_standard_interface="interface UserRepository { findById(id: string): User }"
        )
        
        assert issue.validate() is True
        assert issue.severity == DriftSeverity.HIGH


class TestTraceabilityModels:
    """Test traceability tracking models"""
    
    def test_traceability_link_model(self):
        """Test TraceabilityLink model"""
        link = TraceabilityLink(
            original_spec="legacy-spec",
            original_requirement_id="REQ-001",
            consolidated_spec="unified-spec",
            consolidated_requirement_id="UNIFIED-REQ-001",
            transformation_type="merged",
            rationale="Combined with similar requirement from another spec",
            confidence_score=0.95
        )
        
        assert link.validate() is True
        assert link.transformation_type == "merged"
        assert link.confidence_score == 0.95
    
    def test_traceability_map_data_model(self):
        """Test TraceabilityMap and TraceabilityLink structures"""
        links = [
            TraceabilityLink(
                original_spec="spec-a",
                original_requirement_id="REQ-001",
                consolidated_spec="unified-spec",
                consolidated_requirement_id="UNIFIED-REQ-001",
                transformation_type="merged",
                rationale="Combined authentication requirements"
            ),
            TraceabilityLink(
                original_spec="spec-b",
                original_requirement_id="REQ-002",
                consolidated_spec="unified-spec",
                consolidated_requirement_id="UNIFIED-REQ-001",
                transformation_type="merged",
                rationale="Combined authentication requirements"
            )
        ]
        
        traceability_map = TraceabilityMap(
            consolidation_id="consolidation-001",
            links=links,
            impact_analysis={"authentication": ["spec-a", "spec-b"]},
            validation_status={"REQ-001": True, "REQ-002": True}
        )
        
        assert traceability_map.validate() is True
        assert len(traceability_map.links) == 2
        
        # Test completeness score calculation
        completeness = traceability_map.update_completeness_score()
        assert completeness == 1.0  # All validations passed
        
        # Test with partial validation
        traceability_map.validation_status["REQ-003"] = False
        completeness = traceability_map.update_completeness_score()
        assert completeness == 2.0 / 3.0  # 2 out of 3 passed


class TestMonitoringModels:
    """Test monitoring and drift detection models"""
    
    def test_drift_detection_model(self):
        """Test DriftDetection model"""
        drift = DriftDetection(
            drift_type="terminology_inconsistency",
            severity=DriftSeverity.MEDIUM,
            affected_specs=["spec-a", "spec-b"],
            description="New terminology variations detected",
            detected_at=datetime.now(),
            metrics_before={"consistency_score": 0.95},
            metrics_after={"consistency_score": 0.82},
            recommended_actions=["Update terminology registry", "Notify spec owners"]
        )
        
        assert drift.validate() is True
        assert drift.severity == DriftSeverity.MEDIUM
        
        # Test drift magnitude calculation
        magnitude = drift.calculate_drift_magnitude()
        assert magnitude > 0  # Should detect the consistency score drop
    
    def test_drift_report_data_model(self):
        """Test DriftReport and DriftDetection data models"""
        drift_detections = [
            DriftDetection(
                drift_type="terminology",
                severity=DriftSeverity.HIGH,
                affected_specs=["spec-1"],
                description="High severity terminology drift",
                detected_at=datetime.now(),
                metrics_before={"score": 0.9},
                metrics_after={"score": 0.6}
            ),
            DriftDetection(
                drift_type="interface",
                severity=DriftSeverity.LOW,
                affected_specs=["spec-2"],
                description="Low severity interface drift",
                detected_at=datetime.now(),
                metrics_before={"score": 0.8},
                metrics_after={"score": 0.75}
            )
        ]
        
        drift_report = DriftReport(
            report_id="drift-report-001",
            generated_at=datetime.now(),
            overall_drift_score=0.7,
            detected_drifts=drift_detections,
            trend_analysis={"trend": "degrading"},
            predictive_warnings=["Consistency may drop below threshold"],
            immediate_actions=["Review terminology changes"],
            monitoring_recommendations=["Increase monitoring frequency"]
        )
        
        assert drift_report.validate() is True
        assert len(drift_report.detected_drifts) == 2
        
        # Test critical drifts filtering
        critical_drifts = drift_report.get_critical_drifts()
        assert len(critical_drifts) == 0  # No critical drifts in test data
        
        # Test drift summary
        summary = drift_report.get_drift_summary()
        assert summary[DriftSeverity.HIGH.value] == 1
        assert summary[DriftSeverity.LOW.value] == 1
        assert summary[DriftSeverity.CRITICAL.value] == 0


class TestControlModels:
    """Test control and workflow models"""
    
    def test_trigger_condition_evaluation(self):
        """Test TriggerCondition evaluation logic"""
        # Threshold condition
        condition = TriggerCondition(
            condition_type="threshold",
            condition_expression="consistency_score < 0.8",
            parameters={
                "metric": "consistency_score",
                "threshold": 0.8,
                "operator": "<"
            }
        )
        
        # Test evaluation
        context = {"consistency_score": 0.7}
        assert condition.evaluate(context) is True
        
        context = {"consistency_score": 0.9}
        assert condition.evaluate(context) is False
    
    def test_validation_rule_model(self):
        """Test ValidationRule model"""
        rule = ValidationRule(
            rule_type="terminology",
            rule_expression="deprecated_term_1|deprecated_term_2",
            error_message="Use of deprecated terminology detected",
            severity="warning"
        )
        
        assert rule.validate() is True
        
        # Test content validation
        is_valid, message = rule.validate_content("This uses deprecated_term_1 in the text")
        assert is_valid is False
        assert "deprecated terminology" in message
        
        is_valid, message = rule.validate_content("This uses acceptable terminology")
        assert is_valid is True
        assert message == ""
    
    def test_enforcement_action_model(self):
        """Test EnforcementAction model"""
        action = EnforcementAction(
            action_type="warn",
            action_parameters={"severity": "medium"},
            description="Issue warning for policy violation"
        )
        
        assert action.validate() is True
        
        # Test action execution
        result = action.execute({})
        assert result["action_type"] == "warn"
        assert result["success"] is True
        assert "Warning" in result["message"]
    
    def test_monitoring_metric_model(self):
        """Test MonitoringMetric model"""
        metric = MonitoringMetric(
            metric_name="consistency_score",
            metric_type="gauge",
            description="Overall consistency score",
            target_value=0.95
        )
        
        assert metric.validate() is True
        
        # Test value updates
        metric.update_value(0.92)
        assert metric.current_value == 0.92
        assert metric.last_updated is not None
        
        # Test target comparison
        assert metric.is_within_target() is True  # 0.92 is within 10% of 0.95
        
        metric.update_value(0.80)
        assert metric.is_within_target() is False  # 0.80 is not within 10% of 0.95


class TestConsistencyModels:
    """Test consistency and validation models"""
    
    def test_terminology_report_model(self):
        """Test TerminologyReport model"""
        report = TerminologyReport(
            consistent_terms={"user", "account", "service"},
            inconsistent_terms={"login": ["signin", "logon"], "user": ["customer", "client"]},
            new_terms={"oauth_token"},
            deprecated_terms={"legacy_auth"},
            recommendations=["Standardize login terminology", "Update deprecated terms"]
        )
        
        assert report.validate() is True
        
        # Test consistency score calculation
        score = report.calculate_consistency_score()
        # 3 consistent terms, 2 inconsistent terms = 3/5 = 0.6
        assert score == 0.6
        assert report.consistency_score == 0.6
    
    def test_consistency_metrics_model(self):
        """Test ConsistencyMetrics model"""
        metrics = ConsistencyMetrics(
            terminology_score=0.85,
            interface_score=0.90,
            pattern_score=0.80,
            improvement_areas=["Terminology standardization", "Pattern compliance"]
        )
        
        assert metrics.validate() is True
        
        # Test overall score calculation
        overall_score = metrics.calculate_overall_score()
        expected_score = (0.85 + 0.90 + 0.80) / 3
        assert abs(overall_score - expected_score) < 0.01
        
        # Test consistency level determination
        assert metrics.consistency_level == ConsistencyLevel.GOOD  # 85% average


class TestWorkflowModels:
    """Test workflow and process models"""
    
    def test_correction_workflow_model(self):
        """Test CorrectionWorkflow model"""
        workflow = CorrectionWorkflow(
            workflow_id="workflow-001",
            correction_type="terminology_standardization",
            target_specs=["spec-a", "spec-b"],
            correction_steps=["Identify conflicts", "Apply corrections", "Validate results"],
            status=CorrectionStatus.PENDING
        )
        
        assert workflow.validate() is True
        assert workflow.can_retry() is False  # Not failed yet
        
        # Test log entry
        workflow.add_log_entry("Starting workflow execution")
        assert len(workflow.execution_log) == 1
        assert "Starting workflow execution" in workflow.execution_log[0]
        
        # Test retry logic
        workflow.status = CorrectionStatus.FAILED
        assert workflow.can_retry() is True
        
        workflow.retry_count = 3
        assert workflow.can_retry() is False  # Exceeded max retries
    
    def test_architectural_decision_model(self):
        """Test ArchitecturalDecision model"""
        decision = ArchitecturalDecision(
            decision_id="ADR-001",
            title="Standardize Authentication Interface",
            description="All authentication services must implement IAuthenticationService",
            rationale="Ensures consistent authentication patterns across services",
            affected_components=["UserService", "AuthService", "TokenService"],
            constraints=["Must maintain backward compatibility"],
            alternatives_considered=["Custom interfaces per service", "No standardization"]
        )
        
        assert decision.validate() is True
        assert decision.status == "proposed"
        assert len(decision.affected_components) == 3


class TestRequirementAnalysisModel:
    """Test requirement analysis model"""
    
    def test_requirement_analysis_model(self):
        """Test RequirementAnalysis model functionality"""
        analysis = RequirementAnalysis(
            requirement_id="REQ-001",
            content="As a user, I want to authenticate using OAuth2 so that I can securely access the system",
            functionality_keywords={"authentication", "oauth2", "security"},
            acceptance_criteria=[
                "User can login with OAuth2 provider",
                "System validates OAuth2 tokens",
                "Failed authentication is logged"
            ],
            stakeholder_personas=["End User", "Security Administrator"],
            complexity_score=0.7
        )
        
        assert analysis.validate() is True
        
        # Test quality score calculation
        quality_score = analysis.calculate_quality_score()
        assert quality_score == 1.0  # All quality factors present
        assert analysis.quality_score == 1.0
        
        # Test with minimal content
        minimal_analysis = RequirementAnalysis(
            requirement_id="REQ-002",
            content="Short requirement"  # Less than 50 characters
        )
        
        quality_score = minimal_analysis.calculate_quality_score()
        assert quality_score < 1.0  # Should have lower quality score


class TestModelUtilities:
    """Test model utility functions"""
    
    def test_get_model_class(self):
        """Test get_model_class utility function"""
        model_class = get_model_class("SpecAnalysis")
        assert model_class == SpecAnalysis
        
        model_class = get_model_class("NonExistentModel")
        assert model_class is None
    
    def test_create_model_instance(self):
        """Test create_model_instance utility function"""
        instance = create_model_instance(
            "SpecAnalysis",
            spec_id="test-spec"
        )
        assert isinstance(instance, SpecAnalysis)
        assert instance.spec_id == "test-spec"
        
        # Test with invalid model name
        with pytest.raises(ValueError):
            create_model_instance("NonExistentModel")
    
    def test_validate_all_models(self):
        """Test validate_all_models utility function"""
        results = validate_all_models()
        
        # Should return results for all models
        assert len(results) > 0
        
        # Most models should validate successfully
        successful_validations = sum(1 for result in results.values() if result)
        total_models = len(results)
        success_rate = successful_validations / total_models
        
        assert success_rate >= 0.8  # At least 80% should validate successfully


class TestModelSerialization:
    """Test model serialization and deserialization"""
    
    def test_json_serialization_roundtrip(self):
        """Test JSON serialization and deserialization roundtrip"""
        original = SpecAnalysis(
            spec_id="test-spec-001",
            overlapping_specs=["spec-a", "spec-b"],
            conflicting_requirements=[],
            terminology_issues=[],
            interface_inconsistencies=[],
            consolidation_opportunities=[],
            prevention_recommendations=[]
        )
        
        # Serialize to JSON
        json_str = original.to_json()
        assert isinstance(json_str, str)
        
        # Parse JSON and recreate object
        data = json.loads(json_str)
        recreated = SpecAnalysis.from_dict(data)
        
        assert recreated.spec_id == original.spec_id
        assert recreated.overlapping_specs == original.overlapping_specs
    
    def test_datetime_serialization(self):
        """Test datetime field serialization"""
        now = datetime.now()
        drift = DriftDetection(
            drift_type="test",
            severity=DriftSeverity.LOW,
            affected_specs=["spec-1"],
            description="Test drift",
            detected_at=now
        )
        
        # Serialize to dict
        data_dict = drift.to_dict()
        assert isinstance(data_dict["detected_at"], str)
        assert "T" in data_dict["detected_at"]  # ISO format
        
        # Test JSON serialization
        json_str = drift.to_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed["detected_at"], str)
    
    def test_enum_serialization(self):
        """Test enum field serialization"""
        conflict = ConflictReport(
            conflicting_specs=["spec-a", "spec-b"],
            conflict_type="interface",
            severity=OverlapSeverity.HIGH,
            description="Test conflict",
            suggested_resolution="Test resolution"
        )
        
        # Serialize to dict
        data_dict = conflict.to_dict()
        assert data_dict["severity"] == "high"  # Enum value, not enum object
        
        # Test JSON serialization
        json_str = conflict.to_json()
        parsed = json.loads(json_str)
        assert parsed["severity"] == "high"


if __name__ == "__main__":
    pytest.main([__file__])