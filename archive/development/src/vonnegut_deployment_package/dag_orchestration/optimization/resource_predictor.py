#!/usr/bin/env python3
"""
Resource Predictor for DAG Orchestration System
===============================================

Intelligent resource planning and prediction for DAG orchestrated parallel execution.
Provides resource requirement forecasting, capacity planning, and optimization recommendations.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import os
import psutil
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


class ResourceType(Enum):
    """Types of system resources."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    IO = "io"


class PredictionHorizon(Enum):
    """Time horizons for resource predictions."""
    SHORT_TERM = "short_term"  # Next 1-5 minutes
    MEDIUM_TERM = "medium_term"  # Next 15-30 minutes
    LONG_TERM = "long_term"  # Next 1-2 hours


@dataclass
class ResourceMetrics:
    """Current resource utilization metrics."""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io_mbps: float
    disk_io_mbps: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceRequirement:
    """Resource requirement specification for a task."""
    cpu_cores: float
    memory_mb: int
    disk_mb: int
    network_mbps: float
    io_mbps: float
    duration_minutes: float
    confidence: float = 0.8


@dataclass
class ResourcePrediction:
    """Resource utilization prediction."""
    resource_type: ResourceType
    horizon: PredictionHorizon
    predicted_utilization: float
    confidence_interval: Tuple[float, float]
    peak_utilization: float
    bottleneck_probability: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CapacityPlan:
    """Resource capacity planning recommendation."""
    current_capacity: Dict[str, float]
    predicted_demand: Dict[str, float]
    capacity_gap: Dict[str, float]
    scaling_recommendations: List[str]
    optimization_opportunities: List[str]
    confidence_score: float


