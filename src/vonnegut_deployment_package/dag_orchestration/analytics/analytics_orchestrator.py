"""
Analytics Orchestrator - Unified analytics and optimization system

This module orchestrates all analytics components to provide comprehensive
insights, recommendations, and continuous improvement for DAG orchestration.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.analytics.execution_pattern_analyzer import (
    ExecutionPatternAnalyzer, ExecutionMetrics, PatternInsight, OptimizationRecommendation
)
from src.dag_orchestration.analytics.dag_structure_optimizer import (
    DAGStructureOptimizer, DAGNode, OptimizedDAGStructure
)
from src.dag_orchestration.analytics.resource_utilization_analyzer import (
    ResourceUtilizationAnalyzer, ResourceSnapshot, ResourceTrend, CapacityPrediction
)
from src.dag_orchestration.analytics.performance_regression_detector import (
    PerformanceRegressionDetector, RegressionDetection, AnomalyDetection, PredictiveAlert
)
from src.dag_orchestration.analytics.cost_optimization_analyzer import (
    CostOptimizationAnalyzer, CostBreakdown, ProviderCostAnalysis, CostOptimizationOpportunity
)


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""
    generated_at: datetime
    analysis_period_days: int
    
    # Execution patterns
    execution_insights: List[PatternInsight]
    execution_recommendations: List[OptimizationRecommendation]
    execution_efficiency_metrics: Dict[str, Any]
    
    # DAG structure optimization
    dag_optimization: Optional[OptimizedDAGStructure]
    
    # Resource utilization
    resource_trends: List[ResourceTrend]
    capacity_predictions: List[CapacityPrediction]
    resource_status: Dict[str, Any]
    
    # Performance regression
    performance_regressions: List[RegressionDetection]
    performance_anomalies: List[AnomalyDetection]
    predictive_alerts: List[PredictiveAlert]
    performance_health_score: Dict[str, Any]
    
    # Cost optimization
    cost_breakdown: List[CostBreakdown]
    cost_optimization_opportunities: List[CostOptimizationOpportunity]
    cost_efficiency_metrics: Dict[str, Any]
    
    # Summary and recommendations
    overall_health_score: float
    priority_recommendations: List[Dict[str, Any]]
    continuous_improvement_plan: List[Dict[str, Any]]


@dataclass
class ContinuousImprovementAction:
    """Action item for continuous improvement."""
    category: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    estimated_impact: Dict[str, float]
    implementation_effort: str
    timeline: str
    success_metrics: List[str]
    dependencies: List[str]


class AnalyticsOrchestrator(ReflectiveModule):
    """
    Unified analytics orchestrator for DAG orchestration system.
    
    Coordinates all analytics components to provide comprehensive insights,
    optimization recommendations, and continuous improvement guidance.
    """
    
    def __init__(self, 
                 analysis_interval_minutes: int = 60,
                 budget_limit: Optional[float] = None):
        super().__init__()
        self.analysis_interval_minutes = analysis_interval_minutes
        
        # Initialize analytics components
        self.execution_analyzer = ExecutionPatternAnalyzer()
        self.dag_optimizer = DAGStructureOptimizer()
        self.resource_analyzer = ResourceUtilizationAnalyzer()
        self.regression_detector = PerformanceRegressionDetector()
        self.cost_analyzer = CostOptimizationAnalyzer(budget_limit)
        
        # Analytics state
        self.last_analysis_time: Optional[datetime] = None
        self.analysis_history: List[AnalyticsReport] = []
        
        self.logger = logging.getLogger(__name__)
    
    def add_execution_metrics(self, metrics: List[ExecutionMetrics]) -> None:
        """Add execution metrics to all analytics components."""
        with self.trace_operation("add_execution_metrics"):
            # Distribute metrics to all analyzers
            self.execution_analyzer.add_execution_metrics(metrics)
            self.dag_optimizer.add_execution_data(metrics)
            self.regression_detector.add_execution_metrics(metrics)
            self.cost_analyzer.add_execution_metrics(metrics)
            
            self.logger.info(
                f"Added {len(metrics)} execution metrics to analytics system",
                extra={'metrics_count': len(metrics)}
            )
    
    def update_dag_structure(self, dag_structure: Dict[str, DAGNode]) -> None:
        """Update DAG structure for optimization analysis."""
        with self.trace_operation("update_dag_structure"):
            self.dag_optimizer.update_dag_structure(dag_structure)
            
            self.logger.info(
                f"Updated DAG structure with {len(dag_structure)} nodes",
                extra={'node_count': len(dag_structure)}
            )
    
    def capture_resource_snapshot(self, active_tasks: int = 0, 
                                concurrent_executions: int = 0) -> ResourceSnapshot:
        """Capture current resource utilization snapshot."""
        with self.trace_operation("capture_resource_snapshot"):
            snapshot = self.resource_analyzer.capture_resource_snapshot(
                active_tasks, concurrent_executions
            )
            
            self.logger.debug(
                "Captured resource snapshot",
                extra={
                    'cpu_percent': snapshot.cpu_percent,
                    'memory_percent': snapshot.memory_percent,
                    'active_tasks': active_tasks
                }
            )
            
            return snapshot
    
    def run_comprehensive_analysis(self, 
                                 analysis_period_days: int = 7) -> AnalyticsReport:
        """
        Run comprehensive analysis across all analytics components.
        
        Args:
            analysis_period_days: Days of history to analyze
            
        Returns:
            Comprehensive analytics report with insights and recommendations
        """
        with self.trace_operation("run_comprehensive_analysis"):
            self.logger.info(
                f"Starting comprehensive analysis for {analysis_period_days} days",
                extra={'analysis_period_days': analysis_period_days}
            )
            
            # Execution pattern analysis
            execution_insights = self.execution_analyzer.analyze_execution_patterns(
                time_window_hours=analysis_period_days * 24
            )
            execution_recommendations = self.execution_analyzer.generate_optimization_recommendations(
                execution_insights
            )
            execution_efficiency_metrics = self.execution_analyzer.get_execution_efficiency_metrics()
            
            # DAG structure optimization
            dag_optimization = self.dag_optimizer.analyze_and_optimize_structure()
            
            # Resource utilization analysis
            resource_trends = self.resource_analyzer.analyze_resource_trends(
                hours_back=analysis_period_days * 24
            )
            capacity_predictions = self.resource_analyzer.predict_capacity_requirements()
            resource_status = self.resource_analyzer.get_current_resource_status()
            
            # Performance regression detection
            performance_regressions = self.regression_detector.detect_performance_regressions()
            performance_anomalies = self.regression_detector.detect_performance_anomalies()
            predictive_alerts = self.regression_detector.generate_predictive_alerts()
            performance_health_score = self.regression_detector.get_performance_health_score()
            
            # Cost optimization analysis
            cost_breakdown = self.cost_analyzer.analyze_cost_breakdown(analysis_period_days)
            cost_optimization_opportunities = self.cost_analyzer.identify_optimization_opportunities(
                analysis_period_days
            )
            cost_efficiency_metrics = self.cost_analyzer.get_cost_efficiency_metrics()
            
            # Calculate overall health score
            overall_health_score = self._calculate_overall_health_score(
                execution_efficiency_metrics,
                performance_health_score,
                resource_trends,
                cost_efficiency_metrics
            )
            
            # Generate priority recommendations
            priority_recommendations = self._generate_priority_recommendations(
                execution_recommendations,
                dag_optimization,
                resource_trends,
                performance_regressions,
                cost_optimization_opportunities
            )
            
            # Generate continuous improvement plan
            continuous_improvement_plan = self._generate_continuous_improvement_plan(
                priority_recommendations,
                predictive_alerts
            )
            
            # Create comprehensive report
            report = AnalyticsReport(
                generated_at=datetime.now(),
                analysis_period_days=analysis_period_days,
                execution_insights=execution_insights,
                execution_recommendations=execution_recommendations,
                execution_efficiency_metrics=execution_efficiency_metrics,
                dag_optimization=dag_optimization,
                resource_trends=resource_trends,
                capacity_predictions=capacity_predictions,
                resource_status=resource_status,
                performance_regressions=performance_regressions,
                performance_anomalies=performance_anomalies,
                predictive_alerts=predictive_alerts,
                performance_health_score=performance_health_score,
                cost_breakdown=cost_breakdown,
                cost_optimization_opportunities=cost_optimization_opportunities,
                cost_efficiency_metrics=cost_efficiency_metrics,
                overall_health_score=overall_health_score,
                priority_recommendations=priority_recommendations,
                continuous_improvement_plan=continuous_improvement_plan
            )
            
            # Store in history
            self.analysis_history.append(report)
            self.last_analysis_time = datetime.now()
            
            self.logger.info(
                "Completed comprehensive analysis",
                extra={
                    'overall_health_score': overall_health_score,
                    'priority_recommendations': len(priority_recommendations),
                    'improvement_actions': len(continuous_improvement_plan),
                    'execution_insights': len(execution_insights),
                    'performance_regressions': len(performance_regressions),
                    'cost_opportunities': len(cost_optimization_opportunities)
                }
            )
            
            return report
    
    def get_real_time_insights(self) -> Dict[str, Any]:
        """
        Get real-time insights and alerts.
        
        Returns:
            Dictionary with current system insights and alerts
        """
        with self.trace_operation("get_real_time_insights"):
            insights = {
                'timestamp': datetime.now().isoformat(),
                'resource_status': self.resource_analyzer.get_current_resource_status(),
                'cost_alerts': self.cost_analyzer.generate_cost_alerts(),
                'performance_health': self.regression_detector.get_performance_health_score(),
                'recent_anomalies': self.regression_detector.detect_performance_anomalies(
                    analysis_window_hours=1
                ),
                'system_recommendations': self._get_immediate_recommendations()
            }
            
            return insights
    
    def should_run_analysis(self) -> bool:
        """Check if it's time to run analysis based on interval."""
        if self.last_analysis_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last.total_seconds() >= (self.analysis_interval_minutes * 60)
    
    def auto_analyze_if_needed(self) -> Optional[AnalyticsReport]:
        """Run analysis automatically if interval has passed."""
        if self.should_run_analysis():
            return self.run_comprehensive_analysis()
        return None
    
    def _calculate_overall_health_score(self,
                                      execution_metrics: Dict[str, Any],
                                      performance_health: Dict[str, Any],
                                      resource_trends: List[ResourceTrend],
                                      cost_metrics: Dict[str, Any]) -> float:
        """Calculate overall system health score (0-100)."""
        scores = []
        
        # Execution efficiency score
        if execution_metrics:
            parallel_efficiency = execution_metrics.get('parallel_efficiency', {}).get('efficiency', 0.5)
            resource_efficiency = execution_metrics.get('resource_efficiency', {}).get('cpu_efficiency', 0.5)
            execution_score = (parallel_efficiency + resource_efficiency) * 50
            scores.append(execution_score)
        
        # Performance health score
        if performance_health:
            perf_score = performance_health.get('overall_score', 50)
            scores.append(perf_score)
        
        # Resource health score
        resource_score = 100  # Start optimistic
        for trend in resource_trends:
            if trend.current_level.value in ['high', 'critical']:
                resource_score -= 20
            elif trend.trend_direction == 'increasing' and trend.trend_strength > 0.7:
                resource_score -= 10
        resource_score = max(0, resource_score)
        scores.append(resource_score)
        
        # Cost efficiency score
        if cost_metrics:
            cost_score = cost_metrics.get('efficiency_score', 50)
            scores.append(cost_score)
        
        # Calculate weighted average
        if scores:
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 50  # Neutral score if no data
        
        return min(100, max(0, overall_score))
    
    def _generate_priority_recommendations(self,
                                         execution_recommendations: List[OptimizationRecommendation],
                                         dag_optimization: Optional[OptimizedDAGStructure],
                                         resource_trends: List[ResourceTrend],
                                         performance_regressions: List[RegressionDetection],
                                         cost_opportunities: List[CostOptimizationOpportunity]) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations across all analytics areas."""
        recommendations = []
        
        # Critical performance regressions
        critical_regressions = [r for r in performance_regressions if r.severity.value == 'critical']
        for regression in critical_regressions:
            recommendations.append({
                'category': 'Performance',
                'priority': 'CRITICAL',
                'title': f'Address critical {regression.regression_type.value} regression',
                'description': regression.description,
                'estimated_impact': {'performance_improvement': regression.degradation_percent},
                'source': 'performance_regression_detector'
            })
        
        # High-impact cost optimizations
        high_impact_cost = [o for o in cost_opportunities if o.potential_savings > 100]
        for opportunity in high_impact_cost[:3]:  # Top 3
            recommendations.append({
                'category': 'Cost',
                'priority': 'HIGH',
                'title': opportunity.description,
                'description': f"Potential savings: ${opportunity.potential_savings:.2f}",
                'estimated_impact': {'cost_savings': opportunity.potential_savings},
                'source': 'cost_optimization_analyzer'
            })
        
        # Critical resource trends
        critical_resources = [t for t in resource_trends if t.current_level.value == 'critical']
        for trend in critical_resources:
            recommendations.append({
                'category': 'Resources',
                'priority': 'CRITICAL',
                'title': f'Address critical {trend.resource_type.value} utilization',
                'description': f'{trend.resource_type.value.title()} at critical level',
                'estimated_impact': {'resource_optimization': 30},
                'source': 'resource_utilization_analyzer'
            })
        
        # High-priority execution optimizations
        high_priority_exec = [r for r in execution_recommendations if r.priority == 'HIGH']
        for rec in high_priority_exec[:2]:  # Top 2
            recommendations.append({
                'category': 'Execution',
                'priority': 'HIGH',
                'title': rec.title,
                'description': rec.description,
                'estimated_impact': rec.expected_benefit,
                'source': 'execution_pattern_analyzer'
            })
        
        # DAG structure optimizations
        if dag_optimization and dag_optimization.optimizations_applied:
            total_improvement = dag_optimization.performance_prediction.get('total_improvement', 0)
            if total_improvement > 20:  # Significant improvement
                recommendations.append({
                    'category': 'Architecture',
                    'priority': 'MEDIUM',
                    'title': 'Apply DAG structure optimizations',
                    'description': f'Potential {total_improvement:.1f}% improvement from structure optimization',
                    'estimated_impact': {'performance_improvement': total_improvement},
                    'source': 'dag_structure_optimizer'
                })
        
        # Sort by priority
        priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _generate_continuous_improvement_plan(self,
                                            priority_recommendations: List[Dict[str, Any]],
                                            predictive_alerts: List[PredictiveAlert]) -> List[Dict[str, Any]]:
        """Generate continuous improvement action plan."""
        improvement_actions = []
        
        # Convert priority recommendations to improvement actions
        for rec in priority_recommendations:
            action = {
                'category': rec['category'],
                'priority': rec['priority'],
                'title': rec['title'],
                'description': rec['description'],
                'estimated_impact': rec['estimated_impact'],
                'implementation_effort': 'MEDIUM',  # Default
                'timeline': self._estimate_timeline(rec['priority']),
                'success_metrics': self._generate_success_metrics(rec),
                'dependencies': [],
                'source': rec['source']
            }
            improvement_actions.append(action)
        
        # Add preventive actions from predictive alerts
        for alert in predictive_alerts:
            if alert.severity.value in ['high', 'critical']:
                action = {
                    'category': 'Prevention',
                    'priority': alert.severity.value.upper(),
                    'title': f'Prevent {alert.alert_type}',
                    'description': alert.description,
                    'estimated_impact': {'risk_reduction': 50},
                    'implementation_effort': 'MEDIUM',
                    'timeline': self._estimate_timeline_from_prediction(alert),
                    'success_metrics': ['Alert prevented', 'System stability maintained'],
                    'dependencies': [],
                    'source': 'performance_regression_detector'
                }
                improvement_actions.append(action)
        
        # Add systematic improvements
        improvement_actions.extend(self._generate_systematic_improvements())
        
        return improvement_actions
    
    def _get_immediate_recommendations(self) -> List[Dict[str, Any]]:
        """Get immediate recommendations for current system state."""
        recommendations = []
        
        # Check resource status
        resource_status = self.resource_analyzer.get_current_resource_status()
        
        for resource_type, status in resource_status.items():
            if isinstance(status, dict) and status.get('level') == 'critical':
                recommendations.append({
                    'type': 'immediate_action',
                    'priority': 'CRITICAL',
                    'title': f'Critical {resource_type} utilization',
                    'action': f'Reduce {resource_type} load immediately',
                    'urgency': 'NOW'
                })
        
        # Check cost alerts
        cost_alerts = self.cost_analyzer.generate_cost_alerts()
        critical_cost_alerts = [a for a in cost_alerts if a.severity == 'CRITICAL']
        
        for alert in critical_cost_alerts:
            recommendations.append({
                'type': 'immediate_action',
                'priority': 'CRITICAL',
                'title': alert.description,
                'action': alert.recommended_actions[0] if alert.recommended_actions else 'Review cost controls',
                'urgency': 'NOW'
            })
        
        return recommendations
    
    def _estimate_timeline(self, priority: str) -> str:
        """Estimate implementation timeline based on priority."""
        timeline_map = {
            'CRITICAL': 'IMMEDIATE',
            'HIGH': 'DAYS',
            'MEDIUM': 'WEEKS',
            'LOW': 'MONTHS'
        }
        return timeline_map.get(priority, 'WEEKS')
    
    def _estimate_timeline_from_prediction(self, alert: PredictiveAlert) -> str:
        """Estimate timeline based on predictive alert timing."""
        time_to_occurrence = alert.predicted_occurrence_time - datetime.now()
        
        if time_to_occurrence.total_seconds() < 3600:  # Less than 1 hour
            return 'IMMEDIATE'
        elif time_to_occurrence.total_seconds() < 86400:  # Less than 1 day
            return 'HOURS'
        elif time_to_occurrence.days < 7:  # Less than 1 week
            return 'DAYS'
        else:
            return 'WEEKS'
    
    def _generate_success_metrics(self, recommendation: Dict[str, Any]) -> List[str]:
        """Generate success metrics for a recommendation."""
        category = recommendation['category'].lower()
        
        if category == 'performance':
            return [
                'Execution time improvement measured',
                'Success rate increase verified',
                'Performance regression resolved'
            ]
        elif category == 'cost':
            return [
                'Cost reduction achieved',
                'Cost efficiency improved',
                'Budget targets met'
            ]
        elif category == 'resources':
            return [
                'Resource utilization optimized',
                'Capacity thresholds maintained',
                'Resource efficiency improved'
            ]
        elif category == 'execution':
            return [
                'Execution patterns optimized',
                'Parallel efficiency increased',
                'Task completion rate improved'
            ]
        else:
            return [
                'Improvement objectives met',
                'System stability maintained',
                'Performance targets achieved'
            ]
    
    def _generate_systematic_improvements(self) -> List[Dict[str, Any]]:
        """Generate systematic improvement actions."""
        return [
            {
                'category': 'Monitoring',
                'priority': 'MEDIUM',
                'title': 'Enhance analytics data collection',
                'description': 'Improve data collection for better insights',
                'estimated_impact': {'insight_quality': 20},
                'implementation_effort': 'LOW',
                'timeline': 'WEEKS',
                'success_metrics': [
                    'Data collection coverage increased',
                    'Analytics accuracy improved',
                    'Insight generation enhanced'
                ],
                'dependencies': [],
                'source': 'analytics_orchestrator'
            },
            {
                'category': 'Automation',
                'priority': 'LOW',
                'title': 'Implement automated optimization',
                'description': 'Automate routine optimization tasks',
                'estimated_impact': {'efficiency': 15},
                'implementation_effort': 'HIGH',
                'timeline': 'MONTHS',
                'success_metrics': [
                    'Automation coverage increased',
                    'Manual intervention reduced',
                    'System self-optimization improved'
                ],
                'dependencies': ['Enhanced monitoring'],
                'source': 'analytics_orchestrator'
            }
        ]
    
    def export_comprehensive_report(self, report: AnalyticsReport, output_path: Path) -> None:
        """Export comprehensive analytics report to file."""
        with self.trace_operation("export_comprehensive_report"):
            # Convert report to serializable format
            report_dict = asdict(report)
            
            # Add metadata
            report_dict['metadata'] = {
                'report_version': '1.0',
                'analytics_components': [
                    'execution_pattern_analyzer',
                    'dag_structure_optimizer',
                    'resource_utilization_analyzer',
                    'performance_regression_detector',
                    'cost_optimization_analyzer'
                ],
                'analysis_capabilities': [
                    'Pattern recognition',
                    'Structure optimization',
                    'Resource monitoring',
                    'Regression detection',
                    'Cost optimization',
                    'Predictive analytics'
                ]
            }
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write report
            with open(output_path, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
            
            self.logger.info(
                f"Exported comprehensive analytics report to {output_path}",
                extra={
                    'report_size': len(json.dumps(report_dict)),
                    'overall_health_score': report.overall_health_score,
                    'recommendations_count': len(report.priority_recommendations)
                }
            )
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of analytics system status."""
        with self.trace_operation("get_analytics_summary"):
            latest_report = self.analysis_history[-1] if self.analysis_history else None
            
            summary = {
                'analytics_status': 'active',
                'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
                'analysis_interval_minutes': self.analysis_interval_minutes,
                'reports_generated': len(self.analysis_history),
                'components_active': {
                    'execution_analyzer': True,
                    'dag_optimizer': True,
                    'resource_analyzer': True,
                    'regression_detector': True,
                    'cost_analyzer': True
                }
            }
            
            if latest_report:
                summary['latest_analysis'] = {
                    'overall_health_score': latest_report.overall_health_score,
                    'priority_recommendations': len(latest_report.priority_recommendations),
                    'performance_regressions': len(latest_report.performance_regressions),
                    'cost_opportunities': len(latest_report.cost_optimization_opportunities),
                    'predictive_alerts': len(latest_report.predictive_alerts)
                }
            
            return summary