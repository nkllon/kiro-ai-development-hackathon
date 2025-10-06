#!/usr/bin/env python3
"""
Execution Pattern Analyzer for DAG Orchestration
================================================

Analyzes execution patterns and provides optimization recommendations
based on historical execution data.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class PatternType(Enum):
    """Types of execution patterns."""
    PERFORMANCE_TREND = "performance_trend"
    RESOURCE_USAGE = "resource_usage"
    FAILURE_PATTERN = "failure_pattern"
    COST_PATTERN = "cost_pattern"
    SCHEDULING_PATTERN = "scheduling_pattern"
    DEPENDENCY_PATTERN = "dependency_pattern"


@dataclass
class ExecutionPattern:
    """Represents an identified execution pattern."""
    pattern_id: str
    pattern_type: PatternType
    description: str
    confidence: float  # 0.0 to 1.0
    frequency: int  # How often this pattern occurs
    impact_score: float  # 0.0 to 1.0 (higher = more impactful)
    first_observed: datetime
    last_observed: datetime
    pattern_data: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Result of execution pattern analysis."""
    analysis_id: str
    analysis_timestamp: datetime
    patterns_identified: List[ExecutionPattern]
    summary_statistics: Dict[str, Any]
    optimization_opportunities: List[str]
    analysis_duration: float
    data_points_analyzed: int


