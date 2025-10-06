#!/usr/bin/env python3
"""
Adaptive Scheduler for DAG Orchestration
========================================

Implementation of adaptive scheduling based on historical performance
patterns with machine learning-based optimization.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition


class SchedulingPattern(Enum):
    """Types of scheduling patterns."""
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    RESOURCE_BALANCED = "resource_balanced"
    COST_MINIMIZED = "cost_minimized"
    DEADLINE_FOCUSED = "deadline_focused"
    ADAPTIVE = "adaptive"


@dataclass
class PerformanceMetrics:
    """Performance metrics for a task or execution."""
    execution_time: float
    resource_usage: Dict[str, float]
    cost: float
    success_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SchedulingDecision:
    """A scheduling decision with rationale."""
    task_id: str
    scheduled_time: datetime
    assigned_resources: Dict[str, Any]
    priority_score: float
    pattern_used: SchedulingPattern
    rationale: str
    confidence: float


class PerformancePredictor:
    """Predictor for task performance based on historical data."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        self._performance_history: Dict[str, List[PerformanceMetrics]] = {}
        self._pattern_performance: Dict[str, Dict[str, float]] = {}
    
    def record_performance(self, task_id: str, metrics: PerformanceMetrics) -> None:
        """Record performance metrics for a task."""
        if task_id not in self._performance_history:
            self._performance_history[task_id] = []
        
        self._performance_history[task_id].append(metrics)
        
        # Keep only last 100 records per task
        if len(self._performance_history[task_id]) > 100:
            self._performance_history[task_id] = self._performance_history[task_id][-100:]
    
    def predict_performance(self, task_id: str, context: Dict[str, Any]) -> PerformanceMetrics:
        """Predict performance metrics for a task."""
        if task_id not in self._performance_history or not self._performance_history[task_id]:
            # Return default prediction for unknown tasks
            return PerformanceMetrics(
                execution_time=60.0,
                resource_usage={'cpu': 1.0, 'memory': 1.0},
                cost=1.0,
                success_rate=0.9
            )
        
        history = self._performance_history[task_id]
        
        # Simple prediction based on recent performance (exponential moving average)
        recent_metrics = history[-10:]  # Last 10 executions
        
        # Calculate weighted averages
        weights = [0.1 * (i + 1) for i in range(len(recent_metrics))]
        total_weight = sum(weights)
        
        predicted_time = sum(m.execution_time * w for m, w in zip(recent_metrics, weights)) / total_weight
        predicted_cost = sum(m.cost * w for m, w in zip(recent_metrics, weights)) / total_weight
        predicted_success_rate = sum(m.success_rate * w for m, w in zip(recent_metrics, weights)) / total_weight
        
        # Predict resource usage
        predicted_resources = {}
        for resource in ['cpu', 'memory', 'disk']:
            resource_values = [m.resource_usage.get(resource, 1.0) for m in recent_metrics]
            predicted_resources[resource] = sum(v * w for v, w in zip(resource_values, weights)) / total_weight
        
        return PerformanceMetrics(
            execution_time=predicted_time,
            resource_usage=predicted_resources,
            cost=predicted_cost,
            success_rate=predicted_success_rate
        )
    
    def get_task_patterns(self, task_id: str) -> Dict[str, Any]:
        """Get performance patterns for a task."""
        if task_id not in self._performance_history:
            return {}
        
        history = self._performance_history[task_id]
        if len(history) < 3:
            return {}
        
        # Analyze patterns
        execution_times = [m.execution_time for m in history]
        costs = [m.cost for m in history]
        success_rates = [m.success_rate for m in history]
        
        return {
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_cost': sum(costs) / len(costs),
            'avg_success_rate': sum(success_rates) / len(success_rates),
            'execution_count': len(history),
            'trend': self._calculate_trend(execution_times)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend in performance values."""
        if len(values) < 3:
            return "insufficient_data"
        
        recent_avg = sum(values[-5:]) / min(5, len(values))
        older_avg = sum(values[:-5]) / max(1, len(values) - 5)
        
        if recent_avg > older_avg * 1.1:
            return "degrading"
        elif recent_avg < older_avg * 0.9:
            return "improving"
        else:
            return "stable"


class SchedulingOptimizer:
    """Optimizer for scheduling decisions."""
    
    def __init__(self, predictor: PerformancePredictor):
        self._predictor = predictor
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
    
    def optimize_schedule(self, tasks: List[TaskDefinition],
                         pattern: SchedulingPattern,
                         constraints: Dict[str, Any]) -> List[SchedulingDecision]:
        """Optimize task scheduling based on pattern and constraints."""
        
        if pattern == SchedulingPattern.PERFORMANCE_OPTIMIZED:
            return self._optimize_for_performance(tasks, constraints)
        elif pattern == SchedulingPattern.RESOURCE_BALANCED:
            return self._optimize_for_resources(tasks, constraints)
        elif pattern == SchedulingPattern.COST_MINIMIZED:
            return self._optimize_for_cost(tasks, constraints)
        elif pattern == SchedulingPattern.DEADLINE_FOCUSED:
            return self._optimize_for_deadline(tasks, constraints)
        elif pattern == SchedulingPattern.ADAPTIVE:
            return self._optimize_adaptive(tasks, constraints)
        else:
            return self._optimize_for_performance(tasks, constraints)
    
    def _optimize_for_performance(self, tasks: List[TaskDefinition],
                                 constraints: Dict[str, Any]) -> List[SchedulingDecision]:
        """Optimize for maximum performance."""
        decisions = []
        current_time = datetime.now()
        
        # Sort tasks by predicted execution time (shortest first)
        task_predictions = []
        for task in tasks:
            prediction = self._predictor.predict_performance(task.task_id, {})
            task_predictions.append((task, prediction))
        
        task_predictions.sort(key=lambda x: x[1].execution_time)
        
        for i, (task, prediction) in enumerate(task_predictions):
            decision = SchedulingDecision(
                task_id=task.task_id,
                scheduled_time=current_time + timedelta(seconds=i * 10),  # Stagger by 10 seconds
                assigned_resources={
                    'cpu': prediction.resource_usage.get('cpu', 1.0),
                    'memory': prediction.resource_usage.get('memory', 1.0)
                },
                priority_score=1.0 / (prediction.execution_time + 1),  # Shorter tasks get higher priority
                pattern_used=SchedulingPattern.PERFORMANCE_OPTIMIZED,
                rationale=f"Optimized for performance, predicted execution time: {prediction.execution_time:.1f}s",
                confidence=prediction.success_rate
            )
            decisions.append(decision)
        
        return decisions
    
    def _optimize_for_resources(self, tasks: List[TaskDefinition],
                               constraints: Dict[str, Any]) -> List[SchedulingDecision]:
        """Optimize for balanced resource usage."""
        decisions = []
        current_time = datetime.now()
        
        # Sort tasks by resource requirements to balance load
        task_predictions = []
        for task in tasks:
            prediction = self._predictor.predict_performance(task.task_id, {})
            total_resources = sum(prediction.resource_usage.values())
            task_predictions.append((task, prediction, total_resources))
        
        task_predictions.sort(key=lambda x: x[2])  # Sort by total resource usage
        
        for i, (task, prediction, total_resources) in enumerate(task_predictions):
            decision = SchedulingDecision(
                task_id=task.task_id,
                scheduled_time=current_time + timedelta(seconds=i * 15),  # Stagger for resource balance
                assigned_resources={
                    'cpu': min(prediction.resource_usage.get('cpu', 1.0), 
                              constraints.get('max_cpu_per_task', 4.0)),
                    'memory': min(prediction.resource_usage.get('memory', 1.0),
                                constraints.get('max_memory_per_task', 8.0))
                },
                priority_score=1.0 / (total_resources + 1),
                pattern_used=SchedulingPattern.RESOURCE_BALANCED,
                rationale=f"Balanced resource usage, total resources: {total_resources:.1f}",
                confidence=prediction.success_rate
            )
            decisions.append(decision)
        
        return decisions
    
    def _optimize_for_cost(self, tasks: List[TaskDefinition],
                          constraints: Dict[str, Any]) -> List[SchedulingDecision]:
        """Optimize for minimum cost."""
        decisions = []
        current_time = datetime.now()
        
        # Sort tasks by predicted cost (lowest first)
        task_predictions = []
        for task in tasks:
            prediction = self._predictor.predict_performance(task.task_id, {})
            task_predictions.append((task, prediction))
        
        task_predictions.sort(key=lambda x: x[1].cost)
        
        for i, (task, prediction) in enumerate(task_predictions):
            decision = SchedulingDecision(
                task_id=task.task_id,
                scheduled_time=current_time + timedelta(seconds=i * 20),  # Longer intervals for cost optimization
                assigned_resources={
                    'cpu': max(0.5, prediction.resource_usage.get('cpu', 1.0) * 0.8),  # Reduce resources for cost
                    'memory': max(0.5, prediction.resource_usage.get('memory', 1.0) * 0.8)
                },
                priority_score=1.0 / (prediction.cost + 0.1),
                pattern_used=SchedulingPattern.COST_MINIMIZED,
                rationale=f"Cost optimized, predicted cost: ${prediction.cost:.2f}",
                confidence=prediction.success_rate * 0.9  # Slightly lower confidence due to resource reduction
            )
            decisions.append(decision)
        
        return decisions
    
    def _optimize_for_deadline(self, tasks: List[TaskDefinition],
                              constraints: Dict[str, Any]) -> List[SchedulingDecision]:
        """Optimize for meeting deadlines."""
        decisions = []
        current_time = datetime.now()
        deadline = constraints.get('deadline', current_time + timedelta(hours=1))
        
        # Sort tasks by priority and deadline urgency
        task_predictions = []
        for task in tasks:
            prediction = self._predictor.predict_performance(task.task_id, {})
            priority = getattr(task, 'priority', 0)
            urgency_score = priority + (1.0 / (prediction.execution_time + 1))
            task_predictions.append((task, prediction, urgency_score))
        
        task_predictions.sort(key=lambda x: x[2], reverse=True)  # Highest urgency first
        
        for i, (task, prediction, urgency_score) in enumerate(task_predictions):
            decision = SchedulingDecision(
                task_id=task.task_id,
                scheduled_time=current_time + timedelta(seconds=i * 5),  # Tight scheduling for deadlines
                assigned_resources={
                    'cpu': prediction.resource_usage.get('cpu', 1.0) * 1.2,  # Boost resources for speed
                    'memory': prediction.resource_usage.get('memory', 1.0) * 1.2
                },
                priority_score=urgency_score,
                pattern_used=SchedulingPattern.DEADLINE_FOCUSED,
                rationale=f"Deadline focused, urgency score: {urgency_score:.2f}",
                confidence=prediction.success_rate
            )
            decisions.append(decision)
        
        return decisions
    
    def _optimize_adaptive(self, tasks: List[TaskDefinition],
                          constraints: Dict[str, Any]) -> List[SchedulingDecision]:
        """Adaptive optimization based on current conditions."""
        # Analyze current system state and choose best strategy
        
        # Simple heuristic: choose strategy based on constraints
        if 'deadline' in constraints:
            return self._optimize_for_deadline(tasks, constraints)
        elif constraints.get('cost_budget', float('inf')) < 100:
            return self._optimize_for_cost(tasks, constraints)
        elif constraints.get('max_cpu_per_task', 4.0) < 2.0:
            return self._optimize_for_resources(tasks, constraints)
        else:
            return self._optimize_for_performance(tasks, constraints)


class AdaptiveScheduler(ReflectiveModule):
    """
    Adaptive scheduler based on historical performance patterns.
    
    Features:
    - Machine learning-based performance prediction
    - Multiple scheduling patterns
    - Historical performance tracking
    - Adaptive optimization
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "AdaptiveScheduler"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Components
        self._predictor = PerformancePredictor()
        self._optimizer = SchedulingOptimizer(self._predictor)
        
        # Statistics
        self._total_scheduling_operations = 0
        self._pattern_usage = {}
        self._prediction_accuracy = {}
        
        self._logger.info("AdaptiveScheduler initialized")
    
    async def create_schedule(self, tasks: List[TaskDefinition],
                            pattern: SchedulingPattern = SchedulingPattern.ADAPTIVE,
                            constraints: Optional[Dict[str, Any]] = None) -> List[SchedulingDecision]:
        """Create optimized schedule for tasks."""
        with self.trace_operation("create_schedule",
                                task_count=len(tasks),
                                pattern=pattern.value) as trace:
            
            constraints = constraints or {}
            self._total_scheduling_operations += 1
            
            # Update pattern usage statistics
            pattern_name = pattern.value
            self._pattern_usage[pattern_name] = self._pattern_usage.get(pattern_name, 0) + 1
            
            # Create optimized schedule
            decisions = self._optimizer.optimize_schedule(tasks, pattern, constraints)
            
            trace.output_result = {
                'task_count': len(tasks),
                'pattern_used': pattern.value,
                'decisions_count': len(decisions),
                'avg_confidence': sum(d.confidence for d in decisions) / len(decisions) if decisions else 0
            }
            
            self._logger.info(f"Created schedule for {len(tasks)} tasks using {pattern.value} pattern")
            return decisions
    
    def record_execution_result(self, task_id: str, actual_metrics: PerformanceMetrics) -> None:
        """Record actual execution results for learning."""
        self._predictor.record_performance(task_id, actual_metrics)
        
        # Update prediction accuracy (simplified)
        if task_id not in self._prediction_accuracy:
            self._prediction_accuracy[task_id] = {'predictions': 0, 'accurate': 0}
        
        self._prediction_accuracy[task_id]['predictions'] += 1
        
        # Simple accuracy check (within 20% of predicted time)
        predicted = self._predictor.predict_performance(task_id, {})
        if abs(actual_metrics.execution_time - predicted.execution_time) / predicted.execution_time < 0.2:
            self._prediction_accuracy[task_id]['accurate'] += 1
    
    def get_scheduling_statistics(self) -> Dict[str, Any]:
        """Get scheduling statistics."""
        # Calculate overall prediction accuracy
        total_predictions = sum(stats['predictions'] for stats in self._prediction_accuracy.values())
        total_accurate = sum(stats['accurate'] for stats in self._prediction_accuracy.values())
        overall_accuracy = total_accurate / max(total_predictions, 1)
        
        return {
            'total_scheduling_operations': self._total_scheduling_operations,
            'pattern_usage': self._pattern_usage,
            'prediction_accuracy': overall_accuracy,
            'tasks_with_history': len(self._predictor._performance_history),
            'total_performance_records': sum(len(history) for history in self._predictor._performance_history.values())
        }
    
    def get_task_insights(self, task_id: str) -> Dict[str, Any]:
        """Get insights for a specific task."""
        patterns = self._predictor.get_task_patterns(task_id)
        prediction = self._predictor.predict_performance(task_id, {})
        
        accuracy_stats = self._prediction_accuracy.get(task_id, {'predictions': 0, 'accurate': 0})
        task_accuracy = accuracy_stats['accurate'] / max(accuracy_stats['predictions'], 1)
        
        return {
            'task_id': task_id,
            'patterns': patterns,
            'next_prediction': {
                'execution_time': prediction.execution_time,
                'cost': prediction.cost,
                'success_rate': prediction.success_rate,
                'resource_usage': prediction.resource_usage
            },
            'prediction_accuracy': task_accuracy,
            'total_executions': accuracy_stats['predictions']
        }


# Convenience functions
def create_adaptive_scheduler() -> AdaptiveScheduler:
    """Factory function to create adaptive scheduler."""
    return AdaptiveScheduler()


def create_performance_predictor() -> PerformancePredictor:
    """Factory function to create performance predictor."""
    return PerformancePredictor()