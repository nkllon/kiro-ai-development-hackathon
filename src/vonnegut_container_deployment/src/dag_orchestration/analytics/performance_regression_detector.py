"""
Performance Regression Detector - Automated detection of performance degradation

This module provides automated detection of performance regressions,
anomaly detection, and predictive failure analysis.
"""

import json
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.analytics.execution_pattern_analyzer import ExecutionMetrics


class RegressionType(Enum):
    """Types of performance regressions."""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    RESOURCE_USAGE = "resource_usage"
    COST_EFFICIENCY = "cost_efficiency"
    THROUGHPUT = "throughput"
    LATENCY = "latency"


class AnomalyType(Enum):
    """Types of performance anomalies."""
    SPIKE = "spike"
    DROP = "drop"
    DRIFT = "drift"
    OSCILLATION = "oscillation"
    PLATEAU = "plateau"


class Severity(Enum):
    """Severity levels for regressions and anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceBaseline:
    """Performance baseline for comparison."""
    metric_name: str
    baseline_value: float
    baseline_variance: float
    sample_count: int
    baseline_period_start: datetime
    baseline_period_end: datetime
    confidence_interval: Tuple[float, float]


@dataclass
class RegressionDetection:
    """Detected performance regression."""
    regression_type: RegressionType
    severity: Severity
    confidence: float
    affected_tasks: List[str]
    baseline_value: float
    current_value: float
    degradation_percent: float
    detection_time: datetime
    first_occurrence: datetime
    description: str
    root_cause_analysis: Dict[str, Any]
    mitigation_suggestions: List[str]


@dataclass
class AnomalyDetection:
    """Detected performance anomaly."""
    anomaly_type: AnomalyType
    severity: Severity
    confidence: float
    affected_metric: str
    affected_tasks: List[str]
    anomaly_value: float
    expected_value: float
    deviation_score: float
    detection_time: datetime
    duration: Optional[timedelta]
    description: str
    context: Dict[str, Any]


@dataclass
class PredictiveAlert:
    """Predictive alert for potential future issues."""
    alert_type: str
    severity: Severity
    confidence: float
    predicted_occurrence_time: datetime
    affected_components: List[str]
    prediction_basis: str
    description: str
    preventive_actions: List[str]
    monitoring_recommendations: List[str]


class PerformanceRegressionDetector(ReflectiveModule):
    """
    Advanced performance regression detector with anomaly detection.
    
    Provides automated detection of performance degradation, anomalies,
    and predictive alerts for potential future issues.
    """
    
    def __init__(self, baseline_window_hours: int = 168, detection_sensitivity: float = 0.8):
        super().__init__()
        self.baseline_window_hours = baseline_window_hours  # 1 week default
        self.detection_sensitivity = detection_sensitivity
        
        self.execution_history: List[ExecutionMetrics] = []
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.regression_history: List[RegressionDetection] = []
        self.anomaly_history: List[AnomalyDetection] = []
        self.predictive_alerts: List[PredictiveAlert] = []
        
        # Detection thresholds
        self.thresholds = {
            'regression_threshold': 0.15,  # 15% degradation
            'anomaly_threshold': 2.0,      # 2 standard deviations
            'critical_threshold': 0.5,     # 50% degradation = critical
            'trend_threshold': 0.7,        # Trend confidence threshold
            'prediction_threshold': 0.6,   # Prediction confidence threshold
        }
        
        # Sliding window for real-time detection
        self.sliding_window_size = 50
        self.recent_metrics: deque = deque(maxlen=self.sliding_window_size)
        
        self.logger = logging.getLogger(__name__)
    
    def add_execution_metrics(self, metrics: List[ExecutionMetrics]) -> None:
        """Add execution metrics for analysis."""
        with self.trace_operation("add_execution_metrics"):
            self.execution_history.extend(metrics)
            
            # Add to sliding window for real-time detection
            for metric in metrics:
                self.recent_metrics.append(metric)
            
            # Update baselines periodically
            self._update_baselines()
            
            self.logger.info(
                f"Added {len(metrics)} execution metrics for regression analysis",
                extra={
                    'total_metrics': len(self.execution_history),
                    'recent_window_size': len(self.recent_metrics)
                }
            )
    
    def detect_performance_regressions(self, 
                                     comparison_window_hours: int = 24) -> List[RegressionDetection]:
        """
        Detect performance regressions by comparing recent performance to baselines.
        
        Args:
            comparison_window_hours: Hours of recent data to compare against baselines
            
        Returns:
            List of detected performance regressions
        """
        with self.trace_operation("detect_performance_regressions"):
            if not self.execution_history or not self.baselines:
                return []
            
            # Get recent metrics for comparison
            cutoff_time = datetime.now() - timedelta(hours=comparison_window_hours)
            recent_metrics = [
                m for m in self.execution_history 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return []
            
            regressions = []
            
            # Detect different types of regressions
            regressions.extend(self._detect_execution_time_regressions(recent_metrics))
            regressions.extend(self._detect_success_rate_regressions(recent_metrics))
            regressions.extend(self._detect_resource_usage_regressions(recent_metrics))
            regressions.extend(self._detect_cost_efficiency_regressions(recent_metrics))
            regressions.extend(self._detect_throughput_regressions(recent_metrics))
            
            # Sort by severity and confidence
            regressions.sort(key=lambda x: (x.severity.value, x.confidence), reverse=True)
            
            # Store in history
            self.regression_history.extend(regressions)
            
            self.logger.info(
                f"Detected {len(regressions)} performance regressions",
                extra={
                    'regressions_count': len(regressions),
                    'critical_regressions': len([r for r in regressions if r.severity == Severity.CRITICAL]),
                    'high_regressions': len([r for r in regressions if r.severity == Severity.HIGH])
                }
            )
            
            return regressions
    
    def detect_performance_anomalies(self, 
                                   analysis_window_hours: int = 24) -> List[AnomalyDetection]:
        """
        Detect performance anomalies using statistical analysis.
        
        Args:
            analysis_window_hours: Hours of data to analyze for anomalies
            
        Returns:
            List of detected performance anomalies
        """
        with self.trace_operation("detect_performance_anomalies"):
            if not self.execution_history:
                return []
            
            # Get metrics for analysis
            cutoff_time = datetime.now() - timedelta(hours=analysis_window_hours)
            analysis_metrics = [
                m for m in self.execution_history 
                if m.timestamp >= cutoff_time
            ]
            
            if len(analysis_metrics) < 10:  # Need minimum data for anomaly detection
                return []
            
            anomalies = []
            
            # Detect different types of anomalies
            anomalies.extend(self._detect_execution_time_anomalies(analysis_metrics))
            anomalies.extend(self._detect_resource_usage_anomalies(analysis_metrics))
            anomalies.extend(self._detect_cost_anomalies(analysis_metrics))
            anomalies.extend(self._detect_success_rate_anomalies(analysis_metrics))
            
            # Sort by severity and confidence
            anomalies.sort(key=lambda x: (x.severity.value, x.confidence), reverse=True)
            
            # Store in history
            self.anomaly_history.extend(anomalies)
            
            self.logger.info(
                f"Detected {len(anomalies)} performance anomalies",
                extra={
                    'anomalies_count': len(anomalies),
                    'critical_anomalies': len([a for a in anomalies if a.severity == Severity.CRITICAL]),
                    'high_anomalies': len([a for a in anomalies if a.severity == Severity.HIGH])
                }
            )
            
            return anomalies
    
    def generate_predictive_alerts(self, 
                                 prediction_horizon_hours: int = 72) -> List[PredictiveAlert]:
        """
        Generate predictive alerts for potential future performance issues.
        
        Args:
            prediction_horizon_hours: Hours ahead to predict
            
        Returns:
            List of predictive alerts
        """
        with self.trace_operation("generate_predictive_alerts"):
            if len(self.execution_history) < 50:  # Need sufficient history for prediction
                return []
            
            alerts = []
            
            # Predict different types of issues
            alerts.extend(self._predict_capacity_exhaustion(prediction_horizon_hours))
            alerts.extend(self._predict_performance_degradation(prediction_horizon_hours))
            alerts.extend(self._predict_failure_rate_increase(prediction_horizon_hours))
            alerts.extend(self._predict_cost_overruns(prediction_horizon_hours))
            
            # Filter by confidence threshold
            alerts = [a for a in alerts if a.confidence >= self.thresholds['prediction_threshold']]
            
            # Sort by severity and predicted occurrence time
            alerts.sort(key=lambda x: (x.severity.value, x.predicted_occurrence_time))
            
            # Store alerts
            self.predictive_alerts = alerts
            
            self.logger.info(
                f"Generated {len(alerts)} predictive alerts",
                extra={
                    'alerts_count': len(alerts),
                    'critical_alerts': len([a for a in alerts if a.severity == Severity.CRITICAL]),
                    'prediction_horizon_hours': prediction_horizon_hours
                }
            )
            
            return alerts
    
    def get_performance_health_score(self) -> Dict[str, Any]:
        """
        Calculate overall performance health score.
        
        Returns:
            Dictionary with health scores and metrics
        """
        with self.trace_operation("get_performance_health_score"):
            if not self.execution_history:
                return {'overall_score': 0, 'status': 'insufficient_data'}
            
            # Get recent regressions and anomalies
            recent_regressions = self.detect_performance_regressions(24)
            recent_anomalies = self.detect_performance_anomalies(24)
            
            # Calculate component scores
            regression_score = self._calculate_regression_score(recent_regressions)
            anomaly_score = self._calculate_anomaly_score(recent_anomalies)
            trend_score = self._calculate_trend_score()
            stability_score = self._calculate_stability_score()
            
            # Calculate overall score (0-100)
            overall_score = (
                regression_score * 0.3 +
                anomaly_score * 0.25 +
                trend_score * 0.25 +
                stability_score * 0.2
            )
            
            # Determine status
            if overall_score >= 90:
                status = 'excellent'
            elif overall_score >= 75:
                status = 'good'
            elif overall_score >= 60:
                status = 'fair'
            elif overall_score >= 40:
                status = 'poor'
            else:
                status = 'critical'
            
            health_score = {
                'overall_score': overall_score,
                'status': status,
                'component_scores': {
                    'regression_score': regression_score,
                    'anomaly_score': anomaly_score,
                    'trend_score': trend_score,
                    'stability_score': stability_score
                },
                'recent_issues': {
                    'regressions': len(recent_regressions),
                    'anomalies': len(recent_anomalies),
                    'critical_issues': len([r for r in recent_regressions if r.severity == Severity.CRITICAL]) +
                                     len([a for a in recent_anomalies if a.severity == Severity.CRITICAL])
                },
                'recommendations': self._generate_health_recommendations(overall_score, recent_regressions, recent_anomalies)
            }
            
            return health_score
    
    def _update_baselines(self) -> None:
        """Update performance baselines based on historical data."""
        if len(self.execution_history) < 20:  # Need minimum data for baseline
            return
        
        # Get baseline period data
        baseline_end = datetime.now() - timedelta(hours=24)  # Exclude last 24 hours
        baseline_start = baseline_end - timedelta(hours=self.baseline_window_hours)
        
        baseline_metrics = [
            m for m in self.execution_history 
            if baseline_start <= m.timestamp <= baseline_end
        ]
        
        if len(baseline_metrics) < 10:
            return
        
        # Update baselines for different metrics
        self._update_execution_time_baseline(baseline_metrics, baseline_start, baseline_end)
        self._update_success_rate_baseline(baseline_metrics, baseline_start, baseline_end)
        self._update_resource_usage_baseline(baseline_metrics, baseline_start, baseline_end)
        self._update_cost_baseline(baseline_metrics, baseline_start, baseline_end)
    
    def _update_execution_time_baseline(self, metrics: List[ExecutionMetrics], 
                                      start_time: datetime, end_time: datetime) -> None:
        """Update execution time baseline."""
        execution_times = [m.execution_time for m in metrics]
        
        if not execution_times:
            return
        
        mean_time = statistics.mean(execution_times)
        variance = statistics.variance(execution_times) if len(execution_times) > 1 else 0
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        confidence_interval = (
            mean_time - 1.96 * std_dev,
            mean_time + 1.96 * std_dev
        )
        
        self.baselines['execution_time'] = PerformanceBaseline(
            metric_name='execution_time',
            baseline_value=mean_time,
            baseline_variance=variance,
            sample_count=len(execution_times),
            baseline_period_start=start_time,
            baseline_period_end=end_time,
            confidence_interval=confidence_interval
        )
    
    def _update_success_rate_baseline(self, metrics: List[ExecutionMetrics], 
                                    start_time: datetime, end_time: datetime) -> None:
        """Update success rate baseline."""
        success_rate = sum(1 for m in metrics if m.success) / len(metrics)
        
        # For success rate, variance is p(1-p)/n
        variance = success_rate * (1 - success_rate) / len(metrics)
        std_dev = variance ** 0.5
        
        confidence_interval = (
            max(0, success_rate - 1.96 * std_dev),
            min(1, success_rate + 1.96 * std_dev)
        )
        
        self.baselines['success_rate'] = PerformanceBaseline(
            metric_name='success_rate',
            baseline_value=success_rate,
            baseline_variance=variance,
            sample_count=len(metrics),
            baseline_period_start=start_time,
            baseline_period_end=end_time,
            confidence_interval=confidence_interval
        )
    
    def _update_resource_usage_baseline(self, metrics: List[ExecutionMetrics], 
                                      start_time: datetime, end_time: datetime) -> None:
        """Update resource usage baselines."""
        cpu_usage = [m.cpu_usage for m in metrics if m.cpu_usage > 0]
        memory_usage = [m.memory_usage for m in metrics if m.memory_usage > 0]
        
        if cpu_usage:
            mean_cpu = statistics.mean(cpu_usage)
            variance_cpu = statistics.variance(cpu_usage) if len(cpu_usage) > 1 else 0
            std_dev_cpu = statistics.stdev(cpu_usage) if len(cpu_usage) > 1 else 0
            
            self.baselines['cpu_usage'] = PerformanceBaseline(
                metric_name='cpu_usage',
                baseline_value=mean_cpu,
                baseline_variance=variance_cpu,
                sample_count=len(cpu_usage),
                baseline_period_start=start_time,
                baseline_period_end=end_time,
                confidence_interval=(
                    mean_cpu - 1.96 * std_dev_cpu,
                    mean_cpu + 1.96 * std_dev_cpu
                )
            )
        
        if memory_usage:
            mean_memory = statistics.mean(memory_usage)
            variance_memory = statistics.variance(memory_usage) if len(memory_usage) > 1 else 0
            std_dev_memory = statistics.stdev(memory_usage) if len(memory_usage) > 1 else 0
            
            self.baselines['memory_usage'] = PerformanceBaseline(
                metric_name='memory_usage',
                baseline_value=mean_memory,
                baseline_variance=variance_memory,
                sample_count=len(memory_usage),
                baseline_period_start=start_time,
                baseline_period_end=end_time,
                confidence_interval=(
                    mean_memory - 1.96 * std_dev_memory,
                    mean_memory + 1.96 * std_dev_memory
                )
            )
    
    def _update_cost_baseline(self, metrics: List[ExecutionMetrics], 
                            start_time: datetime, end_time: datetime) -> None:
        """Update cost baseline."""
        costs = [m.cost for m in metrics if m.cost > 0]
        
        if not costs:
            return
        
        mean_cost = statistics.mean(costs)
        variance = statistics.variance(costs) if len(costs) > 1 else 0
        std_dev = statistics.stdev(costs) if len(costs) > 1 else 0
        
        self.baselines['cost'] = PerformanceBaseline(
            metric_name='cost',
            baseline_value=mean_cost,
            baseline_variance=variance,
            sample_count=len(costs),
            baseline_period_start=start_time,
            baseline_period_end=end_time,
            confidence_interval=(
                mean_cost - 1.96 * std_dev,
                mean_cost + 1.96 * std_dev
            )
        )
    
    def _detect_execution_time_regressions(self, recent_metrics: List[ExecutionMetrics]) -> List[RegressionDetection]:
        """Detect execution time regressions."""
        regressions = []
        
        if 'execution_time' not in self.baselines:
            return regressions
        
        baseline = self.baselines['execution_time']
        recent_times = [m.execution_time for m in recent_metrics]
        
        if not recent_times:
            return regressions
        
        current_mean = statistics.mean(recent_times)
        degradation_percent = (current_mean - baseline.baseline_value) / baseline.baseline_value
        
        if degradation_percent > self.thresholds['regression_threshold']:
            # Determine severity
            if degradation_percent > self.thresholds['critical_threshold']:
                severity = Severity.CRITICAL
            elif degradation_percent > 0.3:
                severity = Severity.HIGH
            elif degradation_percent > 0.2:
                severity = Severity.MEDIUM
            else:
                severity = Severity.LOW
            
            # Calculate confidence based on statistical significance
            confidence = min(degradation_percent * 2, 1.0)
            
            # Find first occurrence
            first_occurrence = recent_metrics[0].timestamp
            for metric in recent_metrics:
                if metric.execution_time > baseline.baseline_value * (1 + self.thresholds['regression_threshold']):
                    first_occurrence = metric.timestamp
                    break
            
            # Analyze affected tasks
            affected_tasks = list(set(m.task_id for m in recent_metrics 
                                    if m.execution_time > baseline.baseline_value * 1.2))
            
            regressions.append(RegressionDetection(
                regression_type=RegressionType.EXECUTION_TIME,
                severity=severity,
                confidence=confidence,
                affected_tasks=affected_tasks,
                baseline_value=baseline.baseline_value,
                current_value=current_mean,
                degradation_percent=degradation_percent * 100,
                detection_time=datetime.now(),
                first_occurrence=first_occurrence,
                description=f"Execution time increased by {degradation_percent:.1%} from baseline",
                root_cause_analysis={
                    'baseline_period': f"{baseline.baseline_period_start} to {baseline.baseline_period_end}",
                    'sample_size': len(recent_times),
                    'variance_change': statistics.variance(recent_times) / baseline.baseline_variance if baseline.baseline_variance > 0 else 1.0
                },
                mitigation_suggestions=[
                    "Profile slow tasks to identify performance bottlenecks",
                    "Check for resource contention or system load issues",
                    "Review recent code changes that might impact performance",
                    "Consider scaling resources or optimizing algorithms"
                ]
            ))
        
        return regressions
    
    def _detect_success_rate_regressions(self, recent_metrics: List[ExecutionMetrics]) -> List[RegressionDetection]:
        """Detect success rate regressions."""
        regressions = []
        
        if 'success_rate' not in self.baselines:
            return regressions
        
        baseline = self.baselines['success_rate']
        current_success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
        
        degradation_percent = (baseline.baseline_value - current_success_rate) / baseline.baseline_value
        
        if degradation_percent > self.thresholds['regression_threshold']:
            # Determine severity
            if degradation_percent > self.thresholds['critical_threshold']:
                severity = Severity.CRITICAL
            elif degradation_percent > 0.3:
                severity = Severity.HIGH
            elif degradation_percent > 0.2:
                severity = Severity.MEDIUM
            else:
                severity = Severity.LOW
            
            confidence = min(degradation_percent * 2, 1.0)
            
            # Find affected tasks
            failed_tasks = [m.task_id for m in recent_metrics if not m.success]
            affected_tasks = list(set(failed_tasks))
            
            regressions.append(RegressionDetection(
                regression_type=RegressionType.SUCCESS_RATE,
                severity=severity,
                confidence=confidence,
                affected_tasks=affected_tasks,
                baseline_value=baseline.baseline_value,
                current_value=current_success_rate,
                degradation_percent=degradation_percent * 100,
                detection_time=datetime.now(),
                first_occurrence=recent_metrics[0].timestamp,
                description=f"Success rate decreased by {degradation_percent:.1%} from baseline",
                root_cause_analysis={
                    'failure_count': len(failed_tasks),
                    'unique_failed_tasks': len(affected_tasks),
                    'common_errors': self._analyze_common_errors(recent_metrics)
                },
                mitigation_suggestions=[
                    "Investigate common failure patterns and error types",
                    "Review error handling and retry mechanisms",
                    "Check for infrastructure or dependency issues",
                    "Implement better input validation and error recovery"
                ]
            ))
        
        return regressions
    
    def _detect_resource_usage_regressions(self, recent_metrics: List[ExecutionMetrics]) -> List[RegressionDetection]:
        """Detect resource usage regressions."""
        regressions = []
        
        # Check CPU usage regression
        if 'cpu_usage' in self.baselines:
            cpu_values = [m.cpu_usage for m in recent_metrics if m.cpu_usage > 0]
            if cpu_values:
                baseline = self.baselines['cpu_usage']
                current_mean = statistics.mean(cpu_values)
                degradation_percent = (current_mean - baseline.baseline_value) / baseline.baseline_value
                
                if degradation_percent > self.thresholds['regression_threshold']:
                    severity = self._determine_severity(degradation_percent)
                    
                    regressions.append(RegressionDetection(
                        regression_type=RegressionType.RESOURCE_USAGE,
                        severity=severity,
                        confidence=min(degradation_percent * 1.5, 1.0),
                        affected_tasks=list(set(m.task_id for m in recent_metrics if m.cpu_usage > baseline.baseline_value * 1.2)),
                        baseline_value=baseline.baseline_value,
                        current_value=current_mean,
                        degradation_percent=degradation_percent * 100,
                        detection_time=datetime.now(),
                        first_occurrence=recent_metrics[0].timestamp,
                        description=f"CPU usage increased by {degradation_percent:.1%} from baseline",
                        root_cause_analysis={'resource_type': 'cpu'},
                        mitigation_suggestions=[
                            "Implement CPU-aware task scheduling",
                            "Profile CPU-intensive tasks for optimization",
                            "Consider resource limits and throttling"
                        ]
                    ))
        
        # Check memory usage regression
        if 'memory_usage' in self.baselines:
            memory_values = [m.memory_usage for m in recent_metrics if m.memory_usage > 0]
            if memory_values:
                baseline = self.baselines['memory_usage']
                current_mean = statistics.mean(memory_values)
                degradation_percent = (current_mean - baseline.baseline_value) / baseline.baseline_value
                
                if degradation_percent > self.thresholds['regression_threshold']:
                    severity = self._determine_severity(degradation_percent)
                    
                    regressions.append(RegressionDetection(
                        regression_type=RegressionType.RESOURCE_USAGE,
                        severity=severity,
                        confidence=min(degradation_percent * 1.5, 1.0),
                        affected_tasks=list(set(m.task_id for m in recent_metrics if m.memory_usage > baseline.baseline_value * 1.2)),
                        baseline_value=baseline.baseline_value,
                        current_value=current_mean,
                        degradation_percent=degradation_percent * 100,
                        detection_time=datetime.now(),
                        first_occurrence=recent_metrics[0].timestamp,
                        description=f"Memory usage increased by {degradation_percent:.1%} from baseline",
                        root_cause_analysis={'resource_type': 'memory'},
                        mitigation_suggestions=[
                            "Implement memory-aware task scheduling",
                            "Add memory cleanup and garbage collection",
                            "Profile memory usage patterns for optimization"
                        ]
                    ))
        
        return regressions
    
    def _detect_cost_efficiency_regressions(self, recent_metrics: List[ExecutionMetrics]) -> List[RegressionDetection]:
        """Detect cost efficiency regressions."""
        regressions = []
        
        if 'cost' not in self.baselines:
            return regressions
        
        baseline = self.baselines['cost']
        recent_costs = [m.cost for m in recent_metrics if m.cost > 0]
        
        if not recent_costs:
            return regressions
        
        current_mean = statistics.mean(recent_costs)
        degradation_percent = (current_mean - baseline.baseline_value) / baseline.baseline_value
        
        if degradation_percent > self.thresholds['regression_threshold']:
            severity = self._determine_severity(degradation_percent)
            
            regressions.append(RegressionDetection(
                regression_type=RegressionType.COST_EFFICIENCY,
                severity=severity,
                confidence=min(degradation_percent * 1.5, 1.0),
                affected_tasks=list(set(m.task_id for m in recent_metrics if m.cost > baseline.baseline_value * 1.2)),
                baseline_value=baseline.baseline_value,
                current_value=current_mean,
                degradation_percent=degradation_percent * 100,
                detection_time=datetime.now(),
                first_occurrence=recent_metrics[0].timestamp,
                description=f"Cost per task increased by {degradation_percent:.1%} from baseline",
                root_cause_analysis={
                    'cost_analysis': self._analyze_cost_patterns(recent_metrics)
                },
                mitigation_suggestions=[
                    "Review LLM provider selection and pricing",
                    "Implement cost-aware task scheduling",
                    "Optimize task complexity and resource usage",
                    "Consider task batching for cost efficiency"
                ]
            ))
        
        return regressions
    
    def _detect_throughput_regressions(self, recent_metrics: List[ExecutionMetrics]) -> List[RegressionDetection]:
        """Detect throughput regressions."""
        regressions = []
        
        if len(recent_metrics) < 10:
            return regressions
        
        # Calculate throughput (tasks per hour)
        time_span = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds() / 3600
        if time_span <= 0:
            return regressions
        
        current_throughput = len(recent_metrics) / time_span
        
        # Compare with historical throughput
        historical_metrics = [m for m in self.execution_history if m not in recent_metrics]
        if len(historical_metrics) < 10:
            return regressions
        
        # Calculate historical throughput
        historical_time_span = (historical_metrics[-1].timestamp - historical_metrics[0].timestamp).total_seconds() / 3600
        if historical_time_span <= 0:
            return regressions
        
        historical_throughput = len(historical_metrics) / historical_time_span
        
        degradation_percent = (historical_throughput - current_throughput) / historical_throughput
        
        if degradation_percent > self.thresholds['regression_threshold']:
            severity = self._determine_severity(degradation_percent)
            
            regressions.append(RegressionDetection(
                regression_type=RegressionType.THROUGHPUT,
                severity=severity,
                confidence=min(degradation_percent * 1.5, 1.0),
                affected_tasks=[],
                baseline_value=historical_throughput,
                current_value=current_throughput,
                degradation_percent=degradation_percent * 100,
                detection_time=datetime.now(),
                first_occurrence=recent_metrics[0].timestamp,
                description=f"Throughput decreased by {degradation_percent:.1%} from historical average",
                root_cause_analysis={
                    'current_throughput': current_throughput,
                    'historical_throughput': historical_throughput,
                    'time_span_hours': time_span
                },
                mitigation_suggestions=[
                    "Analyze task scheduling efficiency",
                    "Check for resource bottlenecks",
                    "Review parallel execution effectiveness",
                    "Optimize task dependencies and ordering"
                ]
            ))
        
        return regressions
    
    def _detect_execution_time_anomalies(self, metrics: List[ExecutionMetrics]) -> List[AnomalyDetection]:
        """Detect execution time anomalies."""
        anomalies = []
        
        execution_times = [m.execution_time for m in metrics]
        if len(execution_times) < 10:
            return anomalies
        
        mean_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times)
        
        # Detect outliers (values beyond threshold standard deviations)
        threshold = self.thresholds['anomaly_threshold']
        
        for metric in metrics:
            deviation_score = abs(metric.execution_time - mean_time) / std_dev if std_dev > 0 else 0
            
            if deviation_score > threshold:
                anomaly_type = AnomalyType.SPIKE if metric.execution_time > mean_time else AnomalyType.DROP
                severity = self._determine_anomaly_severity(deviation_score)
                
                anomalies.append(AnomalyDetection(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    confidence=min(deviation_score / threshold, 1.0),
                    affected_metric='execution_time',
                    affected_tasks=[metric.task_id],
                    anomaly_value=metric.execution_time,
                    expected_value=mean_time,
                    deviation_score=deviation_score,
                    detection_time=datetime.now(),
                    duration=None,
                    description=f"Execution time {anomaly_type.value} detected: {metric.execution_time:.2f}s vs expected {mean_time:.2f}s",
                    context={
                        'task_id': metric.task_id,
                        'timestamp': metric.timestamp.isoformat(),
                        'deviation_std_devs': deviation_score
                    }
                ))
        
        return anomalies
    
    def _detect_resource_usage_anomalies(self, metrics: List[ExecutionMetrics]) -> List[AnomalyDetection]:
        """Detect resource usage anomalies."""
        anomalies = []
        
        # CPU usage anomalies
        cpu_values = [m.cpu_usage for m in metrics if m.cpu_usage > 0]
        if len(cpu_values) >= 10:
            mean_cpu = statistics.mean(cpu_values)
            std_dev_cpu = statistics.stdev(cpu_values)
            
            for metric in metrics:
                if metric.cpu_usage > 0:
                    deviation_score = abs(metric.cpu_usage - mean_cpu) / std_dev_cpu if std_dev_cpu > 0 else 0
                    
                    if deviation_score > self.thresholds['anomaly_threshold']:
                        anomaly_type = AnomalyType.SPIKE if metric.cpu_usage > mean_cpu else AnomalyType.DROP
                        severity = self._determine_anomaly_severity(deviation_score)
                        
                        anomalies.append(AnomalyDetection(
                            anomaly_type=anomaly_type,
                            severity=severity,
                            confidence=min(deviation_score / self.thresholds['anomaly_threshold'], 1.0),
                            affected_metric='cpu_usage',
                            affected_tasks=[metric.task_id],
                            anomaly_value=metric.cpu_usage,
                            expected_value=mean_cpu,
                            deviation_score=deviation_score,
                            detection_time=datetime.now(),
                            duration=None,
                            description=f"CPU usage {anomaly_type.value} detected: {metric.cpu_usage:.1%} vs expected {mean_cpu:.1%}",
                            context={'task_id': metric.task_id, 'timestamp': metric.timestamp.isoformat()}
                        ))
        
        # Memory usage anomalies
        memory_values = [m.memory_usage for m in metrics if m.memory_usage > 0]
        if len(memory_values) >= 10:
            mean_memory = statistics.mean(memory_values)
            std_dev_memory = statistics.stdev(memory_values)
            
            for metric in metrics:
                if metric.memory_usage > 0:
                    deviation_score = abs(metric.memory_usage - mean_memory) / std_dev_memory if std_dev_memory > 0 else 0
                    
                    if deviation_score > self.thresholds['anomaly_threshold']:
                        anomaly_type = AnomalyType.SPIKE if metric.memory_usage > mean_memory else AnomalyType.DROP
                        severity = self._determine_anomaly_severity(deviation_score)
                        
                        anomalies.append(AnomalyDetection(
                            anomaly_type=anomaly_type,
                            severity=severity,
                            confidence=min(deviation_score / self.thresholds['anomaly_threshold'], 1.0),
                            affected_metric='memory_usage',
                            affected_tasks=[metric.task_id],
                            anomaly_value=metric.memory_usage,
                            expected_value=mean_memory,
                            deviation_score=deviation_score,
                            detection_time=datetime.now(),
                            duration=None,
                            description=f"Memory usage {anomaly_type.value} detected: {metric.memory_usage:.1%} vs expected {mean_memory:.1%}",
                            context={'task_id': metric.task_id, 'timestamp': metric.timestamp.isoformat()}
                        ))
        
        return anomalies
    
    def _detect_cost_anomalies(self, metrics: List[ExecutionMetrics]) -> List[AnomalyDetection]:
        """Detect cost anomalies."""
        anomalies = []
        
        costs = [m.cost for m in metrics if m.cost > 0]
        if len(costs) < 10:
            return anomalies
        
        mean_cost = statistics.mean(costs)
        std_dev_cost = statistics.stdev(costs)
        
        for metric in metrics:
            if metric.cost > 0:
                deviation_score = abs(metric.cost - mean_cost) / std_dev_cost if std_dev_cost > 0 else 0
                
                if deviation_score > self.thresholds['anomaly_threshold']:
                    anomaly_type = AnomalyType.SPIKE if metric.cost > mean_cost else AnomalyType.DROP
                    severity = self._determine_anomaly_severity(deviation_score)
                    
                    anomalies.append(AnomalyDetection(
                        anomaly_type=anomaly_type,
                        severity=severity,
                        confidence=min(deviation_score / self.thresholds['anomaly_threshold'], 1.0),
                        affected_metric='cost',
                        affected_tasks=[metric.task_id],
                        anomaly_value=metric.cost,
                        expected_value=mean_cost,
                        deviation_score=deviation_score,
                        detection_time=datetime.now(),
                        duration=None,
                        description=f"Cost {anomaly_type.value} detected: ${metric.cost:.4f} vs expected ${mean_cost:.4f}",
                        context={
                            'task_id': metric.task_id,
                            'llm_provider': metric.llm_provider,
                            'timestamp': metric.timestamp.isoformat()
                        }
                    ))
        
        return anomalies
    
    def _detect_success_rate_anomalies(self, metrics: List[ExecutionMetrics]) -> List[AnomalyDetection]:
        """Detect success rate anomalies."""
        anomalies = []
        
        # Group metrics by time windows to detect success rate anomalies
        window_size = max(10, len(metrics) // 10)  # Adaptive window size
        
        for i in range(0, len(metrics) - window_size + 1, window_size // 2):
            window_metrics = metrics[i:i + window_size]
            success_rate = sum(1 for m in window_metrics if m.success) / len(window_metrics)
            
            # Compare with overall success rate
            overall_success_rate = sum(1 for m in metrics if m.success) / len(metrics)
            
            deviation = abs(success_rate - overall_success_rate)
            
            if deviation > 0.2:  # 20% deviation threshold
                anomaly_type = AnomalyType.DROP if success_rate < overall_success_rate else AnomalyType.SPIKE
                severity = self._determine_anomaly_severity(deviation * 5)  # Scale for severity
                
                failed_tasks = [m.task_id for m in window_metrics if not m.success]
                
                anomalies.append(AnomalyDetection(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    confidence=min(deviation * 3, 1.0),
                    affected_metric='success_rate',
                    affected_tasks=list(set(failed_tasks)),
                    anomaly_value=success_rate,
                    expected_value=overall_success_rate,
                    deviation_score=deviation,
                    detection_time=datetime.now(),
                    duration=window_metrics[-1].timestamp - window_metrics[0].timestamp,
                    description=f"Success rate {anomaly_type.value} detected: {success_rate:.1%} vs expected {overall_success_rate:.1%}",
                    context={
                        'window_start': window_metrics[0].timestamp.isoformat(),
                        'window_end': window_metrics[-1].timestamp.isoformat(),
                        'failed_tasks_count': len(failed_tasks)
                    }
                ))
        
        return anomalies
    
    def _predict_capacity_exhaustion(self, horizon_hours: int) -> List[PredictiveAlert]:
        """Predict capacity exhaustion based on trends."""
        alerts = []
        
        if len(self.execution_history) < 20:
            return alerts
        
        # Analyze resource usage trends
        recent_metrics = self.execution_history[-50:]  # Last 50 executions
        
        # CPU trend analysis
        cpu_values = [m.cpu_usage for m in recent_metrics if m.cpu_usage > 0]
        if len(cpu_values) >= 10:
            trend_slope = self._calculate_trend_slope(cpu_values)
            if trend_slope > 0.01:  # Increasing trend
                current_cpu = cpu_values[-1]
                predicted_cpu = current_cpu + (trend_slope * horizon_hours)
                
                if predicted_cpu > 0.9:  # 90% threshold
                    hours_to_exhaustion = (0.95 - current_cpu) / trend_slope
                    
                    alerts.append(PredictiveAlert(
                        alert_type='capacity_exhaustion',
                        severity=Severity.HIGH if hours_to_exhaustion < 24 else Severity.MEDIUM,
                        confidence=min(trend_slope * 50, 1.0),
                        predicted_occurrence_time=datetime.now() + timedelta(hours=hours_to_exhaustion),
                        affected_components=['cpu'],
                        prediction_basis=f"CPU usage trending upward at {trend_slope:.3f} per hour",
                        description=f"CPU capacity exhaustion predicted in {hours_to_exhaustion:.1f} hours",
                        preventive_actions=[
                            "Scale CPU resources proactively",
                            "Implement CPU throttling and limits",
                            "Optimize CPU-intensive tasks"
                        ],
                        monitoring_recommendations=[
                            "Monitor CPU usage every 15 minutes",
                            "Set up alerts at 85% CPU utilization",
                            "Track CPU usage trends hourly"
                        ]
                    ))
        
        return alerts
    
    def _predict_performance_degradation(self, horizon_hours: int) -> List[PredictiveAlert]:
        """Predict performance degradation based on trends."""
        alerts = []
        
        if len(self.execution_history) < 30:
            return alerts
        
        # Analyze execution time trends
        recent_metrics = self.execution_history[-30:]
        execution_times = [m.execution_time for m in recent_metrics]
        
        trend_slope = self._calculate_trend_slope(execution_times)
        
        if trend_slope > 0.1:  # Increasing execution time trend
            current_time = execution_times[-1]
            predicted_time = current_time + (trend_slope * horizon_hours)
            
            if 'execution_time' in self.baselines:
                baseline_time = self.baselines['execution_time'].baseline_value
                predicted_degradation = (predicted_time - baseline_time) / baseline_time
                
                if predicted_degradation > 0.3:  # 30% degradation
                    alerts.append(PredictiveAlert(
                        alert_type='performance_degradation',
                        severity=Severity.HIGH if predicted_degradation > 0.5 else Severity.MEDIUM,
                        confidence=min(trend_slope * 5, 1.0),
                        predicted_occurrence_time=datetime.now() + timedelta(hours=horizon_hours),
                        affected_components=['execution_time'],
                        prediction_basis=f"Execution time trending upward at {trend_slope:.3f}s per hour",
                        description=f"Performance degradation of {predicted_degradation:.1%} predicted",
                        preventive_actions=[
                            "Profile and optimize slow tasks",
                            "Review recent code changes",
                            "Check for resource contention"
                        ],
                        monitoring_recommendations=[
                            "Monitor execution times every 30 minutes",
                            "Set up performance regression alerts",
                            "Track task-level performance metrics"
                        ]
                    ))
        
        return alerts
    
    def _predict_failure_rate_increase(self, horizon_hours: int) -> List[PredictiveAlert]:
        """Predict failure rate increases."""
        alerts = []
        
        if len(self.execution_history) < 50:
            return alerts
        
        # Analyze failure rate trends over time windows
        window_size = 10
        failure_rates = []
        
        for i in range(len(self.execution_history) - window_size + 1):
            window = self.execution_history[i:i + window_size]
            failure_rate = 1 - (sum(1 for m in window if m.success) / len(window))
            failure_rates.append(failure_rate)
        
        if len(failure_rates) >= 5:
            trend_slope = self._calculate_trend_slope(failure_rates)
            
            if trend_slope > 0.01:  # Increasing failure rate
                current_failure_rate = failure_rates[-1]
                predicted_failure_rate = current_failure_rate + (trend_slope * horizon_hours / 24)
                
                if predicted_failure_rate > 0.2:  # 20% failure rate
                    alerts.append(PredictiveAlert(
                        alert_type='failure_rate_increase',
                        severity=Severity.HIGH if predicted_failure_rate > 0.4 else Severity.MEDIUM,
                        confidence=min(trend_slope * 100, 1.0),
                        predicted_occurrence_time=datetime.now() + timedelta(hours=horizon_hours),
                        affected_components=['reliability'],
                        prediction_basis=f"Failure rate trending upward at {trend_slope:.4f} per day",
                        description=f"Failure rate increase to {predicted_failure_rate:.1%} predicted",
                        preventive_actions=[
                            "Review and improve error handling",
                            "Implement better retry mechanisms",
                            "Investigate common failure patterns"
                        ],
                        monitoring_recommendations=[
                            "Monitor failure rates every hour",
                            "Set up failure pattern analysis",
                            "Track error types and frequencies"
                        ]
                    ))
        
        return alerts
    
    def _predict_cost_overruns(self, horizon_hours: int) -> List[PredictiveAlert]:
        """Predict cost overruns."""
        alerts = []
        
        costs = [m.cost for m in self.execution_history if m.cost > 0]
        if len(costs) < 20:
            return alerts
        
        recent_costs = costs[-20:]
        trend_slope = self._calculate_trend_slope(recent_costs)
        
        if trend_slope > 0.001:  # Increasing cost trend
            current_cost = recent_costs[-1]
            predicted_cost = current_cost + (trend_slope * horizon_hours)
            
            if 'cost' in self.baselines:
                baseline_cost = self.baselines['cost'].baseline_value
                cost_increase = (predicted_cost - baseline_cost) / baseline_cost
                
                if cost_increase > 0.5:  # 50% cost increase
                    alerts.append(PredictiveAlert(
                        alert_type='cost_overrun',
                        severity=Severity.HIGH if cost_increase > 1.0 else Severity.MEDIUM,
                        confidence=min(trend_slope * 1000, 1.0),
                        predicted_occurrence_time=datetime.now() + timedelta(hours=horizon_hours),
                        affected_components=['cost'],
                        prediction_basis=f"Cost trending upward at ${trend_slope:.6f} per hour",
                        description=f"Cost increase of {cost_increase:.1%} predicted",
                        preventive_actions=[
                            "Review LLM provider selection",
                            "Implement cost-aware scheduling",
                            "Optimize task complexity"
                        ],
                        monitoring_recommendations=[
                            "Monitor costs every hour",
                            "Set up budget alerts",
                            "Track cost per task trends"
                        ]
                    ))
        
        return alerts
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _determine_severity(self, degradation_percent: float) -> Severity:
        """Determine severity based on degradation percentage."""
        if degradation_percent > self.thresholds['critical_threshold']:
            return Severity.CRITICAL
        elif degradation_percent > 0.3:
            return Severity.HIGH
        elif degradation_percent > 0.2:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def _determine_anomaly_severity(self, deviation_score: float) -> Severity:
        """Determine anomaly severity based on deviation score."""
        if deviation_score > 4.0:
            return Severity.CRITICAL
        elif deviation_score > 3.0:
            return Severity.HIGH
        elif deviation_score > 2.5:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def _analyze_common_errors(self, metrics: List[ExecutionMetrics]) -> Dict[str, int]:
        """Analyze common error patterns."""
        error_counts = defaultdict(int)
        
        for metric in metrics:
            if not metric.success and metric.error_type:
                error_counts[metric.error_type] += 1
        
        return dict(error_counts)
    
    def _analyze_cost_patterns(self, metrics: List[ExecutionMetrics]) -> Dict[str, Any]:
        """Analyze cost patterns."""
        cost_by_provider = defaultdict(list)
        
        for metric in metrics:
            if metric.cost > 0 and metric.llm_provider:
                cost_by_provider[metric.llm_provider].append(metric.cost)
        
        analysis = {}
        for provider, costs in cost_by_provider.items():
            analysis[provider] = {
                'average_cost': statistics.mean(costs),
                'total_cost': sum(costs),
                'cost_variance': statistics.variance(costs) if len(costs) > 1 else 0
            }
        
        return analysis
    
    def _calculate_regression_score(self, regressions: List[RegressionDetection]) -> float:
        """Calculate regression score (0-100, higher is better)."""
        if not regressions:
            return 100.0
        
        # Weight regressions by severity
        severity_weights = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1
        }
        
        total_weight = sum(severity_weights[r.severity] for r in regressions)
        max_possible_weight = len(regressions) * severity_weights[Severity.CRITICAL]
        
        score = max(0, 100 - (total_weight / max_possible_weight * 100))
        return score
    
    def _calculate_anomaly_score(self, anomalies: List[AnomalyDetection]) -> float:
        """Calculate anomaly score (0-100, higher is better)."""
        if not anomalies:
            return 100.0
        
        # Weight anomalies by severity
        severity_weights = {
            Severity.CRITICAL: 4,
            Severity.HIGH: 3,
            Severity.MEDIUM: 2,
            Severity.LOW: 1
        }
        
        total_weight = sum(severity_weights[a.severity] for a in anomalies)
        max_possible_weight = len(anomalies) * severity_weights[Severity.CRITICAL]
        
        score = max(0, 100 - (total_weight / max_possible_weight * 100))
        return score
    
    def _calculate_trend_score(self) -> float:
        """Calculate trend score based on recent performance trends."""
        if len(self.execution_history) < 20:
            return 50.0  # Neutral score for insufficient data
        
        recent_metrics = self.execution_history[-20:]
        execution_times = [m.execution_time for m in recent_metrics]
        
        trend_slope = self._calculate_trend_slope(execution_times)
        
        # Negative slope (improving) = higher score
        # Positive slope (degrading) = lower score
        if trend_slope <= 0:
            return min(100, 80 + abs(trend_slope) * 100)
        else:
            return max(0, 80 - trend_slope * 100)
    
    def _calculate_stability_score(self) -> float:
        """Calculate stability score based on variance in performance."""
        if len(self.execution_history) < 10:
            return 50.0
        
        recent_metrics = self.execution_history[-20:]
        execution_times = [m.execution_time for m in recent_metrics]
        
        if len(execution_times) < 2:
            return 50.0
        
        mean_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times)
        
        # Lower coefficient of variation = higher stability score
        cv = std_dev / mean_time if mean_time > 0 else 1.0
        stability_score = max(0, 100 - cv * 100)
        
        return stability_score
    
    def _generate_health_recommendations(self, 
                                       overall_score: float,
                                       regressions: List[RegressionDetection],
                                       anomalies: List[AnomalyDetection]) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        if overall_score < 40:
            recommendations.append("CRITICAL: Immediate performance investigation required")
        elif overall_score < 60:
            recommendations.append("Performance issues detected - prioritize optimization")
        elif overall_score < 80:
            recommendations.append("Monitor performance trends closely")
        
        if regressions:
            recommendations.append(f"Address {len(regressions)} performance regressions")
            
        if anomalies:
            recommendations.append(f"Investigate {len(anomalies)} performance anomalies")
        
        # Add specific recommendations based on patterns
        critical_issues = [r for r in regressions if r.severity == Severity.CRITICAL]
        if critical_issues:
            recommendations.append("Focus on critical performance regressions first")
        
        return recommendations
    
    def export_regression_analysis_report(self, output_path: Path) -> None:
        """Export comprehensive regression analysis report."""
        with self.trace_operation("export_regression_analysis_report"):
            regressions = self.detect_performance_regressions()
            anomalies = self.detect_performance_anomalies()
            alerts = self.generate_predictive_alerts()
            health_score = self.get_performance_health_score()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'analysis_summary': {
                    'metrics_analyzed': len(self.execution_history),
                    'baselines_established': len(self.baselines),
                    'analysis_period_hours': self.baseline_window_hours
                },
                'health_score': health_score,
                'regressions': [asdict(r) for r in regressions],
                'anomalies': [asdict(a) for a in anomalies],
                'predictive_alerts': [asdict(alert) for alert in alerts],
                'baselines': {name: asdict(baseline) for name, baseline in self.baselines.items()},
                'summary': {
                    'total_regressions': len(regressions),
                    'total_anomalies': len(anomalies),
                    'total_alerts': len(alerts),
                    'critical_issues': len([r for r in regressions if r.severity == Severity.CRITICAL]) +
                                     len([a for a in anomalies if a.severity == Severity.CRITICAL]),
                    'overall_health_score': health_score.get('overall_score', 0)
                }
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(
                f"Exported regression analysis report to {output_path}",
                extra={'report_size': len(json.dumps(report))}
            )