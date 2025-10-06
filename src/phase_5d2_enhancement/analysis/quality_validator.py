"""
Quality validation system for Phase 5D2 Enhancement System
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config
from ..tracing.jaeger_trace_manager import JaegerTraceManager
from .dimension_analyzer import DimensionScores


@dataclass
class ValidationResult:
    """Result of a quality validation check."""
    validation_name: str
    passed: bool
    target_value: Any
    actual_value: Any
    message: str
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def status_emoji(self) -> str:
        """Get emoji representation of validation status."""
        return "✅" if self.passed else "❌"


@dataclass
class CompletionStatus:
    """Phase 5D2 completion status assessment."""
    overall_quality_score: float
    critical_gap_percentage: float
    dimension_scores: Dict[str, float]
    completion_criteria_met: bool
    phase_5d3_ready: bool
    blocking_issues: List[str] = field(default_factory=list)
    completion_timestamp: datetime = field(default_factory=datetime.utcnow)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of completion status."""
        return {
            "overall_quality_score": self.overall_quality_score,
            "critical_gap_percentage": self.critical_gap_percentage,
            "completion_criteria_met": self.completion_criteria_met,
            "phase_5d3_ready": self.phase_5d3_ready,
            "blocking_issues_count": len(self.blocking_issues),
            "validation_results_count": len(self.validation_results),
            "passed_validations": sum(1 for v in self.validation_results if v.passed),
            "failed_validations": sum(1 for v in self.validation_results if not v.passed)
        }