class ResourcePredictor(ReflectiveModule):
    """
    Intelligent resource planning and prediction system.
    
    Provides:
    - Resource requirement forecasting based on task analysis
    - System capacity planning and bottleneck prediction
    - Resource optimization recommendations
    - Historical trend analysis and learning
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "ResourcePredictor"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or self._get_default_config()
        
        # Historical data storage
        self.resource_history: List[ResourceMetrics] = []
        self.task_resource_patterns: Dict[str, List[ResourceRequirement]] = {}
        self.prediction_accuracy_history: List[Dict[str, Any]] = []
        
        # Prediction models (simplified - would use actual ML in production)
        self.cpu_predictor = self._initialize_cpu_predictor()
        self.memory_predictor = self._initialize_memory_predictor()
        self.io_predictor = self._initialize_io_predictor()
        
        # System baseline
        self.system_baseline = self._establish_system_baseline()
        
        self._logger.info("ResourcePredictor initialized with intelligent forecasting capabilities")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'history_retention_hours': 24,
            'prediction_update_interval_minutes': 5,
            'cpu_bottleneck_threshold': 0.85,
            'memory_bottleneck_threshold': 0.90,
            'disk_bottleneck_threshold': 0.95,
            'confidence_threshold': 0.7,
            'learning_rate': 0.1,
            'trend_analysis_window_minutes': 60,
            'capacity_planning_horizon_hours': 4
        }
    
    def _initialize_cpu_predictor(self) -> Dict[str, Any]:
        """Initialize CPU utilization predictor."""
        return {
            'model_type': 'exponential_smoothing',
            'alpha': 0.3,  # Smoothing parameter
            'beta': 0.1,   # Trend parameter
            'gamma': 0.05, # Seasonal parameter
            'last_prediction': 0.0,
            'trend': 0.0,
            'seasonal_factors': [1.0] * 24  # Hourly seasonal factors
        }
    
    def _initialize_memory_predictor(self) -> Dict[str, Any]:
        """Initialize memory utilization predictor."""
        return {
            'model_type': 'linear_trend',
            'slope': 0.0,
            'intercept': 0.0,
            'r_squared': 0.0,
            'last_values': [],
            'max_history': 100
        }
    
    def _initialize_io_predictor(self) -> Dict[str, Any]:
        """Initialize I/O utilization predictor."""
        return {
            'model_type': 'moving_average',
            'window_size': 10,
            'weights': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            'history': [],
            'variance': 0.0
        }
    
    def _establish_system_baseline(self) -> Dict[str, float]:
        """Establish system baseline metrics."""
        try:
            # Collect baseline measurements
            baseline_samples = []
            for _ in range(5):
                metrics = self._collect_current_metrics()
                baseline_samples.append(metrics)
                import time
                time.sleep(1)
            
            # Calculate baseline averages
            baseline = {
                'cpu_percent': np.mean([m.cpu_percent for m in baseline_samples]),
                'memory_percent': np.mean([m.memory_percent for m in baseline_samples]),
                'disk_percent': np.mean([m.disk_percent for m in baseline_samples]),
                'network_io_mbps': np.mean([m.network_io_mbps for m in baseline_samples]),
                'disk_io_mbps': np.mean([m.disk_io_mbps for m in baseline_samples])
            }
            
            self._logger.info(f"System baseline established: {baseline}")
            return baseline
            
        except Exception as e:
            self._logger.error(f"Failed to establish system baseline: {e}")
            return {
                'cpu_percent': 10.0,
                'memory_percent': 30.0,
                'disk_percent': 50.0,
                'network_io_mbps': 1.0,
                'disk_io_mbps': 5.0
            }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "ResourcePredictor",
            "version": "1.0.0",
            "description": "Intelligent resource planning and prediction system",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "config": self.config,
            "history_size": len(self.resource_history),
            "task_patterns": len(self.task_resource_patterns),
            "system_baseline": self.system_baseline
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Check prediction accuracy
            recent_accuracy = self._calculate_recent_prediction_accuracy()
            
            # Check data freshness
            data_freshness = self._check_data_freshness()
            
            issues = []
            health_score = 1.0
            
            # Assess prediction accuracy
            if recent_accuracy < 0.6:
                issues.append(f"Low prediction accuracy: {recent_accuracy:.2f}")
                health_score *= 0.7
            
            # Assess data freshness
            if not data_freshness:
                issues.append("Stale resource data")
                health_score *= 0.8
            
            # Check system resource availability for predictions
            try:
                current_metrics = self._collect_current_metrics()
                if current_metrics.cpu_percent > 95:
                    issues.append("System CPU critically high")
                    health_score *= 0.6
            except Exception:
                issues.append("Cannot collect system metrics")
                health_score *= 0.5
            
            # Determine status
            if health_score >= 0.8:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.5:
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
            # In degraded mode, we can still provide basic predictions
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
            
            degraded_capabilities = [
                ModuleCapability.DATA_PROCESSING  # May lose complex analysis
            ]
            
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
    
    def predict_task_resource_requirements(self, task_definition: Dict[str, Any]) -> ResourceRequirement:
        """
        Predict resource requirements for a specific task.
        
        Args:
            task_definition: Task definition with metadata
            
        Returns:
            ResourceRequirement prediction
        """
        with self.trace_operation("predict_task_resource_requirements") as trace:
            try:
                task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
                
                # Get historical patterns for this task type
                historical_patterns = self.task_resource_patterns.get(task_type, [])
                
                if historical_patterns:
                    # Use historical data for prediction
                    prediction = self._predict_from_historical_patterns(task_definition, historical_patterns)
                else:
                    # Use heuristic-based prediction for new task types
                    prediction = self._predict_from_heuristics(task_definition)
                
                trace.output_result = {
                    'task_type': task_type,
                    'cpu_cores': prediction.cpu_cores,
                    'memory_mb': prediction.memory_mb,
                    'duration_minutes': prediction.duration_minutes,
                    'confidence': prediction.confidence
                }
                
                return prediction
                
            except Exception as e:
                self._logger.error(f"Error predicting task resource requirements: {e}")
                trace.output_result = {'error': str(e)}
                
                # Return conservative default
                return ResourceRequirement(
                    cpu_cores=1.0,
                    memory_mb=512,
                    disk_mb=100,
                    network_mbps=1.0,
                    io_mbps=5.0,
                    duration_minutes=30.0,
                    confidence=0.3
                )
    
    def _predict_from_historical_patterns(self, task_definition: Dict[str, Any], 
                                        patterns: List[ResourceRequirement]) -> ResourceRequirement:
        """Predict resource requirements from historical patterns."""
        # Calculate weighted averages based on recency and similarity
        weights = []
        total_weight = 0
        
        for i, pattern in enumerate(patterns):
            # More recent patterns get higher weight
            recency_weight = 1.0 / (i + 1)
            
            # Similar complexity gets higher weight
            complexity_similarity = self._calculate_complexity_similarity(task_definition, pattern)
            
            weight = recency_weight * complexity_similarity
            weights.append(weight)
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(patterns)] * len(patterns)
        
        # Calculate weighted predictions
        cpu_cores = sum(p.cpu_cores * w for p, w in zip(patterns, weights))
        memory_mb = sum(p.memory_mb * w for p, w in zip(patterns, weights))
        disk_mb = sum(p.disk_mb * w for p, w in zip(patterns, weights))
        network_mbps = sum(p.network_mbps * w for p, w in zip(patterns, weights))
        io_mbps = sum(p.io_mbps * w for p, w in zip(patterns, weights))
        duration_minutes = sum(p.duration_minutes * w for p, w in zip(patterns, weights))
        
        # Calculate confidence based on pattern consistency
        confidence = self._calculate_pattern_confidence(patterns)
        
        return ResourceRequirement(
            cpu_cores=cpu_cores,
            memory_mb=int(memory_mb),
            disk_mb=int(disk_mb),
            network_mbps=network_mbps,
            io_mbps=io_mbps,
            duration_minutes=duration_minutes,
            confidence=confidence
        )
    
    def _predict_from_heuristics(self, task_definition: Dict[str, Any]) -> ResourceRequirement:
        """Predict resource requirements using heuristics for new task types."""
        task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
        complexity_score = self._calculate_task_complexity(task_definition)
        
        # Base resource requirements by task type
        base_requirements = {
            'implementation': {'cpu': 2.0, 'memory': 1024, 'duration': 45},
            'testing': {'cpu': 1.5, 'memory': 768, 'duration': 20},
            'deployment': {'cpu': 1.0, 'memory': 512, 'duration': 15},
            'monitoring': {'cpu': 0.5, 'memory': 256, 'duration': 10},
            'analysis': {'cpu': 2.5, 'memory': 2048, 'duration': 60},
            'general': {'cpu': 1.0, 'memory': 512, 'duration': 30}
        }
        
        base = base_requirements.get(task_type, base_requirements['general'])
        
        # Adjust based on complexity
        complexity_multiplier = 0.5 + (complexity_score / 5.0)  # 0.5 to 1.5 range
        
        return ResourceRequirement(
            cpu_cores=base['cpu'] * complexity_multiplier,
            memory_mb=int(base['memory'] * complexity_multiplier),
            disk_mb=100,  # Base disk requirement
            network_mbps=1.0,  # Base network requirement
            io_mbps=5.0,  # Base I/O requirement
            duration_minutes=base['duration'] * complexity_multiplier,
            confidence=0.6  # Lower confidence for heuristic predictions
        )
    
    def _calculate_complexity_similarity(self, task_definition: Dict[str, Any], 
                                       pattern: ResourceRequirement) -> float:
        """Calculate similarity between task and historical pattern."""
        # Simplified similarity calculation
        task_complexity = self._calculate_task_complexity(task_definition)
        pattern_complexity = pattern.duration_minutes / 30.0  # Normalize to complexity score
        
        # Similarity decreases with complexity difference
        complexity_diff = abs(task_complexity - pattern_complexity)
        similarity = max(0.1, 1.0 - (complexity_diff / 5.0))
        
        return similarity
    
    def _calculate_task_complexity(self, task_definition: Dict[str, Any]) -> float:
        """Calculate task complexity score."""
        complexity = 1.0
        
        # Factor in dependencies
        dep_count = len(task_definition.get('dependencies', []))
        complexity += dep_count * 0.3
        
        # Factor in resource requirements if specified
        resource_reqs = task_definition.get('resource_requirements', {})
        if 'cpu_cores' in resource_reqs:
            complexity += (resource_reqs['cpu_cores'] - 1) * 0.5
        if 'memory_mb' in resource_reqs:
            complexity += (resource_reqs['memory_mb'] - 512) / 1024 * 0.4
        
        # Factor in task type
        task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
        type_multipliers = {
            'implementation': 1.5,
            'analysis': 1.8,
            'testing': 0.8,
            'deployment': 1.2,
            'monitoring': 0.6,
            'general': 1.0
        }
        complexity *= type_multipliers.get(task_type, 1.0)
        
        return min(complexity, 5.0)  # Cap at 5.0
    
    def _calculate_pattern_confidence(self, patterns: List[ResourceRequirement]) -> float:
        """Calculate confidence based on pattern consistency."""
        if len(patterns) < 2:
            return 0.5
        
        # Calculate coefficient of variation for key metrics
        cpu_values = [p.cpu_cores for p in patterns]
        memory_values = [p.memory_mb for p in patterns]
        duration_values = [p.duration_minutes for p in patterns]
        
        def coefficient_of_variation(values):
            if len(values) < 2:
                return 1.0
            mean_val = np.mean(values)
            if mean_val == 0:
                return 1.0
            return np.std(values) / mean_val
        
        cpu_cv = coefficient_of_variation(cpu_values)
        memory_cv = coefficient_of_variation(memory_values)
        duration_cv = coefficient_of_variation(duration_values)
        
        # Lower coefficient of variation = higher confidence
        avg_cv = (cpu_cv + memory_cv + duration_cv) / 3
        confidence = max(0.3, 1.0 - avg_cv)
        
        # Boost confidence with more data points
        data_boost = min(0.2, len(patterns) * 0.02)
        confidence += data_boost
        
        return min(confidence, 1.0)
    
    def predict_system_utilization(self, horizon: PredictionHorizon, 
                                 planned_tasks: Optional[List[Dict[str, Any]]] = None) -> List[ResourcePrediction]:
        """
        Predict system resource utilization for a given time horizon.
        
        Args:
            horizon: Prediction time horizon
            planned_tasks: Optional list of planned tasks to factor in
            
        Returns:
            List of ResourcePrediction objects
        """
        with self.trace_operation("predict_system_utilization", horizon=horizon.value) as trace:
            predictions = []
            
            try:
                # Update resource history
                self._update_resource_history()
                
                # Predict each resource type
                for resource_type in ResourceType:
                    prediction = self._predict_resource_utilization(resource_type, horizon, planned_tasks)
                    predictions.append(prediction)
                
                trace.output_result = {
                    'horizon': horizon.value,
                    'predictions_count': len(predictions),
                    'planned_tasks_count': len(planned_tasks) if planned_tasks else 0
                }
                
            except Exception as e:
                self._logger.error(f"Error predicting system utilization: {e}")
                trace.output_result = {'error': str(e)}
            
            return predictions
    
    def _predict_resource_utilization(self, resource_type: ResourceType, horizon: PredictionHorizon,
                                    planned_tasks: Optional[List[Dict[str, Any]]]) -> ResourcePrediction:
        """Predict utilization for a specific resource type."""
        try:
            # Get current baseline utilization
            current_utilization = self._get_current_resource_utilization(resource_type)
            
            # Predict baseline trend
            baseline_prediction = self._predict_baseline_trend(resource_type, horizon)
            
            # Add planned task impact
            task_impact = 0.0
            if planned_tasks:
                task_impact = self._calculate_planned_task_impact(resource_type, planned_tasks)
            
            # Combine predictions
            predicted_utilization = min(1.0, baseline_prediction + task_impact)
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(
                resource_type, predicted_utilization, horizon
            )
            
            # Estimate peak utilization
            peak_utilization = min(1.0, predicted_utilization * 1.2)
            
            # Calculate bottleneck probability
            bottleneck_probability = self._calculate_bottleneck_probability(
                resource_type, predicted_utilization
            )
            
            return ResourcePrediction(
                resource_type=resource_type,
                horizon=horizon,
                predicted_utilization=predicted_utilization,
                confidence_interval=confidence_interval,
                peak_utilization=peak_utilization,
                bottleneck_probability=bottleneck_probability
            )
            
        except Exception as e:
            self._logger.error(f"Error predicting {resource_type.value} utilization: {e}")
            
            # Return conservative prediction
            return ResourcePrediction(
                resource_type=resource_type,
                horizon=horizon,
                predicted_utilization=0.5,
                confidence_interval=(0.3, 0.7),
                peak_utilization=0.6,
                bottleneck_probability=0.1
            )
    
    def generate_capacity_plan(self, planned_tasks: List[Dict[str, Any]], 
                             planning_horizon_hours: int = 4) -> CapacityPlan:
        """
        Generate capacity planning recommendations.
        
        Args:
            planned_tasks: List of tasks to plan for
            planning_horizon_hours: Planning horizon in hours
            
        Returns:
            CapacityPlan with recommendations
        """
        with self.trace_operation("generate_capacity_plan") as trace:
            try:
                # Get current system capacity
                current_capacity = self._get_current_system_capacity()
                
                # Predict resource demand
                predicted_demand = self._predict_resource_demand(planned_tasks, planning_horizon_hours)
                
                # Calculate capacity gaps
                capacity_gap = {}
                for resource, demand in predicted_demand.items():
                    gap = demand - current_capacity.get(resource, 0)
                    capacity_gap[resource] = max(0, gap)
                
                # Generate scaling recommendations
                scaling_recommendations = self._generate_scaling_recommendations(capacity_gap)
                
                # Generate optimization opportunities
                optimization_opportunities = self._identify_optimization_opportunities(
                    current_capacity, predicted_demand
                )
                
                # Calculate confidence score
                confidence_score = self._calculate_capacity_plan_confidence(planned_tasks)
                
                plan = CapacityPlan(
                    current_capacity=current_capacity,
                    predicted_demand=predicted_demand,
                    capacity_gap=capacity_gap,
                    scaling_recommendations=scaling_recommendations,
                    optimization_opportunities=optimization_opportunities,
                    confidence_score=confidence_score
                )
                
                trace.output_result = {
                    'planning_horizon_hours': planning_horizon_hours,
                    'tasks_count': len(planned_tasks),
                    'capacity_gaps': len([g for g in capacity_gap.values() if g > 0]),
                    'recommendations_count': len(scaling_recommendations),
                    'confidence_score': confidence_score
                }
                
                return plan
                
            except Exception as e:
                self._logger.error(f"Error generating capacity plan: {e}")
                trace.output_result = {'error': str(e)}
                raise
    
    def update_task_resource_pattern(self, task_id: str, task_definition: Dict[str, Any], 
                                   actual_usage: Dict[str, Any]) -> None:
        """Update task resource patterns based on actual usage."""
        try:
            task_type = task_definition.get('execution_context', {}).get('task_type', 'general')
            
            # Create resource requirement from actual usage
            requirement = ResourceRequirement(
                cpu_cores=actual_usage.get('cpu_cores', 1.0),
                memory_mb=actual_usage.get('memory_mb', 512),
                disk_mb=actual_usage.get('disk_mb', 100),
                network_mbps=actual_usage.get('network_mbps', 1.0),
                io_mbps=actual_usage.get('io_mbps', 5.0),
                duration_minutes=actual_usage.get('duration_minutes', 30.0),
                confidence=1.0  # Actual data has high confidence
            )
            
            # Add to patterns
            if task_type not in self.task_resource_patterns:
                self.task_resource_patterns[task_type] = []
            
            self.task_resource_patterns[task_type].append(requirement)
            
            # Limit pattern history
            max_patterns = 50
            if len(self.task_resource_patterns[task_type]) > max_patterns:
                self.task_resource_patterns[task_type] = self.task_resource_patterns[task_type][-max_patterns:]
            
            self._logger.debug(f"Updated resource pattern for task type {task_type}")
            
        except Exception as e:
            self._logger.error(f"Error updating task resource pattern: {e}")
    
    def _collect_current_metrics(self) -> ResourceMetrics:
        """Collect current system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O metrics (simplified)
            network_io = psutil.net_io_counters()
            network_io_mbps = (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024)  # Rough estimate
            
            # Disk I/O metrics (simplified)
            disk_io = psutil.disk_io_counters()
            disk_io_mbps = (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)  # Rough estimate
            
            return ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io_mbps=network_io_mbps,
                disk_io_mbps=disk_io_mbps
            )
            
        except Exception as e:
            self._logger.error(f"Error collecting current metrics: {e}")
            # Return default metrics
            return ResourceMetrics(
                cpu_percent=50.0,
                memory_percent=60.0,
                disk_percent=70.0,
                network_io_mbps=1.0,
                disk_io_mbps=5.0
            )
    
    def _update_resource_history(self) -> None:
        """Update resource history with current metrics."""
        try:
            current_metrics = self._collect_current_metrics()
            self.resource_history.append(current_metrics)
            
            # Limit history size
            max_history = int(self.config['history_retention_hours'] * 12)  # 5-minute intervals
            if len(self.resource_history) > max_history:
                self.resource_history = self.resource_history[-max_history:]
                
        except Exception as e:
            self._logger.error(f"Error updating resource history: {e}")
    
    def _get_current_resource_utilization(self, resource_type: ResourceType) -> float:
        """Get current utilization for a specific resource type."""
        try:
            current_metrics = self._collect_current_metrics()
            
            if resource_type == ResourceType.CPU:
                return current_metrics.cpu_percent / 100.0
            elif resource_type == ResourceType.MEMORY:
                return current_metrics.memory_percent / 100.0
            elif resource_type == ResourceType.DISK:
                return current_metrics.disk_percent / 100.0
            elif resource_type == ResourceType.NETWORK:
                return min(1.0, current_metrics.network_io_mbps / 100.0)  # Normalize to 100 Mbps
            elif resource_type == ResourceType.IO:
                return min(1.0, current_metrics.disk_io_mbps / 50.0)  # Normalize to 50 Mbps
            else:
                return 0.5  # Default
                
        except Exception as e:
            self._logger.error(f"Error getting current {resource_type.value} utilization: {e}")
            return 0.5
    
    def _predict_baseline_trend(self, resource_type: ResourceType, horizon: PredictionHorizon) -> float:
        """Predict baseline resource trend."""
        if len(self.resource_history) < 5:
            return self._get_current_resource_utilization(resource_type)
        
        # Simple trend analysis
        recent_values = []
        for metrics in self.resource_history[-10:]:
            if resource_type == ResourceType.CPU:
                recent_values.append(metrics.cpu_percent / 100.0)
            elif resource_type == ResourceType.MEMORY:
                recent_values.append(metrics.memory_percent / 100.0)
            elif resource_type == ResourceType.DISK:
                recent_values.append(metrics.disk_percent / 100.0)
            elif resource_type == ResourceType.NETWORK:
                recent_values.append(min(1.0, metrics.network_io_mbps / 100.0))
            elif resource_type == ResourceType.IO:
                recent_values.append(min(1.0, metrics.disk_io_mbps / 50.0))
        
        if len(recent_values) < 2:
            return recent_values[0] if recent_values else 0.5
        
        # Calculate simple linear trend
        x = np.arange(len(recent_values))
        slope, intercept = np.polyfit(x, recent_values, 1)
        
        # Project forward based on horizon
        horizon_multipliers = {
            PredictionHorizon.SHORT_TERM: 1,
            PredictionHorizon.MEDIUM_TERM: 3,
            PredictionHorizon.LONG_TERM: 12
        }
        
        future_x = len(recent_values) + horizon_multipliers[horizon]
        predicted_value = slope * future_x + intercept
        
        return max(0.0, min(1.0, predicted_value))
    
    def _calculate_planned_task_impact(self, resource_type: ResourceType, 
                                     planned_tasks: List[Dict[str, Any]]) -> float:
        """Calculate impact of planned tasks on resource utilization."""
        total_impact = 0.0
        
        for task in planned_tasks:
            # Predict resource requirements for this task
            requirements = self.predict_task_resource_requirements(task)
            
            # Convert to utilization impact
            if resource_type == ResourceType.CPU:
                # Assume 8-core system for normalization
                impact = requirements.cpu_cores / 8.0
            elif resource_type == ResourceType.MEMORY:
                # Assume 16GB system for normalization
                impact = requirements.memory_mb / (16 * 1024)
            elif resource_type == ResourceType.DISK:
                # Disk impact is usually temporary
                impact = 0.05
            elif resource_type == ResourceType.NETWORK:
                impact = requirements.network_mbps / 100.0
            elif resource_type == ResourceType.IO:
                impact = requirements.io_mbps / 50.0
            else:
                impact = 0.0
            
            total_impact += impact
        
        return min(1.0, total_impact)
    
    def _calculate_confidence_interval(self, resource_type: ResourceType, 
                                     predicted_utilization: float, 
                                     horizon: PredictionHorizon) -> Tuple[float, float]:
        """Calculate confidence interval for prediction."""
        # Base uncertainty increases with prediction horizon
        base_uncertainty = {
            PredictionHorizon.SHORT_TERM: 0.05,
            PredictionHorizon.MEDIUM_TERM: 0.10,
            PredictionHorizon.LONG_TERM: 0.20
        }[horizon]
        
        # Adjust uncertainty based on historical variance
        if len(self.resource_history) > 5:
            recent_values = []
            for metrics in self.resource_history[-20:]:
                if resource_type == ResourceType.CPU:
                    recent_values.append(metrics.cpu_percent / 100.0)
                elif resource_type == ResourceType.MEMORY:
                    recent_values.append(metrics.memory_percent / 100.0)
                # Add other resource types as needed
            
            if recent_values:
                historical_std = np.std(recent_values)
                base_uncertainty += historical_std * 0.5
        
        lower_bound = max(0.0, predicted_utilization - base_uncertainty)
        upper_bound = min(1.0, predicted_utilization + base_uncertainty)
        
        return (lower_bound, upper_bound)
    
    def _calculate_bottleneck_probability(self, resource_type: ResourceType, 
                                        predicted_utilization: float) -> float:
        """Calculate probability of resource becoming a bottleneck."""
        thresholds = {
            ResourceType.CPU: self.config['cpu_bottleneck_threshold'],
            ResourceType.MEMORY: self.config['memory_bottleneck_threshold'],
            ResourceType.DISK: self.config['disk_bottleneck_threshold'],
            ResourceType.NETWORK: 0.80,
            ResourceType.IO: 0.85
        }
        
        threshold = thresholds.get(resource_type, 0.85)
        
        if predicted_utilization < threshold * 0.7:
            return 0.0
        elif predicted_utilization > threshold:
            return 1.0
        else:
            # Linear interpolation between 70% and 100% of threshold
            range_start = threshold * 0.7
            range_size = threshold - range_start
            position = (predicted_utilization - range_start) / range_size
            return position
    
    def _get_current_system_capacity(self) -> Dict[str, float]:
        """Get current system capacity metrics."""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_cores': float(cpu_count),
                'memory_gb': memory.total / (1024**3),
                'disk_gb': disk.total / (1024**3),
                'network_mbps': 100.0,  # Assume 100 Mbps
                'io_mbps': 50.0  # Assume 50 Mbps I/O capacity
            }
        except Exception as e:
            self._logger.error(f"Error getting system capacity: {e}")
            return {
                'cpu_cores': 4.0,
                'memory_gb': 8.0,
                'disk_gb': 100.0,
                'network_mbps': 100.0,
                'io_mbps': 50.0
            }
    
    def _predict_resource_demand(self, planned_tasks: List[Dict[str, Any]], 
                               planning_horizon_hours: int) -> Dict[str, float]:
        """Predict resource demand for planned tasks."""
        total_demand = {
            'cpu_cores': 0.0,
            'memory_gb': 0.0,
            'disk_gb': 0.0,
            'network_mbps': 0.0,
            'io_mbps': 0.0
        }
        
        for task in planned_tasks:
            requirements = self.predict_task_resource_requirements(task)
            
            # Accumulate peak demand (assuming some overlap)
            overlap_factor = 0.7  # Assume 70% overlap
            total_demand['cpu_cores'] += requirements.cpu_cores * overlap_factor
            total_demand['memory_gb'] += (requirements.memory_mb / 1024) * overlap_factor
            total_demand['disk_gb'] += (requirements.disk_mb / 1024) * overlap_factor
            total_demand['network_mbps'] += requirements.network_mbps * overlap_factor
            total_demand['io_mbps'] += requirements.io_mbps * overlap_factor
        
        return total_demand
    
    def _generate_scaling_recommendations(self, capacity_gap: Dict[str, float]) -> List[str]:
        """Generate scaling recommendations based on capacity gaps."""
        recommendations = []
        
        for resource, gap in capacity_gap.items():
            if gap > 0:
                if resource == 'cpu_cores':
                    recommendations.append(f"Consider adding {gap:.1f} CPU cores or upgrading to higher-performance CPUs")
                elif resource == 'memory_gb':
                    recommendations.append(f"Consider adding {gap:.1f}GB of RAM")
                elif resource == 'disk_gb':
                    recommendations.append(f"Consider adding {gap:.1f}GB of disk storage")
                elif resource == 'network_mbps':
                    recommendations.append(f"Consider upgrading network bandwidth by {gap:.1f}Mbps")
                elif resource == 'io_mbps':
                    recommendations.append(f"Consider upgrading to faster storage (SSD) for {gap:.1f}Mbps additional I/O")
        
        if not recommendations:
            recommendations.append("Current system capacity appears sufficient for planned workload")
        
        return recommendations
    
    def _identify_optimization_opportunities(self, current_capacity: Dict[str, float], 
                                           predicted_demand: Dict[str, float]) -> List[str]:
        """Identify resource optimization opportunities."""
        opportunities = []
        
        for resource, capacity in current_capacity.items():
            demand = predicted_demand.get(resource, 0)
            utilization = demand / capacity if capacity > 0 else 0
            
            if utilization < 0.3:
                opportunities.append(f"Low {resource} utilization ({utilization:.1%}) - consider workload consolidation")
            elif utilization > 0.9:
                opportunities.append(f"High {resource} utilization ({utilization:.1%}) - consider load balancing or scaling")
        
        # General optimization opportunities
        opportunities.extend([
            "Consider implementing resource pooling for better utilization",
            "Evaluate task scheduling optimization to reduce peak demand",
            "Consider implementing auto-scaling based on demand patterns"
        ])
        
        return opportunities
    
    def _calculate_capacity_plan_confidence(self, planned_tasks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for capacity plan."""
        if not planned_tasks:
            return 0.5
        
        # Base confidence
        confidence = 0.7
        
        # Increase confidence with more historical data
        total_patterns = sum(len(patterns) for patterns in self.task_resource_patterns.values())
        if total_patterns > 50:
            confidence += 0.2
        elif total_patterns > 20:
            confidence += 0.1
        
        # Decrease confidence for unknown task types
        known_types = set(self.task_resource_patterns.keys())
        task_types = set(task.get('execution_context', {}).get('task_type', 'general') for task in planned_tasks)
        unknown_types = task_types - known_types
        
        if unknown_types:
            confidence -= len(unknown_types) * 0.1
        
        return max(0.3, min(1.0, confidence))
    
    def _calculate_recent_prediction_accuracy(self) -> float:
        """Calculate recent prediction accuracy."""
        if not self.prediction_accuracy_history:
            return 0.7  # Default accuracy
        
        recent_accuracies = [entry['accuracy'] for entry in self.prediction_accuracy_history[-10:]]
        return np.mean(recent_accuracies) if recent_accuracies else 0.7
    
    def _check_data_freshness(self) -> bool:
        """Check if resource data is fresh."""
        if not self.resource_history:
            return False
        
        last_update = self.resource_history[-1].timestamp
        age_minutes = (datetime.now() - last_update).total_seconds() / 60
        
        return age_minutes < self.config['prediction_update_interval_minutes'] * 2


# Convenience functions
def predict_task_resources(task_definition: Dict[str, Any]) -> ResourceRequirement:
    """
    Convenience function to predict task resource requirements.
    
    Args:
        task_definition: Task definition with metadata
        
    Returns:
        ResourceRequirement prediction
    """
    predictor = ResourcePredictor()
    return predictor.predict_task_resource_requirements(task_definition)


def generate_system_capacity_plan(planned_tasks: List[Dict[str, Any]], 
                                 planning_horizon_hours: int = 4) -> CapacityPlan:
    """
    Convenience function to generate system capacity plan.
    
    Args:
        planned_tasks: List of tasks to plan for
        planning_horizon_hours: Planning horizon in hours
        
    Returns:
        CapacityPlan with recommendations
    """
    predictor = ResourcePredictor()
    return predictor.generate_capacity_plan(planned_tasks, planning_horizon_hours)


if __name__ == "__main__":
    # Example usage
    predictor = ResourcePredictor()
    
    # Example task
    task = {
        'id': 'test_task_1',
        'name': 'Test Resource Prediction',
        'dependencies': ['task_0'],
        'resource_requirements': {
            'cpu_cores': 2,
            'memory_mb': 1024
        },
        'execution_context': {
            'task_type': 'implementation',
            'priority': 'high'
        }
    }
    
    # Predict resource requirements
    requirements = predictor.predict_task_resource_requirements(task)
    print(f"Predicted Requirements:")
    print(f"  CPU Cores: {requirements.cpu_cores:.1f}")
    print(f"  Memory: {requirements.memory_mb}MB")
    print(f"  Duration: {requirements.duration_minutes:.1f} minutes")
    print(f"  Confidence: {requirements.confidence:.2f}")
    
    # Generate capacity plan
    capacity_plan = predictor.generate_capacity_plan([task])
    print(f"\nCapacity Plan:")
    print(f"  Current Capacity: {capacity_plan.current_capacity}")
    print(f"  Predicted Demand: {capacity_plan.predicted_demand}")
    print(f"  Capacity Gaps: {capacity_plan.capacity_gap}")
    print(f"  Confidence: {capacity_plan.confidence_score:.2f}")
    
    for rec in capacity_plan.scaling_recommendations:
        print(f"  - {rec}")