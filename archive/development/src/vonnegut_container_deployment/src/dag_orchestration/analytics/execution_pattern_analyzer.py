"""
Execution Pattern Analyzer - Advanced Analytics for DAG Orchestration

This module provides comprehensive analysis of DAG execution patterns,
identifying optimization opportunities and performance insights.
"""

import json
import logging
import statistics
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class PatternType(Enum):
    """Types of execution patterns that can be detected."""
    SEQUENTIAL_BOTTLENECK = "sequential_bottleneck"
    RESOURCE_CONTENTION = "resource_contention"
    DEPENDENCY_HOTSPOT = "dependency_hotspot"
    PARALLEL_INEFFICIENCY = "parallel_inefficiency"
    COST_OPTIMIZATION = "cost_optimization"
    FAILURE_CORRELATION = "failure_correlation"


@dataclass
class ExecutionMetrics:
    """Metrics for a single task execution."""
    task_id: str
    execution_time: float
    cpu_usage: float
    memory_usage: float
    cost: float
    success: bool
    timestamp: datetime
    dependencies: List[str]
    parallel_group: Optional[str] = None
    llm_provider: Optional[str] = None
    error_type: Optional[str] = None


@dataclass
class PatternInsight:
    """Insight discovered from pattern analysis."""
    pattern_type: PatternType
    confidence: float
    impact_score: float
    description: str
    affected_tasks: List[str]
    optimization_recommendation: str
    estimated_improvement: Dict[str, float]  # metric -> improvement percentage


@dataclass
class OptimizationRecommendation:
    """Specific optimization recommendation."""
    category: str
    priority: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    implementation_effort: str  # TRIVIAL, LOW, MEDIUM, HIGH
    expected_benefit: Dict[str, float]  # metric -> improvement
    affected_components: List[str]
    implementation_steps: List[str]


