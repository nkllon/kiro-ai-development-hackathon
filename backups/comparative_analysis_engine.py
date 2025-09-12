"""
Beast Mode Framework - Comparative Analysis Engine
Performs statistical comparison of systematic vs ad-hoc approaches
Requirements: R8.5 - Provide concrete metrics proving Beast Mode superiority
"""

import statistics
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..core.reflective_module import ReflectiveModule, HealthStatus
from .adhoc_approach_simulator import AdhocSimulationResult
from .systematic_approach_tracker import SystematicTrackingResult

@dataclass
class ComparisonResult:
    category: str
    adhoc_mean: float
    systematic_mean: float
    improvement_ratio: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    sample_sizes: Tuple[int, int]  # (adhoc_samples, systematic_samples)
    superiority_proven: bool

@dataclass
class SuperiorityReport:
    overall_superiority_score: float
    evidence_quality_score: float
    comparison_results: Dict[str, ComparisonResult]
    statistical_summary: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

class ComparativeAnalysisEngine(ReflectiveModule):
    """
    Performs statistical comparison between systematic and ad-hoc approaches
    Generates concrete evidence of Beast Mode superiority
    """
    
    def __init__(self):
        super().__init__("comparative_analysis_engine")
        self.analysis_count = 0
        self.total_analyses = 0
        
        # Statistical thresholds for superiority claims
        self.superiority_thresholds = {
            'minimum_improvement_ratio': 1.2,  # 20% improvement required
            'minimum_statistical_significance': 2.0,  # 2-sigma confidence
            'minimum_sample_size': 5,  # Minimum samples per approach
            'confidence_level': 0.95  # 95% confidence intervals
        }
        
        self._update_health_indicator(
            "analysis_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "Comparative analysis engine ready"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "analyses_performed": self.total_analyses,
            "current_analyses": self.analysis_count,
            "superiority_thresholds": self.superiority_thresholds,
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for analysis capability"""
        return not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics"""
        return {
            "analysis_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "analyses_completed": self.total_analyses,
                "current_load": self.analysis_count
            },
            "statistical_integrity": {
                "status": "healthy",
                "thresholds_configured": len(self.superiority_thresholds),
                "confidence_level": self.superiority_thresholds['confidence_level']
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Statistical comparison and superiority analysis"""
        return "statistical_comparison_and_superiority_analysis"
        
    def compare_approaches(self, 
                          adhoc_results: List[AdhocSimulationResult],
                          systematic_results: List[SystematicTrackingResult],
                          category: str) -> Optional[ComparisonResult]:
        """
        Perform statistical comparison between ad-hoc and systematic approaches
        
        Args:
            adhoc_results: Results from ad-hoc approach simulation
            systematic_results: Results from systematic approach tracking
            category: Category being compared (decision_making, problem_solving, tool_management)
            
        Returns:
            ComparisonResult with statistical analysis
        """
        self.analysis_count += 1
        
        try:
            # Extract relevant metrics based on category
            if category == "decision_making":
                adhoc_values = [r.success_rate for r in adhoc_results]
                systematic_values = [r.success_rate for r in systematic_results]
                metric_name = "success_rate"
                higher_is_better = True
                
            elif category == "problem_solving":
                adhoc_values = [r.time_taken for r in adhoc_results]
                systematic_values = [r.time_taken for r in systematic_results]
                metric_name = "resolution_time"
                higher_is_better = False  # Lower time is better
                
            elif category == "tool_management":
                adhoc_values = [r.quality_score for r in adhoc_results]
                systematic_values = [r.quality_score for r in systematic_results]
                metric_name = "quality_score"
                higher_is_better = True
                
            else:
                self.logger.error(f"Unknown comparison category: {category}")
                return None
                
            # Check minimum sample sizes
            if (len(adhoc_values) < self.superiority_thresholds['minimum_sample_size'] or
                len(systematic_values) < self.superiority_thresholds['minimum_sample_size']):
                self.logger.warning(f"Insufficient samples for {category}: adhoc={len(adhoc_values)}, systematic={len(systematic_values)}")
                return None
                
            # Calculate basic statistics
            adhoc_mean = statistics.mean(adhoc_values)
            systematic_mean = statistics.mean(systematic_values)
            
            # Calculate improvement ratio
            if higher_is_better:
                improvement_ratio = systematic_mean / adhoc_mean if adhoc_mean > 0 else float('inf')
            else:
                improvement_ratio = adhoc_mean / systematic_mean if systematic_mean > 0 else float('inf')
                
            # Calculate statistical significance (simplified t-test)
            adhoc_std = statistics.stdev(adhoc_values) if len(adhoc_values) > 1 else 0
            systematic_std = statistics.stdev(systematic_values) if len(systematic_values) > 1 else 0
            
            # Pooled standard error
            n1, n2 = len(adhoc_values), len(systematic_values)
            pooled_variance = ((n1-1)*adhoc_std**2 + (n2-1)*systematic_std**2) / (n1+n2-2) if n1+n2 > 2 else 1
            standard_error = math.sqrt(pooled_variance * (1/n1 + 1/n2)) if pooled_variance > 0 else 1
            
            # T-statistic
            mean_difference = abs(systematic_mean - adhoc_mean)
            t_statistic = mean_difference / standard_error if standard_error > 0 else 0
            
            # Confidence interval (simplified)
            margin_of_error = 1.96 * standard_error  # 95% confidence
            if higher_is_better:
                ci_lower = (systematic_mean - adhoc_mean) - margin_of_error
                ci_upper = (systematic_mean - adhoc_mean) + margin_of_error
            else:
                ci_lower = (adhoc_mean - systematic_mean) - margin_of_error
                ci_upper = (adhoc_mean - systematic_mean) + margin_of_error
                
            # Determine if superiority is proven
            superiority_proven = (
                improvement_ratio >= self.superiority_thresholds['minimum_improvement_ratio'] and
                t_statistic >= self.superiority_thresholds['minimum_statistical_significance'] and
                ci_lower > 0  # Confidence interval doesn't include zero
            )
            
            return ComparisonResult(
                category=category,
                adhoc_mean=adhoc_mean,
                systematic_mean=systematic_mean,
                improvement_ratio=improvement_ratio,
                statistical_significance=t_statistic,
                confidence_interval=(ci_lower, ci_upper),
                sample_sizes=(len(adhoc_values), len(systematic_values)),
                superiority_proven=superiority_proven
            )
            
        finally:
            self.analysis_count -= 1
            self.total_analyses += 1
            
    def generate_superiority_report(self, 
                                  comparison_results: Dict[str, ComparisonResult]) -> SuperiorityReport:
        """
        Generate comprehensive superiority report from comparison results
        
        Args:
            comparison_results: Dictionary of comparison results by category
            
        Returns:
            SuperiorityReport with overall assessment
        """
        if not comparison_results:
            return SuperiorityReport(
                overall_superiority_score=0.0,
                evidence_quality_score=0.0,
                comparison_results={},
                statistical_summary={},
                recommendations=["Insufficient data for superiority analysis"],
                timestamp=datetime.now()
            )
            
        # Calculate overall superiority score
        improvement_ratios = [r.improvement_ratio for r in comparison_results.values()]
        superiority_scores = [min(2.0, r.improvement_ratio) for r in comparison_results.values()]  # Cap at 2.0
        overall_superiority_score = statistics.mean(superiority_scores)
        
        # Calculate evidence quality score
        significance_scores = [min(1.0, r.statistical_significance / 3.0) for r in comparison_results.values()]  # Normalize to 0-1
        sample_quality_scores = [min(1.0, min(r.sample_sizes) / 20) for r in comparison_results.values()]  # 20 samples = perfect
        proven_scores = [1.0 if r.superiority_proven else 0.0 for r in comparison_results.values()]
        
        evidence_quality_score = statistics.mean([
            statistics.mean(significance_scores),
            statistics.mean(sample_quality_scores),
            statistics.mean(proven_scores)
        ])
        
        # Statistical summary
        statistical_summary = {
            "categories_analyzed": len(comparison_results),
            "categories_with_proven_superiority": sum(1 for r in comparison_results.values() if r.superiority_proven),
            "average_improvement_ratio": statistics.mean(improvement_ratios),
            "average_statistical_significance": statistics.mean([r.statistical_significance for r in comparison_results.values()]),
            "total_samples": sum(sum(r.sample_sizes) for r in comparison_results.values()),
            "confidence_level": self.superiority_thresholds['confidence_level']
        }
        
        # Generate recommendations
        recommendations = []
        
        if overall_superiority_score >= 1.5:
            recommendations.append("Strong evidence of systematic approach superiority - ready for production deployment")
        elif overall_superiority_score >= 1.2:
            recommendations.append("Moderate evidence of systematic approach superiority - consider additional validation")
        else:
            recommendations.append("Insufficient evidence of systematic approach superiority - investigate methodology")
            
        if evidence_quality_score >= 0.8:
            recommendations.append("High-quality evidence suitable for stakeholder presentation")
        elif evidence_quality_score >= 0.6:
            recommendations.append("Moderate-quality evidence - consider collecting more samples")
        else:
            recommendations.append("Low-quality evidence - increase sample sizes and improve statistical rigor")
            
        # Category-specific recommendations
        for category, result in comparison_results.items():
            if not result.superiority_proven:
                recommendations.append(f"Investigate {category} - superiority not statistically proven")
            if min(result.sample_sizes) < 10:
                recommendations.append(f"Collect more {category} samples for better statistical power")
                
        return SuperiorityReport(
            overall_superiority_score=overall_superiority_score,
            evidence_quality_score=evidence_quality_score,
            comparison_results=comparison_results,
            statistical_summary=statistical_summary,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
    def validate_superiority_claims(self, report: SuperiorityReport) -> Dict[str, Any]:
        """
        Validate superiority claims against statistical rigor requirements
        
        Args:
            report: SuperiorityReport to validate
            
        Returns:
            Validation results with pass/fail status
        """
        validation_results = {
            "overall_validation": "PASS",
            "validation_details": {},
            "critical_issues": [],
            "warnings": []
        }
        
        # Check overall superiority threshold
        if report.overall_superiority_score < self.superiority_thresholds['minimum_improvement_ratio']:
            validation_results["critical_issues"].append(
                f"Overall superiority score {report.overall_superiority_score:.2f} below threshold {self.superiority_thresholds['minimum_improvement_ratio']}"
            )
            validation_results["overall_validation"] = "FAIL"
            
        # Check evidence quality
        if report.evidence_quality_score < 0.6:
            validation_results["warnings"].append(
                f"Evidence quality score {report.evidence_quality_score:.2f} is low - consider improving data collection"
            )
            
        # Check individual categories
        for category, result in report.comparison_results.items():
            category_validation = {
                "superiority_proven": result.superiority_proven,
                "improvement_ratio_ok": result.improvement_ratio >= self.superiority_thresholds['minimum_improvement_ratio'],
                "statistical_significance_ok": result.statistical_significance >= self.superiority_thresholds['minimum_statistical_significance'],
                "sample_size_ok": min(result.sample_sizes) >= self.superiority_thresholds['minimum_sample_size']
            }
            
            validation_results["validation_details"][category] = category_validation
            
            if not all(category_validation.values()):
                validation_results["warnings"].append(f"Category {category} has validation issues")
                
        # Final validation status
        if validation_results["critical_issues"]:
            validation_results["overall_validation"] = "FAIL"
        elif validation_results["warnings"]:
            validation_results["overall_validation"] = "PASS_WITH_WARNINGS"
            
        return validation_results