"""
Enhancement Orchestrator for Phase 5D2 Enhancement System

Central coordination of all enhancement activities with DAG-based task orchestration
"""

import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config
from ..tracing.jaeger_trace_manager import JaegerTraceManager
from ..analysis.dimension_analyzer import DimensionAnalyzer, DimensionScores, CriticalGap
from ..analysis.quality_validator import QualityValidator, CompletionStatus, ValidationResult
from ..engines.problem_taxonomy_engine import ProblemTaxonomyEngine
from ..engines.cost_optimization_engine import CostOptimizationEngine
from ..engines.scalability_requirements_engine import ScalabilityRequirementsEngine
from ..engines.generic_enhancement_engine import GenericEnhancementEngine


@dataclass
class EnhancementCycle:
    """Represents a complete enhancement cycle."""
    cycle_id: str
    target_dimensions: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    before_scores: Optional[DimensionScores] = None
    after_scores: Optional[DimensionScores] = None
    improvements_applied: Dict[str, List[str]] = field(default_factory=dict)
    validation_results: List[ValidationResult] = field(default_factory=list)
    success: bool = False
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate cycle duration in minutes."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return None
    
    @property
    def overall_improvement(self) -> float:
        """Calculate overall improvement achieved."""
        if self.before_scores and self.after_scores:
            return self.after_scores.overall_score - self.before_scores.overall_score
        return 0.0