class ExecutionAnalyzer(ReflectiveModule):
    """
    Analyzer for execution patterns and optimization opportunities.
    
    Features:
    - Pattern identification and analysis
    - Performance trend analysis
    - Resource utilization patterns
    - Failure pattern detection
    - Optimization recommendations
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "ExecutionAnalyzer"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Analysis state
        self._execution_history: List[Dict[str, Any]] = []
        self._identified_patterns: Dict[str, ExecutionPattern] = {}
        self._analysis_history: List[AnalysisResult] = []
        
        # Configuration
        self._min_pattern_frequency = 3
        self._min_confidence_threshold = 0.7
        self._analysis_window_days = 30
        
        # Statistics
        self._total_analyses = 0
        self._patterns_identified = 0
        self._recommendations_generated = 0
        
        self._logger.info("ExecutionAnalyzer initialized")
    
    def record_execution(self, execution_data: Dict[str, Any]) -> None:
        """Record execution data for analysis."""
        execution_record = {
            'timestamp': datetime.now(),
            'execution_id': execution_data.get('execution_id', str(uuid.uuid4())),
            'duration': execution_data.get('duration', 0.0),
            'task_count': execution_data.get('task_count', 0),
            'success_rate': execution_data.get('success_rate', 1.0),
            'resource_usage': execution_data.get('resource_usage', {}),
            'cost': execution_data.get('cost', 0.0),
            'strategy': execution_data.get('strategy', 'unknown'),
            'errors': execution_data.get('errors', []),
            'metadata': execution_data.get('metadata', {})
        }
        
        self._execution_history.append(execution_record)
        
        # Keep only recent history (configurable window)
        cutoff_date = datetime.now() - timedelta(days=self._analysis_window_days)
        self._execution_history = [
            record for record in self._execution_history
            if record['timestamp'] > cutoff_date
        ]
        
        self._logger.debug(f"Recorded execution {execution_record['execution_id']}")
    
    async def analyze_patterns(self, analysis_window_hours: Optional[int] = None) -> AnalysisResult:
        """Analyze execution patterns and identify optimization opportunities."""
        with self.trace_operation("analyze_patterns", 
                                analysis_window_hours=analysis_window_hours) as trace:
            
            start_time = datetime.now()
            analysis_id = str(uuid.uuid4())
            
            # Filter data by analysis window
            if analysis_window_hours:
                cutoff_time = datetime.now() - timedelta(hours=analysis_window_hours)
                analysis_data = [
                    record for record in self._execution_history
                    if record['timestamp'] > cutoff_time
                ]
            else:
                analysis_data = self._execution_history.copy()
            
            if not analysis_data:
                self._logger.warning("No execution data available for analysis")
                return AnalysisResult(
                    analysis_id=analysis_id,
                    analysis_timestamp=start_time,
                    patterns_identified=[],
                    summary_statistics={},
                    optimization_opportunities=[],
                    analysis_duration=0.0,
                    data_points_analyzed=0
                )
            
            try:
                # Analyze different pattern types
                patterns = []
                
                # Performance trend patterns
                performance_patterns = self._analyze_performance_trends(analysis_data)
                patterns.extend(performance_patterns)
                
                # Resource usage patterns
                resource_patterns = self._analyze_resource_patterns(analysis_data)
                patterns.extend(resource_patterns)
                
                # Failure patterns
                failure_patterns = self._analyze_failure_patterns(analysis_data)
                patterns.extend(failure_patterns)
                
                # Cost patterns
                cost_patterns = self._analyze_cost_patterns(analysis_data)
                patterns.extend(cost_patterns)
                
                # Scheduling patterns
                scheduling_patterns = self._analyze_scheduling_patterns(analysis_data)
                patterns.extend(scheduling_patterns)
                
                # Filter patterns by confidence threshold
                significant_patterns = [
                    pattern for pattern in patterns
                    if pattern.confidence >= self._min_confidence_threshold
                ]
                
                # Update pattern registry
                for pattern in significant_patterns:
                    self._identified_patterns[pattern.pattern_id] = pattern
                
                # Generate summary statistics
                summary_stats = self._generate_summary_statistics(analysis_data)
                
                # Generate optimization opportunities
                optimization_opportunities = self._generate_optimization_opportunities(
                    significant_patterns, summary_stats
                )
                
                # Calculate analysis duration
                end_time = datetime.now()
                analysis_duration = (end_time - start_time).total_seconds()
                
                # Create analysis result
                result = AnalysisResult(
                    analysis_id=analysis_id,
                    analysis_timestamp=start_time,
                    patterns_identified=significant_patterns,
                    summary_statistics=summary_stats,
                    optimization_opportunities=optimization_opportunities,
                    analysis_duration=analysis_duration,
                    data_points_analyzed=len(analysis_data)
                )
                
                # Update statistics
                self._total_analyses += 1
                self._patterns_identified += len(significant_patterns)
                self._recommendations_generated += len(optimization_opportunities)
                
                # Store analysis result
                self._analysis_history.append(result)
                
                # Keep only recent analysis history
                if len(self._analysis_history) > 50:
                    self._analysis_history = self._analysis_history[-50:]
                
                trace.output_result = {
                    'analysis_id': analysis_id,
                    'patterns_found': len(significant_patterns),
                    'data_points_analyzed': len(analysis_data),
                    'analysis_duration': analysis_duration,
                    'optimization_opportunities': len(optimization_opportunities)
                }
                
                self._logger.info(f"Analysis {analysis_id} completed: "
                                f"{len(significant_patterns)} patterns identified, "
                                f"{len(optimization_opportunities)} optimization opportunities")
                
                return result
                
            except Exception as e:
                self._logger.error(f"Pattern analysis failed: {e}")
                trace.output_result = {'error': str(e)}
                raise e
    
    def _analyze_performance_trends(self, data: List[Dict[str, Any]]) -> List[ExecutionPattern]:
        """Analyze performance trends in execution data."""
        patterns = []
        
        if len(data) < 5:  # Need minimum data points
            return patterns
        
        # Extract performance metrics
        durations = [record['duration'] for record in data]
        success_rates = [record['success_rate'] for record in data]
        timestamps = [record['timestamp'] for record in data]
        
        # Analyze duration trends
        if len(durations) >= 5:
            # Simple trend analysis using linear regression approximation
            recent_durations = durations[-10:]  # Last 10 executions
            older_durations = durations[:-10] if len(durations) > 10 else durations[:5]
            
            recent_avg = statistics.mean(recent_durations)
            older_avg = statistics.mean(older_durations)
            
            if recent_avg > older_avg * 1.2:  # 20% increase
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.PERFORMANCE_TREND,
                    description="Performance degradation detected - execution times increasing",
                    confidence=0.8,
                    frequency=len(recent_durations),
                    impact_score=0.7,
                    first_observed=timestamps[-10] if len(timestamps) > 10 else timestamps[0],
                    last_observed=timestamps[-1],
                    pattern_data={
                        'recent_avg_duration': recent_avg,
                        'older_avg_duration': older_avg,
                        'degradation_percentage': ((recent_avg - older_avg) / older_avg) * 100
                    },
                    recommendations=[
                        "Investigate resource constraints",
                        "Review recent changes to execution strategy",
                        "Consider scaling up resources"
                    ]
                )
                patterns.append(pattern)
            
            elif recent_avg < older_avg * 0.8:  # 20% decrease
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.PERFORMANCE_TREND,
                    description="Performance improvement detected - execution times decreasing",
                    confidence=0.8,
                    frequency=len(recent_durations),
                    impact_score=0.5,
                    first_observed=timestamps[-10] if len(timestamps) > 10 else timestamps[0],
                    last_observed=timestamps[-1],
                    pattern_data={
                        'recent_avg_duration': recent_avg,
                        'older_avg_duration': older_avg,
                        'improvement_percentage': ((older_avg - recent_avg) / older_avg) * 100
                    },
                    recommendations=[
                        "Document successful optimizations",
                        "Consider applying similar optimizations to other workflows"
                    ]
                )
                patterns.append(pattern)
        
        # Analyze success rate trends
        if len(success_rates) >= 5:
            recent_success_rates = success_rates[-10:]
            recent_avg_success = statistics.mean(recent_success_rates)
            
            if recent_avg_success < 0.9:  # Less than 90% success rate
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.PERFORMANCE_TREND,
                    description="Low success rate pattern detected",
                    confidence=0.9,
                    frequency=len([sr for sr in recent_success_rates if sr < 0.9]),
                    impact_score=0.9,
                    first_observed=timestamps[-10] if len(timestamps) > 10 else timestamps[0],
                    last_observed=timestamps[-1],
                    pattern_data={
                        'recent_avg_success_rate': recent_avg_success,
                        'failure_frequency': len([sr for sr in recent_success_rates if sr < 1.0])
                    },
                    recommendations=[
                        "Investigate common failure causes",
                        "Implement additional error handling",
                        "Review task dependencies and timeouts"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_resource_patterns(self, data: List[Dict[str, Any]]) -> List[ExecutionPattern]:
        """Analyze resource usage patterns."""
        patterns = []
        
        # Extract resource usage data
        resource_data = [record['resource_usage'] for record in data if record['resource_usage']]
        
        if not resource_data:
            return patterns
        
        # Analyze CPU usage patterns
        cpu_usages = [res.get('cpu', 0) for res in resource_data]
        if cpu_usages:
            avg_cpu = statistics.mean(cpu_usages)
            max_cpu = max(cpu_usages)
            
            if avg_cpu > 0.8:  # High average CPU usage
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.RESOURCE_USAGE,
                    description="High CPU utilization pattern detected",
                    confidence=0.8,
                    frequency=len([cpu for cpu in cpu_usages if cpu > 0.8]),
                    impact_score=0.7,
                    first_observed=data[0]['timestamp'],
                    last_observed=data[-1]['timestamp'],
                    pattern_data={
                        'average_cpu_usage': avg_cpu,
                        'max_cpu_usage': max_cpu,
                        'high_usage_frequency': len([cpu for cpu in cpu_usages if cpu > 0.8])
                    },
                    recommendations=[
                        "Consider increasing CPU resources",
                        "Optimize task parallelization",
                        "Review CPU-intensive tasks"
                    ]
                )
                patterns.append(pattern)
        
        # Analyze memory usage patterns
        memory_usages = [res.get('memory', 0) for res in resource_data]
        if memory_usages:
            avg_memory = statistics.mean(memory_usages)
            max_memory = max(memory_usages)
            
            if avg_memory > 0.8:  # High average memory usage
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.RESOURCE_USAGE,
                    description="High memory utilization pattern detected",
                    confidence=0.8,
                    frequency=len([mem for mem in memory_usages if mem > 0.8]),
                    impact_score=0.7,
                    first_observed=data[0]['timestamp'],
                    last_observed=data[-1]['timestamp'],
                    pattern_data={
                        'average_memory_usage': avg_memory,
                        'max_memory_usage': max_memory,
                        'high_usage_frequency': len([mem for mem in memory_usages if mem > 0.8])
                    },
                    recommendations=[
                        "Consider increasing memory allocation",
                        "Optimize memory-intensive tasks",
                        "Implement memory cleanup strategies"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_failure_patterns(self, data: List[Dict[str, Any]]) -> List[ExecutionPattern]:
        """Analyze failure patterns in execution data."""
        patterns = []
        
        # Extract failure data
        failed_executions = [record for record in data if record['success_rate'] < 1.0]
        
        if not failed_executions:
            return patterns
        
        # Analyze failure frequency
        failure_rate = len(failed_executions) / len(data)
        
        if failure_rate > 0.1:  # More than 10% failure rate
            # Analyze error patterns
            all_errors = []
            for execution in failed_executions:
                all_errors.extend(execution.get('errors', []))
            
            # Count error types
            error_counts = {}
            for error in all_errors:
                error_type = error.get('type', 'unknown')
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Find most common error
            if error_counts:
                most_common_error = max(error_counts, key=error_counts.get)
                
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.FAILURE_PATTERN,
                    description=f"High failure rate pattern detected - most common: {most_common_error}",
                    confidence=0.9,
                    frequency=len(failed_executions),
                    impact_score=0.9,
                    first_observed=failed_executions[0]['timestamp'],
                    last_observed=failed_executions[-1]['timestamp'],
                    pattern_data={
                        'failure_rate': failure_rate,
                        'total_failures': len(failed_executions),
                        'most_common_error': most_common_error,
                        'error_distribution': error_counts
                    },
                    recommendations=[
                        f"Focus on resolving {most_common_error} errors",
                        "Implement better error handling and retry logic",
                        "Review task dependencies and resource requirements"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_cost_patterns(self, data: List[Dict[str, Any]]) -> List[ExecutionPattern]:
        """Analyze cost patterns in execution data."""
        patterns = []
        
        # Extract cost data
        costs = [record['cost'] for record in data if record['cost'] > 0]
        
        if not costs:
            return patterns
        
        # Analyze cost trends
        if len(costs) >= 5:
            recent_costs = costs[-10:]
            older_costs = costs[:-10] if len(costs) > 10 else costs[:5]
            
            recent_avg = statistics.mean(recent_costs)
            older_avg = statistics.mean(older_costs)
            
            if recent_avg > older_avg * 1.3:  # 30% cost increase
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.COST_PATTERN,
                    description="Cost increase pattern detected",
                    confidence=0.8,
                    frequency=len(recent_costs),
                    impact_score=0.8,
                    first_observed=data[-10]['timestamp'] if len(data) > 10 else data[0]['timestamp'],
                    last_observed=data[-1]['timestamp'],
                    pattern_data={
                        'recent_avg_cost': recent_avg,
                        'older_avg_cost': older_avg,
                        'cost_increase_percentage': ((recent_avg - older_avg) / older_avg) * 100
                    },
                    recommendations=[
                        "Review LLM usage and selection policies",
                        "Optimize task batching to reduce costs",
                        "Consider cost-first execution strategies"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_scheduling_patterns(self, data: List[Dict[str, Any]]) -> List[ExecutionPattern]:
        """Analyze scheduling patterns in execution data."""
        patterns = []
        
        # Extract strategy usage
        strategies = [record['strategy'] for record in data]
        strategy_counts = {}
        for strategy in strategies:
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # Analyze strategy effectiveness
        strategy_performance = {}
        for record in data:
            strategy = record['strategy']
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {'durations': [], 'success_rates': []}
            
            strategy_performance[strategy]['durations'].append(record['duration'])
            strategy_performance[strategy]['success_rates'].append(record['success_rate'])
        
        # Find best and worst performing strategies
        strategy_scores = {}
        for strategy, perf in strategy_performance.items():
            if len(perf['durations']) >= 3:  # Minimum data points
                avg_duration = statistics.mean(perf['durations'])
                avg_success_rate = statistics.mean(perf['success_rates'])
                # Score combines speed and reliability
                score = avg_success_rate / (avg_duration + 1)
                strategy_scores[strategy] = score
        
        if len(strategy_scores) > 1:
            best_strategy = max(strategy_scores, key=strategy_scores.get)
            worst_strategy = min(strategy_scores, key=strategy_scores.get)
            
            if strategy_scores[best_strategy] > strategy_scores[worst_strategy] * 1.5:
                pattern = ExecutionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=PatternType.SCHEDULING_PATTERN,
                    description=f"Strategy performance gap detected - {best_strategy} outperforms {worst_strategy}",
                    confidence=0.7,
                    frequency=strategy_counts.get(worst_strategy, 0),
                    impact_score=0.6,
                    first_observed=data[0]['timestamp'],
                    last_observed=data[-1]['timestamp'],
                    pattern_data={
                        'best_strategy': best_strategy,
                        'worst_strategy': worst_strategy,
                        'best_score': strategy_scores[best_strategy],
                        'worst_score': strategy_scores[worst_strategy],
                        'strategy_distribution': strategy_counts
                    },
                    recommendations=[
                        f"Increase usage of {best_strategy} strategy",
                        f"Investigate issues with {worst_strategy} strategy",
                        "Consider adaptive strategy selection based on task characteristics"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _generate_summary_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the analysis period."""
        if not data:
            return {}
        
        durations = [record['duration'] for record in data]
        success_rates = [record['success_rate'] for record in data]
        costs = [record['cost'] for record in data if record['cost'] > 0]
        task_counts = [record['task_count'] for record in data]
        
        stats = {
            'total_executions': len(data),
            'time_period': {
                'start': data[0]['timestamp'].isoformat(),
                'end': data[-1]['timestamp'].isoformat()
            },
            'duration_stats': {
                'average': statistics.mean(durations) if durations else 0,
                'median': statistics.median(durations) if durations else 0,
                'min': min(durations) if durations else 0,
                'max': max(durations) if durations else 0
            },
            'success_rate_stats': {
                'average': statistics.mean(success_rates) if success_rates else 0,
                'min': min(success_rates) if success_rates else 0,
                'failures': len([sr for sr in success_rates if sr < 1.0])
            },
            'cost_stats': {
                'total': sum(costs) if costs else 0,
                'average': statistics.mean(costs) if costs else 0,
                'max': max(costs) if costs else 0
            },
            'task_stats': {
                'total_tasks': sum(task_counts) if task_counts else 0,
                'average_tasks_per_execution': statistics.mean(task_counts) if task_counts else 0
            }
        }
        
        return stats
    
    def _generate_optimization_opportunities(self, patterns: List[ExecutionPattern],
                                           summary_stats: Dict[str, Any]) -> List[str]:
        """Generate optimization opportunities based on patterns and statistics."""
        opportunities = []
        
        # High-impact patterns generate specific opportunities
        high_impact_patterns = [p for p in patterns if p.impact_score > 0.7]
        
        for pattern in high_impact_patterns:
            opportunities.extend(pattern.recommendations)
        
        # General opportunities based on summary statistics
        if summary_stats.get('success_rate_stats', {}).get('average', 1.0) < 0.95:
            opportunities.append("Improve overall reliability - success rate below 95%")
        
        if summary_stats.get('duration_stats', {}).get('average', 0) > 300:  # 5 minutes
            opportunities.append("Optimize execution time - average duration exceeds 5 minutes")
        
        if summary_stats.get('cost_stats', {}).get('average', 0) > 10:  # $10 per execution
            opportunities.append("Optimize costs - average execution cost exceeds $10")
        
        # Remove duplicates and return
        return list(set(opportunities))
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of all identified patterns."""
        pattern_types = {}
        for pattern in self._identified_patterns.values():
            pattern_type = pattern.pattern_type.value
            if pattern_type not in pattern_types:
                pattern_types[pattern_type] = {'count': 0, 'avg_confidence': 0, 'avg_impact': 0}
            
            pattern_types[pattern_type]['count'] += 1
            pattern_types[pattern_type]['avg_confidence'] += pattern.confidence
            pattern_types[pattern_type]['avg_impact'] += pattern.impact_score
        
        # Calculate averages
        for pattern_type in pattern_types:
            count = pattern_types[pattern_type]['count']
            pattern_types[pattern_type]['avg_confidence'] /= count
            pattern_types[pattern_type]['avg_impact'] /= count
        
        return {
            'total_patterns': len(self._identified_patterns),
            'pattern_types': pattern_types,
            'total_analyses': self._total_analyses,
            'recommendations_generated': self._recommendations_generated,
            'data_points_available': len(self._execution_history)
        }


# Convenience functions
def create_execution_analyzer() -> ExecutionAnalyzer:
    """Factory function to create execution analyzer."""
    return ExecutionAnalyzer()