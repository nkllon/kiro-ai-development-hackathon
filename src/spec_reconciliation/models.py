"""
Data Models for Spec Consistency and Technical Debt Reconciliation System

This module contains all data models used throughout the spec reconciliation system,
including validation, serialization, and relationship management.
"""

import json
import logging
from dataclasses import dataclass, field, asdict, MISSING
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import hashlib
import re


class ReflectiveModule:
    """
    Base class for all spec reconciliation modules.
    
    Provides common functionality for module status reporting and reflection.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized_at = datetime.now()
    
    def get_module_status(self) -> Dict[str, Any]:
        """
        Get the current status of this module.
        
        Returns:
            Dictionary containing module status information
        """
        return {
            "module_name": self.__class__.__name__,
            "initialized_at": self._initialized_at.isoformat(),
            "status": "active"
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get information about this module.
        
        Returns:
            Dictionary containing module information
        """
        return {
            "module_name": self.__class__.__name__,
            "module_type": "spec_reconciliation",
            "capabilities": self._get_capabilities(),
            "version": "1.0.0"
        }
    
    def _get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this module.
        
        Returns:
            List of capability names
        """
        # Default implementation - subclasses should override
        return ["base_functionality"]


# Enums for type safety and validation

class ValidationResult(Enum):
    """Validation result types"""
    APPROVED = "approved"
    REJECTED = "rejected" 
    REQUIRES_REVIEW = "requires_review"
    REQUIRES_CONSOLIDATION = "requires_consolidation"


class OverlapSeverity(Enum):
    """Overlap severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConsolidationStatus(Enum):
    """Consolidation status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    MERGE_COMPATIBLE = "merge_compatible"
    PRIORITIZE_NEWER = "prioritize_newer"
    PRIORITIZE_MORE_DETAILED = "prioritize_more_detailed"
    MANUAL_REVIEW = "manual_review"
    KEEP_SEPARATE = "keep_separate"


class DriftSeverity(Enum):
    """Severity levels for detected drift"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CorrectionStatus(Enum):
    """Status of automatic corrections"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class ConsistencyLevel(Enum):
    """Consistency level indicators"""
    EXCELLENT = "excellent"  # >95%
    GOOD = "good"  # 85-95%
    FAIR = "fair"  # 70-85%
    POOR = "poor"  # <70%


class PreventionType(Enum):
    """Types of prevention controls"""
    GOVERNANCE = "governance"
    VALIDATION = "validation"
    MONITORING = "monitoring"
    ENFORCEMENT = "enforcement"


# Base validation mixin for all data models

class DataModelMixin:
    """Base mixin providing validation and serialization for all data models"""
    
    def validate(self) -> bool:
        """Validate the data model instance"""
        try:
            # Get dataclass fields to check which are required
            if hasattr(self.__class__, '__dataclass_fields__'):
                for field_name, field_info in self.__class__.__dataclass_fields__.items():
                    field_value = getattr(self, field_name)
                    
                    # Check if field is required (no default value)
                    is_required = (field_info.default is MISSING and field_info.default_factory is MISSING)
                    
                    # Only validate required fields
                    if is_required:
                        if field_value is None:
                            logging.warning(f"Required field {field_name} is None in {self.__class__.__name__}")
                            return False
                        if isinstance(field_value, str) and len(field_value) == 0:
                            logging.warning(f"Required field {field_name} is empty string in {self.__class__.__name__}")
                            return False
            
            return True
        except Exception as e:
            logging.error(f"Validation error in {self.__class__.__name__}: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        try:
            result = {}
            for key, value in asdict(self).items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, set):
                    result[key] = list(value)
                elif isinstance(value, Path):
                    result[key] = str(value)
                else:
                    result[key] = value
            return result
        except Exception as e:
            logging.error(f"Serialization error in {self.__class__.__name__}: {e}")
            return {}
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary"""
        try:
            # Handle datetime fields
            for key, value in data.items():
                if isinstance(value, str) and 'T' in value and ':' in value:
                    try:
                        data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        pass  # Not a datetime string
            return cls(**data)
        except Exception as e:
            logging.error(f"Deserialization error in {cls.__name__}: {e}")
            raise