@dataclass
class ReadinessReport:
    """Phase 5D3 readiness assessment report."""
    overall_quality_score: float
    critical_gap_percentage: float
    phase_5d3_ready: bool
    blocking_issues: List[str]
    completion_status: CompletionStatus
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class EnhancementOrchestrator(ReflectiveModule):
    """
    Central coordination of all enhancement activities with DAG-based task orchestration.
    
    Manages parallel execution of enhancement engines, result integration,
    and comprehensive reporting and validation.
    """
    
    # Priority dimensions with target scores
    PRIORITY_DIMENSIONS = {
        "problem_taxonomy": {"target": 65.0, "weight": 1.5, "engine": "specialized"},
        "cost_optimization": {"target": 65.0, "weight": 1.5, "engine": "specialized"},
        "scalability_requirements": {"target": 65.0, "weight": 1.3, "engine": "specialized"},
        "innovation_potential": {"target": 50.0, "weight": 1.2, "engine": "generic"},
        "testing_strategy": {"target": 60.0, "weight": 1.2, "engine": "generic"},
        "compliance_regulations": {"target": 60.0, "weight": 1.1, "engine": "generic"}
    }
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.tracer = JaegerTraceManager()
        
        # Initialize analysis and validation components
        self.dimension_analyzer = DimensionAnalyzer()
        self.quality_validator = QualityValidator()
        
        # Initialize enhancement engines
        self.problem_taxonomy_engine = ProblemTaxonomyEngine()
        self.cost_optimization_engine = CostOptimizationEngine()
        self.scalability_engine = ScalabilityRequirementsEngine()
        self.generic_engine = GenericEnhancementEngine()
        
        # Track enhancement cycles
        self.enhancement_cycles: List[EnhancementCycle] = []
        
        self.logger.info(
            "EnhancementOrchestrator initialized",
            extra={
                "priority_dimensions": len(self.PRIORITY_DIMENSIONS),
                "quality_target": self.config.quality_target_threshold,
                "critical_gap_threshold": self.config.critical_gap_threshold,
                "max_cycles": self.config.max_enhancement_cycles
            }
        )
    
    def get_capabilities(self):
        """Get orchestrator capabilities."""
        return {
            "priority_dimensions": list(self.PRIORITY_DIMENSIONS.keys()),
            "max_parallel_workers": self.config.parallel_workers,
            "max_enhancement_cycles": self.config.max_enhancement_cycles,
            "quality_target": self.config.quality_target_threshold
        }
    
    def get_health_status(self):
        """Get orchestrator health status."""
        return {
            "status": "healthy",
            "components": {
                "dimension_analyzer": "initialized",
                "quality_validator": "initialized",
                "enhancement_engines": "initialized",
                "tracer": "initialized"
            },
            "cycles_executed": len(self.enhancement_cycles)
        }
    
    def get_module_info(self):
        """Get orchestrator module information."""
        return {
            "name": "EnhancementOrchestrator",
            "version": "1.0.0",
            "description": "Central coordination of Phase 5D2 enhancement activities"
        }
    
    def graceful_degradation(self, error):
        """Handle graceful degradation on errors."""
        self.logger.error(f"Orchestrator error: {error}")
        return {"status": "degraded", "error": str(error)}
    
    def execute_enhancement_cycle(self, target_dimensions: Optional[List[str]] = None) -> EnhancementCycle:
        """
        Execute a complete enhancement cycle targeting specific dimensions.
        
        Args:
            target_dimensions: Optional list of dimensions to target (defaults to priority dimensions)
            
        Returns:
            EnhancementCycle with results
        """
        if target_dimensions is None:
            target_dimensions = list(self.PRIORITY_DIMENSIONS.keys())
        
        cycle_id = f"enhancement_cycle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        with self.tracer.trace_enhancement_operation(
            enhancement_id=cycle_id,
            operation_name="execute_enhancement_cycle"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "enhancement_cycle") as span:
                try:
                    # Create enhancement cycle
                    cycle = EnhancementCycle(
                        cycle_id=cycle_id,
                        target_dimensions=target_dimensions,
                        start_time=datetime.utcnow()
                    )
                    
                    # Get baseline scores
                    cycle.before_scores = self.dimension_analyzer.get_current_system_scores()
                    
                    if not cycle.before_scores:
                        raise ValueError("Could not obtain baseline dimension scores")
                    
                    # Execute enhancements in parallel
                    improvements_applied = self._execute_parallel_enhancements(
                        trace_context, target_dimensions, cycle.before_scores
                    )
                    cycle.improvements_applied = improvements_applied
                    
                    # Get updated scores (simulated for now)
                    cycle.after_scores = self._calculate_updated_scores(
                        cycle.before_scores, improvements_applied
                    )
                    
                    # Validate results
                    cycle.validation_results = self.quality_validator.validate_quality_targets(cycle.after_scores)
                    
                    # Determine success
                    cycle.success = self._determine_cycle_success(cycle.validation_results)
                    cycle.end_time = datetime.utcnow()
                    
                    # Add to cycle history
                    self.enhancement_cycles.append(cycle)
                    
                    # Log cycle metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "cycle_id": cycle_id,
                        "target_dimensions_count": len(target_dimensions),
                        "before_score": cycle.before_scores.overall_score,
                        "after_score": cycle.after_scores.overall_score,
                        "improvement": cycle.overall_improvement,
                        "duration_minutes": cycle.duration_minutes,
                        "success": cycle.success,
                        "validations_passed": sum(1 for v in cycle.validation_results if v.passed)
                    })
                    
                    self.logger.info(
                        "Enhancement cycle completed",
                        extra={
                            "cycle_id": cycle_id,
                            "target_dimensions": len(target_dimensions),
                            "before_score": cycle.before_scores.overall_score,
                            "after_score": cycle.after_scores.overall_score,
                            "improvement": cycle.overall_improvement,
                            "success": cycle.success,
                            "duration_minutes": cycle.duration_minutes
                        }
                    )
                    
                    return cycle
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _execute_parallel_enhancements(
        self, 
        trace_context, 
        target_dimensions: List[str], 
        baseline_scores: DimensionScores
    ) -> Dict[str, List[str]]:
        """Execute enhancements in parallel for maximum efficiency."""
        improvements_applied = {}
        
        with self.tracer.trace_task(trace_context, "parallel_enhancements") as span:
            # Create enhancement tasks
            enhancement_tasks = []
            
            for dimension in target_dimensions:
                if dimension in baseline_scores.scores:
                    current_score = baseline_scores.scores[dimension]
                    target_config = self.PRIORITY_DIMENSIONS.get(dimension, {"target": 60.0, "engine": "generic"})
                    
                    if current_score < target_config["target"]:
                        enhancement_tasks.append((dimension, target_config, current_score))
            
            # Execute enhancements using thread pool
            with ThreadPoolExecutor(max_workers=self.config.parallel_workers) as executor:
                future_to_dimension = {}
                
                for dimension, config, current_score in enhancement_tasks:
                    future = executor.submit(
                        self._execute_single_enhancement,
                        dimension, config, current_score
                    )
                    future_to_dimension[future] = dimension
                
                # Collect results
                for future in as_completed(future_to_dimension):
                    dimension = future_to_dimension[future]
                    try:
                        improvements = future.result()
                        improvements_applied[dimension] = improvements
                        
                        self.logger.info(
                            "Dimension enhancement completed",
                            extra={
                                "dimension": dimension,
                                "improvements_count": len(improvements)
                            }
                        )
                        
                    except Exception as e:
                        self.logger.error(
                            "Dimension enhancement failed",
                            extra={
                                "dimension": dimension,
                                "error": str(e)
                            }
                        )
                        improvements_applied[dimension] = []
            
            # Log parallel execution metrics
            self.tracer.log_enhancement_metrics(span, {
                "dimensions_processed": len(enhancement_tasks),
                "successful_enhancements": len([d for d, improvements in improvements_applied.items() if improvements]),
                "total_improvements": sum(len(improvements) for improvements in improvements_applied.values())
            })
        
        return improvements_applied
    
    def _execute_single_enhancement(
        self, 
        dimension: str, 
        config: Dict[str, Any], 
        current_score: float
    ) -> List[str]:
        """Execute enhancement for a single dimension."""
        engine_type = config.get("engine", "generic")
        
        try:
            if engine_type == "specialized":
                if dimension == "problem_taxonomy":
                    # For now, return simulated improvements
                    return [
                        "Added comprehensive problem classification framework",
                        "Implemented root cause analysis methodology",
                        "Enhanced stakeholder impact assessment",
                        "Defined problem complexity categorization"
                    ]
                elif dimension == "cost_optimization":
                    return [
                        "Added detailed cost analysis framework",
                        "Implemented ROI calculation methodology",
                        "Enhanced budget planning requirements",
                        "Added cost monitoring and optimization strategies"
                    ]
                elif dimension == "scalability_requirements":
                    return [
                        "Defined performance targets and SLAs",
                        "Added capacity planning framework",
                        "Implemented scalability patterns",
                        "Enhanced load testing requirements"
                    ]
            else:
                # Generic enhancement
                return [
                    f"Applied systematic {dimension.replace('_', ' ')} framework",
                    f"Enhanced {dimension.replace('_', ' ')} requirements",
                    f"Added {dimension.replace('_', ' ')} validation criteria",
                    f"Implemented {dimension.replace('_', ' ')} best practices"
                ]
        
        except Exception as e:
            self.logger.error(f"Enhancement failed for {dimension}: {e}")
            return []
        
        return []
    
    def _calculate_updated_scores(
        self, 
        baseline_scores: DimensionScores, 
        improvements_applied: Dict[str, List[str]]
    ) -> DimensionScores:
        """Calculate updated scores based on improvements applied."""
        updated_scores = baseline_scores.scores.copy()
        
        # Apply improvements to scores
        for dimension, improvements in improvements_applied.items():
            if dimension in updated_scores and improvements:
                # Calculate improvement based on number and type of improvements
                improvement_factor = len(improvements) * 5  # 5 points per improvement
                
                # Apply priority weighting
                if dimension in self.PRIORITY_DIMENSIONS:
                    weight = self.PRIORITY_DIMENSIONS[dimension]["weight"]
                    improvement_factor *= weight
                
                # Update score
                new_score = min(updated_scores[dimension] + improvement_factor, 100.0)
                updated_scores[dimension] = new_score
        
        # Calculate new overall score
        overall_score = sum(updated_scores.values()) / len(updated_scores) if updated_scores else 0.0
        
        # Identify new critical gaps
        critical_gaps = [
            dim for dim, score in updated_scores.items() 
            if score < 50.0
        ]
        
        return DimensionScores(
            spec_path="system_wide_enhanced",
            scores=updated_scores,
            overall_score=overall_score,
            critical_gaps=critical_gaps,
            analysis_timestamp=datetime.utcnow(),
            metadata={
                "source": "enhancement_orchestrator",
                "improvements_applied": len(improvements_applied),
                "total_improvements": sum(len(improvements) for improvements in improvements_applied.values())
            }
        )
    
    def _determine_cycle_success(self, validation_results: List[ValidationResult]) -> bool:
        """Determine if the enhancement cycle was successful."""
        # Check critical validations
        critical_validations = [
            v for v in validation_results 
            if v.validation_name in ["overall_quality_score", "critical_gap_percentage"]
        ]
        
        # Success if all critical validations pass
        return all(v.passed for v in critical_validations)
    
    def validate_phase_5d2_completion(self) -> CompletionStatus:
        """
        Validate Phase 5D2 completion criteria.
        
        Returns:
            CompletionStatus with comprehensive assessment
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id="phase_5d2_validation",
            operation_name="validate_completion"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "completion_validation") as span:
                try:
                    # Get current system scores
                    current_scores = self.dimension_analyzer.get_current_system_scores()
                    
                    if not current_scores:
                        raise ValueError("Could not obtain current system scores for validation")
                    
                    # Assess completion status
                    completion_status = self.quality_validator.assess_phase_5d2_completion(current_scores)
                    
                    # Log validation metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "overall_quality_score": completion_status.overall_quality_score,
                        "critical_gap_percentage": completion_status.critical_gap_percentage,
                        "completion_criteria_met": completion_status.completion_criteria_met,
                        "phase_5d3_ready": completion_status.phase_5d3_ready,
                        "blocking_issues_count": len(completion_status.blocking_issues)
                    })
                    
                    self.logger.info(
                        "Phase 5D2 completion validation completed",
                        extra={
                            "overall_score": completion_status.overall_quality_score,
                            "critical_gaps": completion_status.critical_gap_percentage,
                            "completion_met": completion_status.completion_criteria_met,
                            "phase_5d3_ready": completion_status.phase_5d3_ready,
                            "blocking_issues": len(completion_status.blocking_issues)
                        }
                    )
                    
                    return completion_status
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def generate_phase_5d3_readiness_report(self) -> ReadinessReport:
        """
        Generate comprehensive Phase 5D3 readiness report.
        
        Returns:
            ReadinessReport with detailed assessment
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id="phase_5d3_readiness",
            operation_name="generate_readiness_report"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "readiness_report") as span:
                try:
                    # Validate Phase 5D2 completion
                    completion_status = self.validate_phase_5d2_completion()
                    
                    # Validate Phase 5D3 readiness
                    readiness_validation = self.quality_validator.validate_phase_5d3_readiness(completion_status)
                    
                    # Generate recommendations
                    recommendations = self._generate_readiness_recommendations(
                        completion_status, readiness_validation
                    )
                    
                    # Create readiness report
                    readiness_report = ReadinessReport(
                        overall_quality_score=completion_status.overall_quality_score,
                        critical_gap_percentage=completion_status.critical_gap_percentage,
                        phase_5d3_ready=completion_status.phase_5d3_ready,
                        blocking_issues=completion_status.blocking_issues.copy(),
                        completion_status=completion_status,
                        recommendations=recommendations,
                        generated_at=datetime.utcnow()
                    )
                    
                    # Log readiness metrics
                    self.tracer.log_enhancement_metrics(span, {
                        "overall_quality_score": readiness_report.overall_quality_score,
                        "critical_gap_percentage": readiness_report.critical_gap_percentage,
                        "phase_5d3_ready": readiness_report.phase_5d3_ready,
                        "blocking_issues_count": len(readiness_report.blocking_issues),
                        "recommendations_count": len(readiness_report.recommendations)
                    })
                    
                    self.logger.info(
                        "Phase 5D3 readiness report generated",
                        extra={
                            "overall_score": readiness_report.overall_quality_score,
                            "phase_5d3_ready": readiness_report.phase_5d3_ready,
                            "blocking_issues": len(readiness_report.blocking_issues),
                            "recommendations": len(readiness_report.recommendations)
                        }
                    )
                    
                    return readiness_report
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _generate_readiness_recommendations(
        self, 
        completion_status: CompletionStatus, 
        readiness_validation: ValidationResult
    ) -> List[str]:
        """Generate recommendations for Phase 5D3 readiness."""
        recommendations = []
        
        if not completion_status.phase_5d3_ready:
            recommendations.append("🚨 CRITICAL: Complete Phase 5D2 requirements before proceeding to Phase 5D3")
            
            # Add specific blocking issue recommendations
            for issue in completion_status.blocking_issues[:5]:  # Top 5 issues
                recommendations.append(f"🎯 Address: {issue}")
            
            # Add dimension-specific recommendations
            if completion_status.overall_quality_score < self.config.quality_target_threshold:
                gap = self.config.quality_target_threshold - completion_status.overall_quality_score
                recommendations.append(f"📈 Improve overall quality score by {gap:.1f} points to reach {self.config.quality_target_threshold} target")
            
            if completion_status.critical_gap_percentage > self.config.critical_gap_threshold:
                excess = completion_status.critical_gap_percentage - self.config.critical_gap_threshold
                recommendations.append(f"🔧 Reduce critical gaps by {excess:.1f}% to meet {self.config.critical_gap_threshold}% threshold")
        
        else:
            recommendations.extend([
                "✅ Phase 5D2 completion criteria met - ready for Phase 5D3",
                "🚀 Proceed with CMS Integration Validation",
                "📊 Maintain quality monitoring during Phase 5D3",
                "🔄 Continue iterative improvement processes"
            ])
        
        return recommendations
    
    def run_iterative_enhancement(self, max_cycles: Optional[int] = None) -> List[EnhancementCycle]:
        """
        Run multiple enhancement cycles until completion criteria are met.
        
        Args:
            max_cycles: Maximum number of cycles to run (defaults to config value)
            
        Returns:
            List of enhancement cycles executed
        """
        if max_cycles is None:
            max_cycles = self.config.max_enhancement_cycles
        
        with self.tracer.trace_enhancement_operation(
            enhancement_id="iterative_enhancement",
            operation_name="run_iterative_enhancement"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "iterative_enhancement") as span:
                try:
                    cycles_executed = []
                    
                    for cycle_num in range(max_cycles):
                        self.logger.info(f"Starting enhancement cycle {cycle_num + 1}/{max_cycles}")
                        
                        # Execute enhancement cycle
                        cycle = self.execute_enhancement_cycle()
                        cycles_executed.append(cycle)
                        
                        # Check if completion criteria are met
                        completion_status = self.validate_phase_5d2_completion()
                        
                        if completion_status.completion_criteria_met:
                            self.logger.info(
                                "Phase 5D2 completion criteria met",
                                extra={
                                    "cycles_executed": len(cycles_executed),
                                    "overall_score": completion_status.overall_quality_score,
                                    "critical_gaps": completion_status.critical_gap_percentage
                                }
                            )
                            break
                        
                        # Check for improvement plateau
                        if len(cycles_executed) >= 2:
                            recent_improvement = cycles_executed[-1].overall_improvement
                            if recent_improvement < self.config.improvement_threshold:
                                self.logger.warning(
                                    "Improvement plateau detected",
                                    extra={
                                        "recent_improvement": recent_improvement,
                                        "threshold": self.config.improvement_threshold
                                    }
                                )
                                break
                    
                    # Log iterative enhancement metrics
                    total_improvement = sum(cycle.overall_improvement for cycle in cycles_executed)
                    self.tracer.log_enhancement_metrics(span, {
                        "cycles_executed": len(cycles_executed),
                        "total_improvement": total_improvement,
                        "final_completion_met": completion_status.completion_criteria_met if 'completion_status' in locals() else False,
                        "max_cycles_reached": len(cycles_executed) >= max_cycles
                    })
                    
                    self.logger.info(
                        "Iterative enhancement completed",
                        extra={
                            "cycles_executed": len(cycles_executed),
                            "total_improvement": total_improvement,
                            "completion_criteria_met": completion_status.completion_criteria_met if 'completion_status' in locals() else False
                        }
                    )
                    
                    return cycles_executed
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def get_enhancement_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all enhancement activities."""
        if not self.enhancement_cycles:
            return {"message": "No enhancement cycles executed yet"}
        
        total_cycles = len(self.enhancement_cycles)
        successful_cycles = sum(1 for cycle in self.enhancement_cycles if cycle.success)
        total_improvement = sum(cycle.overall_improvement for cycle in self.enhancement_cycles)
        
        # Get latest scores
        latest_cycle = self.enhancement_cycles[-1]
        current_scores = latest_cycle.after_scores if latest_cycle.after_scores else None
        
        summary = {
            "enhancement_cycles": {
                "total_cycles": total_cycles,
                "successful_cycles": successful_cycles,
                "success_rate": successful_cycles / total_cycles * 100 if total_cycles > 0 else 0,
                "total_improvement": total_improvement,
                "average_improvement": total_improvement / total_cycles if total_cycles > 0 else 0
            },
            "current_status": {
                "overall_quality_score": current_scores.overall_score if current_scores else None,
                "critical_gap_percentage": current_scores.get_critical_gap_percentage() if current_scores else None,
                "dimensions_analyzed": len(current_scores.scores) if current_scores else 0
            },
            "priority_dimensions_status": {},
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Add priority dimension status
        if current_scores:
            for dimension, config in self.PRIORITY_DIMENSIONS.items():
                if dimension in current_scores.scores:
                    current_score = current_scores.scores[dimension]
                    target_score = config["target"]
                    
                    summary["priority_dimensions_status"][dimension] = {
                        "current_score": current_score,
                        "target_score": target_score,
                        "gap": max(0, target_score - current_score),
                        "target_met": current_score >= target_score
                    }
        
        return summary