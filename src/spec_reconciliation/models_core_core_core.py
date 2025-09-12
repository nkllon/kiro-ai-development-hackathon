"""
Models Core Core Core

This module was extracted from models_core_core.py
as part of RM-DDD compliance refactoring.
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
        return {'module_name': self.__class__.__name__, 'initialized_at': self._initialized_at.isoformat(), 'status': 'active'}

    def get_module_info(self) -> Dict[str, Any]:
        """
        Get information about this module.
        
        Returns:
            Dictionary containing module information
        """
        return {'module_name': self.__class__.__name__, 'module_type': 'spec_reconciliation', 'capabilities': self._get_capabilities(), 'version': '1.0.0'}

    def _get_capabilities(self) -> List[str]:
        """
        Get the capabilities of this module.
        
        Returns:
            List of capability names
        """
        return ['base_functionality']

class ValidationResult(Enum):
    """Validation result types"""
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REQUIRES_REVIEW = 'requires_review'
    REQUIRES_CONSOLIDATION = 'requires_consolidation'

class OverlapSeverity(Enum):
    """Overlap severity levels"""
    NONE = 'none'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class ConsolidationStatus(Enum):
    """Consolidation status types"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REQUIRES_MANUAL_REVIEW = 'requires_manual_review'

class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    MERGE_COMPATIBLE = 'merge_compatible'
    PRIORITIZE_NEWER = 'prioritize_newer'
    PRIORITIZE_MORE_DETAILED = 'prioritize_more_detailed'
    MANUAL_REVIEW = 'manual_review'
    KEEP_SEPARATE = 'keep_separate'

class DriftSeverity(Enum):
    """Severity levels for detected drift"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class CorrectionStatus(Enum):
    """Status of automatic corrections"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    ESCALATED = 'escalated'

class ConsistencyLevel(Enum):
    """Consistency level indicators"""
    EXCELLENT = 'excellent'
    GOOD = 'good'
    FAIR = 'fair'
    POOR = 'poor'