class ExecutionPatternAnalyzer(ReflectiveModule):
    """
    Advanced analytics engine for DAG execution pattern analysis.
    
    Provides comprehensive analysis of execution patterns, identifies
    optimization opportunities, and generates actionable recommendations.
    """
    
    def __init__(self, history_retention_days: int = 30):
        super().__init__()
        self.history_retention_days = history_retention_days
        self.execution_history: List[ExecutionMetrics] = []
        self.pattern_cache: Dict[str, List[PatternInsight]] = {}
        self.optimization_history: List[OptimizationRecommendation] = []
        
        # Pattern detection thresholds
        self.thresholds = {
            'bottleneck_ratio': 0.8,  # Task takes 80%+ of total time
            'resource_contention': 0.9,  # Resource usage > 90%
            'parallel_efficiency': 0.6,  # Parallel efficiency < 60%
            'cost_variance': 0.3,  # Cost variance > 30%
            'failure_correlation': 0.7,  # Failure correlation > 70%
        }
        
        self.logger = logging.getLogger(__name__)
    
    def add_execution_metrics(self, metrics: ExecutionMetrics) -> None:
        """Add execution metrics to the analysis dataset."""
        with self.trace_operation("add_execution_metrics"):
            self.execution_history.append(metrics)
            self._cleanup_old_metrics()
            self._invalidate_pattern_cache()
            
            self.logger.info(
                f"Added execution metrics for task {metrics.task_id}",
                extra={
                    'task_id': metrics.task_id,
                    'execution_time': metrics.execution_time,
                    'success': metrics.success,
                    'cost': metrics.cost
                }
            )
    
    def analyze_execution_patterns(self, 
                                 time_window_hours: Optional[int] = None) -> List[PatternInsight]:
        """
        Analyze execution patterns and identify optimization opportunities.
        
        Args:
            time_window_hours: Limit analysis to recent executions (None for all)
            
        Returns:
            List of pattern insights with optimization recommendations
        """
        with self.trace_operation("analyze_execution_patterns"):
            cache_key = f"patterns_{time_window_hours or 'all'}"
            
            if cache_key in self.pattern_cache:
                return self.pattern_cache[cache_key]
            
            # Filter metrics by time window
            metrics = self._filter_metrics_by_time(time_window_hours)
            
            if not metrics:
                return []
            
            insights = []
            
            # Detect different pattern types
            insights.extend(self._detect_sequential_bottlenecks(metrics))
            insights.extend(self._detect_resource_contention(metrics))
            insights.extend(self._detect_dependency_hotspots(metrics))
            insights.extend(self._detect_parallel_inefficiencies(metrics))
            insights.extend(self._detect_cost_optimization_opportunities(metrics))
            insights.extend(self._detect_failure_correlations(metrics))
            
            # Sort by impact score
            insights.sort(key=lambda x: x.impact_score, reverse=True)
            
            # Cache results
            self.pattern_cache[cache_key] = insights
            
            self.logger.info(
                f"Analyzed execution patterns: {len(insights)} insights found",
                extra={
                    'insights_count': len(insights),
                    'time_window_hours': time_window_hours,
                    'metrics_analyzed': len(metrics)
                }
            )
            
            return insights
    
    def generate_optimization_recommendations(self, 
                                           insights: Optional[List[PatternInsight]] = None) -> List[OptimizationRecommendation]:
        """
        Generate specific optimization recommendations based on pattern insights.
        
        Args:
            insights: Pattern insights to base recommendations on (None for latest)
            
        Returns:
            List of prioritized optimization recommendations
        """
        with self.trace_operation("generate_optimization_recommendations"):
            if insights is None:
                insights = self.analyze_execution_patterns()
            
            recommendations = []
            
            for insight in insights:
                recs = self._generate_recommendations_for_pattern(insight)
                recommendations.extend(recs)
            
            # Deduplicate and prioritize
            recommendations = self._deduplicate_recommendations(recommendations)
            recommendations = self._prioritize_recommendations(recommendations)
            
            # Store in history
            self.optimization_history.extend(recommendations)
            
            self.logger.info(
                f"Generated {len(recommendations)} optimization recommendations",
                extra={
                    'recommendations_count': len(recommendations),
                    'high_priority': len([r for r in recommendations if r.priority == 'HIGH']),
                    'medium_priority': len([r for r in recommendations if r.priority == 'MEDIUM']),
                    'low_priority': len([r for r in recommendations if r.priority == 'LOW'])
                }
            )
            
            return recommendations
    
    def get_execution_efficiency_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive execution efficiency metrics.
        
        Returns:
            Dictionary of efficiency metrics and trends
        """
        with self.trace_operation("get_execution_efficiency_metrics"):
            if not self.execution_history:
                return {}
            
            metrics = {}
            
            # Overall efficiency metrics
            metrics['overall'] = self._calculate_overall_efficiency()
            
            # Parallel execution efficiency
            metrics['parallel_efficiency'] = self._calculate_parallel_efficiency()
            
            # Resource utilization efficiency
            metrics['resource_efficiency'] = self._calculate_resource_efficiency()
            
            # Cost efficiency
            metrics['cost_efficiency'] = self._calculate_cost_efficiency()
            
            # Failure rate analysis
            metrics['reliability'] = self._calculate_reliability_metrics()
            
            # Trend analysis
            metrics['trends'] = self._calculate_trend_metrics()
            
            self.logger.info(
                "Calculated execution efficiency metrics",
                extra={'metrics_categories': list(metrics.keys())}
            )
            
            return metrics
    
    def _filter_metrics_by_time(self, hours: Optional[int]) -> List[ExecutionMetrics]:
        """Filter metrics by time window."""
        if hours is None:
            return self.execution_history
        
        cutoff = datetime.now() - timedelta(hours=hours)
        return [m for m in self.execution_history if m.timestamp >= cutoff]
    
    def _detect_sequential_bottlenecks(self, metrics: List[ExecutionMetrics]) -> List[PatternInsight]:
        """Detect tasks that create sequential bottlenecks."""
        insights = []
        
        # Group by execution session (assuming tasks with similar timestamps)
        sessions = self._group_by_execution_session(metrics)
        
        for session_metrics in sessions:
            if len(session_metrics) < 2:
                continue
            
            total_time = sum(m.execution_time for m in session_metrics)
            
            for metric in session_metrics:
                time_ratio = metric.execution_time / total_time
                
                if time_ratio > self.thresholds['bottleneck_ratio']:
                    insights.append(PatternInsight(
                        pattern_type=PatternType.SEQUENTIAL_BOTTLENECK,
                        confidence=min(time_ratio, 1.0),
                        impact_score=time_ratio * 100,
                        description=f"Task {metric.task_id} consumes {time_ratio:.1%} of total execution time",
                        affected_tasks=[metric.task_id],
                        optimization_recommendation=f"Consider parallelizing or optimizing task {metric.task_id}",
                        estimated_improvement={'execution_time': time_ratio * 50}  # 50% of bottleneck time
                    ))
        
        return insights
    
    def _detect_resource_contention(self, metrics: List[ExecutionMetrics]) -> List[PatternInsight]:
        """Detect resource contention patterns."""
        insights = []
        
        # Analyze CPU and memory usage patterns
        high_cpu_tasks = [m for m in metrics if m.cpu_usage > self.thresholds['resource_contention']]
        high_memory_tasks = [m for m in metrics if m.memory_usage > self.thresholds['resource_contention']]
        
        if high_cpu_tasks:
            task_ids = [m.task_id for m in high_cpu_tasks]
            avg_cpu = statistics.mean(m.cpu_usage for m in high_cpu_tasks)
            
            insights.append(PatternInsight(
                pattern_type=PatternType.RESOURCE_CONTENTION,
                confidence=min(avg_cpu, 1.0),
                impact_score=len(high_cpu_tasks) * avg_cpu * 50,
                description=f"{len(high_cpu_tasks)} tasks showing high CPU usage (avg: {avg_cpu:.1%})",
                affected_tasks=task_ids,
                optimization_recommendation="Consider CPU-aware scheduling or task optimization",
                estimated_improvement={'resource_efficiency': 25, 'execution_time': 15}
            ))
        
        if high_memory_tasks:
            task_ids = [m.task_id for m in high_memory_tasks]
            avg_memory = statistics.mean(m.memory_usage for m in high_memory_tasks)
            
            insights.append(PatternInsight(
                pattern_type=PatternType.RESOURCE_CONTENTION,
                confidence=min(avg_memory, 1.0),
                impact_score=len(high_memory_tasks) * avg_memory * 50,
                description=f"{len(high_memory_tasks)} tasks showing high memory usage (avg: {avg_memory:.1%})",
                affected_tasks=task_ids,
                optimization_recommendation="Consider memory-aware scheduling or task optimization",
                estimated_improvement={'resource_efficiency': 20, 'execution_time': 10}
            ))
        
        return insights
    
    def _detect_dependency_hotspots(self, metrics: List[ExecutionMetrics]) -> List[PatternInsight]:
        """Detect tasks that are dependency hotspots."""
        insights = []
        
        # Count how often each task appears as a dependency
        dependency_counts = Counter()
        for metric in metrics:
            for dep in metric.dependencies:
                dependency_counts[dep] += 1
        
        if not dependency_counts:
            return insights
        
        # Find hotspots (tasks that are dependencies for many others)
        max_deps = max(dependency_counts.values())
        hotspot_threshold = max(3, max_deps * 0.5)  # At least 3 or 50% of max
        
        for task_id, count in dependency_counts.items():
            if count >= hotspot_threshold:
                # Find metrics for this task
                task_metrics = [m for m in metrics if m.task_id == task_id]
                if task_metrics:
                    avg_time = statistics.mean(m.execution_time for m in task_metrics)
                    
                    insights.append(PatternInsight(
                        pattern_type=PatternType.DEPENDENCY_HOTSPOT,
                        confidence=min(count / max_deps, 1.0),
                        impact_score=count * avg_time,
                        description=f"Task {task_id} is a dependency for {count} other tasks",
                        affected_tasks=[task_id],
                        optimization_recommendation=f"Optimize task {task_id} as it blocks {count} dependent tasks",
                        estimated_improvement={'execution_time': count * 10, 'parallel_efficiency': 20}
                    ))
        
        return insights
    
    def _detect_parallel_inefficiencies(self, metrics: List[ExecutionMetrics]) -> List[PatternInsight]:
        """Detect parallel execution inefficiencies."""
        insights = []
        
        # Group by parallel groups
        parallel_groups = defaultdict(list)
        for metric in metrics:
            if metric.parallel_group:
                parallel_groups[metric.parallel_group].append(metric)
        
        for group_id, group_metrics in parallel_groups.items():
            if len(group_metrics) < 2:
                continue
            
            # Calculate parallel efficiency
            execution_times = [m.execution_time for m in group_metrics]
            max_time = max(execution_times)
            total_time = sum(execution_times)
            
            # Ideal parallel time would be max_time
            # Actual sequential time would be total_time
            efficiency = max_time / (total_time / len(execution_times))
            
            if efficiency < self.thresholds['parallel_efficiency']:
                task_ids = [m.task_id for m in group_metrics]
                
                insights.append(PatternInsight(
                    pattern_type=PatternType.PARALLEL_INEFFICIENCY,
                    confidence=1.0 - efficiency,
                    impact_score=(1.0 - efficiency) * total_time,
                    description=f"Parallel group {group_id} has low efficiency ({efficiency:.1%})",
                    affected_tasks=task_ids,
                    optimization_recommendation=f"Rebalance parallel group {group_id} or optimize slow tasks",
                    estimated_improvement={'parallel_efficiency': (1.0 - efficiency) * 50}
                ))
        
        return insights
    
    def _detect_cost_optimization_opportunities(self, metrics: List[ExecutionMetrics]) -> List[PatternInsight]:
        """Detect cost optimization opportunities."""
        insights = []
        
        # Analyze cost patterns by LLM provider
        provider_costs = defaultdict(list)
        for metric in metrics:
            if metric.llm_provider and metric.cost > 0:
                provider_costs[metric.llm_provider].append(metric.cost)
        
        if len(provider_costs) > 1:
            # Compare provider costs
            provider_avg_costs = {
                provider: statistics.mean(costs)
                for provider, costs in provider_costs.items()
            }
            
            min_cost_provider = min(provider_avg_costs, key=provider_avg_costs.get)
            max_cost_provider = max(provider_avg_costs, key=provider_avg_costs.get)
            
            cost_difference = (provider_avg_costs[max_cost_provider] - 
                             provider_avg_costs[min_cost_provider])
            
            if cost_difference > 0:
                savings_potential = cost_difference / provider_avg_costs[max_cost_provider]
                
                insights.append(PatternInsight(
                    pattern_type=PatternType.COST_OPTIMIZATION,
                    confidence=min(savings_potential * 2, 1.0),
                    impact_score=savings_potential * 100,
                    description=f"Cost difference between providers: {min_cost_provider} vs {max_cost_provider}",
                    affected_tasks=[],
                    optimization_recommendation=f"Consider using {min_cost_provider} more frequently",
                    estimated_improvement={'cost': savings_potential * 100}
                ))
        
        return insights
    
    def _detect_failure_correlations(self, metrics: List[ExecutionMetrics]) -> List[PatternInsight]:
        """Detect failure correlation patterns."""
        insights = []
        
        failed_metrics = [m for m in metrics if not m.success]
        if not failed_metrics:
            return insights
        
        # Analyze failure patterns
        failure_by_task = defaultdict(int)
        failure_by_provider = defaultdict(int)
        failure_by_error_type = defaultdict(int)
        
        for metric in failed_metrics:
            failure_by_task[metric.task_id] += 1
            if metric.llm_provider:
                failure_by_provider[metric.llm_provider] += 1
            if metric.error_type:
                failure_by_error_type[metric.error_type] += 1
        
        total_executions = len(metrics)
        total_failures = len(failed_metrics)
        
        # High failure rate tasks
        for task_id, failure_count in failure_by_task.items():
            task_total = len([m for m in metrics if m.task_id == task_id])
            failure_rate = failure_count / task_total
            
            if failure_rate > self.thresholds['failure_correlation']:
                insights.append(PatternInsight(
                    pattern_type=PatternType.FAILURE_CORRELATION,
                    confidence=failure_rate,
                    impact_score=failure_rate * failure_count * 50,
                    description=f"Task {task_id} has high failure rate ({failure_rate:.1%})",
                    affected_tasks=[task_id],
                    optimization_recommendation=f"Investigate and fix reliability issues in task {task_id}",
                    estimated_improvement={'reliability': failure_rate * 80}
                ))
        
        return insights
    
    def _group_by_execution_session(self, metrics: List[ExecutionMetrics]) -> List[List[ExecutionMetrics]]:
        """Group metrics by execution session (similar timestamps)."""
        if not metrics:
            return []
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        sessions = []
        current_session = [sorted_metrics[0]]
        
        for metric in sorted_metrics[1:]:
            # If more than 1 hour gap, start new session
            if (metric.timestamp - current_session[-1].timestamp).total_seconds() > 3600:
                sessions.append(current_session)
                current_session = [metric]
            else:
                current_session.append(metric)
        
        if current_session:
            sessions.append(current_session)
        
        return sessions
    
    def _generate_recommendations_for_pattern(self, insight: PatternInsight) -> List[OptimizationRecommendation]:
        """Generate specific recommendations for a pattern insight."""
        recommendations = []
        
        if insight.pattern_type == PatternType.SEQUENTIAL_BOTTLENECK:
            recommendations.append(OptimizationRecommendation(
                category="Performance",
                priority="HIGH" if insight.impact_score > 50 else "MEDIUM",
                title=f"Optimize bottleneck task {insight.affected_tasks[0]}",
                description=insight.description,
                implementation_effort="MEDIUM",
                expected_benefit=insight.estimated_improvement,
                affected_components=insight.affected_tasks,
                implementation_steps=[
                    "Profile the bottleneck task to identify optimization opportunities",
                    "Consider breaking the task into smaller parallel subtasks",
                    "Optimize algorithms or data structures used in the task",
                    "Consider caching or memoization for repeated operations"
                ]
            ))
        
        elif insight.pattern_type == PatternType.RESOURCE_CONTENTION:
            recommendations.append(OptimizationRecommendation(
                category="Resource Management",
                priority="HIGH" if insight.impact_score > 75 else "MEDIUM",
                title="Implement resource-aware scheduling",
                description=insight.description,
                implementation_effort="MEDIUM",
                expected_benefit=insight.estimated_improvement,
                affected_components=insight.affected_tasks,
                implementation_steps=[
                    "Implement resource monitoring and limits",
                    "Add resource-aware task scheduling",
                    "Consider task queuing based on resource availability",
                    "Optimize resource-intensive tasks"
                ]
            ))
        
        elif insight.pattern_type == PatternType.DEPENDENCY_HOTSPOT:
            recommendations.append(OptimizationRecommendation(
                category="Architecture",
                priority="HIGH",
                title=f"Optimize dependency hotspot {insight.affected_tasks[0]}",
                description=insight.description,
                implementation_effort="HIGH",
                expected_benefit=insight.estimated_improvement,
                affected_components=insight.affected_tasks,
                implementation_steps=[
                    "Analyze why this task is a dependency for so many others",
                    "Consider breaking the task into smaller, independent parts",
                    "Implement caching for the task results",
                    "Optimize the task for faster execution"
                ]
            ))
        
        elif insight.pattern_type == PatternType.PARALLEL_INEFFICIENCY:
            recommendations.append(OptimizationRecommendation(
                category="Parallelization",
                priority="MEDIUM",
                title="Improve parallel execution efficiency",
                description=insight.description,
                implementation_effort="MEDIUM",
                expected_benefit=insight.estimated_improvement,
                affected_components=insight.affected_tasks,
                implementation_steps=[
                    "Analyze task execution times within parallel groups",
                    "Rebalance parallel groups to have similar execution times",
                    "Consider dynamic load balancing",
                    "Optimize slow tasks in parallel groups"
                ]
            ))
        
        elif insight.pattern_type == PatternType.COST_OPTIMIZATION:
            recommendations.append(OptimizationRecommendation(
                category="Cost Management",
                priority="MEDIUM",
                title="Optimize LLM provider selection",
                description=insight.description,
                implementation_effort="LOW",
                expected_benefit=insight.estimated_improvement,
                affected_components=[],
                implementation_steps=[
                    "Analyze task complexity vs provider capabilities",
                    "Implement cost-aware LLM selection",
                    "Consider task batching for cost efficiency",
                    "Monitor and adjust provider selection policies"
                ]
            ))
        
        elif insight.pattern_type == PatternType.FAILURE_CORRELATION:
            recommendations.append(OptimizationRecommendation(
                category="Reliability",
                priority="HIGH",
                title=f"Fix reliability issues in {insight.affected_tasks[0]}",
                description=insight.description,
                implementation_effort="MEDIUM",
                expected_benefit=insight.estimated_improvement,
                affected_components=insight.affected_tasks,
                implementation_steps=[
                    "Analyze failure logs and error patterns",
                    "Implement better error handling and retry logic",
                    "Add input validation and sanitization",
                    "Consider fallback mechanisms for critical tasks"
                ]
            ))
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Remove duplicate recommendations."""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            key = (rec.category, rec.title, tuple(sorted(rec.affected_components)))
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _prioritize_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Sort recommendations by priority and expected benefit."""
        priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        
        def sort_key(rec):
            priority_score = priority_order.get(rec.priority, 0)
            benefit_score = sum(rec.expected_benefit.values())
            return (priority_score, benefit_score)
        
        return sorted(recommendations, key=sort_key, reverse=True)
    
    def _calculate_overall_efficiency(self) -> Dict[str, float]:
        """Calculate overall execution efficiency metrics."""
        if not self.execution_history:
            return {}
        
        total_time = sum(m.execution_time for m in self.execution_history)
        total_cost = sum(m.cost for m in self.execution_history)
        success_rate = sum(1 for m in self.execution_history if m.success) / len(self.execution_history)
        
        return {
            'average_execution_time': total_time / len(self.execution_history),
            'total_cost': total_cost,
            'success_rate': success_rate,
            'cost_per_success': total_cost / max(sum(1 for m in self.execution_history if m.success), 1)
        }
    
    def _calculate_parallel_efficiency(self) -> Dict[str, float]:
        """Calculate parallel execution efficiency."""
        parallel_groups = defaultdict(list)
        for metric in self.execution_history:
            if metric.parallel_group:
                parallel_groups[metric.parallel_group].append(metric)
        
        if not parallel_groups:
            return {'efficiency': 0.0, 'groups_analyzed': 0}
        
        efficiencies = []
        for group_metrics in parallel_groups.values():
            if len(group_metrics) > 1:
                execution_times = [m.execution_time for m in group_metrics]
                max_time = max(execution_times)
                avg_time = statistics.mean(execution_times)
                efficiency = max_time / (sum(execution_times) / len(execution_times))
                efficiencies.append(efficiency)
        
        return {
            'efficiency': statistics.mean(efficiencies) if efficiencies else 0.0,
            'groups_analyzed': len(efficiencies)
        }
    
    def _calculate_resource_efficiency(self) -> Dict[str, float]:
        """Calculate resource utilization efficiency."""
        if not self.execution_history:
            return {}
        
        cpu_usage = [m.cpu_usage for m in self.execution_history if m.cpu_usage > 0]
        memory_usage = [m.memory_usage for m in self.execution_history if m.memory_usage > 0]
        
        return {
            'average_cpu_usage': statistics.mean(cpu_usage) if cpu_usage else 0.0,
            'average_memory_usage': statistics.mean(memory_usage) if memory_usage else 0.0,
            'cpu_efficiency': min(statistics.mean(cpu_usage), 1.0) if cpu_usage else 0.0,
            'memory_efficiency': min(statistics.mean(memory_usage), 1.0) if memory_usage else 0.0
        }
    
    def _calculate_cost_efficiency(self) -> Dict[str, float]:
        """Calculate cost efficiency metrics."""
        if not self.execution_history:
            return {}
        
        costs = [m.cost for m in self.execution_history if m.cost > 0]
        times = [m.execution_time for m in self.execution_history if m.cost > 0]
        
        if not costs:
            return {'cost_per_second': 0.0, 'total_cost': 0.0}
        
        return {
            'cost_per_second': sum(costs) / sum(times) if times else 0.0,
            'total_cost': sum(costs),
            'average_cost_per_task': statistics.mean(costs)
        }
    
    def _calculate_reliability_metrics(self) -> Dict[str, float]:
        """Calculate reliability and failure metrics."""
        if not self.execution_history:
            return {}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for m in self.execution_history if m.success)
        failed_executions = total_executions - successful_executions
        
        # Failure rate by error type
        error_types = Counter(m.error_type for m in self.execution_history if not m.success and m.error_type)
        
        return {
            'success_rate': successful_executions / total_executions,
            'failure_rate': failed_executions / total_executions,
            'total_failures': failed_executions,
            'most_common_error': error_types.most_common(1)[0][0] if error_types else None
        }
    
    def _calculate_trend_metrics(self) -> Dict[str, Any]:
        """Calculate trend metrics over time."""
        if len(self.execution_history) < 2:
            return {}
        
        # Sort by timestamp
        sorted_metrics = sorted(self.execution_history, key=lambda m: m.timestamp)
        
        # Split into two halves for trend analysis
        mid_point = len(sorted_metrics) // 2
        first_half = sorted_metrics[:mid_point]
        second_half = sorted_metrics[mid_point:]
        
        def calculate_period_metrics(metrics):
            if not metrics:
                return {}
            return {
                'avg_execution_time': statistics.mean(m.execution_time for m in metrics),
                'success_rate': sum(1 for m in metrics if m.success) / len(metrics),
                'avg_cost': statistics.mean(m.cost for m in metrics if m.cost > 0) or 0.0
            }
        
        first_metrics = calculate_period_metrics(first_half)
        second_metrics = calculate_period_metrics(second_half)
        
        trends = {}
        for metric in ['avg_execution_time', 'success_rate', 'avg_cost']:
            if metric in first_metrics and metric in second_metrics:
                if first_metrics[metric] > 0:
                    change = (second_metrics[metric] - first_metrics[metric]) / first_metrics[metric]
                    trends[f'{metric}_trend'] = change
        
        return trends
    
    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.history_retention_days)
        self.execution_history = [
            m for m in self.execution_history 
            if m.timestamp >= cutoff
        ]
    
    def _invalidate_pattern_cache(self) -> None:
        """Invalidate pattern analysis cache."""
        self.pattern_cache.clear()
    
    def export_analytics_report(self, output_path: Path) -> None:
        """Export comprehensive analytics report to JSON file."""
        with self.trace_operation("export_analytics_report"):
            insights = self.analyze_execution_patterns()
            recommendations = self.generate_optimization_recommendations(insights)
            efficiency_metrics = self.get_execution_efficiency_metrics()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'metrics_analyzed': len(self.execution_history),
                'insights': [asdict(insight) for insight in insights],
                'recommendations': [asdict(rec) for rec in recommendations],
                'efficiency_metrics': efficiency_metrics,
                'summary': {
                    'total_insights': len(insights),
                    'high_priority_recommendations': len([r for r in recommendations if r.priority == 'HIGH']),
                    'estimated_improvements': self._calculate_total_estimated_improvements(recommendations)
                }
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(
                f"Exported analytics report to {output_path}",
                extra={'report_size': len(json.dumps(report))}
            )
    
    def _calculate_total_estimated_improvements(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, float]:
        """Calculate total estimated improvements from all recommendations."""
        total_improvements = defaultdict(float)
        
        for rec in recommendations:
            for metric, improvement in rec.expected_benefit.items():
                total_improvements[metric] += improvement
        
        return dict(total_improvements)