# Core Analysis Models

@dataclass
class SpecAnalysis(DataModelMixin):
    """Comprehensive analysis of a specification (from design document)"""
    spec_id: str
    overlapping_specs: List[str] = field(default_factory=list)
    conflicting_requirements: List['ConflictReport'] = field(default_factory=list)
    terminology_issues: List['TerminologyIssue'] = field(default_factory=list)
    interface_inconsistencies: List['InterfaceIssue'] = field(default_factory=list)
    consolidation_opportunities: List['ConsolidationOpportunity'] = field(default_factory=list)
    prevention_recommendations: List['PreventionRecommendation'] = field(default_factory=list)
    
    def get_overlap_count(self) -> int:
        """Get total number of overlapping specs"""
        return len(self.overlapping_specs)
    
    def get_critical_issues_count(self) -> int:
        """Get count of critical issues requiring immediate attention"""
        critical_count = 0
        critical_count += len([cr for cr in self.conflicting_requirements if cr.severity == OverlapSeverity.CRITICAL])
        critical_count += len([ti for ti in self.terminology_issues if ti.severity == DriftSeverity.CRITICAL])
        return critical_count


@dataclass
class ConsolidationPlan(DataModelMixin):
    """Detailed plan for consolidating specs (from design document)"""
    target_specs: List[str]
    unified_spec_name: str
    requirement_mapping: Dict[str, str] = field(default_factory=dict)  # original_req_id -> unified_req_id
    interface_standardization: List['InterfaceChange'] = field(default_factory=list)
    terminology_unification: List['TerminologyChange'] = field(default_factory=list)
    migration_steps: List['MigrationStep'] = field(default_factory=list)
    validation_criteria: List['ValidationCriterion'] = field(default_factory=list)
    
    # Additional fields for comprehensive planning
    plan_id: str = field(default_factory=lambda: f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    consolidation_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MERGE_COMPATIBLE
    estimated_effort: int = 0  # hours
    risk_mitigation: List[str] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: ConsolidationStatus = ConsolidationStatus.PENDING
    
    def get_total_migration_steps(self) -> int:
        """Get total number of migration steps"""
        return len(self.migration_steps)
    
    def get_estimated_duration_days(self) -> float:
        """Get estimated duration in days (assuming 8 hours per day)"""
        return self.estimated_effort / 8.0 if self.estimated_effort > 0 else 0


@dataclass
class PreventionControl(DataModelMixin):
    """Prevention control configuration (from design document)"""
    control_type: PreventionType
    trigger_conditions: List['TriggerCondition'] = field(default_factory=list)
    validation_rules: List['ValidationRule'] = field(default_factory=list)
    enforcement_actions: List['EnforcementAction'] = field(default_factory=list)
    escalation_procedures: List['EscalationStep'] = field(default_factory=list)
    monitoring_metrics: List['MonitoringMetric'] = field(default_factory=list)
    
    # Additional fields for control management
    control_id: str = field(default_factory=lambda: f"ctrl_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    name: str = ""
    description: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    
    def is_triggered(self, context: Dict[str, Any]) -> bool:
        """Check if control should be triggered based on context"""
        for condition in self.trigger_conditions:
            if condition.evaluate(context):
                return True
        return False


# Overlap and Conflict Analysis Models

@dataclass
class OverlapAnalysis(DataModelMixin):
    """Comprehensive analysis of overlaps between specs"""
    spec_pairs: List[Tuple[str, str]] = field(default_factory=list)
    functional_overlaps: Dict[str, List[str]] = field(default_factory=dict)
    terminology_conflicts: Dict[str, List[str]] = field(default_factory=dict)
    interface_conflicts: Dict[str, List[str]] = field(default_factory=dict)
    dependency_relationships: Dict[str, List[str]] = field(default_factory=dict)
    consolidation_opportunities: List['ConsolidationOpportunity'] = field(default_factory=list)
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    effort_estimates: Dict[str, int] = field(default_factory=dict)  # hours
    
    # Analysis metadata
    analysis_id: str = field(default_factory=lambda: f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    analyzed_at: datetime = field(default_factory=datetime.now)
    total_specs_analyzed: int = 0
    
    def get_highest_risk_pairs(self) -> List[Tuple[str, str]]:
        """Get spec pairs with highest consolidation risk"""
        return sorted(self.spec_pairs, 
                     key=lambda pair: self.risk_assessment.get(f"{pair[0]}-{pair[1]}", 0.0), 
                     reverse=True)


@dataclass
class ConsolidationOpportunity(DataModelMixin):
    """Represents an opportunity for spec consolidation"""
    target_specs: List[str]
    overlap_percentage: float
    consolidation_type: str  # "merge", "absorb", "split"
    effort_estimate: int  # hours
    risk_level: str  # "low", "medium", "high"
    benefits: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    recommended_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MERGE_COMPATIBLE
    
    # Additional analysis fields
    opportunity_id: str = field(default_factory=lambda: f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    priority_score: float = 0.0
    feasibility_score: float = 0.0
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_priority_score(self) -> float:
        """Calculate priority score based on overlap, effort, and risk"""
        risk_multiplier = {"low": 1.0, "medium": 0.7, "high": 0.4}.get(self.risk_level, 0.5)
        effort_factor = max(0.1, 1.0 - (self.effort_estimate / 100.0))  # Normalize effort
        self.priority_score = self.overlap_percentage * risk_multiplier * effort_factor
        return self.priority_score


# Conflict and Issue Models

@dataclass
class ConflictReport(DataModelMixin):
    """Reports conflicts between specs"""
    conflicting_specs: List[str]
    conflict_type: str
    severity: OverlapSeverity
    description: str
    suggested_resolution: str
    
    # Additional conflict details
    conflict_id: str = field(default_factory=lambda: f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    detected_at: datetime = field(default_factory=datetime.now)
    affected_requirements: List[str] = field(default_factory=list)
    resolution_status: str = "open"  # "open", "in_progress", "resolved", "deferred"


@dataclass
class TerminologyIssue(DataModelMixin):
    """Represents a terminology consistency issue"""
    term: str
    conflicting_definitions: Dict[str, str]  # spec_name -> definition
    severity: DriftSeverity
    affected_specs: List[str]
    recommended_unified_definition: str = ""
    
    # Issue tracking
    issue_id: str = field(default_factory=lambda: f"term_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    detected_at: datetime = field(default_factory=datetime.now)
    resolution_status: str = "open"


@dataclass
class InterfaceIssue(DataModelMixin):
    """Represents an interface consistency issue"""
    interface_name: str
    conflicting_definitions: Dict[str, str]  # spec_name -> interface_definition
    severity: DriftSeverity
    affected_specs: List[str]
    recommended_standard_interface: str = ""
    
    # Issue tracking
    issue_id: str = field(default_factory=lambda: f"iface_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    detected_at: datetime = field(default_factory=datetime.now)
    resolution_status: str = "open"


@dataclass
class PreventionRecommendation(DataModelMixin):
    """Recommendation for preventing future issues"""
    recommendation_type: str  # "governance", "validation", "monitoring", "training"
    description: str
    implementation_steps: List[str]
    priority: str  # "low", "medium", "high", "critical"
    estimated_effort: int  # hours
    
    # Recommendation tracking
    recommendation_id: str = field(default_factory=lambda: f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    implementation_status: str = "proposed"  # "proposed", "approved", "in_progress", "completed"


# Change and Migration Models

@dataclass
class InterfaceChange(DataModelMixin):
    """Represents a change to standardize interfaces"""
    original_interface: str
    standardized_interface: str
    affected_specs: List[str]
    migration_guidance: str
    
    # Change tracking
    change_id: str = field(default_factory=lambda: f"ichange_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    change_type: str = "standardization"  # "standardization", "consolidation", "deprecation"
    impact_level: str = "medium"  # "low", "medium", "high"
    backward_compatible: bool = True


@dataclass
class TerminologyChange(DataModelMixin):
    """Represents a terminology unification change"""
    original_terms: List[str]
    unified_term: str
    affected_specs: List[str]
    definition: str
    
    # Change tracking
    change_id: str = field(default_factory=lambda: f"tchange_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    change_rationale: str = ""
    migration_complexity: str = "low"  # "low", "medium", "high"


@dataclass
class MigrationStep(DataModelMixin):
    """Single step in migration process"""
    step_id: str
    description: str
    prerequisites: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)
    estimated_effort: int = 0  # hours
    
    # Step execution tracking
    status: str = "pending"  # "pending", "in_progress", "completed", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_notes: str = ""


@dataclass
class ValidationCriterion(DataModelMixin):
    """Criteria for validating successful consolidation"""
    criterion_id: str
    description: str
    validation_method: str
    success_threshold: Any
    measurement_approach: str
    
    # Validation tracking
    is_met: Optional[bool] = None
    measured_value: Optional[Any] = None
    validation_date: Optional[datetime] = None
    validation_notes: str = ""


# Traceability Models

@dataclass
class TraceabilityLink(DataModelMixin):
    """Links original requirements to consolidated requirements"""
    original_spec: str
    original_requirement_id: str
    consolidated_spec: str
    consolidated_requirement_id: str
    transformation_type: str  # "merged", "split", "unchanged", "deprecated"
    rationale: str
    
    # Link metadata
    link_id: str = field(default_factory=lambda: f"link_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0  # 0.0 to 1.0


@dataclass
class TraceabilityMap(DataModelMixin):
    """Complete traceability mapping for consolidation"""
    consolidation_id: str
    links: List[TraceabilityLink] = field(default_factory=list)
    impact_analysis: Dict[str, List[str]] = field(default_factory=dict)
    change_log: List[Dict[str, Any]] = field(default_factory=list)
    validation_status: Dict[str, bool] = field(default_factory=dict)
    
    # Map metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    completeness_score: float = 0.0  # 0.0 to 1.0
    
    def update_completeness_score(self) -> float:
        """Calculate and update completeness score based on validation status"""
        if not self.validation_status:
            self.completeness_score = 0.0
        else:
            validated_count = sum(1 for status in self.validation_status.values() if status)
            self.completeness_score = validated_count / len(self.validation_status)
        self.last_updated = datetime.now()
        return self.completeness_score


# Monitoring and Drift Models

@dataclass
class DriftDetection(DataModelMixin):
    """Detected drift in specifications"""
    drift_type: str
    severity: DriftSeverity
    affected_specs: List[str]
    description: str
    detected_at: datetime
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    recommended_actions: List[str] = field(default_factory=list)
    
    # Detection metadata
    detection_id: str = field(default_factory=lambda: f"drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    confidence_level: float = 0.0  # 0.0 to 1.0
    
    def calculate_drift_magnitude(self) -> float:
        """Calculate magnitude of drift based on before/after metrics"""
        if not self.metrics_before or not self.metrics_after:
            return 0.0
        
        total_change = 0.0
        metric_count = 0
        
        for metric_name in self.metrics_before:
            if metric_name in self.metrics_after:
                before_val = self.metrics_before[metric_name]
                after_val = self.metrics_after[metric_name]
                if before_val != 0:
                    change = abs(after_val - before_val) / before_val
                    total_change += change
                    metric_count += 1
        
        return total_change / metric_count if metric_count > 0 else 0.0


@dataclass
class DriftReport(DataModelMixin):
    """Comprehensive drift analysis report"""
    report_id: str
    generated_at: datetime
    overall_drift_score: float
    detected_drifts: List[DriftDetection] = field(default_factory=list)
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    predictive_warnings: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)
    monitoring_recommendations: List[str] = field(default_factory=list)
    
    def get_critical_drifts(self) -> List[DriftDetection]:
        """Get all critical severity drifts"""
        return [drift for drift in self.detected_drifts if drift.severity == DriftSeverity.CRITICAL]
    
    def get_drift_summary(self) -> Dict[str, int]:
        """Get summary count of drifts by severity"""
        summary = {severity.value: 0 for severity in DriftSeverity}
        for drift in self.detected_drifts:
            summary[drift.severity.value] += 1
        return summary


# Control and Workflow Models

@dataclass
class TriggerCondition(DataModelMixin):
    """Condition that triggers a prevention control"""
    condition_type: str  # "threshold", "pattern", "event", "schedule"
    condition_expression: str  # The actual condition logic
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if condition is met given context"""
        # This would contain the actual evaluation logic
        # For now, return a simple implementation
        try:
            if self.condition_type == "threshold":
                metric_name = self.parameters.get("metric")
                threshold = self.parameters.get("threshold", 0)
                operator = self.parameters.get("operator", ">")
                
                if metric_name in context:
                    value = context[metric_name]
                    if operator == ">":
                        return value > threshold
                    elif operator == "<":
                        return value < threshold
                    elif operator == ">=":
                        return value >= threshold
                    elif operator == "<=":
                        return value <= threshold
                    elif operator == "==":
                        return value == threshold
            
            return False
        except Exception:
            return False


@dataclass
class ValidationRule(DataModelMixin):
    """Rule for validating spec changes"""
    rule_type: str  # "terminology", "interface", "structure", "content"
    rule_expression: str
    error_message: str
    severity: str = "error"  # "error", "warning", "info"
    
    def validate_content(self, content: str) -> Tuple[bool, str]:
        """Validate content against this rule"""
        # Simplified validation - would contain actual rule logic
        try:
            if self.rule_type == "terminology":
                # Check for forbidden terms or patterns
                forbidden_patterns = self.rule_expression.split("|")
                for pattern in forbidden_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return False, self.error_message
            
            return True, ""
        except Exception as e:
            return False, f"Validation error: {e}"


@dataclass
class EnforcementAction(DataModelMixin):
    """Action to enforce compliance"""
    action_type: str  # "block", "warn", "auto_correct", "escalate"
    action_parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the enforcement action"""
        result = {
            "action_type": self.action_type,
            "executed_at": datetime.now().isoformat(),
            "success": False,
            "message": ""
        }
        
        try:
            if self.action_type == "block":
                result["success"] = True
                result["message"] = "Action blocked due to policy violation"
            elif self.action_type == "warn":
                result["success"] = True
                result["message"] = f"Warning: {self.description}"
            elif self.action_type == "escalate":
                result["success"] = True
                result["message"] = "Issue escalated for manual review"
            
            return result
        except Exception as e:
            result["message"] = f"Enforcement action failed: {e}"
            return result


@dataclass
class EscalationStep(DataModelMixin):
    """Step in escalation procedure"""
    step_order: int
    escalation_target: str  # "tech_lead", "architect", "review_board"
    escalation_criteria: str
    timeout_hours: int = 24
    
    def should_escalate(self, context: Dict[str, Any]) -> bool:
        """Check if escalation criteria are met"""
        # Simplified escalation logic
        return context.get("requires_escalation", False)


@dataclass
class MonitoringMetric(DataModelMixin):
    """Metric for monitoring prevention control effectiveness"""
    metric_name: str
    metric_type: str  # "counter", "gauge", "histogram"
    description: str
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    last_updated: Optional[datetime] = None
    
    def update_value(self, new_value: float):
        """Update metric value"""
        self.current_value = new_value
        self.last_updated = datetime.now()
    
    def is_within_target(self) -> Optional[bool]:
        """Check if current value meets target"""
        if self.current_value is None or self.target_value is None:
            return None
        return abs(self.current_value - self.target_value) <= (self.target_value * 0.1)  # 10% tolerance


# Consistency and Validation Models

@dataclass
class TerminologyReport(DataModelMixin):
    """Report on terminology consistency"""
    consistent_terms: Set[str] = field(default_factory=set)
    inconsistent_terms: Dict[str, List[str]] = field(default_factory=dict)  # term -> variations
    new_terms: Set[str] = field(default_factory=set)
    deprecated_terms: Set[str] = field(default_factory=set)
    consistency_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    # Report metadata
    report_id: str = field(default_factory=lambda: f"term_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    generated_at: datetime = field(default_factory=datetime.now)
    
    def calculate_consistency_score(self) -> float:
        """Calculate overall terminology consistency score"""
        total_terms = len(self.consistent_terms) + len(self.inconsistent_terms)
        if total_terms == 0:
            self.consistency_score = 1.0
        else:
            self.consistency_score = len(self.consistent_terms) / total_terms
        return self.consistency_score


@dataclass
class ComplianceReport(DataModelMixin):
    """Report on interface compliance"""
    compliant_interfaces: List[str] = field(default_factory=list)
    non_compliant_interfaces: List[str] = field(default_factory=list)
    compliance_issues: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    # Report metadata
    report_id: str = field(default_factory=lambda: f"comp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PatternReport(DataModelMixin):
    """Report on design pattern consistency"""
    consistent_patterns: List[str] = field(default_factory=list)
    inconsistent_patterns: List[str] = field(default_factory=list)
    pattern_violations: List[str] = field(default_factory=list)
    pattern_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    # Report metadata
    report_id: str = field(default_factory=lambda: f"pattern_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsistencyMetrics(DataModelMixin):
    """Overall consistency metrics"""
    terminology_score: float = 0.0
    interface_score: float = 0.0
    pattern_score: float = 0.0
    overall_score: float = 0.0
    consistency_level: ConsistencyLevel = ConsistencyLevel.POOR
    improvement_areas: List[str] = field(default_factory=list)
    
    # Metrics metadata
    metrics_id: str = field(default_factory=lambda: f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    calculated_at: datetime = field(default_factory=datetime.now)
    
    def calculate_overall_score(self) -> float:
        """Calculate overall consistency score"""
        scores = [self.terminology_score, self.interface_score, self.pattern_score]
        valid_scores = [s for s in scores if s > 0]
        
        if valid_scores:
            self.overall_score = sum(valid_scores) / len(valid_scores)
        else:
            self.overall_score = 0.0
        
        # Determine consistency level
        if self.overall_score >= 0.95:
            self.consistency_level = ConsistencyLevel.EXCELLENT
        elif self.overall_score >= 0.85:
            self.consistency_level = ConsistencyLevel.GOOD
        elif self.overall_score >= 0.70:
            self.consistency_level = ConsistencyLevel.FAIR
        else:
            self.consistency_level = ConsistencyLevel.POOR
        
        return self.overall_score


# Governance Models

@dataclass
class SpecProposal(DataModelMixin):
    """Represents a proposed new specification"""
    name: str
    content: str
    requirements: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    terminology: Set[str] = field(default_factory=set)
    functionality_keywords: Set[str] = field(default_factory=set)
    
    # Proposal metadata
    proposal_id: str = field(default_factory=lambda: f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    submitted_at: datetime = field(default_factory=datetime.now)
    submitted_by: str = ""
    justification: str = ""


@dataclass
class OverlapReport(DataModelMixin):
    """Reports functional overlaps between specs"""
    spec_pairs: List[Tuple[str, str]] = field(default_factory=list)
    overlap_percentage: float = 0.0
    overlapping_functionality: List[str] = field(default_factory=list)
    severity: OverlapSeverity = OverlapSeverity.NONE
    consolidation_recommendation: str = ""
    
    # Report metadata
    report_id: str = field(default_factory=lambda: f"overlap_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalStatus(DataModelMixin):
    """Status of approval workflow"""
    status: ValidationResult
    reviewer: str
    timestamp: str
    comments: str = ""
    required_actions: List[str] = field(default_factory=list)
    
    # Approval metadata
    approval_id: str = field(default_factory=lambda: f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}")


# Workflow Models

@dataclass
class CorrectionWorkflow(DataModelMixin):
    """Automated correction workflow"""
    workflow_id: str
    correction_type: str
    target_specs: List[str]
    correction_steps: List[str] = field(default_factory=list)
    status: CorrectionStatus = CorrectionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    success_rate: float = 0.0
    escalation_reason: Optional[str] = None
    
    # Workflow execution details
    execution_log: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    
    def add_log_entry(self, message: str):
        """Add entry to execution log"""
        timestamp = datetime.now().isoformat()
        self.execution_log.append(f"[{timestamp}] {message}")
    
    def can_retry(self) -> bool:
        """Check if workflow can be retried"""
        return self.retry_count < self.max_retries and self.status == CorrectionStatus.FAILED


@dataclass
class ArchitecturalDecision(DataModelMixin):
    """Architectural decision for validation"""
    decision_id: str
    title: str
    description: str
    rationale: str
    affected_components: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    decision_date: datetime = field(default_factory=datetime.now)
    
    # Decision tracking
    status: str = "proposed"  # "proposed", "approved", "implemented", "deprecated"
    decision_maker: str = ""
    impact_assessment: Dict[str, Any] = field(default_factory=dict)


# Additional Analysis Models

@dataclass
class RequirementAnalysis(DataModelMixin):
    """Analysis of a single requirement"""
    requirement_id: str
    content: str
    functionality_keywords: Set[str] = field(default_factory=set)
    acceptance_criteria: List[str] = field(default_factory=list)
    stakeholder_personas: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    quality_score: float = 0.0
    
    # Analysis metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    analysis_version: str = "1.0"
    
    def calculate_quality_score(self) -> float:
        """Calculate quality score based on various factors"""
        score = 0.0
        
        # Check if content is substantial
        if len(self.content) > 50:
            score += 0.2
        
        # Check if acceptance criteria exist
        if self.acceptance_criteria:
            score += 0.3
        
        # Check if stakeholders are identified
        if self.stakeholder_personas:
            score += 0.2
        
        # Check if functionality keywords are identified
        if self.functionality_keywords:
            score += 0.3
        
        self.quality_score = min(1.0, score)
        return self.quality_score


@dataclass
class InconsistencyReport(DataModelMixin):
    """Report on terminology inconsistencies"""
    report_id: str
    generated_at: datetime
    terminology_drift: Dict[str, List[str]] = field(default_factory=dict)  # term -> new variations
    new_terminology: Set[str] = field(default_factory=set)
    deprecated_usage: Set[str] = field(default_factory=set)
    consistency_degradation: float = 0.0
    correction_suggestions: List[str] = field(default_factory=list)
    
    def get_total_inconsistencies(self) -> int:
        """Get total count of inconsistencies"""
        return len(self.terminology_drift) + len(self.new_terminology) + len(self.deprecated_usage)


# Model Registry for dynamic access
MODEL_REGISTRY = {
    # Base Classes
    'ReflectiveModule': ReflectiveModule,
    
    # Core Analysis Models
    'SpecAnalysis': SpecAnalysis,
    'ConsolidationPlan': ConsolidationPlan,
    'PreventionControl': PreventionControl,
    
    # Overlap and Conflict Models
    'OverlapAnalysis': OverlapAnalysis,
    'ConsolidationOpportunity': ConsolidationOpportunity,
    'ConflictReport': ConflictReport,
    'TerminologyIssue': TerminologyIssue,
    'InterfaceIssue': InterfaceIssue,
    'PreventionRecommendation': PreventionRecommendation,
    
    # Change and Migration Models
    'InterfaceChange': InterfaceChange,
    'TerminologyChange': TerminologyChange,
    'MigrationStep': MigrationStep,
    'ValidationCriterion': ValidationCriterion,
    
    # Traceability Models
    'TraceabilityLink': TraceabilityLink,
    'TraceabilityMap': TraceabilityMap,
    
    # Monitoring and Drift Models
    'DriftDetection': DriftDetection,
    'DriftReport': DriftReport,
    
    # Control and Workflow Models
    'TriggerCondition': TriggerCondition,
    'ValidationRule': ValidationRule,
    'EnforcementAction': EnforcementAction,
    'EscalationStep': EscalationStep,
    'MonitoringMetric': MonitoringMetric,
    
    # Consistency and Validation Models
    'TerminologyReport': TerminologyReport,
    'ComplianceReport': ComplianceReport,
    'PatternReport': PatternReport,
    'ConsistencyMetrics': ConsistencyMetrics,
    
    # Governance Models
    'SpecProposal': SpecProposal,
    'OverlapReport': OverlapReport,
    'ApprovalStatus': ApprovalStatus,
    
    # Workflow Models
    'CorrectionWorkflow': CorrectionWorkflow,
    'ArchitecturalDecision': ArchitecturalDecision,
    
    # Additional Models
    'RequirementAnalysis': RequirementAnalysis,
    'InconsistencyReport': InconsistencyReport,
}


def get_model_class(model_name: str):
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name)


def create_model_instance(model_name: str, **kwargs):
    """Create model instance by name"""
    model_class = get_model_class(model_name)
    if model_class:
        return model_class(**kwargs)
    raise ValueError(f"Unknown model: {model_name}")


def validate_all_models() -> Dict[str, bool]:
    """Validate all model classes can be instantiated"""
    results = {}
    for model_name, model_class in MODEL_REGISTRY.items():
        try:
            # Try to create instance with minimal required fields
            if hasattr(model_class, '__dataclass_fields__'):
                required_fields = {}
                for field_name, field_info in model_class.__dataclass_fields__.items():
                    # Check if field has no default value (is required)
                    if field_info.default is MISSING and field_info.default_factory is MISSING:
                        # This is a required field, provide a default value based on type
                        field_type = field_info.type
                        if field_type == str:
                            required_fields[field_name] = f"test_{field_name}"
                        elif field_type == int:
                            required_fields[field_name] = 0
                        elif field_type == float:
                            required_fields[field_name] = 0.0
                        elif field_type == bool:
                            required_fields[field_name] = False
                        elif field_type == datetime:
                            required_fields[field_name] = datetime.now()
                        elif hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                            required_fields[field_name] = []
                        elif hasattr(field_type, '__origin__') and field_type.__origin__ is dict:
                            required_fields[field_name] = {}
                        elif hasattr(field_type, '__origin__') and field_type.__origin__ is set:
                            required_fields[field_name] = set()
                        else:
                            # For enum types and other complex types, try to get a default
                            if hasattr(field_type, '__members__'):  # Enum
                                required_fields[field_name] = list(field_type.__members__.values())[0]
                            else:
                                required_fields[field_name] = f"test_{field_name}"
                
                instance = model_class(**required_fields)
                results[model_name] = instance.validate() if hasattr(instance, 'validate') else True
            else:
                results[model_name] = True
        except Exception as e:
            logging.error(f"Failed to validate model {model_name}: {e}")
            results[model_name] = False
    
    return results