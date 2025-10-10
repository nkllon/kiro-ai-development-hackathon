"""
Comprehensive dimension analyzer for Phase 5D2 Enhancement System
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config
from ..tracing.jaeger_trace_manager import JaegerTraceManager, TraceContext


@dataclass
class CriticalGap:
    """Represents a critical gap in dimension quality."""
    dimension_name: str
    current_score: float
    target_score: float
    gap_severity: str  # CRITICAL, POOR, MODERATE
    affected_specs: List[str]
    improvement_recommendations: List[str]
    
    @property
    def improvement_needed(self) -> float:
        """Calculate improvement needed to reach target."""
        return max(0, self.target_score - self.current_score)


@dataclass
class DimensionScores:
    """Comprehensive dimension scoring results."""
    spec_path: str
    scores: Dict[str, float] = field(default_factory=dict)  # dimension_name -> score
    overall_score: float = 0.0
    critical_gaps: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_critical_gap_percentage(self) -> float:
        """Calculate percentage of dimensions with critical gaps."""
        if not self.scores:
            return 0.0
        return len(self.critical_gaps) / len(self.scores) * 100
    
    def get_dimension_score(self, dimension_name: str) -> Optional[float]:
        """Get score for a specific dimension."""
        return self.scores.get(dimension_name)
    
    def get_lowest_scoring_dimensions(self, count: int = 5) -> List[Tuple[str, float]]:
        """Get the lowest scoring dimensions."""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1])
        return sorted_scores[:count]
    
    def get_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of quality ratings."""
        distribution = {"CRITICAL": 0, "POOR": 0, "MODERATE": 0, "GOOD": 0, "EXCELLENT": 0}
        
        for score in self.scores.values():
            if score < 30:
                distribution["CRITICAL"] += 1
            elif score < 50:
                distribution["POOR"] += 1
            elif score < 70:
                distribution["MODERATE"] += 1
            elif score < 90:
                distribution["GOOD"] += 1
            else:
                distribution["EXCELLENT"] += 1
        
        return distribution


