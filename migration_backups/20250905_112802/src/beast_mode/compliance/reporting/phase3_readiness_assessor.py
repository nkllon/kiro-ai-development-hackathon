"""
Phase 3 readiness assessment system.

This module provides the Phase3ReadinessAssessor class that evaluates
compliance analysis results to determine readiness for Phase 3 initiation,
including blocking issues identification and readiness scoring.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..models import (
    ComplianceAnalysisResult,
    ComplianceIssue,
    IssueSeverity,
    ComplianceIssueType
)


class ReadinessStatus(Enum):
    """Phase 3 readiness status levels."""
    READY = "ready"
    CONDITIONALLY_READY = "conditionally_ready"
    NOT_READY = "not_ready"
    BLOCKED = "blocked"


class ReadinessCriteria(Enum):
    """Criteria for Phase 3 readiness assessment."""
    RDI_COMPLIANCE = "rdi_compliance"
    RM_COMPLIANCE = "rm_compliance"
    TEST_COVERAGE = "test_coverage"
    BLOCKING_ISSUES = "blocking_issues"
    TASK_COMPLETION = "task_completion"
    OVERALL_SCORE = "overall_score"


@dataclass
class ReadinessMetric:
    """Individual readiness metric with scoring."""
    criteria: ReadinessCriteria
    current_value: float
    required_value: float
    weight: float
    status: ReadinessStatus
    description: str
    blocking_issues: List[str] = None
    recommendations: List[str] = None


@dataclass
class Phase3ReadinessReport:
    """Comprehensive Phase 3 readiness assessment report."""
    assessment_timestamp: datetime
    overall_readiness_status: ReadinessStatus
    overall_readiness_score: float
    readiness_metrics: List[ReadinessMetric]
    blocking_issues: List[ComplianceIssue]
    conditional_requirements: List[str]
    recommendations: List[str]
    next_steps: List[str]
    estimated_time_to_ready: str
    risk_assessment: Dict[str, Any]
    go_no_go_decision: Dict[str, Any]


class Phase3ReadinessAssessor:
    """
    Comprehensive Phase 3 readiness assessment system.
    
    Evaluates compliance analysis results against Phase 3 readiness criteria,
    identifies blocking issues, and provides readiness scoring with recommendations.
    """
    
    def __init__(self):
        """Initialize the Phase 3 readiness assessor."""
        self.readiness_thresholds = self._initialize_readiness_thresholds()
        self.criteria_weights = self._initialize_criteria_weights()
        self.blocking_issue_types = self._initialize_blocking_issue_types()
    
    def assess_phase3_readiness(self, analysis_result: ComplianceAnalysisResult) -> Phase3ReadinessReport:
        """
        Perform comprehensive Phase 3 readiness assessment.
        
        Args:
            analysis_result: The compliance analysis results
            
        Returns:
            Comprehensive Phase 3 readiness assessment report
        """
        # Evaluate individual readiness metrics
        readiness_metrics = self._evaluate_readiness_metrics(analysis_result)
        
        # Calculate overall readiness score
        overall_score = self._calculate_overall_readiness_score(readiness_metrics)
        
        # Determine overall readiness status
        overall_status = self._determine_overall_readiness_status(readiness_metrics, overall_score)
        
        # Identify blocking issues
        blocking_issues = self._identify_blocking_issues(analysis_result)
        
        # Generate conditional requirements
        conditional_requirements = self._generate_conditional_requirements(readiness_metrics, blocking_issues)
        
        # Generate recommendations
        recommendations = self._generate_readiness_recommendations(readiness_metrics, blocking_issues)
        
        # Generate next steps
        next_steps = self._generate_next_steps(overall_status, blocking_issues)
        
        # Estimate time to ready
        time_to_ready = self._estimate_time_to_ready(readiness_metrics, blocking_issues)
        
        # Perform risk assessment
        risk_assessment = self._perform_risk_assessment(analysis_result, readiness_metrics)
        
        # Make go/no-go decision
        go_no_go_decision = self._make_go_no_go_decision(overall_status, blocking_issues, risk_assessment)
        
        return Phase3ReadinessReport(
            assessment_timestamp=datetime.now(),
            overall_readiness_status=overall_status,
            overall_readiness_score=overall_score,
            readiness_metrics=readiness_metrics,
            blocking_issues=blocking_issues,
            conditional_requirements=conditional_requirements,
            recommendations=recommendations,
            next_steps=next_steps,
            estimated_time_to_ready=time_to_ready,
            risk_assessment=risk_assessment,
            go_no_go_decision=go_no_go_decision
        )
    
    def get_readiness_summary(self, analysis_result: ComplianceAnalysisResult) -> Dict[str, Any]:
        """
        Get a quick readiness summary.
        
        Args:
            analysis_result: The compliance analysis results
            
        Returns:
            Dictionary with key readiness indicators
        """
        readiness_metrics = self._evaluate_readiness_metrics(analysis_result)
        overall_score = self._calculate_overall_readiness_score(readiness_metrics)
        overall_status = self._determine_overall_readiness_status(readiness_metrics, overall_score)
        blocking_issues = self._identify_blocking_issues(analysis_result)
        
        return {
            "readiness_status": overall_status.value,
            "readiness_score": overall_score,
            "blocking_issues_count": len(blocking_issues),
            "critical_blockers": [issue.description for issue in blocking_issues if issue.severity == IssueSeverity.CRITICAL][:3],
            "ready_for_phase3": overall_status in [ReadinessStatus.READY, ReadinessStatus.CONDITIONALLY_READY] and len(blocking_issues) == 0,
            "key_metrics": {
                metric.criteria.value: {
                    "current": metric.current_value,
                    "required": metric.required_value,
                    "status": metric.status.value
                }
                for metric in readiness_metrics
            }
        }
    
    def _initialize_readiness_thresholds(self) -> Dict[ReadinessCriteria, float]:
        """Initialize readiness thresholds for each criteria."""
        return {
            ReadinessCriteria.RDI_COMPLIANCE: 80.0,
            ReadinessCriteria.RM_COMPLIANCE: 80.0,
            ReadinessCriteria.TEST_COVERAGE: 96.7,  # Phase 2 baseline
            ReadinessCriteria.BLOCKING_ISSUES: 0.0,  # No blocking issues allowed
            ReadinessCriteria.TASK_COMPLETION: 90.0,
            ReadinessCriteria.OVERALL_SCORE: 85.0
        }
    
    def _initialize_criteria_weights(self) -> Dict[ReadinessCriteria, float]:
        """Initialize weights for each readiness criteria."""
        return {
            ReadinessCriteria.RDI_COMPLIANCE: 0.25,
            ReadinessCriteria.RM_COMPLIANCE: 0.25,
            ReadinessCriteria.TEST_COVERAGE: 0.20,
            ReadinessCriteria.BLOCKING_ISSUES: 0.15,
            ReadinessCriteria.TASK_COMPLETION: 0.10,
            ReadinessCriteria.OVERALL_SCORE: 0.05
        }
    
    def _initialize_blocking_issue_types(self) -> List[ComplianceIssueType]:
        """Initialize issue types that are considered blocking for Phase 3."""
        return [
            ComplianceIssueType.RM_NON_COMPLIANCE,
            ComplianceIssueType.TEST_FAILURE,
            ComplianceIssueType.ARCHITECTURAL_VIOLATION
        ]
    
    def _evaluate_readiness_metrics(self, analysis_result: ComplianceAnalysisResult) -> List[ReadinessMetric]:
        """Evaluate individual readiness metrics."""
        metrics = []
        
        # RDI Compliance Metric
        rdi_metric = self._evaluate_rdi_compliance_metric(analysis_result.rdi_compliance)
        metrics.append(rdi_metric)
        
        # RM Compliance Metric
        rm_metric = self._evaluate_rm_compliance_metric(analysis_result.rm_compliance)
        metrics.append(rm_metric)
        
        # Test Coverage Metric
        test_metric = self._evaluate_test_coverage_metric(analysis_result.test_coverage_status)
        metrics.append(test_metric)
        
        # Blocking Issues Metric
        blocking_metric = self._evaluate_blocking_issues_metric(analysis_result)
        metrics.append(blocking_metric)
        
        # Task Completion Metric
        task_metric = self._evaluate_task_completion_metric(analysis_result.task_completion_reconciliation)
        metrics.append(task_metric)
        
        # Overall Score Metric
        overall_metric = self._evaluate_overall_score_metric(analysis_result.overall_compliance_score)
        metrics.append(overall_metric)
        
        return metrics
    
    def _evaluate_rdi_compliance_metric(self, rdi_status) -> ReadinessMetric:
        """Evaluate RDI compliance readiness metric."""
        current_score = rdi_status.compliance_score
        required_score = self.readiness_thresholds[ReadinessCriteria.RDI_COMPLIANCE]
        
        if current_score >= required_score:
            status = ReadinessStatus.READY
        elif current_score >= required_score * 0.8:
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.NOT_READY
        
        blocking_issues = []
        recommendations = []
        
        if not rdi_status.requirements_traced:
            blocking_issues.append("Requirements traceability not established")
            recommendations.append("Complete requirement traceability mapping")
        
        if not rdi_status.design_aligned:
            blocking_issues.append("Design-implementation alignment issues")
            recommendations.append("Align implementation with design specifications")
        
        if not rdi_status.implementation_complete:
            blocking_issues.append("Implementation not complete")
            recommendations.append("Complete all planned implementation work")
        
        return ReadinessMetric(
            criteria=ReadinessCriteria.RDI_COMPLIANCE,
            current_value=current_score,
            required_value=required_score,
            weight=self.criteria_weights[ReadinessCriteria.RDI_COMPLIANCE],
            status=status,
            description=f"RDI methodology compliance score: {current_score:.1f}% (required: {required_score:.1f}%)",
            blocking_issues=blocking_issues,
            recommendations=recommendations
        )
    
    def _evaluate_rm_compliance_metric(self, rm_status) -> ReadinessMetric:
        """Evaluate RM compliance readiness metric."""
        current_score = rm_status.compliance_score
        required_score = self.readiness_thresholds[ReadinessCriteria.RM_COMPLIANCE]
        
        if current_score >= required_score:
            status = ReadinessStatus.READY
        elif current_score >= required_score * 0.8:
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.NOT_READY
        
        blocking_issues = []
        recommendations = []
        
        if not rm_status.interface_implemented:
            blocking_issues.append("RM interface not fully implemented")
            recommendations.append("Implement all required RM interface methods")
        
        if not rm_status.size_constraints_met:
            blocking_issues.append("Module size constraints violated")
            recommendations.append("Refactor modules to meet ≤200 lines constraint")
        
        if not rm_status.health_monitoring_present:
            blocking_issues.append("Health monitoring not implemented")
            recommendations.append("Implement health monitoring capabilities")
        
        if not rm_status.registry_integrated:
            blocking_issues.append("Registry integration missing")
            recommendations.append("Complete RM registry integration")
        
        return ReadinessMetric(
            criteria=ReadinessCriteria.RM_COMPLIANCE,
            current_value=current_score,
            required_value=required_score,
            weight=self.criteria_weights[ReadinessCriteria.RM_COMPLIANCE],
            status=status,
            description=f"RM architectural compliance score: {current_score:.1f}% (required: {required_score:.1f}%)",
            blocking_issues=blocking_issues,
            recommendations=recommendations
        )
    
    def _evaluate_test_coverage_metric(self, test_status) -> ReadinessMetric:
        """Evaluate test coverage readiness metric."""
        current_coverage = test_status.current_coverage
        required_coverage = self.readiness_thresholds[ReadinessCriteria.TEST_COVERAGE]
        
        if current_coverage >= required_coverage:
            status = ReadinessStatus.READY
        elif current_coverage >= required_coverage * 0.95:  # Within 5% of baseline
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.NOT_READY
        
        blocking_issues = []
        recommendations = []
        
        if len(test_status.failing_tests) > 0:
            blocking_issues.append(f"{len(test_status.failing_tests)} failing tests")
            recommendations.append("Fix all failing tests before Phase 3")
        
        if not test_status.coverage_adequate:
            blocking_issues.append("Test coverage below baseline")
            recommendations.append(f"Increase test coverage to {required_coverage}%")
        
        if len(test_status.missing_tests) > 0:
            recommendations.append("Add missing test cases for complete coverage")
        
        return ReadinessMetric(
            criteria=ReadinessCriteria.TEST_COVERAGE,
            current_value=current_coverage,
            required_value=required_coverage,
            weight=self.criteria_weights[ReadinessCriteria.TEST_COVERAGE],
            status=status,
            description=f"Test coverage: {current_coverage:.1f}% (required: {required_coverage:.1f}%)",
            blocking_issues=blocking_issues,
            recommendations=recommendations
        )
    
    def _evaluate_blocking_issues_metric(self, analysis_result: ComplianceAnalysisResult) -> ReadinessMetric:
        """Evaluate blocking issues readiness metric."""
        all_issues = self._collect_all_issues(analysis_result)
        blocking_issues = [
            issue for issue in all_issues 
            if issue.blocking_merge or issue.severity == IssueSeverity.CRITICAL
        ]
        
        current_count = len(blocking_issues)
        required_count = self.readiness_thresholds[ReadinessCriteria.BLOCKING_ISSUES]
        
        if current_count <= required_count:
            status = ReadinessStatus.READY
        elif current_count <= 2:  # Allow up to 2 minor blocking issues
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.BLOCKED
        
        issue_descriptions = [issue.description for issue in blocking_issues[:5]]  # Top 5
        recommendations = [
            "Resolve all blocking issues before Phase 3",
            "Prioritize critical severity issues first",
            "Validate fixes don't introduce new issues"
        ]
        
        return ReadinessMetric(
            criteria=ReadinessCriteria.BLOCKING_ISSUES,
            current_value=current_count,
            required_value=required_count,
            weight=self.criteria_weights[ReadinessCriteria.BLOCKING_ISSUES],
            status=status,
            description=f"Blocking issues: {current_count} (required: {int(required_count)})",
            blocking_issues=issue_descriptions,
            recommendations=recommendations
        )
    
    def _evaluate_task_completion_metric(self, task_status) -> ReadinessMetric:
        """Evaluate task completion readiness metric."""
        current_score = task_status.reconciliation_score
        required_score = self.readiness_thresholds[ReadinessCriteria.TASK_COMPLETION]
        
        if current_score >= required_score:
            status = ReadinessStatus.READY
        elif current_score >= required_score * 0.85:
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.NOT_READY
        
        blocking_issues = []
        recommendations = []
        
        if len(task_status.missing_implementations) > 0:
            blocking_issues.append(f"{len(task_status.missing_implementations)} incomplete tasks")
            recommendations.append("Complete all claimed tasks before Phase 3")
        
        missing_tasks = task_status.missing_implementations[:3]  # Top 3
        if missing_tasks:
            recommendations.extend([f"Complete task: {task}" for task in missing_tasks])
        
        return ReadinessMetric(
            criteria=ReadinessCriteria.TASK_COMPLETION,
            current_value=current_score,
            required_value=required_score,
            weight=self.criteria_weights[ReadinessCriteria.TASK_COMPLETION],
            status=status,
            description=f"Task completion reconciliation: {current_score:.1f}% (required: {required_score:.1f}%)",
            blocking_issues=blocking_issues,
            recommendations=recommendations
        )
    
    def _evaluate_overall_score_metric(self, overall_score: float) -> ReadinessMetric:
        """Evaluate overall compliance score readiness metric."""
        required_score = self.readiness_thresholds[ReadinessCriteria.OVERALL_SCORE]
        
        if overall_score >= required_score:
            status = ReadinessStatus.READY
        elif overall_score >= required_score * 0.9:
            status = ReadinessStatus.CONDITIONALLY_READY
        else:
            status = ReadinessStatus.NOT_READY
        
        recommendations = []
        if overall_score < required_score:
            recommendations.append("Improve overall compliance score through targeted fixes")
            recommendations.append("Focus on high-impact compliance improvements")
        
        return ReadinessMetric(
            criteria=ReadinessCriteria.OVERALL_SCORE,
            current_value=overall_score,
            required_value=required_score,
            weight=self.criteria_weights[ReadinessCriteria.OVERALL_SCORE],
            status=status,
            description=f"Overall compliance score: {overall_score:.1f}% (required: {required_score:.1f}%)",
            blocking_issues=[],
            recommendations=recommendations
        )
    
    def _calculate_overall_readiness_score(self, readiness_metrics: List[ReadinessMetric]) -> float:
        """Calculate weighted overall readiness score."""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for metric in readiness_metrics:
            # Convert status to numeric score
            status_score = self._convert_status_to_score(metric.status)
            
            # Calculate metric score based on current vs required value
            if metric.required_value > 0:
                metric_score = min(100.0, (metric.current_value / metric.required_value) * 100.0)
            else:
                # For metrics where 0 is the target (like blocking issues)
                metric_score = 100.0 if metric.current_value == 0 else max(0.0, 100.0 - metric.current_value * 10)
            
            # Combine status score and metric score
            combined_score = (status_score * 0.6) + (metric_score * 0.4)
            
            total_weighted_score += combined_score * metric.weight
            total_weight += metric.weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_overall_readiness_status(self, readiness_metrics: List[ReadinessMetric], 
                                          overall_score: float) -> ReadinessStatus:
        """Determine overall readiness status based on metrics and score."""
        # Check for any blocked metrics
        if any(metric.status == ReadinessStatus.BLOCKED for metric in readiness_metrics):
            return ReadinessStatus.BLOCKED
        
        # Check for critical failures
        critical_failures = [
            metric for metric in readiness_metrics 
            if metric.status == ReadinessStatus.NOT_READY and metric.weight >= 0.2
        ]
        
        if len(critical_failures) > 0:
            return ReadinessStatus.NOT_READY
        
        # Count ready vs conditional metrics
        ready_count = len([m for m in readiness_metrics if m.status == ReadinessStatus.READY])
        conditional_count = len([m for m in readiness_metrics if m.status == ReadinessStatus.CONDITIONALLY_READY])
        not_ready_count = len([m for m in readiness_metrics if m.status == ReadinessStatus.NOT_READY])
        
        # Decision logic
        if ready_count >= len(readiness_metrics) * 0.8 and overall_score >= 85.0:
            return ReadinessStatus.READY
        elif ready_count + conditional_count >= len(readiness_metrics) * 0.8 and overall_score >= 75.0:
            return ReadinessStatus.CONDITIONALLY_READY
        else:
            return ReadinessStatus.NOT_READY
    
    def _identify_blocking_issues(self, analysis_result: ComplianceAnalysisResult) -> List[ComplianceIssue]:
        """Identify issues that block Phase 3 initiation."""
        all_issues = self._collect_all_issues(analysis_result)
        
        blocking_issues = []
        for issue in all_issues:
            # Critical severity issues are always blocking
            if issue.severity == IssueSeverity.CRITICAL:
                blocking_issues.append(issue)
            # Issues explicitly marked as blocking merge
            elif issue.blocking_merge:
                blocking_issues.append(issue)
            # Specific issue types that are blocking
            elif issue.issue_type in self.blocking_issue_types:
                blocking_issues.append(issue)
        
        # Sort by severity (critical first)
        blocking_issues.sort(key=lambda x: self._get_severity_weight(x.severity), reverse=True)
        
        return blocking_issues
    
    def _generate_conditional_requirements(self, readiness_metrics: List[ReadinessMetric], 
                                         blocking_issues: List[ComplianceIssue]) -> List[str]:
        """Generate conditional requirements for Phase 3 readiness."""
        requirements = []
        
        # Requirements from metrics
        for metric in readiness_metrics:
            if metric.status == ReadinessStatus.CONDITIONALLY_READY:
                requirements.append(f"Monitor {metric.criteria.value} closely during Phase 3")
                if metric.blocking_issues:
                    requirements.extend([f"Address: {issue}" for issue in metric.blocking_issues[:2]])
        
        # Requirements from blocking issues
        if len(blocking_issues) > 0:
            requirements.append("Resolve all blocking issues before full Phase 3 deployment")
            
        # Add specific conditional requirements
        if any(m.criteria == ReadinessCriteria.TEST_COVERAGE and m.status != ReadinessStatus.READY 
               for m in readiness_metrics):
            requirements.append("Maintain test coverage monitoring throughout Phase 3")
        
        if any(m.criteria == ReadinessCriteria.RM_COMPLIANCE and m.status != ReadinessStatus.READY 
               for m in readiness_metrics):
            requirements.append("Complete RM compliance before adding new modules")
        
        return requirements
    
    def _generate_readiness_recommendations(self, readiness_metrics: List[ReadinessMetric], 
                                          blocking_issues: List[ComplianceIssue]) -> List[str]:
        """Generate recommendations for achieving Phase 3 readiness."""
        recommendations = []
        
        # Collect recommendations from metrics
        for metric in readiness_metrics:
            if metric.recommendations:
                recommendations.extend(metric.recommendations)
        
        # Add priority-based recommendations
        not_ready_metrics = [m for m in readiness_metrics if m.status == ReadinessStatus.NOT_READY]
        if not_ready_metrics:
            # Sort by weight (importance)
            not_ready_metrics.sort(key=lambda x: x.weight, reverse=True)
            top_metric = not_ready_metrics[0]
            recommendations.insert(0, f"Priority: Address {top_metric.criteria.value} issues first")
        
        # Add blocking issue recommendations
        if len(blocking_issues) > 0:
            recommendations.insert(0, "Immediate action required: Resolve all blocking issues")
            
        # Add general recommendations
        recommendations.extend([
            "Run compliance analysis daily to track progress",
            "Validate fixes don't introduce new issues",
            "Consider phased Phase 3 rollout if conditionally ready"
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # Limit to top 10
    
    def _generate_next_steps(self, overall_status: ReadinessStatus, 
                           blocking_issues: List[ComplianceIssue]) -> List[str]:
        """Generate specific next steps based on readiness status."""
        next_steps = []
        
        if overall_status == ReadinessStatus.READY:
            next_steps.extend([
                "Proceed with Phase 3 planning and initiation",
                "Schedule Phase 3 kickoff meeting",
                "Begin Phase 3 requirements gathering",
                "Set up Phase 3 monitoring and tracking"
            ])
        elif overall_status == ReadinessStatus.CONDITIONALLY_READY:
            next_steps.extend([
                "Address conditional requirements before Phase 3",
                "Implement enhanced monitoring for conditional areas",
                "Plan phased Phase 3 rollout with checkpoints",
                "Schedule readiness re-assessment in 1 week"
            ])
        elif overall_status == ReadinessStatus.NOT_READY:
            next_steps.extend([
                "Execute remediation plan for not-ready criteria",
                "Focus on highest-weight readiness metrics first",
                "Schedule daily progress reviews",
                "Re-assess readiness after remediation"
            ])
        else:  # BLOCKED
            next_steps.extend([
                "STOP: Do not proceed with Phase 3",
                "Resolve all blocking issues immediately",
                "Conduct root cause analysis for blocking issues",
                "Re-assess readiness only after all blockers resolved"
            ])
        
        return next_steps
    
    def _estimate_time_to_ready(self, readiness_metrics: List[ReadinessMetric], 
                              blocking_issues: List[ComplianceIssue]) -> str:
        """Estimate time required to achieve Phase 3 readiness."""
        not_ready_metrics = [m for m in readiness_metrics if m.status != ReadinessStatus.READY]
        
        if len(not_ready_metrics) == 0 and len(blocking_issues) == 0:
            return "Ready now"
        
        # Estimate based on severity and complexity
        effort_points = 0
        
        # Add effort for not-ready metrics
        for metric in not_ready_metrics:
            if metric.status == ReadinessStatus.CONDITIONALLY_READY:
                effort_points += 2
            elif metric.status == ReadinessStatus.NOT_READY:
                effort_points += 5 * metric.weight * 10  # Weight factor
            else:  # BLOCKED
                effort_points += 10
        
        # Add effort for blocking issues
        for issue in blocking_issues:
            if issue.severity == IssueSeverity.CRITICAL:
                effort_points += 8
            elif issue.severity == IssueSeverity.HIGH:
                effort_points += 4
            else:
                effort_points += 2
        
        # Convert to time estimate
        if effort_points <= 5:
            return "1-2 days"
        elif effort_points <= 15:
            return "3-5 days"
        elif effort_points <= 30:
            return "1-2 weeks"
        elif effort_points <= 60:
            return "2-4 weeks"
        else:
            return "1+ months"
    
    def _perform_risk_assessment(self, analysis_result: ComplianceAnalysisResult, 
                               readiness_metrics: List[ReadinessMetric]) -> Dict[str, Any]:
        """Perform risk assessment for Phase 3 initiation."""
        risks = []
        risk_level = "LOW"
        
        # Assess metric-based risks
        high_risk_metrics = [
            m for m in readiness_metrics 
            if m.status in [ReadinessStatus.NOT_READY, ReadinessStatus.BLOCKED] and m.weight >= 0.2
        ]
        
        if len(high_risk_metrics) > 0:
            risks.append("High-weight readiness criteria not met")
            risk_level = "HIGH"
        
        # Assess test coverage risk
        if analysis_result.test_coverage_status.current_coverage < 90.0:
            risks.append("Low test coverage increases regression risk")
            risk_level = max(risk_level, "MEDIUM")
        
        # Assess failing tests risk
        if len(analysis_result.test_coverage_status.failing_tests) > 3:
            risks.append("Multiple failing tests indicate instability")
            risk_level = "HIGH"
        
        # Assess compliance score risk
        if analysis_result.overall_compliance_score < 70.0:
            risks.append("Low overall compliance score")
            risk_level = "HIGH"
        
        # Assess architectural risks
        if not analysis_result.rm_compliance.interface_implemented:
            risks.append("Incomplete RM architecture may cause integration issues")
            risk_level = max(risk_level, "MEDIUM")
        
        return {
            "risk_level": risk_level,
            "identified_risks": risks,
            "mitigation_strategies": self._generate_risk_mitigation_strategies(risks),
            "contingency_plans": self._generate_contingency_plans(risk_level)
        }
    
    def _make_go_no_go_decision(self, overall_status: ReadinessStatus, 
                              blocking_issues: List[ComplianceIssue], 
                              risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Make go/no-go decision for Phase 3 initiation."""
        
        if overall_status == ReadinessStatus.READY and len(blocking_issues) == 0:
            decision = "GO"
            confidence = "HIGH"
            rationale = "All readiness criteria met, no blocking issues"
        elif overall_status == ReadinessStatus.CONDITIONALLY_READY and len(blocking_issues) <= 1:
            decision = "CONDITIONAL GO"
            confidence = "MEDIUM"
            rationale = "Most criteria met, manageable conditions"
        elif overall_status == ReadinessStatus.NOT_READY:
            decision = "NO GO"
            confidence = "HIGH"
            rationale = "Key readiness criteria not met"
        else:  # BLOCKED
            decision = "NO GO"
            confidence = "HIGH"
            rationale = "Blocking issues prevent Phase 3 initiation"
        
        # Adjust based on risk assessment
        if risk_assessment["risk_level"] == "HIGH" and decision == "GO":
            decision = "CONDITIONAL GO"
            confidence = "MEDIUM"
            rationale += " (adjusted for high risk)"
        
        return {
            "decision": decision,
            "confidence": confidence,
            "rationale": rationale,
            "conditions": self._generate_go_conditions(overall_status, blocking_issues),
            "review_date": self._calculate_review_date(decision, overall_status)
        }
    
    def _collect_all_issues(self, analysis_result: ComplianceAnalysisResult) -> List[ComplianceIssue]:
        """Collect all issues from analysis result."""
        all_issues = []
        all_issues.extend(analysis_result.rdi_compliance.issues)
        all_issues.extend(analysis_result.rm_compliance.issues)
        all_issues.extend(analysis_result.test_coverage_status.issues)
        all_issues.extend(analysis_result.task_completion_reconciliation.issues)
        all_issues.extend(analysis_result.critical_issues)
        
        # Remove duplicates
        unique_issues = []
        seen = set()
        for issue in all_issues:
            key = (issue.description, tuple(sorted(issue.affected_files)))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _convert_status_to_score(self, status: ReadinessStatus) -> float:
        """Convert readiness status to numeric score."""
        status_scores = {
            ReadinessStatus.READY: 100.0,
            ReadinessStatus.CONDITIONALLY_READY: 75.0,
            ReadinessStatus.NOT_READY: 25.0,
            ReadinessStatus.BLOCKED: 0.0
        }
        return status_scores.get(status, 0.0)
    
    def _get_severity_weight(self, severity: IssueSeverity) -> int:
        """Get numeric weight for severity."""
        weights = {
            IssueSeverity.CRITICAL: 4,
            IssueSeverity.HIGH: 3,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 1
        }
        return weights.get(severity, 2)
    
    def _generate_risk_mitigation_strategies(self, risks: List[str]) -> List[str]:
        """Generate risk mitigation strategies."""
        strategies = []
        
        for risk in risks:
            if "test coverage" in risk.lower():
                strategies.append("Implement comprehensive test suite before Phase 3")
            elif "failing tests" in risk.lower():
                strategies.append("Fix all failing tests and add regression prevention")
            elif "compliance score" in risk.lower():
                strategies.append("Focus remediation on high-impact compliance issues")
            elif "rm architecture" in risk.lower():
                strategies.append("Complete RM implementation with thorough testing")
            else:
                strategies.append("Implement monitoring and rollback procedures")
        
        return strategies
    
    def _generate_contingency_plans(self, risk_level: str) -> List[str]:
        """Generate contingency plans based on risk level."""
        if risk_level == "HIGH":
            return [
                "Prepare immediate rollback procedures",
                "Implement enhanced monitoring and alerting",
                "Have dedicated support team on standby",
                "Plan for emergency fixes and hotfixes"
            ]
        elif risk_level == "MEDIUM":
            return [
                "Set up monitoring dashboards",
                "Plan regular checkpoint reviews",
                "Prepare rollback procedures if needed"
            ]
        else:
            return [
                "Standard monitoring and support procedures",
                "Regular progress reviews"
            ]
    
    def _generate_go_conditions(self, overall_status: ReadinessStatus, 
                              blocking_issues: List[ComplianceIssue]) -> List[str]:
        """Generate conditions for go decision."""
        conditions = []
        
        if overall_status == ReadinessStatus.CONDITIONALLY_READY:
            conditions.extend([
                "Monitor conditional readiness criteria closely",
                "Implement enhanced testing and validation",
                "Plan phased rollout with checkpoints"
            ])
        
        if len(blocking_issues) > 0:
            conditions.append("Resolve all blocking issues before proceeding")
        
        conditions.extend([
            "Maintain compliance monitoring throughout Phase 3",
            "Have rollback plan ready if issues arise"
        ])
        
        return conditions
    
    def _calculate_review_date(self, decision: str, overall_status: ReadinessStatus) -> str:
        """Calculate when to review the go/no-go decision."""
        if decision == "GO":
            return "Review after Phase 3 initiation"
        elif decision == "CONDITIONAL GO":
            return "Review in 1 week"
        else:
            if overall_status == ReadinessStatus.BLOCKED:
                return "Review after blocking issues resolved"
            else:
                return "Review in 3-5 days after remediation"