class PreventionType(Enum):
    """Types of prevention controls"""
    GOVERNANCE = 'governance'
    VALIDATION = 'validation'
    MONITORING = 'monitoring'
    ENFORCEMENT = 'enforcement'

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
    requirement_mapping: Dict[str, str] = field(default_factory=dict)
    interface_standardization: List['InterfaceChange'] = field(default_factory=list)
    terminology_unification: List['TerminologyChange'] = field(default_factory=list)
    migration_steps: List['MigrationStep'] = field(default_factory=list)
    validation_criteria: List['ValidationCriterion'] = field(default_factory=list)
    plan_id: str = field(default_factory=lambda: f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    consolidation_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MERGE_COMPATIBLE
    estimated_effort: int = 0
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
    control_id: str = field(default_factory=lambda: f"ctrl_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    name: str = ''
    description: str = ''
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None

    def is_triggered(self, context: Dict[str, Any]) -> bool:
        """Check if control should be triggered based on context"""
        for condition in self.trigger_conditions:
            if condition.evaluate(context):
                return True
        return False

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
    effort_estimates: Dict[str, int] = field(default_factory=dict)
    analysis_id: str = field(default_factory=lambda: f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    analyzed_at: datetime = field(default_factory=datetime.now)
    total_specs_analyzed: int = 0

    def get_highest_risk_pairs(self) -> List[Tuple[str, str]]:
        """Get spec pairs with highest consolidation risk"""
        return sorted(self.spec_pairs, key=lambda pair: self.risk_assessment.get(f'{pair[0]}-{pair[1]}', 0.0), reverse=True)

@dataclass
class ConsolidationOpportunity(DataModelMixin):
    """Represents an opportunity for spec consolidation"""
    target_specs: List[str]
    overlap_percentage: float
    consolidation_type: str
    effort_estimate: int
    risk_level: str
    benefits: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    recommended_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MERGE_COMPATIBLE
    opportunity_id: str = field(default_factory=lambda: f"opp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    priority_score: float = 0.0
    feasibility_score: float = 0.0
    impact_assessment: Dict[str, Any] = field(default_factory=dict)

    def calculate_priority_score(self) -> float:
        """Calculate priority score based on overlap, effort, and risk"""
        risk_multiplier = {'low': 1.0, 'medium': 0.7, 'high': 0.4}.get(self.risk_level, 0.5)
        effort_factor = max(0.1, 1.0 - self.effort_estimate / 100.0)
        self.priority_score = self.overlap_percentage * risk_multiplier * effort_factor
        return self.priority_score

@dataclass
class ConflictReport(DataModelMixin):
    """Reports conflicts between specs"""
    conflicting_specs: List[str]
    conflict_type: str
    severity: OverlapSeverity
    description: str
    suggested_resolution: str
    conflict_id: str = field(default_factory=lambda: f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    detected_at: datetime = field(default_factory=datetime.now)
    affected_requirements: List[str] = field(default_factory=list)
    resolution_status: str = 'open'

@dataclass
class TerminologyIssue(DataModelMixin):
    """Represents a terminology consistency issue"""
    term: str
    conflicting_definitions: Dict[str, str]
    severity: DriftSeverity
    affected_specs: List[str]
    recommended_unified_definition: str = ''
    issue_id: str = field(default_factory=lambda: f"term_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    detected_at: datetime = field(default_factory=datetime.now)
    resolution_status: str = 'open'

@dataclass
class InterfaceIssue(DataModelMixin):
    """Represents an interface consistency issue"""
    interface_name: str
    conflicting_definitions: Dict[str, str]
    severity: DriftSeverity
    affected_specs: List[str]
    recommended_standard_interface: str = ''
    issue_id: str = field(default_factory=lambda: f"iface_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    detected_at: datetime = field(default_factory=datetime.now)
    resolution_status: str = 'open'

@dataclass
class PreventionRecommendation(DataModelMixin):
    """Recommendation for preventing future issues"""
    recommendation_type: str
    description: str
    implementation_steps: List[str]
    priority: str
    estimated_effort: int
    recommendation_id: str = field(default_factory=lambda: f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    implementation_status: str = 'proposed'

@dataclass
class InterfaceChange(DataModelMixin):
    """Represents a change to standardize interfaces"""
    original_interface: str
    standardized_interface: str
    affected_specs: List[str]
    migration_guidance: str
    change_id: str = field(default_factory=lambda: f"ichange_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    change_type: str = 'standardization'
    impact_level: str = 'medium'
    backward_compatible: bool = True

@dataclass
class TerminologyChange(DataModelMixin):
    """Represents a terminology unification change"""
    original_terms: List[str]
    unified_term: str
    affected_specs: List[str]
    definition: str
    change_id: str = field(default_factory=lambda: f"tchange_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    change_rationale: str = ''
    migration_complexity: str = 'low'

@dataclass
class MigrationStep(DataModelMixin):
    """Single step in migration process"""
    step_id: str
    description: str
    prerequisites: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)
    estimated_effort: int = 0
    status: str = 'pending'
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_notes: str = ''

@dataclass
class ValidationCriterion(DataModelMixin):
    """Criteria for validating successful consolidation"""
    criterion_id: str
    description: str
    validation_method: str
    success_threshold: Any
    measurement_approach: str
    is_met: Optional[bool] = None
    measured_value: Optional[Any] = None
    validation_date: Optional[datetime] = None
    validation_notes: str = ''

@dataclass
class TraceabilityLink(DataModelMixin):
    """Links original requirements to consolidated requirements"""
    original_spec: str
    original_requirement_id: str
    consolidated_spec: str
    consolidated_requirement_id: str
    transformation_type: str
    rationale: str
    link_id: str = field(default_factory=lambda: f"link_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0

@dataclass
class TraceabilityMap(DataModelMixin):
    """Complete traceability mapping for consolidation"""
    consolidation_id: str
    links: List[TraceabilityLink] = field(default_factory=list)
    impact_analysis: Dict[str, List[str]] = field(default_factory=dict)
    change_log: List[Dict[str, Any]] = field(default_factory=list)
    validation_status: Dict[str, bool] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    completeness_score: float = 0.0

    def update_completeness_score(self) -> float:
        """Calculate and update completeness score based on validation status"""
        if not self.validation_status:
            self.completeness_score = 0.0
        else:
            validated_count = sum((1 for status in self.validation_status.values() if status))
            self.completeness_score = validated_count / len(self.validation_status)
        self.last_updated = datetime.now()
        return self.completeness_score

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
    detection_id: str = field(default_factory=lambda: f"drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    confidence_level: float = 0.0

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

@dataclass
class TriggerCondition(DataModelMixin):
    """Condition that triggers a prevention control"""
    condition_type: str
    condition_expression: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if condition is met given context"""
        try:
            if self.condition_type == 'threshold':
                metric_name = self.parameters.get('metric')
                threshold = self.parameters.get('threshold', 0)
                operator = self.parameters.get('operator', '>')
                if metric_name in context:
                    value = context[metric_name]
                    if operator == '>':
                        return value > threshold
                    elif operator == '<':
                        return value < threshold
                    elif operator == '>=':
                        return value >= threshold
                    elif operator == '<=':
                        return value <= threshold
                    elif operator == '==':
                        return value == threshold
            return False
        except Exception:
            return False

@dataclass
class ValidationRule(DataModelMixin):
    """Rule for validating spec changes"""
    rule_type: str
    rule_expression: str
    error_message: str
    severity: str = 'error'

    def validate_content(self, content: str) -> Tuple[bool, str]:
        """Validate content against this rule"""
        try:
            if self.rule_type == 'terminology':
                forbidden_patterns = self.rule_expression.split('|')
                for pattern in forbidden_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return (False, self.error_message)
            return (True, '')
        except Exception as e:
            return (False, f'Validation error: {e}')

@dataclass
class EnforcementAction(DataModelMixin):
    """Action to enforce compliance"""
    action_type: str
    action_parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ''

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the enforcement action"""
        result = {'action_type': self.action_type, 'executed_at': datetime.now().isoformat(), 'success': False, 'message': ''}
        try:
            if self.action_type == 'block':
                result['success'] = True
                result['message'] = 'Action blocked due to policy violation'
            elif self.action_type == 'warn':
                result['success'] = True
                result['message'] = f'Warning: {self.description}'
            elif self.action_type == 'escalate':
                result['success'] = True
                result['message'] = 'Issue escalated for manual review'
            return result
        except Exception as e:
            result['message'] = f'Enforcement action failed: {e}'
            return result

@dataclass
class EscalationStep(DataModelMixin):
    """Step in escalation procedure"""
    step_order: int
    escalation_target: str
    escalation_criteria: str
    timeout_hours: int = 24

    def should_escalate(self, context: Dict[str, Any]) -> bool:
        """Check if escalation criteria are met"""
        return context.get('requires_escalation', False)

@dataclass
class MonitoringMetric(DataModelMixin):
    """Metric for monitoring prevention control effectiveness"""
    metric_name: str
    metric_type: str
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
        return abs(self.current_value - self.target_value) <= self.target_value * 0.1

@dataclass
class TerminologyReport(DataModelMixin):
    """Report on terminology consistency"""
    consistent_terms: Set[str] = field(default_factory=set)
    inconsistent_terms: Dict[str, List[str]] = field(default_factory=dict)
    new_terms: Set[str] = field(default_factory=set)
    deprecated_terms: Set[str] = field(default_factory=set)
    consistency_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
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
        if self.overall_score >= 0.95:
            self.consistency_level = ConsistencyLevel.EXCELLENT
        elif self.overall_score >= 0.85:
            self.consistency_level = ConsistencyLevel.GOOD
        elif self.overall_score >= 0.7:
            self.consistency_level = ConsistencyLevel.FAIR
        else:
            self.consistency_level = ConsistencyLevel.POOR
        return self.overall_score

@dataclass
class SpecProposal(DataModelMixin):
    """Represents a proposed new specification"""
    name: str
    content: str
    requirements: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    terminology: Set[str] = field(default_factory=set)
    functionality_keywords: Set[str] = field(default_factory=set)
    proposal_id: str = field(default_factory=lambda: f"proposal_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    submitted_at: datetime = field(default_factory=datetime.now)
    submitted_by: str = ''
    justification: str = ''

@dataclass
class OverlapReport(DataModelMixin):
    """Reports functional overlaps between specs"""
    spec_pairs: List[Tuple[str, str]] = field(default_factory=list)
    overlap_percentage: float = 0.0
    overlapping_functionality: List[str] = field(default_factory=list)
    severity: OverlapSeverity = OverlapSeverity.NONE
    consolidation_recommendation: str = ''
    report_id: str = field(default_factory=lambda: f"overlap_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    generated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ApprovalStatus(DataModelMixin):
    """Status of approval workflow"""
    status: ValidationResult
    reviewer: str
    timestamp: str
    comments: str = ''
    required_actions: List[str] = field(default_factory=list)
    approval_id: str = field(default_factory=lambda: f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

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
    execution_log: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    def add_log_entry(self, message: str):
        """Add entry to execution log"""
        timestamp = datetime.now().isoformat()
        self.execution_log.append(f'[{timestamp}] {message}')

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
    status: str = 'proposed'
    decision_maker: str = ''
    impact_assessment: Dict[str, Any] = field(default_factory=dict)

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
    analyzed_at: datetime = field(default_factory=datetime.now)
    analysis_version: str = '1.0'

    def calculate_quality_score(self) -> float:
        """Calculate quality score based on various factors"""
        score = 0.0
        if len(self.content) > 50:
            score += 0.2
        if self.acceptance_criteria:
            score += 0.3
        if self.stakeholder_personas:
            score += 0.2
        if self.functionality_keywords:
            score += 0.3
        self.quality_score = min(1.0, score)
        return self.quality_score

@dataclass
class InconsistencyReport(DataModelMixin):
    """Report on terminology inconsistencies"""
    report_id: str
    generated_at: datetime
    terminology_drift: Dict[str, List[str]] = field(default_factory=dict)
    new_terminology: Set[str] = field(default_factory=set)
    deprecated_usage: Set[str] = field(default_factory=set)
    consistency_degradation: float = 0.0
    correction_suggestions: List[str] = field(default_factory=list)

    def get_total_inconsistencies(self) -> int:
        """Get total count of inconsistencies"""
        return len(self.terminology_drift) + len(self.new_terminology) + len(self.deprecated_usage)

def get_model_class(model_name: str):
    """Get model class by name"""
    return MODEL_REGISTRY.get(model_name)

def create_model_instance(model_name: str, **kwargs):
    """Create model instance by name"""
    model_class = get_model_class(model_name)
    if model_class:
        return model_class(**kwargs)
    raise ValueError(f'Unknown model: {model_name}')

def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    self._initialized_at = datetime.now()

def get_module_status(self) -> Dict[str, Any]:
    """
        Get the current status of this module.
        
        Returns:
            Dictionary containing module status information
        """
    return {'module_name': self.__class__.__name__, 'initialized_at': self._initialized_at.isoformat(), 'status': 'active'}

def get_module_info(self) -> Dict[str, Any]:
    """
        Get information about this module.
        
        Returns:
            Dictionary containing module information
        """
    return {'module_name': self.__class__.__name__, 'module_type': 'spec_reconciliation', 'capabilities': self._get_capabilities(), 'version': '1.0.0'}

def _get_capabilities(self) -> List[str]:
    """
        Get the capabilities of this module.
        
        Returns:
            List of capability names
        """
    return ['base_functionality']

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
        logging.error(f'Serialization error in {self.__class__.__name__}: {e}')
        return {}

def to_json(self) -> str:
    """Convert to JSON string"""
    return json.dumps(self.to_dict(), indent=2, default=str)

@classmethod
def from_dict(cls, data: Dict[str, Any]):
    """Create instance from dictionary"""
    try:
        for key, value in data.items():
            if isinstance(value, str) and 'T' in value and (':' in value):
                try:
                    data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    pass
        return cls(**data)
    except Exception as e:
        logging.error(f'Deserialization error in {cls.__name__}: {e}')
        raise

def get_overlap_count(self) -> int:
    """Get total number of overlapping specs"""
    return len(self.overlapping_specs)

def get_critical_issues_count(self) -> int:
    """Get count of critical issues requiring immediate attention"""
    critical_count = 0
    critical_count += len([cr for cr in self.conflicting_requirements if cr.severity == OverlapSeverity.CRITICAL])
    critical_count += len([ti for ti in self.terminology_issues if ti.severity == DriftSeverity.CRITICAL])
    return critical_count

def get_total_migration_steps(self) -> int:
    """Get total number of migration steps"""
    return len(self.migration_steps)

def get_estimated_duration_days(self) -> float:
    """Get estimated duration in days (assuming 8 hours per day)"""
    return self.estimated_effort / 8.0 if self.estimated_effort > 0 else 0

def is_triggered(self, context: Dict[str, Any]) -> bool:
    """Check if control should be triggered based on context"""
    for condition in self.trigger_conditions:
        if condition.evaluate(context):
            return True
    return False

def get_highest_risk_pairs(self) -> List[Tuple[str, str]]:
    """Get spec pairs with highest consolidation risk"""
    return sorted(self.spec_pairs, key=lambda pair: self.risk_assessment.get(f'{pair[0]}-{pair[1]}', 0.0), reverse=True)

def calculate_priority_score(self) -> float:
    """Calculate priority score based on overlap, effort, and risk"""
    risk_multiplier = {'low': 1.0, 'medium': 0.7, 'high': 0.4}.get(self.risk_level, 0.5)
    effort_factor = max(0.1, 1.0 - self.effort_estimate / 100.0)
    self.priority_score = self.overlap_percentage * risk_multiplier * effort_factor
    return self.priority_score

def update_completeness_score(self) -> float:
    """Calculate and update completeness score based on validation status"""
    if not self.validation_status:
        self.completeness_score = 0.0
    else:
        validated_count = sum((1 for status in self.validation_status.values() if status))
        self.completeness_score = validated_count / len(self.validation_status)
    self.last_updated = datetime.now()
    return self.completeness_score

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

def get_critical_drifts(self) -> List[DriftDetection]:
    """Get all critical severity drifts"""
    return [drift for drift in self.detected_drifts if drift.severity == DriftSeverity.CRITICAL]

def get_drift_summary(self) -> Dict[str, int]:
    """Get summary count of drifts by severity"""
    summary = {severity.value: 0 for severity in DriftSeverity}
    for drift in self.detected_drifts:
        summary[drift.severity.value] += 1
    return summary

def evaluate(self, context: Dict[str, Any]) -> bool:
    """Evaluate if condition is met given context"""
    try:
        if self.condition_type == 'threshold':
            metric_name = self.parameters.get('metric')
            threshold = self.parameters.get('threshold', 0)
            operator = self.parameters.get('operator', '>')
            if metric_name in context:
                value = context[metric_name]
                if operator == '>':
                    return value > threshold
                elif operator == '<':
                    return value < threshold
                elif operator == '>=':
                    return value >= threshold
                elif operator == '<=':
                    return value <= threshold
                elif operator == '==':
                    return value == threshold
        return False
    except Exception:
        return False

def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the enforcement action"""
    result = {'action_type': self.action_type, 'executed_at': datetime.now().isoformat(), 'success': False, 'message': ''}
    try:
        if self.action_type == 'block':
            result['success'] = True
            result['message'] = 'Action blocked due to policy violation'
        elif self.action_type == 'warn':
            result['success'] = True
            result['message'] = f'Warning: {self.description}'
        elif self.action_type == 'escalate':
            result['success'] = True
            result['message'] = 'Issue escalated for manual review'
        return result
    except Exception as e:
        result['message'] = f'Enforcement action failed: {e}'
        return result

def should_escalate(self, context: Dict[str, Any]) -> bool:
    """Check if escalation criteria are met"""
    return context.get('requires_escalation', False)

def update_value(self, new_value: float):
    """Update metric value"""
    self.current_value = new_value
    self.last_updated = datetime.now()

def is_within_target(self) -> Optional[bool]:
    """Check if current value meets target"""
    if self.current_value is None or self.target_value is None:
        return None
    return abs(self.current_value - self.target_value) <= self.target_value * 0.1

def calculate_consistency_score(self) -> float:
    """Calculate overall terminology consistency score"""
    total_terms = len(self.consistent_terms) + len(self.inconsistent_terms)
    if total_terms == 0:
        self.consistency_score = 1.0
    else:
        self.consistency_score = len(self.consistent_terms) / total_terms
    return self.consistency_score

def calculate_overall_score(self) -> float:
    """Calculate overall consistency score"""
    scores = [self.terminology_score, self.interface_score, self.pattern_score]
    valid_scores = [s for s in scores if s > 0]
    if valid_scores:
        self.overall_score = sum(valid_scores) / len(valid_scores)
    else:
        self.overall_score = 0.0
    if self.overall_score >= 0.95:
        self.consistency_level = ConsistencyLevel.EXCELLENT
    elif self.overall_score >= 0.85:
        self.consistency_level = ConsistencyLevel.GOOD
    elif self.overall_score >= 0.7:
        self.consistency_level = ConsistencyLevel.FAIR
    else:
        self.consistency_level = ConsistencyLevel.POOR
    return self.overall_score

def add_log_entry(self, message: str):
    """Add entry to execution log"""
    timestamp = datetime.now().isoformat()
    self.execution_log.append(f'[{timestamp}] {message}')

def can_retry(self) -> bool:
    """Check if workflow can be retried"""
    return self.retry_count < self.max_retries and self.status == CorrectionStatus.FAILED

def calculate_quality_score(self) -> float:
    """Calculate quality score based on various factors"""
    score = 0.0
    if len(self.content) > 50:
        score += 0.2
    if self.acceptance_criteria:
        score += 0.3
    if self.stakeholder_personas:
        score += 0.2
    if self.functionality_keywords:
        score += 0.3
    self.quality_score = min(1.0, score)
    return self.quality_score

def get_total_inconsistencies(self) -> int:
    """Get total count of inconsistencies"""
    return len(self.terminology_drift) + len(self.new_terminology) + len(self.deprecated_usage)

def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    self._initialized_at = datetime.now()

def get_module_status(self) -> Dict[str, Any]:
    """
        Get the current status of this module.
        
        Returns:
            Dictionary containing module status information
        """
    return {'module_name': self.__class__.__name__, 'initialized_at': self._initialized_at.isoformat(), 'status': 'active'}

def get_module_info(self) -> Dict[str, Any]:
    """
        Get information about this module.
        
        Returns:
            Dictionary containing module information
        """
    return {'module_name': self.__class__.__name__, 'module_type': 'spec_reconciliation', 'capabilities': self._get_capabilities(), 'version': '1.0.0'}

def _get_capabilities(self) -> List[str]:
    """
        Get the capabilities of this module.
        
        Returns:
            List of capability names
        """
    return ['base_functionality']

def get_overlap_count(self) -> int:
    """Get total number of overlapping specs"""
    return len(self.overlapping_specs)

def get_critical_issues_count(self) -> int:
    """Get count of critical issues requiring immediate attention"""
    critical_count = 0
    critical_count += len([cr for cr in self.conflicting_requirements if cr.severity == OverlapSeverity.CRITICAL])
    critical_count += len([ti for ti in self.terminology_issues if ti.severity == DriftSeverity.CRITICAL])
    return critical_count

def get_total_migration_steps(self) -> int:
    """Get total number of migration steps"""
    return len(self.migration_steps)

def get_estimated_duration_days(self) -> float:
    """Get estimated duration in days (assuming 8 hours per day)"""
    return self.estimated_effort / 8.0 if self.estimated_effort > 0 else 0

def is_triggered(self, context: Dict[str, Any]) -> bool:
    """Check if control should be triggered based on context"""
    for condition in self.trigger_conditions:
        if condition.evaluate(context):
            return True
    return False

def get_highest_risk_pairs(self) -> List[Tuple[str, str]]:
    """Get spec pairs with highest consolidation risk"""
    return sorted(self.spec_pairs, key=lambda pair: self.risk_assessment.get(f'{pair[0]}-{pair[1]}', 0.0), reverse=True)

def calculate_priority_score(self) -> float:
    """Calculate priority score based on overlap, effort, and risk"""
    risk_multiplier = {'low': 1.0, 'medium': 0.7, 'high': 0.4}.get(self.risk_level, 0.5)
    effort_factor = max(0.1, 1.0 - self.effort_estimate / 100.0)
    self.priority_score = self.overlap_percentage * risk_multiplier * effort_factor
    return self.priority_score

def update_completeness_score(self) -> float:
    """Calculate and update completeness score based on validation status"""
    if not self.validation_status:
        self.completeness_score = 0.0
    else:
        validated_count = sum((1 for status in self.validation_status.values() if status))
        self.completeness_score = validated_count / len(self.validation_status)
    self.last_updated = datetime.now()
    return self.completeness_score

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

def get_critical_drifts(self) -> List[DriftDetection]:
    """Get all critical severity drifts"""
    return [drift for drift in self.detected_drifts if drift.severity == DriftSeverity.CRITICAL]

def get_drift_summary(self) -> Dict[str, int]:
    """Get summary count of drifts by severity"""
    summary = {severity.value: 0 for severity in DriftSeverity}
    for drift in self.detected_drifts:
        summary[drift.severity.value] += 1
    return summary

def evaluate(self, context: Dict[str, Any]) -> bool:
    """Evaluate if condition is met given context"""
    try:
        if self.condition_type == 'threshold':
            metric_name = self.parameters.get('metric')
            threshold = self.parameters.get('threshold', 0)
            operator = self.parameters.get('operator', '>')
            if metric_name in context:
                value = context[metric_name]
                if operator == '>':
                    return value > threshold
                elif operator == '<':
                    return value < threshold
                elif operator == '>=':
                    return value >= threshold
                elif operator == '<=':
                    return value <= threshold
                elif operator == '==':
                    return value == threshold
        return False
    except Exception:
        return False

def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the enforcement action"""
    result = {'action_type': self.action_type, 'executed_at': datetime.now().isoformat(), 'success': False, 'message': ''}
    try:
        if self.action_type == 'block':
            result['success'] = True
            result['message'] = 'Action blocked due to policy violation'
        elif self.action_type == 'warn':
            result['success'] = True
            result['message'] = f'Warning: {self.description}'
        elif self.action_type == 'escalate':
            result['success'] = True
            result['message'] = 'Issue escalated for manual review'
        return result
    except Exception as e:
        result['message'] = f'Enforcement action failed: {e}'
        return result

def should_escalate(self, context: Dict[str, Any]) -> bool:
    """Check if escalation criteria are met"""
    return context.get('requires_escalation', False)

def update_value(self, new_value: float):
    """Update metric value"""
    self.current_value = new_value
    self.last_updated = datetime.now()

def is_within_target(self) -> Optional[bool]:
    """Check if current value meets target"""
    if self.current_value is None or self.target_value is None:
        return None
    return abs(self.current_value - self.target_value) <= self.target_value * 0.1

def calculate_consistency_score(self) -> float:
    """Calculate overall terminology consistency score"""
    total_terms = len(self.consistent_terms) + len(self.inconsistent_terms)
    if total_terms == 0:
        self.consistency_score = 1.0
    else:
        self.consistency_score = len(self.consistent_terms) / total_terms
    return self.consistency_score

def calculate_overall_score(self) -> float:
    """Calculate overall consistency score"""
    scores = [self.terminology_score, self.interface_score, self.pattern_score]
    valid_scores = [s for s in scores if s > 0]
    if valid_scores:
        self.overall_score = sum(valid_scores) / len(valid_scores)
    else:
        self.overall_score = 0.0
    if self.overall_score >= 0.95:
        self.consistency_level = ConsistencyLevel.EXCELLENT
    elif self.overall_score >= 0.85:
        self.consistency_level = ConsistencyLevel.GOOD
    elif self.overall_score >= 0.7:
        self.consistency_level = ConsistencyLevel.FAIR
    else:
        self.consistency_level = ConsistencyLevel.POOR
    return self.overall_score

def add_log_entry(self, message: str):
    """Add entry to execution log"""
    timestamp = datetime.now().isoformat()
    self.execution_log.append(f'[{timestamp}] {message}')

def can_retry(self) -> bool:
    """Check if workflow can be retried"""
    return self.retry_count < self.max_retries and self.status == CorrectionStatus.FAILED

def calculate_quality_score(self) -> float:
    """Calculate quality score based on various factors"""
    score = 0.0
    if len(self.content) > 50:
        score += 0.2
    if self.acceptance_criteria:
        score += 0.3
    if self.stakeholder_personas:
        score += 0.2
    if self.functionality_keywords:
        score += 0.3
    self.quality_score = min(1.0, score)
    return self.quality_score

def get_total_inconsistencies(self) -> int:
    """Get total count of inconsistencies"""
    return len(self.terminology_drift) + len(self.new_terminology) + len(self.deprecated_usage)

def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    self._initialized_at = datetime.now()

def get_module_status(self) -> Dict[str, Any]:
    """
        Get the current status of this module.
        
        Returns:
            Dictionary containing module status information
        """
    return {'module_name': self.__class__.__name__, 'initialized_at': self._initialized_at.isoformat(), 'status': 'active'}

def get_module_info(self) -> Dict[str, Any]:
    """
        Get information about this module.
        
        Returns:
            Dictionary containing module information
        """
    return {'module_name': self.__class__.__name__, 'module_type': 'spec_reconciliation', 'capabilities': self._get_capabilities(), 'version': '1.0.0'}

def _get_capabilities(self) -> List[str]:
    """
        Get the capabilities of this module.
        
        Returns:
            List of capability names
        """
    return ['base_functionality']

def get_overlap_count(self) -> int:
    """Get total number of overlapping specs"""
    return len(self.overlapping_specs)

def get_critical_issues_count(self) -> int:
    """Get count of critical issues requiring immediate attention"""
    critical_count = 0
    critical_count += len([cr for cr in self.conflicting_requirements if cr.severity == OverlapSeverity.CRITICAL])
    critical_count += len([ti for ti in self.terminology_issues if ti.severity == DriftSeverity.CRITICAL])
    return critical_count

def get_total_migration_steps(self) -> int:
    """Get total number of migration steps"""
    return len(self.migration_steps)

def get_estimated_duration_days(self) -> float:
    """Get estimated duration in days (assuming 8 hours per day)"""
    return self.estimated_effort / 8.0 if self.estimated_effort > 0 else 0

def is_triggered(self, context: Dict[str, Any]) -> bool:
    """Check if control should be triggered based on context"""
    for condition in self.trigger_conditions:
        if condition.evaluate(context):
            return True
    return False

def get_highest_risk_pairs(self) -> List[Tuple[str, str]]:
    """Get spec pairs with highest consolidation risk"""
    return sorted(self.spec_pairs, key=lambda pair: self.risk_assessment.get(f'{pair[0]}-{pair[1]}', 0.0), reverse=True)

def calculate_priority_score(self) -> float:
    """Calculate priority score based on overlap, effort, and risk"""
    risk_multiplier = {'low': 1.0, 'medium': 0.7, 'high': 0.4}.get(self.risk_level, 0.5)
    effort_factor = max(0.1, 1.0 - self.effort_estimate / 100.0)
    self.priority_score = self.overlap_percentage * risk_multiplier * effort_factor
    return self.priority_score

def update_completeness_score(self) -> float:
    """Calculate and update completeness score based on validation status"""
    if not self.validation_status:
        self.completeness_score = 0.0
    else:
        validated_count = sum((1 for status in self.validation_status.values() if status))
        self.completeness_score = validated_count / len(self.validation_status)
    self.last_updated = datetime.now()
    return self.completeness_score

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

def get_critical_drifts(self) -> List[DriftDetection]:
    """Get all critical severity drifts"""
    return [drift for drift in self.detected_drifts if drift.severity == DriftSeverity.CRITICAL]

def get_drift_summary(self) -> Dict[str, int]:
    """Get summary count of drifts by severity"""
    summary = {severity.value: 0 for severity in DriftSeverity}
    for drift in self.detected_drifts:
        summary[drift.severity.value] += 1
    return summary

def evaluate(self, context: Dict[str, Any]) -> bool:
    """Evaluate if condition is met given context"""
    try:
        if self.condition_type == 'threshold':
            metric_name = self.parameters.get('metric')
            threshold = self.parameters.get('threshold', 0)
            operator = self.parameters.get('operator', '>')
            if metric_name in context:
                value = context[metric_name]
                if operator == '>':
                    return value > threshold
                elif operator == '<':
                    return value < threshold
                elif operator == '>=':
                    return value >= threshold
                elif operator == '<=':
                    return value <= threshold
                elif operator == '==':
                    return value == threshold
        return False
    except Exception:
        return False

def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the enforcement action"""
    result = {'action_type': self.action_type, 'executed_at': datetime.now().isoformat(), 'success': False, 'message': ''}
    try:
        if self.action_type == 'block':
            result['success'] = True
            result['message'] = 'Action blocked due to policy violation'
        elif self.action_type == 'warn':
            result['success'] = True
            result['message'] = f'Warning: {self.description}'
        elif self.action_type == 'escalate':
            result['success'] = True
            result['message'] = 'Issue escalated for manual review'
        return result
    except Exception as e:
        result['message'] = f'Enforcement action failed: {e}'
        return result

def should_escalate(self, context: Dict[str, Any]) -> bool:
    """Check if escalation criteria are met"""
    return context.get('requires_escalation', False)

def update_value(self, new_value: float):
    """Update metric value"""
    self.current_value = new_value
    self.last_updated = datetime.now()

def is_within_target(self) -> Optional[bool]:
    """Check if current value meets target"""
    if self.current_value is None or self.target_value is None:
        return None
    return abs(self.current_value - self.target_value) <= self.target_value * 0.1

def calculate_consistency_score(self) -> float:
    """Calculate overall terminology consistency score"""
    total_terms = len(self.consistent_terms) + len(self.inconsistent_terms)
    if total_terms == 0:
        self.consistency_score = 1.0
    else:
        self.consistency_score = len(self.consistent_terms) / total_terms
    return self.consistency_score

def calculate_overall_score(self) -> float:
    """Calculate overall consistency score"""
    scores = [self.terminology_score, self.interface_score, self.pattern_score]
    valid_scores = [s for s in scores if s > 0]
    if valid_scores:
        self.overall_score = sum(valid_scores) / len(valid_scores)
    else:
        self.overall_score = 0.0
    if self.overall_score >= 0.95:
        self.consistency_level = ConsistencyLevel.EXCELLENT
    elif self.overall_score >= 0.85:
        self.consistency_level = ConsistencyLevel.GOOD
    elif self.overall_score >= 0.7:
        self.consistency_level = ConsistencyLevel.FAIR
    else:
        self.consistency_level = ConsistencyLevel.POOR
    return self.overall_score

def add_log_entry(self, message: str):
    """Add entry to execution log"""
    timestamp = datetime.now().isoformat()
    self.execution_log.append(f'[{timestamp}] {message}')

def can_retry(self) -> bool:
    """Check if workflow can be retried"""
    return self.retry_count < self.max_retries and self.status == CorrectionStatus.FAILED

def calculate_quality_score(self) -> float:
    """Calculate quality score based on various factors"""
    score = 0.0
    if len(self.content) > 50:
        score += 0.2
    if self.acceptance_criteria:
        score += 0.3
    if self.stakeholder_personas:
        score += 0.2
    if self.functionality_keywords:
        score += 0.3
    self.quality_score = min(1.0, score)
    return self.quality_score

def get_total_inconsistencies(self) -> int:
    """Get total count of inconsistencies"""
    return len(self.terminology_drift) + len(self.new_terminology) + len(self.deprecated_usage)