class DimensionAnalyzer(ReflectiveModule):
    """
    Comprehensive analyzer for all 22 dimensions with scoring and gap identification.
    
    Loads existing gap mitigation results and provides enhanced analysis capabilities
    for identifying improvement opportunities and tracking progress.
    """
    
    # All 22 dimensions with their analysis criteria
    DIMENSIONS = {
        1: "problem_taxonomy",
        2: "infrastructure_architecture", 
        3: "solution_architecture",
        4: "risk_assessment",
        5: "performance_requirements",
        6: "security_requirements",
        7: "deployment_strategy",
        8: "data_management",
        9: "dependency_management",
        10: "scalability_requirements",
        11: "maintainability",
        12: "cost_optimization",
        13: "testing_strategy",
        14: "documentation_requirements",
        15: "monitoring_observability",
        16: "recovery_mechanisms",
        17: "optimization_opportunities",
        18: "integration_patterns",
        19: "innovation_potential",
        20: "governance_compliance",
        21: "usability",
        22: "compliance_regulations"
    }
    
    # Quality thresholds for each rating
    QUALITY_THRESHOLDS = {
        "CRITICAL": (0, 30),
        "POOR": (30, 50),
        "MODERATE": (50, 70),
        "GOOD": (70, 90),
        "EXCELLENT": (90, 100)
    }
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.tracer = JaegerTraceManager()
        
        # Load existing gap mitigation results
        self.gap_mitigation_data = self._load_gap_mitigation_results()
        
        self.logger.info(
            "DimensionAnalyzer initialized",
            extra={
                "dimensions_count": len(self.DIMENSIONS),
                "gap_mitigation_loaded": bool(self.gap_mitigation_data),
                "quality_target": self.config.quality_target_threshold
            }
        )
    
    def get_capabilities(self):
        """Get analyzer capabilities."""
        return {
            "dimensions_supported": list(self.DIMENSIONS.values()),
            "gap_mitigation_loaded": bool(self.gap_mitigation_data),
            "quality_thresholds": self.QUALITY_THRESHOLDS
        }
    
    def get_health_status(self):
        """Get analyzer health status."""
        return {
            "status": "healthy",
            "gap_mitigation_data_loaded": bool(self.gap_mitigation_data),
            "dimensions_count": len(self.DIMENSIONS)
        }
    
    def get_module_info(self):
        """Get analyzer module information."""
        return {
            "name": "DimensionAnalyzer",
            "version": "1.0.0",
            "description": "Comprehensive analyzer for all 22 dimensions"
        }
    
    def graceful_degradation(self, error):
        """Handle graceful degradation on errors."""
        self.logger.error(f"Analyzer error: {error}")
        return {"status": "degraded", "error": str(error)}
    
    def _load_gap_mitigation_results(self) -> Optional[Dict[str, Any]]:
        """Load existing gap mitigation results from Phase 5D2 DAG execution."""
        try:
            gap_mitigation_path = Path(self.config.gap_mitigation_path)
            final_report_path = gap_mitigation_path / "phase-5d2-final-report.json"
            
            if final_report_path.exists():
                with open(final_report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logger.info(f"Loaded gap mitigation results from {final_report_path}")
                    return data
            else:
                self.logger.warning(f"Gap mitigation results not found at {final_report_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load gap mitigation results: {e}")
            return None
    
    def analyze_all_dimensions(self, spec_path: str) -> DimensionScores:
        """
        Analyze all 22 dimensions for a specification.
        
        Args:
            spec_path: Path to the specification to analyze
            
        Returns:
            DimensionScores with comprehensive analysis results
        """
        with self.tracer.trace_enhancement_operation(
            enhancement_id=f"analyze-{Path(spec_path).name}",
            operation_name="analyze_all_dimensions"
        ) as trace_context:
            
            with self.tracer.trace_task(trace_context, "dimension_analysis") as span:
                try:
                    # Initialize scores
                    scores = {}
                    critical_gaps = []
                    
                    # Use existing gap mitigation data if available
                    if self.gap_mitigation_data and "dimension_details" in self.gap_mitigation_data:
                        scores = self._extract_scores_from_gap_data()
                        critical_gaps = self._identify_critical_gaps_from_data(scores)
                        
                        span.add_tag("data_source", "gap_mitigation_results")
                        span.add_tag("dimensions_analyzed", len(scores))
                    else:
                        # Fallback to direct analysis (would need implementation)
                        scores = self._analyze_spec_directly(spec_path)
                        critical_gaps = self._identify_critical_gaps_from_scores(scores)
                        
                        span.add_tag("data_source", "direct_analysis")
                        span.add_tag("dimensions_analyzed", len(scores))
                    
                    # Calculate overall score
                    overall_score = sum(scores.values()) / len(scores) if scores else 0.0
                    
                    # Create dimension scores object
                    dimension_scores = DimensionScores(
                        spec_path=spec_path,
                        scores=scores,
                        overall_score=overall_score,
                        critical_gaps=critical_gaps,
                        analysis_timestamp=datetime.utcnow(),
                        metadata={
                            "analyzer_version": "1.0.0",
                            "data_source": "gap_mitigation_results" if self.gap_mitigation_data else "direct_analysis",
                            "quality_distribution": self._calculate_quality_distribution(scores)
                        }
                    )
                    
                    # Log metrics to span
                    self.tracer.log_enhancement_metrics(span, {
                        "overall_score": overall_score,
                        "critical_gaps_count": len(critical_gaps),
                        "critical_gap_percentage": dimension_scores.get_critical_gap_percentage(),
                        "dimensions_analyzed": len(scores)
                    })
                    
                    self.logger.info(
                        "Completed dimension analysis",
                        extra={
                            "spec_path": spec_path,
                            "overall_score": overall_score,
                            "critical_gaps": len(critical_gaps),
                            "dimensions_analyzed": len(scores)
                        }
                    )
                    
                    return dimension_scores
                    
                except Exception as e:
                    self.tracer.handle_enhancement_error(span, e)
                    raise
    
    def _extract_scores_from_gap_data(self) -> Dict[str, float]:
        """Extract dimension scores from gap mitigation data."""
        scores = {}
        
        if "dimension_details" in self.gap_mitigation_data:
            for dim_id, details in self.gap_mitigation_data["dimension_details"].items():
                if "dimension_name" in details and "average_score" in details:
                    dimension_name = details["dimension_name"]
                    score = details["average_score"]
                    scores[dimension_name] = score
        
        return scores
    
    def _identify_critical_gaps_from_data(self, scores: Dict[str, float]) -> List[str]:
        """Identify critical gaps from dimension scores."""
        critical_gaps = []
        
        for dimension_name, score in scores.items():
            if score < self.config.critical_gap_threshold * 5:  # Convert percentage to score threshold
                critical_gaps.append(dimension_name)
        
        return critical_gaps
    
    def _analyze_spec_directly(self, spec_path: str) -> Dict[str, float]:
        """Direct analysis of specification (fallback method)."""
        # This would implement direct spec analysis if gap mitigation data is not available
        # For now, return default scores
        self.logger.warning("Using fallback direct analysis - implement comprehensive analysis")
        
        return {name: 50.0 for name in self.DIMENSIONS.values()}
    
    def _identify_critical_gaps_from_scores(self, scores: Dict[str, float]) -> List[str]:
        """Identify critical gaps from scores."""
        return [name for name, score in scores.items() if score < 50.0]
    
    def _calculate_quality_distribution(self, scores: Dict[str, float]) -> Dict[str, int]:
        """Calculate quality distribution from scores."""
        distribution = {"CRITICAL": 0, "POOR": 0, "MODERATE": 0, "GOOD": 0, "EXCELLENT": 0}
        
        for score in scores.values():
            if score < 30:
                distribution["CRITICAL"] += 1
            elif score < 50:
                distribution["POOR"] += 1
            elif score < 70:
                distribution["MODERATE"] += 1
            elif score < 90:
                distribution["GOOD"] += 1
            else:
                distribution["EXCELLENT"] += 1
        
        return distribution
    
    def identify_critical_gaps(self, scores: DimensionScores) -> List[CriticalGap]:
        """
        Identify critical gaps requiring immediate attention.
        
        Args:
            scores: Dimension scores to analyze
            
        Returns:
            List of critical gaps with improvement recommendations
        """
        critical_gaps = []
        
        # Focus on the most critical dimensions based on current data
        priority_dimensions = {
            "problem_taxonomy": {"target": 65.0, "weight": 1.5},
            "cost_optimization": {"target": 65.0, "weight": 1.5}, 
            "scalability_requirements": {"target": 65.0, "weight": 1.3},
            "innovation_potential": {"target": 50.0, "weight": 1.2},
            "testing_strategy": {"target": 60.0, "weight": 1.2},
            "compliance_regulations": {"target": 60.0, "weight": 1.1}
        }
        
        for dimension_name, current_score in scores.scores.items():
            if dimension_name in priority_dimensions:
                config = priority_dimensions[dimension_name]
                target_score = config["target"]
                
                if current_score < target_score:
                    severity = self._determine_gap_severity(current_score)
                    recommendations = self._generate_improvement_recommendations(dimension_name, current_score)
                    
                    gap = CriticalGap(
                        dimension_name=dimension_name,
                        current_score=current_score,
                        target_score=target_score,
                        gap_severity=severity,
                        affected_specs=["all"],  # Would be more specific in real implementation
                        improvement_recommendations=recommendations
                    )
                    
                    critical_gaps.append(gap)
        
        # Sort by improvement needed (weighted)
        critical_gaps.sort(key=lambda g: g.improvement_needed * priority_dimensions.get(g.dimension_name, {}).get("weight", 1.0), reverse=True)
        
        return critical_gaps
    
    def _determine_gap_severity(self, score: float) -> str:
        """Determine gap severity based on score."""
        if score < 30:
            return "CRITICAL"
        elif score < 50:
            return "POOR"
        else:
            return "MODERATE"
    
    def _generate_improvement_recommendations(self, dimension_name: str, current_score: float) -> List[str]:
        """Generate specific improvement recommendations for a dimension."""
        recommendations = []
        
        if dimension_name == "problem_taxonomy":
            recommendations.extend([
                "Implement comprehensive problem classification frameworks",
                "Add problem domain identification and complexity categorization",
                "Include root cause analysis depth assessment",
                "Define clear problem scope and stakeholder impact"
            ])
        elif dimension_name == "cost_optimization":
            recommendations.extend([
                "Add detailed resource cost analysis and modeling",
                "Implement optimization strategy identification",
                "Include cost-benefit analysis frameworks",
                "Add budget planning and ROI calculation methodologies"
            ])
        elif dimension_name == "scalability_requirements":
            recommendations.extend([
                "Define clear performance targets and capacity planning",
                "Add growth strategy modeling and load testing requirements",
                "Implement scalability architecture patterns",
                "Include performance monitoring and bottleneck identification"
            ])
        elif dimension_name == "innovation_potential":
            recommendations.extend([
                "Identify automation and AI/ML opportunities",
                "Add research and development potential assessment",
                "Include emerging technology integration possibilities",
                "Define innovation metrics and success criteria"
            ])
        elif dimension_name == "testing_strategy":
            recommendations.extend([
                "Implement comprehensive testing frameworks",
                "Add unit, integration, and end-to-end testing strategies",
                "Include performance and security testing requirements",
                "Define test coverage and quality metrics"
            ])
        elif dimension_name == "compliance_regulations":
            recommendations.extend([
                "Add regulatory compliance requirements analysis",
                "Implement compliance framework integration",
                "Include audit trail and documentation requirements",
                "Define compliance validation and monitoring"
            ])
        else:
            recommendations.append(f"Implement systematic enhancement for {dimension_name}")
        
        return recommendations
    
    def generate_improvement_recommendations(self, gaps: List[CriticalGap]) -> List[str]:
        """
        Generate comprehensive improvement recommendations based on critical gaps.
        
        Args:
            gaps: List of critical gaps to address
            
        Returns:
            List of actionable improvement recommendations
        """
        recommendations = []
        
        # Prioritize recommendations by impact and effort
        high_impact_gaps = [g for g in gaps if g.gap_severity in ["CRITICAL", "POOR"]]
        
        if high_impact_gaps:
            recommendations.append("🎯 PRIORITY: Focus on critical dimensions first")
            
            for gap in high_impact_gaps[:3]:  # Top 3 critical gaps
                recommendations.append(f"📈 {gap.dimension_name.title()}: Improve from {gap.current_score:.1f} to {gap.target_score:.1f}")
                recommendations.extend([f"  • {rec}" for rec in gap.improvement_recommendations[:2]])
        
        # Add systematic recommendations
        recommendations.extend([
            "🔄 Implement iterative enhancement cycles",
            "📊 Monitor progress with automated validation",
            "🎨 Use enhancement templates for consistency",
            "🔍 Validate improvements with quality metrics"
        ])
        
        return recommendations
    
    def track_improvement_progress(self, before: DimensionScores, after: DimensionScores) -> Dict[str, Any]:
        """
        Track improvement progress between two dimension score sets.
        
        Args:
            before: Baseline dimension scores
            after: Updated dimension scores after enhancement
            
        Returns:
            Progress report with improvement metrics
        """
        progress_report = {
            "overall_improvement": after.overall_score - before.overall_score,
            "dimension_improvements": {},
            "critical_gaps_change": len(after.critical_gaps) - len(before.critical_gaps),
            "quality_distribution_change": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Track per-dimension improvements
        for dimension_name in before.scores:
            if dimension_name in after.scores:
                improvement = after.scores[dimension_name] - before.scores[dimension_name]
                progress_report["dimension_improvements"][dimension_name] = {
                    "before": before.scores[dimension_name],
                    "after": after.scores[dimension_name],
                    "improvement": improvement,
                    "improvement_percentage": (improvement / before.scores[dimension_name]) * 100 if before.scores[dimension_name] > 0 else 0
                }
        
        # Track quality distribution changes
        before_dist = before.get_quality_distribution()
        after_dist = after.get_quality_distribution()
        
        for quality_level in before_dist:
            change = after_dist.get(quality_level, 0) - before_dist[quality_level]
            progress_report["quality_distribution_change"][quality_level] = change
        
        return progress_report
    
    def get_current_system_scores(self) -> Optional[DimensionScores]:
        """Get current system-wide dimension scores from gap mitigation data."""
        if not self.gap_mitigation_data:
            return None
        
        scores = self._extract_scores_from_gap_data()
        if not scores:
            return None
        
        overall_score = self.gap_mitigation_data.get("final_metrics", {}).get("overall_average_score", 0.0)
        critical_gaps = self._identify_critical_gaps_from_data(scores)
        
        return DimensionScores(
            spec_path="system_wide",
            scores=scores,
            overall_score=overall_score,
            critical_gaps=critical_gaps,
            analysis_timestamp=datetime.utcnow(),
            metadata={
                "source": "gap_mitigation_final_report",
                "total_specs": self.gap_mitigation_data.get("metadata", {}).get("total_specs", 0),
                "validation_status": self.gap_mitigation_data.get("metadata", {}).get("validation_status", "UNKNOWN")
            }
        )