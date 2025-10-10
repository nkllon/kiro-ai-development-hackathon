#!/usr/bin/env python3
"""
ML-Based Intelligent Task Scheduler
===================================

Machine learning-based task execution time prediction and intelligent
scheduling for DAG orchestrated parallel execution.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    """Task scheduling strategies."""
    FIFO = "fifo"
    PRIORITY = "priority"
    CRITICAL_PATH = "critical_path"
    RESOURCE_AWARE = "resource_aware"
    ML_OPTIMIZED = "ml_optimized"
    ADAPTIVE = "adaptive"


@dataclass
class TaskMetrics:
    """Historical task execution metrics."""
    task_type: str
    avg_execution_time: float
    std_execution_time: float
    success_rate: float
    resource_utilization: Dict[str, float]
    complexity_score: float
    dependency_count: int
    execution_count: int = 0


@dataclass
class SchedulingDecision:
    """Task scheduling decision with rationale."""
    task_id: str
    priority_score: float
    estimated_duration: float
    resource_allocation: Dict[str, Any]
    scheduling_rationale: str
    confidence_score: float


@dataclass
class SystemState:
    """Current system state for scheduling decisions."""
    available_cpu_cores: int
    available_memory_mb: int
    current_load: float
    active_tasks: int
    queue_length: int
    timestamp: datetime = field(default_factory=datetime.now)


class MLTaskScheduler(ReflectiveModule):
    """
    Machine learning-based intelligent task scheduler.
    
    Provides ML-based task execution time prediction, dynamic priority
    adjustment, and adaptive scheduling strategies for optimal resource
    utilization and execution efficiency.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "MLTaskScheduler"
        self.config = config or self._get_default_config()
        self.task_metrics: Dict[str, TaskMetrics] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.current_strategy = SchedulingStrategy.ADAPTIVE
        
        # ML model placeholders (would use actual ML libraries in production)
        self.duration_predictor = self._initialize_duration_predictor()
        self.priority_optimizer = self._initialize_priority_optimizer()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default scheduler configuration."""
        return {
            'max_concurrent_tasks': 6,
            'cpu_threshold': 0.8,
            'memory_threshold': 0.85,
            'priority_decay_factor': 0.95,
            'learning_rate': 0.01,
            'prediction_confidence_threshold': 0.7,
            'adaptive_strategy_enabled': True,
            'resource_optimization_enabled': True
        }
    
    def _initialize_duration_predictor(self) -> Dict[str, Any]:
        """Initialize ML model for duration prediction."""
        # Placeholder for actual ML model (e.g., scikit-learn, TensorFlow)
        return {
            'model_type': 'linear_regression',
            'features': ['task_type', 'complexity_score', 'dependency_count', 'resource_requirements'],
            'trained': False,
            'accuracy': 0.0
        }
    
    def _initialize_priority_optimizer(self) -> Dict[str, Any]:
        """Initialize ML model for priority optimization."""
        return {
            'model_type': 'gradient_boosting',
            'features': ['execution_time', 'resource_utilization', 'dependency_impact', 'deadline_pressure'],
            'trained': False,
            'accuracy': 0.0
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "MLTaskScheduler",
            "version": "1.0.0",
            "description": "Machine learning-based intelligent task scheduler",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "config": self.config,
            "current_strategy": self.current_strategy.value,
            "task_metrics_count": len(self.task_metrics),
            "execution_history_count": len(self.execution_history)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check if we have sufficient historical data
            if len(self.task_metrics) == 0:
                issues.append("No historical task metrics available")
                health_score *= 0.8
            
            # Check prediction model status
            if not self.duration_predictor.get('trained', False):
                issues.append("Duration prediction model not trained")
                health_score *= 0.9
            
            if not self.priority_optimizer.get('trained', False):
                issues.append("Priority optimization model not trained")
                health_score *= 0.9
            
            # Check execution history size
            if len(self.execution_history) > 1000:
                issues.append("Large execution history may impact performance")
                health_score *= 0.95
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still provide basic scheduling
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING,  # May lose ML predictions
                ModuleCapability.MONITORING       # May lose detailed monitoring
            ]
            
            # Switch to simpler scheduling strategy
            self.current_strategy = SchedulingStrategy.FIFO
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def predict_execution_time(self, task_definition: Dict[str, Any]) -> Tuple[float, float]:
        """
        Predict task execution time using ML model.
        
        Args:
            task_definition: Task definition with metadata
            
        Returns:
            Tuple of (predicted_duration_minutes, confidence_score)
        """
        try:
            with self.trace_operation("predict_execution_time"):
                task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
                
                # Get historical metrics for this task type
                metrics = self.task_metrics.get(task_type)
                if not metrics:
                    # Use default estimation for unknown task types
                    base_duration = task_definition.get('resource_requirements', {}).get('estimated_duration_minutes', 30)
                    return base_duration, 0.5
                
                # Feature extraction for ML prediction
                features = self._extract_prediction_features(task_definition, metrics)
                
                # ML prediction (simplified - would use actual ML model)
                predicted_duration = self._ml_predict_duration(features, metrics)
                confidence = self._calculate_prediction_confidence(features, metrics)
                
                return predicted_duration, confidence
                
        except Exception as e:
            logger.error(f"Error predicting execution time: {e}")
            # Fallback to basic estimation
            return task_definition.get('resource_requirements', {}).get('estimated_duration_minutes', 30), 0.3
    
    def _extract_prediction_features(self, task_definition: Dict[str, Any], metrics: TaskMetrics) -> Dict[str, float]:
        """Extract features for ML prediction."""
        return {
            'complexity_score': self._calculate_complexity_score(task_definition),
            'dependency_count': len(task_definition.get('dependencies', [])),
            'resource_cpu': task_definition.get('resource_requirements', {}).get('cpu_cores', 1),
            'resource_memory': task_definition.get('resource_requirements', {}).get('memory_mb', 512),
            'historical_avg': metrics.avg_execution_time,
            'historical_std': metrics.std_execution_time,
            'success_rate': metrics.success_rate
        }
    
    def _calculate_complexity_score(self, task_definition: Dict[str, Any]) -> float:
        """Calculate task complexity score based on various factors."""
        score = 1.0
        
        # Factor in resource requirements
        cpu_cores = task_definition.get('resource_requirements', {}).get('cpu_cores', 1)
        memory_mb = task_definition.get('resource_requirements', {}).get('memory_mb', 512)
        
        score += (cpu_cores - 1) * 0.5
        score += (memory_mb - 512) / 1024 * 0.3
        
        # Factor in dependencies
        dep_count = len(task_definition.get('dependencies', []))
        score += dep_count * 0.2
        
        # Factor in task type
        task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
        type_multipliers = {
            'implementation': 1.5,
            'testing': 0.8,
            'deployment': 1.2,
            'monitoring': 0.9,
            'general': 1.0
        }
        score *= type_multipliers.get(task_type, 1.0)
        
        return min(score, 5.0)  # Cap at 5.0
    
    def _ml_predict_duration(self, features: Dict[str, float], metrics: TaskMetrics) -> float:
        """ML-based duration prediction (simplified implementation)."""
        # Simplified ML prediction - would use actual trained model
        base_duration = metrics.avg_execution_time
        
        # Adjust based on complexity
        complexity_factor = features['complexity_score'] / 2.0
        duration = base_duration * complexity_factor
        
        # Adjust based on resource requirements
        resource_factor = (features['resource_cpu'] + features['resource_memory'] / 1024) / 2
        duration *= resource_factor
        
        # Add some variance based on historical standard deviation
        variance = metrics.std_execution_time * 0.1
        duration += variance
        
        return max(duration, 5.0)  # Minimum 5 minutes
    
    def _calculate_prediction_confidence(self, features: Dict[str, float], metrics: TaskMetrics) -> float:
        """Calculate confidence score for prediction."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence with more execution history
        if metrics.execution_count > 10:
            confidence += 0.3
        elif metrics.execution_count > 5:
            confidence += 0.2
        elif metrics.execution_count > 1:
            confidence += 0.1
        
        # Higher confidence with lower variance
        if metrics.std_execution_time < metrics.avg_execution_time * 0.2:
            confidence += 0.2
        
        # Higher confidence with good success rate
        if metrics.success_rate > 0.9:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def calculate_dynamic_priority(self, task_definition: Dict[str, Any], system_state: SystemState) -> float:
        """
        Calculate dynamic task priority based on current system state.
        
        Args:
            task_definition: Task definition
            system_state: Current system state
            
        Returns:
            Priority score (higher = more priority)
        """
        try:
            with self.trace_operation("calculate_dynamic_priority"):
                base_priority = self._get_base_priority(task_definition)
                
                # Adjust for system load
                load_factor = self._calculate_load_factor(system_state)
                
                # Adjust for resource availability
                resource_factor = self._calculate_resource_factor(task_definition, system_state)
                
                # Adjust for deadline pressure
                deadline_factor = self._calculate_deadline_factor(task_definition)
                
                # Adjust for dependency impact
                dependency_factor = self._calculate_dependency_factor(task_definition)
                
                # Combine factors
                priority_score = base_priority * load_factor * resource_factor * deadline_factor * dependency_factor
                
                return max(0.1, min(priority_score, 10.0))  # Clamp between 0.1 and 10.0
                
        except Exception as e:
            logger.error(f"Error calculating dynamic priority: {e}")
            return 1.0  # Default priority
    
    def _get_base_priority(self, task_definition: Dict[str, Any]) -> float:
        """Get base priority from task definition."""
        priority_map = {
            'high': 3.0,
            'medium': 2.0,
            'low': 1.0
        }
        
        priority_str = task_definition.get('execution_context', {}).get('priority', 'medium')
        return priority_map.get(priority_str, 2.0)
    
    def _calculate_load_factor(self, system_state: SystemState) -> float:
        """Calculate load-based priority adjustment factor."""
        if system_state.current_load > 0.8:
            return 0.7  # Lower priority when system is heavily loaded
        elif system_state.current_load < 0.3:
            return 1.3  # Higher priority when system has capacity
        else:
            return 1.0
    
    def _calculate_resource_factor(self, task_definition: Dict[str, Any], system_state: SystemState) -> float:
        """Calculate resource availability factor."""
        required_cpu = task_definition.get('resource_requirements', {}).get('cpu_cores', 1)
        required_memory = task_definition.get('resource_requirements', {}).get('memory_mb', 512)
        
        cpu_ratio = required_cpu / max(system_state.available_cpu_cores, 1)
        memory_ratio = required_memory / max(system_state.available_memory_mb, 1)
        
        # Prioritize tasks that fit well with available resources
        if cpu_ratio <= 0.5 and memory_ratio <= 0.5:
            return 1.2  # Good fit
        elif cpu_ratio <= 1.0 and memory_ratio <= 1.0:
            return 1.0  # Acceptable fit
        else:
            return 0.8  # Poor fit
    
    def _calculate_deadline_factor(self, task_definition: Dict[str, Any]) -> float:
        """Calculate deadline pressure factor."""
        # Simplified - would use actual deadline information
        task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
        
        # Critical tasks get higher priority
        if task_type in ['deployment', 'critical']:
            return 1.5
        elif task_type in ['testing', 'validation']:
            return 1.2
        else:
            return 1.0
    
    def _calculate_dependency_factor(self, task_definition: Dict[str, Any]) -> float:
        """Calculate dependency impact factor."""
        dep_count = len(task_definition.get('dependencies', []))
        
        # Tasks with fewer dependencies can start sooner
        if dep_count == 0:
            return 1.3  # No dependencies - can start immediately
        elif dep_count <= 2:
            return 1.1  # Few dependencies
        else:
            return 0.9  # Many dependencies
    
    def optimize_task_batching(self, tasks: List[Dict[str, Any]], system_state: SystemState) -> List[List[str]]:
        """
        Optimize task batching for improved resource utilization.
        
        Args:
            tasks: List of task definitions
            system_state: Current system state
            
        Returns:
            List of task batches (each batch contains task IDs)
        """
        try:
            with self.trace_operation("optimize_task_batching"):
                # Calculate resource requirements for each task
                task_resources = {}
                for task in tasks:
                    task_id = task['id']
                    task_resources[task_id] = {
                        'cpu': task.get('resource_requirements', {}).get('cpu_cores', 1),
                        'memory': task.get('resource_requirements', {}).get('memory_mb', 512)
                    }
                
                # Create batches using bin packing algorithm
                batches = self._create_resource_optimized_batches(task_resources, system_state)
                
                return batches
                
        except Exception as e:
            logger.error(f"Error optimizing task batching: {e}")
            # Fallback to simple batching
            return [[task['id']] for task in tasks]
    
    def _create_resource_optimized_batches(self, task_resources: Dict[str, Dict[str, int]], 
                                         system_state: SystemState) -> List[List[str]]:
        """Create resource-optimized task batches using bin packing."""
        batches = []
        remaining_tasks = list(task_resources.keys())
        
        while remaining_tasks:
            current_batch = []
            batch_cpu = 0
            batch_memory = 0
            
            # Try to fit tasks into current batch
            tasks_to_remove = []
            for task_id in remaining_tasks:
                task_cpu = task_resources[task_id]['cpu']
                task_memory = task_resources[task_id]['memory']
                
                # Check if task fits in current batch
                if (batch_cpu + task_cpu <= system_state.available_cpu_cores and
                    batch_memory + task_memory <= system_state.available_memory_mb):
                    
                    current_batch.append(task_id)
                    batch_cpu += task_cpu
                    batch_memory += task_memory
                    tasks_to_remove.append(task_id)
            
            # Remove tasks that were added to batch
            for task_id in tasks_to_remove:
                remaining_tasks.remove(task_id)
            
            if current_batch:
                batches.append(current_batch)
            else:
                # If no tasks fit, add the first remaining task alone
                if remaining_tasks:
                    batches.append([remaining_tasks.pop(0)])
        
        return batches
    
    def update_task_metrics(self, task_id: str, execution_result: Dict[str, Any]) -> None:
        """Update task metrics based on execution results."""
        try:
            task_type = execution_result.get('task_type', 'general')
            execution_time = execution_result.get('execution_time', 0)
            success = execution_result.get('success', False)
            resource_usage = execution_result.get('resource_usage', {})
            
            if task_type not in self.task_metrics:
                self.task_metrics[task_type] = TaskMetrics(
                    task_type=task_type,
                    avg_execution_time=execution_time,
                    std_execution_time=0.0,
                    success_rate=1.0 if success else 0.0,
                    resource_utilization=resource_usage,
                    complexity_score=1.0,
                    dependency_count=0,
                    execution_count=1
                )
            else:
                metrics = self.task_metrics[task_type]
                
                # Update running averages
                count = metrics.execution_count
                metrics.avg_execution_time = (metrics.avg_execution_time * count + execution_time) / (count + 1)
                
                # Update success rate
                metrics.success_rate = (metrics.success_rate * count + (1.0 if success else 0.0)) / (count + 1)
                
                # Update execution count
                metrics.execution_count += 1
                
                # Update standard deviation (simplified)
                if count > 1:
                    variance = ((execution_time - metrics.avg_execution_time) ** 2) / count
                    metrics.std_execution_time = np.sqrt(variance)
            
            # Store execution history
            self.execution_history.append({
                'timestamp': datetime.now().isoformat(),
                'task_id': task_id,
                'task_type': task_type,
                'execution_time': execution_time,
                'success': success,
                'resource_usage': resource_usage
            })
            
            # Limit history size
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
                
        except Exception as e:
            logger.error(f"Error updating task metrics: {e}")
    
    def get_scheduling_recommendations(self, tasks: List[Dict[str, Any]], 
                                    system_state: SystemState) -> List[SchedulingDecision]:
        """Get scheduling recommendations for a list of tasks."""
        recommendations = []
        
        for task in tasks:
            try:
                # Predict execution time
                duration, duration_confidence = self.predict_execution_time(task)
                
                # Calculate priority
                priority = self.calculate_dynamic_priority(task, system_state)
                
                # Determine resource allocation
                resource_allocation = self._optimize_resource_allocation(task, system_state)
                
                # Generate rationale
                rationale = self._generate_scheduling_rationale(task, priority, duration, system_state)
                
                # Calculate overall confidence
                confidence = (duration_confidence + 0.8) / 2  # Combine with scheduling confidence
                
                recommendation = SchedulingDecision(
                    task_id=task['id'],
                    priority_score=priority,
                    estimated_duration=duration,
                    resource_allocation=resource_allocation,
                    scheduling_rationale=rationale,
                    confidence_score=confidence
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error generating recommendation for task {task.get('id', 'unknown')}: {e}")
        
        # Sort by priority score (descending)
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        return recommendations
    
    def _optimize_resource_allocation(self, task: Dict[str, Any], system_state: SystemState) -> Dict[str, Any]:
        """Optimize resource allocation for a task."""
        base_cpu = task.get('resource_requirements', {}).get('cpu_cores', 1)
        base_memory = task.get('resource_requirements', {}).get('memory_mb', 512)
        
        # Adjust based on system availability
        available_ratio = min(
            system_state.available_cpu_cores / max(base_cpu, 1),
            system_state.available_memory_mb / max(base_memory, 1)
        )
        
        if available_ratio > 2.0:
            # System has plenty of resources, can allocate more
            return {
                'cpu_cores': min(base_cpu * 1.5, system_state.available_cpu_cores),
                'memory_mb': min(base_memory * 1.2, system_state.available_memory_mb),
                'allocation_strategy': 'generous'
            }
        elif available_ratio < 1.0:
            # System is constrained, allocate conservatively
            return {
                'cpu_cores': max(1, base_cpu * 0.8),
                'memory_mb': max(256, base_memory * 0.8),
                'allocation_strategy': 'conservative'
            }
        else:
            # Normal allocation
            return {
                'cpu_cores': base_cpu,
                'memory_mb': base_memory,
                'allocation_strategy': 'standard'
            }
    
    def _generate_scheduling_rationale(self, task: Dict[str, Any], priority: float, 
                                     duration: float, system_state: SystemState) -> str:
        """Generate human-readable scheduling rationale."""
        rationale_parts = []
        
        # Priority rationale
        if priority > 2.5:
            rationale_parts.append("High priority due to task importance and system state")
        elif priority < 1.5:
            rationale_parts.append("Lower priority due to resource constraints or dependencies")
        else:
            rationale_parts.append("Standard priority based on task characteristics")
        
        # Duration rationale
        if duration > 60:
            rationale_parts.append("Long execution time estimated")
        elif duration < 15:
            rationale_parts.append("Quick execution expected")
        
        # System state rationale
        if system_state.current_load > 0.8:
            rationale_parts.append("System under high load")
        elif system_state.current_load < 0.3:
            rationale_parts.append("System has available capacity")
        
        return "; ".join(rationale_parts)


def create_ml_scheduler(config: Optional[Dict[str, Any]] = None) -> MLTaskScheduler:
    """Factory function to create MLTaskScheduler instance."""
    return MLTaskScheduler(config)


if __name__ == "__main__":
    # Example usage
    scheduler = create_ml_scheduler()
    
    # Example task
    task = {
        'id': 'test_task_1',
        'name': 'Test ML Scheduling',
        'dependencies': [],
        'resource_requirements': {
            'cpu_cores': 2,
            'memory_mb': 1024,
            'estimated_duration_minutes': 30
        },
        'execution_context': {
            'task_type': 'implementation',
            'priority': 'high'
        }
    }
    
    # Example system state
    system_state = SystemState(
        available_cpu_cores=8,
        available_memory_mb=16384,
        current_load=0.4,
        active_tasks=2,
        queue_length=5
    )
    
    # Get recommendations
    recommendations = scheduler.get_scheduling_recommendations([task], system_state)
    
    for rec in recommendations:
        print(f"Task: {rec.task_id}")
        print(f"Priority: {rec.priority_score:.2f}")
        print(f"Estimated Duration: {rec.estimated_duration:.1f} minutes")
        print(f"Rationale: {rec.scheduling_rationale}")
        print(f"Confidence: {rec.confidence_score:.2f}")
        print("---")