class QualityValidator(ReflectiveModule):
    """
    Automated validation of enhancement effectiveness and Phase 5D2 completion criteria.
    
    Provides comprehensive validation of quality targets, completion criteria,
    and Phase 5D3 readiness assessment.
    """
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.tracer = JaegerTraceManager()
        
        # Quality thresholds from configuration
        self.quality_thresholds = self.config.get_quality_thresholds()
        
        self.logger.info(
            "QualityValidator initialized",
            extra={
                "quality_target": self.quality_thresholds["overall_quality_target"],
                "critical_gap_threshold": self.quality_thresholds["critical_gap_threshold"],
                "improvement_threshold": self.quality_thresholds["improvement_threshold"]
            }
        )
    
    def get_capabilities(self):
        """Get validator capabilities."""
        return {
            "quality_thresholds": self.quality_thresholds,
            "validation_types": ["quality_targets", "completion_criteria", "phase_5d3_readiness"]
        }
    
    def get_health_status(self):
        """Get validator health status."""
        return {
            "status": "healthy",
            "quality_target": self.quality_thresholds["overall_quality_target"],
            "critical_gap_threshold": self.quality_thresholds["critical_gap_threshold"]
        }
    
    def get_module_info(self):
        """Get validator module information."""
        return {
            "name": "QualityValidator",
            "version": "1.0.0",
            "description": "Automated validation of enhancement effectiveness"
        }
    
    def graceful_degradation(self, error):
        """Handle graceful degradation on errors."""
        self.logger.error(f"Validator error: {error}")
        return {"status": "degraded", "error": str(error)}
    
    def validate_quality_targets(self, scores: DimensionScores) -> List[ValidationResult]:
        """
        Validate dimension scores against quality targets.
        
        Args:
            scores: Dimension scores to validate
            
        Returns:
            List of validation results
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id="quality_validation",
            operation_name="validate_quality_targets"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "quality_validation") as span:
                validation_results = []
                
                try:
                    # Validate overall quality score
                    overall_validation = self._validate_overall_quality_score(scores)
                    validation_results.append(overall_validation)
                    
                    # Validate critical gap percentage
                    gap_validation = self._validate_critical_gap_percentage(scores)
                    validation_results.append(gap_validation)
                    
                    # Validate individual dimension thresholds
                    dimension_validations = self._validate_dimension_thresholds(scores)
                    validation_results.extend(dimension_validations)
                    
                    # Validate priority dimensions
                    priority_validations = self._validate_priority_dimensions(scores)
                    validation_results.extend(priority_validations)
                    
                    # Log validation metrics
                    passed_count = sum(1 for v in validation_results if v.passed)
                    failed_count = len(validation_results) - passed_count
                    
                    self.tracer.log_enhancement_metrics(span, {
                        "total_validations": len(validation_results),
                        "passed_validations": passed_count,
                        "failed_validations": failed_count,
                        "overall_score": scores.overall_score,
                        "critical_gap_percentage": scores.get_critical_gap_percentage()
                    })
                    
                    self.logger.info(
                        "Quality validation completed",
                        extra={
                            "total_validations": len(validation_results),
                            "passed": passed_count,
                            "failed": failed_count,
                            "overall_score": scores.overall_score
                        }
                    )
                    
                    return validation_results
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _validate_overall_quality_score(self, scores: DimensionScores) -> ValidationResult:
        """Validate overall quality score against target."""
        target = self.quality_thresholds["overall_quality_target"]
        actual = scores.overall_score
        passed = actual >= target
        
        return ValidationResult(
            validation_name="overall_quality_score",
            passed=passed,
            target_value=target,
            actual_value=actual,
            message=f"Overall quality score {actual:.1f} {'meets' if passed else 'below'} target {target:.1f}",
            severity="CRITICAL" if not passed else "INFO",
            recommendations=[
                "Focus on lowest-scoring dimensions",
                "Implement systematic enhancement cycles",
                "Use targeted enhancement engines"
            ] if not passed else []
        )
    
    def _validate_critical_gap_percentage(self, scores: DimensionScores) -> ValidationResult:
        """Validate critical gap percentage against threshold."""
        target = self.quality_thresholds["critical_gap_threshold"]
        actual = scores.get_critical_gap_percentage()
        passed = actual <= target
        
        return ValidationResult(
            validation_name="critical_gap_percentage",
            passed=passed,
            target_value=target,
            actual_value=actual,
            message=f"Critical gaps {actual:.1f}% {'within' if passed else 'exceeds'} threshold {target:.1f}%",
            severity="ERROR" if not passed else "INFO",
            recommendations=[
                "Address dimensions with scores below 50",
                "Prioritize CRITICAL and POOR rated dimensions",
                "Implement comprehensive enhancement strategies"
            ] if not passed else []
        )
    
    def _validate_dimension_thresholds(self, scores: DimensionScores) -> List[ValidationResult]:
        """Validate individual dimensions against minimum thresholds."""
        validations = []
        minimum_threshold = 50.0  # Minimum acceptable score for any dimension
        
        for dimension_name, score in scores.scores.items():
            passed = score >= minimum_threshold
            
            validation = ValidationResult(
                validation_name=f"dimension_{dimension_name}",
                passed=passed,
                target_value=minimum_threshold,
                actual_value=score,
                message=f"{dimension_name}: {score:.1f} {'meets' if passed else 'below'} minimum {minimum_threshold:.1f}",
                severity="WARNING" if not passed else "INFO",
                recommendations=[
                    f"Apply targeted enhancement for {dimension_name}",
                    f"Use dimension-specific improvement patterns"
                ] if not passed else []
            )
            
            validations.append(validation)
        
        return validations
    
    def _validate_priority_dimensions(self, scores: DimensionScores) -> List[ValidationResult]:
        """Validate priority dimensions against enhanced targets."""
        validations = []
        
        # Priority dimensions with higher targets
        priority_targets = {
            "problem_taxonomy": 65.0,
            "cost_optimization": 65.0,
            "scalability_requirements": 65.0,
            "innovation_potential": 50.0,
            "testing_strategy": 60.0,
            "compliance_regulations": 60.0
        }
        
        for dimension_name, target in priority_targets.items():
            if dimension_name in scores.scores:
                actual = scores.scores[dimension_name]
                passed = actual >= target
                
                validation = ValidationResult(
                    validation_name=f"priority_{dimension_name}",
                    passed=passed,
                    target_value=target,
                    actual_value=actual,
                    message=f"Priority dimension {dimension_name}: {actual:.1f} {'meets' if passed else 'below'} target {target:.1f}",
                    severity="ERROR" if not passed else "INFO",
                    recommendations=[
                        f"Apply {dimension_name} enhancement engine",
                        f"Focus on systematic improvement patterns",
                        f"Implement comprehensive {dimension_name} frameworks"
                    ] if not passed else []
                )
                
                validations.append(validation)
        
        return validations
    
    def assess_phase_5d2_completion(self, scores: DimensionScores) -> CompletionStatus:
        """
        Assess Phase 5D2 completion status based on dimension scores.
        
        Args:
            scores: Current dimension scores
            
        Returns:
            CompletionStatus with comprehensive assessment
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id="phase_5d2_assessment",
            operation_name="assess_completion"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "completion_assessment") as span:
                try:
                    # Run all validations
                    validation_results = self.validate_quality_targets(scores)
                    
                    # Determine completion criteria
                    overall_quality_met = scores.overall_score >= self.quality_thresholds["overall_quality_target"]
                    critical_gaps_met = scores.get_critical_gap_percentage() <= self.quality_thresholds["critical_gap_threshold"]
                    
                    completion_criteria_met = overall_quality_met and critical_gaps_met
                    
                    # Identify blocking issues
                    blocking_issues = []
                    
                    if not overall_quality_met:
                        gap = self.quality_thresholds["overall_quality_target"] - scores.overall_score
                        blocking_issues.append(f"Overall quality score {scores.overall_score:.1f} is {gap:.1f} points below target {self.quality_thresholds['overall_quality_target']:.1f}")
                    
                    if not critical_gaps_met:
                        excess = scores.get_critical_gap_percentage() - self.quality_thresholds["critical_gap_threshold"]
                        blocking_issues.append(f"Critical gaps {scores.get_critical_gap_percentage():.1f}% exceed threshold by {excess:.1f}%")
                    
                    # Add specific dimension blocking issues
                    failed_priority_dimensions = [
                        v for v in validation_results 
                        if v.validation_name.startswith("priority_") and not v.passed
                    ]
                    
                    for validation in failed_priority_dimensions:
                        dimension_name = validation.validation_name.replace("priority_", "")
                        blocking_issues.append(f"{dimension_name} score {validation.actual_value:.1f} below target {validation.target_value:.1f}")
                    
                    # Assess Phase 5D3 readiness
                    phase_5d3_ready = completion_criteria_met and len(blocking_issues) == 0
                    
                    completion_status = CompletionStatus(
                        overall_quality_score=scores.overall_score,
                        critical_gap_percentage=scores.get_critical_gap_percentage(),
                        dimension_scores=scores.scores.copy(),
                        completion_criteria_met=completion_criteria_met,
                        phase_5d3_ready=phase_5d3_ready,
                        blocking_issues=blocking_issues,
                        completion_timestamp=datetime.utcnow(),
                        validation_results=validation_results
                    )
                    
                    # Log completion metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "completion_criteria_met": completion_criteria_met,
                        "phase_5d3_ready": phase_5d3_ready,
                        "blocking_issues_count": len(blocking_issues),
                        "overall_quality_score": scores.overall_score,
                        "critical_gap_percentage": scores.get_critical_gap_percentage()
                    })
                    
                    self.logger.info(
                        "Phase 5D2 completion assessment completed",
                        extra={
                            "completion_criteria_met": completion_criteria_met,
                            "phase_5d3_ready": phase_5d3_ready,
                            "blocking_issues": len(blocking_issues),
                            "overall_score": scores.overall_score
                        }
                    )
                    
                    return completion_status
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def validate_phase_5d3_readiness(self, completion_status: CompletionStatus) -> ValidationResult:
        """
        Validate Phase 5D3 readiness based on completion status.
        
        Args:
            completion_status: Phase 5D2 completion status
            
        Returns:
            ValidationResult for Phase 5D3 readiness
        """
        passed = completion_status.phase_5d3_ready
        
        recommendations = []
        if not passed:
            recommendations.extend([
                "Complete Phase 5D2 enhancement requirements",
                "Address all blocking issues identified",
                "Re-run quality validation after improvements",
                "Ensure all priority dimensions meet targets"
            ])
            
            # Add specific recommendations based on blocking issues
            if completion_status.blocking_issues:
                recommendations.append("Specific actions needed:")
                for issue in completion_status.blocking_issues[:3]:  # Top 3 issues
                    recommendations.append(f"  • {issue}")
        
        return ValidationResult(
            validation_name="phase_5d3_readiness",
            passed=passed,
            target_value="All Phase 5D2 criteria met",
            actual_value=f"{len(completion_status.blocking_issues)} blocking issues",
            message=f"Phase 5D3 readiness: {'READY' if passed else 'BLOCKED'} ({len(completion_status.blocking_issues)} blocking issues)",
            severity="INFO" if passed else "CRITICAL",
            recommendations=recommendations
        )
    
    def generate_validation_report(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Generate comprehensive validation report.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Comprehensive validation report
        """
        passed_validations = [v for v in validation_results if v.passed]
        failed_validations = [v for v in validation_results if not v.passed]
        
        # Group by severity
        severity_groups = {}
        for validation in failed_validations:
            severity = validation.severity
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(validation)
        
        # Generate summary
        report = {
            "summary": {
                "total_validations": len(validation_results),
                "passed_validations": len(passed_validations),
                "failed_validations": len(failed_validations),
                "success_rate": len(passed_validations) / len(validation_results) * 100 if validation_results else 0,
                "generated_at": datetime.utcnow().isoformat()
            },
            "results_by_severity": {},
            "failed_validations": [],
            "recommendations": []
        }
        
        # Add results by severity
        for severity, validations in severity_groups.items():
            report["results_by_severity"][severity] = {
                "count": len(validations),
                "validations": [v.validation_name for v in validations]
            }
        
        # Add failed validation details
        for validation in failed_validations:
            report["failed_validations"].append({
                "name": validation.validation_name,
                "target": validation.target_value,
                "actual": validation.actual_value,
                "message": validation.message,
                "severity": validation.severity,
                "recommendations": validation.recommendations
            })
        
        # Collect all recommendations
        all_recommendations = []
        for validation in failed_validations:
            all_recommendations.extend(validation.recommendations)
        
        # Deduplicate and prioritize recommendations
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        report["recommendations"] = unique_recommendations
        
        return report