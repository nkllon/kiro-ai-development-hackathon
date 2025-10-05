"""
Resource Utilization Analyzer - Advanced resource analysis and capacity planning

This module provides comprehensive analysis of resource utilization patterns,
capacity planning, and resource optimization recommendations.
"""

import json
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

import psutil

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ResourceType(Enum):
    """Types of system resources."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    DISK_SPACE = "disk_space"


class UtilizationLevel(Enum):
    """Resource utilization levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ResourceSnapshot:
    """Snapshot of resource utilization at a point in time."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float
    disk_space_used_percent: float
    active_tasks: int
    concurrent_executions: int


@dataclass
class ResourceTrend:
    """Resource utilization trend analysis."""
    resource_type: ResourceType
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0.0 to 1.0
    current_level: UtilizationLevel
    predicted_level: UtilizationLevel
    time_to_threshold: Optional[timedelta]
    confidence: float


@dataclass
class CapacityPrediction:
    """Capacity planning prediction."""
    resource_type: ResourceType
    current_utilization: float
    predicted_peak: float
    time_to_peak: Optional[timedelta]
    capacity_exhaustion_time: Optional[timedelta]
    recommended_capacity: float
    confidence: float


@dataclass
class ResourceBottleneck:
    """Identified resource bottleneck."""
    resource_type: ResourceType
    severity: float  # 0.0 to 1.0
    duration: timedelta
    affected_tasks: List[str]
    impact_score: float
    root_cause: str
    mitigation_strategies: List[str]


@dataclass
class OptimizationRecommendation:
    """Resource optimization recommendation."""
    category: str
    priority: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    resource_impact: Dict[ResourceType, float]
    implementation_effort: str
    expected_savings: Dict[str, float]
    implementation_steps: List[str]


class ResourceUtilizationAnalyzer(ReflectiveModule):
    """
    Advanced resource utilization analyzer and capacity planner.
    
    Provides comprehensive analysis of system resource usage patterns,
    identifies bottlenecks, and generates capacity planning recommendations.
    """
    
    def __init__(self, monitoring_interval: int = 60, history_retention_hours: int = 168):
        super().__init__()
        self.monitoring_interval = monitoring_interval  # seconds
        self.history_retention_hours = history_retention_hours
        self.resource_history: List[ResourceSnapshot] = []
        self.bottleneck_history: List[ResourceBottleneck] = []
        
        # Utilization thresholds
        self.thresholds = {
            ResourceType.CPU: {'normal': 70, 'high': 85, 'critical': 95},
            ResourceType.MEMORY: {'normal': 75, 'high': 90, 'critical': 98},
            ResourceType.DISK_IO: {'normal': 50, 'high': 80, 'critical': 95},
            ResourceType.NETWORK_IO: {'normal': 60, 'high': 85, 'critical': 95},
            ResourceType.DISK_SPACE: {'normal': 80, 'high': 90, 'critical': 95}
        }
        
        # Trend analysis parameters
        self.trend_window_hours = 24
        self.prediction_horizon_hours = 72
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize monitoring
        self._last_network_io = psutil.net_io_counters()
        self._last_disk_io = psutil.disk_io_counters()
        self._last_snapshot_time = datetime.now()
    
    def capture_resource_snapshot(self, active_tasks: int = 0, 
                                concurrent_executions: int = 0) -> ResourceSnapshot:
        """Capture current resource utilization snapshot."""
        with self.trace_operation("capture_resource_snapshot"):
            now = datetime.now()
            
            # Get current resource usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Calculate I/O rates
            current_network_io = psutil.net_io_counters()
            current_disk_io = psutil.disk_io_counters()
            
            time_delta = (now - self._last_snapshot_time).total_seconds()
            
            if time_delta > 0:
                network_sent_rate = (current_network_io.bytes_sent - self._last_network_io.bytes_sent) / time_delta / (1024 * 1024)
                network_recv_rate = (current_network_io.bytes_recv - self._last_network_io.bytes_recv) / time_delta / (1024 * 1024)
                disk_read_rate = (current_disk_io.read_bytes - self._last_disk_io.read_bytes) / time_delta / (1024 * 1024)
                disk_write_rate = (current_disk_io.write_bytes - self._last_disk_io.write_bytes) / time_delta / (1024 * 1024)
            else:
                network_sent_rate = network_recv_rate = disk_read_rate = disk_write_rate = 0.0
            
            # Get disk usage
            disk_usage = psutil.disk_usage('/')
            
            snapshot = ResourceSnapshot(
                timestamp=now,
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_io_read_mb=disk_read_rate,
                disk_io_write_mb=disk_write_rate,
                network_io_sent_mb=network_sent_rate,
                network_io_recv_mb=network_recv_rate,
                disk_space_used_percent=(disk_usage.used / disk_usage.total) * 100,
                active_tasks=active_tasks,
                concurrent_executions=concurrent_executions
            )
            
            # Update tracking variables
            self._last_network_io = current_network_io
            self._last_disk_io = current_disk_io
            self._last_snapshot_time = now
            
            # Add to history
            self.resource_history.append(snapshot)
            self._cleanup_old_snapshots()
            
            self.logger.debug(
                "Captured resource snapshot",
                extra={
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'active_tasks': active_tasks,
                    'concurrent_executions': concurrent_executions
                }
            )
            
            return snapshot
    
    def analyze_resource_trends(self, hours_back: Optional[int] = None) -> List[ResourceTrend]:
        """
        Analyze resource utilization trends.
        
        Args:
            hours_back: Hours of history to analyze (None for default window)
            
        Returns:
            List of resource trend analyses
        """
        with self.trace_operation("analyze_resource_trends"):
            if not self.resource_history:
                return []
            
            hours_back = hours_back or self.trend_window_hours
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Filter snapshots by time window
            recent_snapshots = [
                s for s in self.resource_history 
                if s.timestamp >= cutoff_time
            ]
            
            if len(recent_snapshots) < 2:
                return []
            
            trends = []
            
            # Analyze each resource type
            trends.append(self._analyze_cpu_trend(recent_snapshots))
            trends.append(self._analyze_memory_trend(recent_snapshots))
            trends.append(self._analyze_disk_io_trend(recent_snapshots))
            trends.append(self._analyze_network_io_trend(recent_snapshots))
            trends.append(self._analyze_disk_space_trend(recent_snapshots))
            
            # Filter out None results
            trends = [t for t in trends if t is not None]
            
            self.logger.info(
                f"Analyzed resource trends for {len(recent_snapshots)} snapshots",
                extra={
                    'trends_found': len(trends),
                    'analysis_window_hours': hours_back
                }
            )
            
            return trends
    
    def predict_capacity_requirements(self, prediction_horizon_hours: Optional[int] = None) -> List[CapacityPrediction]:
        """
        Predict future capacity requirements.
        
        Args:
            prediction_horizon_hours: Hours to predict ahead
            
        Returns:
            List of capacity predictions for each resource type
        """
        with self.trace_operation("predict_capacity_requirements"):
            if not self.resource_history:
                return []
            
            horizon_hours = prediction_horizon_hours or self.prediction_horizon_hours
            
            predictions = []
            
            # Predict for each resource type
            predictions.append(self._predict_cpu_capacity(horizon_hours))
            predictions.append(self._predict_memory_capacity(horizon_hours))
            predictions.append(self._predict_disk_space_capacity(horizon_hours))
            
            # Filter out None results
            predictions = [p for p in predictions if p is not None]
            
            self.logger.info(
                f"Generated {len(predictions)} capacity predictions",
                extra={
                    'prediction_horizon_hours': horizon_hours,
                    'predictions_count': len(predictions)
                }
            )
            
            return predictions
    
    def identify_resource_bottlenecks(self, analysis_window_hours: int = 24) -> List[ResourceBottleneck]:
        """
        Identify resource bottlenecks in the specified time window.
        
        Args:
            analysis_window_hours: Hours of history to analyze
            
        Returns:
            List of identified resource bottlenecks
        """
        with self.trace_operation("identify_resource_bottlenecks"):
            if not self.resource_history:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=analysis_window_hours)
            recent_snapshots = [
                s for s in self.resource_history 
                if s.timestamp >= cutoff_time
            ]
            
            if not recent_snapshots:
                return []
            
            bottlenecks = []
            
            # Analyze each resource type for bottlenecks
            bottlenecks.extend(self._identify_cpu_bottlenecks(recent_snapshots))
            bottlenecks.extend(self._identify_memory_bottlenecks(recent_snapshots))
            bottlenecks.extend(self._identify_disk_io_bottlenecks(recent_snapshots))
            bottlenecks.extend(self._identify_network_io_bottlenecks(recent_snapshots))
            bottlenecks.extend(self._identify_disk_space_bottlenecks(recent_snapshots))
            
            # Sort by impact score
            bottlenecks.sort(key=lambda x: x.impact_score, reverse=True)
            
            # Store in history
            self.bottleneck_history.extend(bottlenecks)
            
            self.logger.info(
                f"Identified {len(bottlenecks)} resource bottlenecks",
                extra={
                    'bottlenecks_count': len(bottlenecks),
                    'analysis_window_hours': analysis_window_hours
                }
            )
            
            return bottlenecks
    
    def generate_optimization_recommendations(self, 
                                           bottlenecks: Optional[List[ResourceBottleneck]] = None,
                                           trends: Optional[List[ResourceTrend]] = None) -> List[OptimizationRecommendation]:
        """
        Generate resource optimization recommendations.
        
        Args:
            bottlenecks: Resource bottlenecks to address (None for latest)
            trends: Resource trends to consider (None for latest)
            
        Returns:
            List of optimization recommendations
        """
        with self.trace_operation("generate_optimization_recommendations"):
            if bottlenecks is None:
                bottlenecks = self.identify_resource_bottlenecks()
            
            if trends is None:
                trends = self.analyze_resource_trends()
            
            recommendations = []
            
            # Generate recommendations based on bottlenecks
            for bottleneck in bottlenecks:
                recommendations.extend(self._generate_bottleneck_recommendations(bottleneck))
            
            # Generate recommendations based on trends
            for trend in trends:
                recommendations.extend(self._generate_trend_recommendations(trend))
            
            # Deduplicate and prioritize
            recommendations = self._deduplicate_recommendations(recommendations)
            recommendations = self._prioritize_recommendations(recommendations)
            
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
    
    def get_current_resource_status(self) -> Dict[str, Any]:
        """Get current resource status and utilization levels."""
        with self.trace_operation("get_current_resource_status"):
            if not self.resource_history:
                return {}
            
            latest_snapshot = self.resource_history[-1]
            
            status = {
                'timestamp': latest_snapshot.timestamp.isoformat(),
                'cpu': {
                    'utilization_percent': latest_snapshot.cpu_percent,
                    'level': self._get_utilization_level(ResourceType.CPU, latest_snapshot.cpu_percent),
                    'threshold_status': self._get_threshold_status(ResourceType.CPU, latest_snapshot.cpu_percent)
                },
                'memory': {
                    'utilization_percent': latest_snapshot.memory_percent,
                    'level': self._get_utilization_level(ResourceType.MEMORY, latest_snapshot.memory_percent),
                    'threshold_status': self._get_threshold_status(ResourceType.MEMORY, latest_snapshot.memory_percent)
                },
                'disk_io': {
                    'read_mb_per_sec': latest_snapshot.disk_io_read_mb,
                    'write_mb_per_sec': latest_snapshot.disk_io_write_mb,
                    'total_mb_per_sec': latest_snapshot.disk_io_read_mb + latest_snapshot.disk_io_write_mb
                },
                'network_io': {
                    'sent_mb_per_sec': latest_snapshot.network_io_sent_mb,
                    'recv_mb_per_sec': latest_snapshot.network_io_recv_mb,
                    'total_mb_per_sec': latest_snapshot.network_io_sent_mb + latest_snapshot.network_io_recv_mb
                },
                'disk_space': {
                    'utilization_percent': latest_snapshot.disk_space_used_percent,
                    'level': self._get_utilization_level(ResourceType.DISK_SPACE, latest_snapshot.disk_space_used_percent),
                    'threshold_status': self._get_threshold_status(ResourceType.DISK_SPACE, latest_snapshot.disk_space_used_percent)
                },
                'workload': {
                    'active_tasks': latest_snapshot.active_tasks,
                    'concurrent_executions': latest_snapshot.concurrent_executions
                }
            }
            
            return status
    
    def _analyze_cpu_trend(self, snapshots: List[ResourceSnapshot]) -> Optional[ResourceTrend]:
        """Analyze CPU utilization trend."""
        cpu_values = [s.cpu_percent for s in snapshots]
        
        if len(cpu_values) < 2:
            return None
        
        # Calculate trend
        trend_direction, trend_strength = self._calculate_trend(cpu_values)
        current_level = self._get_utilization_level(ResourceType.CPU, cpu_values[-1])
        
        # Predict future level
        if trend_direction == "increasing" and trend_strength > 0.5:
            predicted_value = cpu_values[-1] + (trend_strength * 20)  # Rough prediction
            predicted_level = self._get_utilization_level(ResourceType.CPU, predicted_value)
        else:
            predicted_level = current_level
        
        # Calculate time to threshold
        time_to_threshold = None
        if trend_direction == "increasing" and trend_strength > 0.3:
            current_value = cpu_values[-1]
            threshold = self.thresholds[ResourceType.CPU]['high']
            if current_value < threshold:
                # Rough estimation
                rate_per_hour = trend_strength * 5  # Simplified rate calculation
                hours_to_threshold = (threshold - current_value) / rate_per_hour
                time_to_threshold = timedelta(hours=hours_to_threshold)
        
        return ResourceTrend(
            resource_type=ResourceType.CPU,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_level=current_level,
            predicted_level=predicted_level,
            time_to_threshold=time_to_threshold,
            confidence=min(trend_strength + 0.3, 1.0)
        )
    
    def _analyze_memory_trend(self, snapshots: List[ResourceSnapshot]) -> Optional[ResourceTrend]:
        """Analyze memory utilization trend."""
        memory_values = [s.memory_percent for s in snapshots]
        
        if len(memory_values) < 2:
            return None
        
        trend_direction, trend_strength = self._calculate_trend(memory_values)
        current_level = self._get_utilization_level(ResourceType.MEMORY, memory_values[-1])
        
        # Predict future level
        if trend_direction == "increasing" and trend_strength > 0.5:
            predicted_value = memory_values[-1] + (trend_strength * 15)
            predicted_level = self._get_utilization_level(ResourceType.MEMORY, predicted_value)
        else:
            predicted_level = current_level
        
        return ResourceTrend(
            resource_type=ResourceType.MEMORY,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_level=current_level,
            predicted_level=predicted_level,
            time_to_threshold=None,  # Simplified for now
            confidence=min(trend_strength + 0.2, 1.0)
        )
    
    def _analyze_disk_io_trend(self, snapshots: List[ResourceSnapshot]) -> Optional[ResourceTrend]:
        """Analyze disk I/O trend."""
        disk_io_values = [s.disk_io_read_mb + s.disk_io_write_mb for s in snapshots]
        
        if len(disk_io_values) < 2:
            return None
        
        trend_direction, trend_strength = self._calculate_trend(disk_io_values)
        
        # Convert to percentage for level calculation (simplified)
        max_observed = max(disk_io_values) if disk_io_values else 1
        current_percent = (disk_io_values[-1] / max_observed) * 100 if max_observed > 0 else 0
        current_level = self._get_utilization_level(ResourceType.DISK_IO, current_percent)
        
        return ResourceTrend(
            resource_type=ResourceType.DISK_IO,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_level=current_level,
            predicted_level=current_level,  # Simplified
            time_to_threshold=None,
            confidence=trend_strength
        )
    
    def _analyze_network_io_trend(self, snapshots: List[ResourceSnapshot]) -> Optional[ResourceTrend]:
        """Analyze network I/O trend."""
        network_io_values = [s.network_io_sent_mb + s.network_io_recv_mb for s in snapshots]
        
        if len(network_io_values) < 2:
            return None
        
        trend_direction, trend_strength = self._calculate_trend(network_io_values)
        
        # Convert to percentage for level calculation (simplified)
        max_observed = max(network_io_values) if network_io_values else 1
        current_percent = (network_io_values[-1] / max_observed) * 100 if max_observed > 0 else 0
        current_level = self._get_utilization_level(ResourceType.NETWORK_IO, current_percent)
        
        return ResourceTrend(
            resource_type=ResourceType.NETWORK_IO,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_level=current_level,
            predicted_level=current_level,  # Simplified
            time_to_threshold=None,
            confidence=trend_strength
        )
    
    def _analyze_disk_space_trend(self, snapshots: List[ResourceSnapshot]) -> Optional[ResourceTrend]:
        """Analyze disk space utilization trend."""
        disk_space_values = [s.disk_space_used_percent for s in snapshots]
        
        if len(disk_space_values) < 2:
            return None
        
        trend_direction, trend_strength = self._calculate_trend(disk_space_values)
        current_level = self._get_utilization_level(ResourceType.DISK_SPACE, disk_space_values[-1])
        
        # Predict future level
        if trend_direction == "increasing" and trend_strength > 0.3:
            predicted_value = disk_space_values[-1] + (trend_strength * 10)
            predicted_level = self._get_utilization_level(ResourceType.DISK_SPACE, predicted_value)
        else:
            predicted_level = current_level
        
        return ResourceTrend(
            resource_type=ResourceType.DISK_SPACE,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            current_level=current_level,
            predicted_level=predicted_level,
            time_to_threshold=None,  # Simplified for now
            confidence=min(trend_strength + 0.4, 1.0)
        )
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and strength from a series of values."""
        if len(values) < 2:
            return "stable", 0.0
        
        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        
        # Determine direction and strength
        if abs(slope) < 0.1:
            return "stable", abs(slope)
        elif slope > 0:
            return "increasing", min(abs(slope), 1.0)
        else:
            return "decreasing", min(abs(slope), 1.0)
    
    def _predict_cpu_capacity(self, horizon_hours: int) -> Optional[CapacityPrediction]:
        """Predict CPU capacity requirements."""
        if not self.resource_history:
            return None
        
        recent_snapshots = self.resource_history[-min(100, len(self.resource_history)):]
        cpu_values = [s.cpu_percent for s in recent_snapshots]
        
        current_utilization = cpu_values[-1]
        
        # Simple prediction based on trend
        trend_direction, trend_strength = self._calculate_trend(cpu_values)
        
        if trend_direction == "increasing":
            predicted_peak = current_utilization + (trend_strength * horizon_hours * 0.5)
        else:
            predicted_peak = current_utilization
        
        # Calculate capacity exhaustion time
        capacity_exhaustion_time = None
        if trend_direction == "increasing" and trend_strength > 0.2:
            threshold = self.thresholds[ResourceType.CPU]['critical']
            if current_utilization < threshold:
                rate_per_hour = trend_strength * 2
                hours_to_exhaustion = (threshold - current_utilization) / rate_per_hour
                capacity_exhaustion_time = timedelta(hours=hours_to_exhaustion)
        
        # Recommend capacity
        recommended_capacity = max(predicted_peak * 1.2, 100.0)  # 20% buffer
        
        return CapacityPrediction(
            resource_type=ResourceType.CPU,
            current_utilization=current_utilization,
            predicted_peak=predicted_peak,
            time_to_peak=timedelta(hours=horizon_hours) if predicted_peak > current_utilization else None,
            capacity_exhaustion_time=capacity_exhaustion_time,
            recommended_capacity=recommended_capacity,
            confidence=trend_strength
        )
    
    def _predict_memory_capacity(self, horizon_hours: int) -> Optional[CapacityPrediction]:
        """Predict memory capacity requirements."""
        if not self.resource_history:
            return None
        
        recent_snapshots = self.resource_history[-min(100, len(self.resource_history)):]
        memory_values = [s.memory_percent for s in recent_snapshots]
        
        current_utilization = memory_values[-1]
        
        # Simple prediction based on trend
        trend_direction, trend_strength = self._calculate_trend(memory_values)
        
        if trend_direction == "increasing":
            predicted_peak = current_utilization + (trend_strength * horizon_hours * 0.3)
        else:
            predicted_peak = current_utilization
        
        # Recommend capacity
        recommended_capacity = max(predicted_peak * 1.3, 100.0)  # 30% buffer for memory
        
        return CapacityPrediction(
            resource_type=ResourceType.MEMORY,
            current_utilization=current_utilization,
            predicted_peak=predicted_peak,
            time_to_peak=timedelta(hours=horizon_hours) if predicted_peak > current_utilization else None,
            capacity_exhaustion_time=None,  # Simplified
            recommended_capacity=recommended_capacity,
            confidence=trend_strength
        )
    
    def _predict_disk_space_capacity(self, horizon_hours: int) -> Optional[CapacityPrediction]:
        """Predict disk space capacity requirements."""
        if not self.resource_history:
            return None
        
        recent_snapshots = self.resource_history[-min(100, len(self.resource_history)):]
        disk_space_values = [s.disk_space_used_percent for s in recent_snapshots]
        
        current_utilization = disk_space_values[-1]
        
        # Simple prediction based on trend
        trend_direction, trend_strength = self._calculate_trend(disk_space_values)
        
        if trend_direction == "increasing":
            predicted_peak = current_utilization + (trend_strength * horizon_hours * 0.1)
        else:
            predicted_peak = current_utilization
        
        # Calculate capacity exhaustion time
        capacity_exhaustion_time = None
        if trend_direction == "increasing" and trend_strength > 0.1:
            threshold = self.thresholds[ResourceType.DISK_SPACE]['critical']
            if current_utilization < threshold:
                rate_per_hour = trend_strength * 0.5
                hours_to_exhaustion = (threshold - current_utilization) / rate_per_hour
                capacity_exhaustion_time = timedelta(hours=hours_to_exhaustion)
        
        # Recommend capacity
        recommended_capacity = max(predicted_peak * 1.1, 100.0)  # 10% buffer
        
        return CapacityPrediction(
            resource_type=ResourceType.DISK_SPACE,
            current_utilization=current_utilization,
            predicted_peak=predicted_peak,
            time_to_peak=timedelta(hours=horizon_hours) if predicted_peak > current_utilization else None,
            capacity_exhaustion_time=capacity_exhaustion_time,
            recommended_capacity=recommended_capacity,
            confidence=trend_strength + 0.2
        )
    
    def _identify_cpu_bottlenecks(self, snapshots: List[ResourceSnapshot]) -> List[ResourceBottleneck]:
        """Identify CPU bottlenecks."""
        bottlenecks = []
        
        high_cpu_periods = []
        current_period_start = None
        
        threshold = self.thresholds[ResourceType.CPU]['high']
        
        for snapshot in snapshots:
            if snapshot.cpu_percent > threshold:
                if current_period_start is None:
                    current_period_start = snapshot.timestamp
            else:
                if current_period_start is not None:
                    duration = snapshot.timestamp - current_period_start
                    if duration.total_seconds() > 300:  # At least 5 minutes
                        high_cpu_periods.append((current_period_start, snapshot.timestamp, duration))
                    current_period_start = None
        
        # Handle ongoing period
        if current_period_start is not None:
            duration = snapshots[-1].timestamp - current_period_start
            if duration.total_seconds() > 300:
                high_cpu_periods.append((current_period_start, snapshots[-1].timestamp, duration))
        
        for start_time, end_time, duration in high_cpu_periods:
            period_snapshots = [s for s in snapshots if start_time <= s.timestamp <= end_time]
            avg_cpu = statistics.mean(s.cpu_percent for s in period_snapshots)
            max_cpu = max(s.cpu_percent for s in period_snapshots)
            
            severity = min(max_cpu / 100.0, 1.0)
            impact_score = severity * duration.total_seconds() / 3600  # Impact in hours
            
            bottlenecks.append(ResourceBottleneck(
                resource_type=ResourceType.CPU,
                severity=severity,
                duration=duration,
                affected_tasks=[],  # Would need task correlation
                impact_score=impact_score,
                root_cause=f"CPU utilization exceeded {threshold}% for {duration}",
                mitigation_strategies=[
                    "Implement CPU-aware task scheduling",
                    "Optimize CPU-intensive tasks",
                    "Consider horizontal scaling",
                    "Add CPU resource limits"
                ]
            ))
        
        return bottlenecks
    
    def _identify_memory_bottlenecks(self, snapshots: List[ResourceSnapshot]) -> List[ResourceBottleneck]:
        """Identify memory bottlenecks."""
        bottlenecks = []
        
        threshold = self.thresholds[ResourceType.MEMORY]['high']
        high_memory_snapshots = [s for s in snapshots if s.memory_percent > threshold]
        
        if len(high_memory_snapshots) > len(snapshots) * 0.2:  # More than 20% of time
            duration = snapshots[-1].timestamp - snapshots[0].timestamp
            avg_memory = statistics.mean(s.memory_percent for s in high_memory_snapshots)
            severity = min(avg_memory / 100.0, 1.0)
            
            bottlenecks.append(ResourceBottleneck(
                resource_type=ResourceType.MEMORY,
                severity=severity,
                duration=duration,
                affected_tasks=[],
                impact_score=severity * len(high_memory_snapshots),
                root_cause=f"Memory utilization frequently exceeded {threshold}%",
                mitigation_strategies=[
                    "Implement memory-aware task scheduling",
                    "Add memory cleanup and garbage collection",
                    "Consider memory limits for tasks",
                    "Optimize memory-intensive operations"
                ]
            ))
        
        return bottlenecks
    
    def _identify_disk_io_bottlenecks(self, snapshots: List[ResourceSnapshot]) -> List[ResourceBottleneck]:
        """Identify disk I/O bottlenecks."""
        bottlenecks = []
        
        # Calculate high I/O periods
        io_values = [s.disk_io_read_mb + s.disk_io_write_mb for s in snapshots]
        if not io_values:
            return bottlenecks
        
        avg_io = statistics.mean(io_values)
        threshold = avg_io * 3  # 3x average as threshold
        
        high_io_count = sum(1 for io in io_values if io > threshold)
        
        if high_io_count > len(io_values) * 0.15:  # More than 15% of time
            duration = snapshots[-1].timestamp - snapshots[0].timestamp
            max_io = max(io_values)
            severity = min(max_io / (avg_io * 5), 1.0)
            
            bottlenecks.append(ResourceBottleneck(
                resource_type=ResourceType.DISK_IO,
                severity=severity,
                duration=duration,
                affected_tasks=[],
                impact_score=severity * high_io_count,
                root_cause=f"Disk I/O frequently exceeded {threshold:.1f} MB/s",
                mitigation_strategies=[
                    "Implement I/O-aware task scheduling",
                    "Add disk I/O throttling",
                    "Optimize file operations",
                    "Consider SSD upgrade or I/O caching"
                ]
            ))
        
        return bottlenecks
    
    def _identify_network_io_bottlenecks(self, snapshots: List[ResourceSnapshot]) -> List[ResourceBottleneck]:
        """Identify network I/O bottlenecks."""
        bottlenecks = []
        
        # Similar logic to disk I/O
        network_values = [s.network_io_sent_mb + s.network_io_recv_mb for s in snapshots]
        if not network_values:
            return bottlenecks
        
        avg_network = statistics.mean(network_values)
        threshold = avg_network * 4  # 4x average as threshold
        
        high_network_count = sum(1 for net in network_values if net > threshold)
        
        if high_network_count > len(network_values) * 0.1:  # More than 10% of time
            duration = snapshots[-1].timestamp - snapshots[0].timestamp
            max_network = max(network_values)
            severity = min(max_network / (avg_network * 6), 1.0)
            
            bottlenecks.append(ResourceBottleneck(
                resource_type=ResourceType.NETWORK_IO,
                severity=severity,
                duration=duration,
                affected_tasks=[],
                impact_score=severity * high_network_count,
                root_cause=f"Network I/O frequently exceeded {threshold:.1f} MB/s",
                mitigation_strategies=[
                    "Implement network-aware task scheduling",
                    "Add network bandwidth throttling",
                    "Optimize network operations",
                    "Consider network upgrade or load balancing"
                ]
            ))
        
        return bottlenecks
    
    def _identify_disk_space_bottlenecks(self, snapshots: List[ResourceSnapshot]) -> List[ResourceBottleneck]:
        """Identify disk space bottlenecks."""
        bottlenecks = []
        
        threshold = self.thresholds[ResourceType.DISK_SPACE]['high']
        high_space_snapshots = [s for s in snapshots if s.disk_space_used_percent > threshold]
        
        if high_space_snapshots:
            duration = snapshots[-1].timestamp - snapshots[0].timestamp
            avg_space = statistics.mean(s.disk_space_used_percent for s in high_space_snapshots)
            severity = min(avg_space / 100.0, 1.0)
            
            bottlenecks.append(ResourceBottleneck(
                resource_type=ResourceType.DISK_SPACE,
                severity=severity,
                duration=duration,
                affected_tasks=[],
                impact_score=severity * len(high_space_snapshots),
                root_cause=f"Disk space utilization exceeded {threshold}%",
                mitigation_strategies=[
                    "Implement disk cleanup procedures",
                    "Add log rotation and archiving",
                    "Monitor and limit temporary file usage",
                    "Consider disk expansion or cleanup automation"
                ]
            ))
        
        return bottlenecks
    
    def _generate_bottleneck_recommendations(self, bottleneck: ResourceBottleneck) -> List[OptimizationRecommendation]:
        """Generate recommendations for a specific bottleneck."""
        recommendations = []
        
        priority = "HIGH" if bottleneck.severity > 0.8 else "MEDIUM" if bottleneck.severity > 0.5 else "LOW"
        
        for strategy in bottleneck.mitigation_strategies:
            recommendations.append(OptimizationRecommendation(
                category=f"{bottleneck.resource_type.value.title()} Optimization",
                priority=priority,
                title=f"Address {bottleneck.resource_type.value} bottleneck",
                description=f"{strategy} - {bottleneck.root_cause}",
                resource_impact={bottleneck.resource_type: bottleneck.severity * -50},  # Negative = improvement
                implementation_effort="MEDIUM",
                expected_savings={
                    'performance_improvement': bottleneck.impact_score * 20,
                    'resource_efficiency': bottleneck.severity * 30
                },
                implementation_steps=[
                    f"Analyze {bottleneck.resource_type.value} usage patterns",
                    f"Implement {strategy.lower()}",
                    f"Monitor {bottleneck.resource_type.value} utilization",
                    "Validate improvement effectiveness"
                ]
            ))
        
        return recommendations
    
    def _generate_trend_recommendations(self, trend: ResourceTrend) -> List[OptimizationRecommendation]:
        """Generate recommendations based on resource trends."""
        recommendations = []
        
        if (trend.trend_direction == "increasing" and 
            trend.trend_strength > 0.5 and 
            trend.current_level in [UtilizationLevel.HIGH, UtilizationLevel.CRITICAL]):
            
            priority = "HIGH" if trend.current_level == UtilizationLevel.CRITICAL else "MEDIUM"
            
            recommendations.append(OptimizationRecommendation(
                category=f"{trend.resource_type.value.title()} Capacity Planning",
                priority=priority,
                title=f"Address increasing {trend.resource_type.value} trend",
                description=f"{trend.resource_type.value.title()} utilization is trending upward with {trend.trend_strength:.1%} strength",
                resource_impact={trend.resource_type: trend.trend_strength * -30},
                implementation_effort="HIGH",
                expected_savings={
                    'capacity_planning': trend.trend_strength * 40,
                    'proactive_scaling': 25
                },
                implementation_steps=[
                    f"Monitor {trend.resource_type.value} trend closely",
                    f"Plan capacity expansion for {trend.resource_type.value}",
                    "Implement proactive scaling policies",
                    "Set up alerting for threshold breaches"
                ]
            ))
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Remove duplicate recommendations."""
        seen = set()
        unique_recommendations = []
        
        for rec in recommendations:
            key = (rec.category, rec.title)
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def _prioritize_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Sort recommendations by priority and expected benefit."""
        priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        
        def sort_key(rec):
            priority_score = priority_order.get(rec.priority, 0)
            benefit_score = sum(rec.expected_savings.values())
            return (priority_score, benefit_score)
        
        return sorted(recommendations, key=sort_key, reverse=True)
    
    def _get_utilization_level(self, resource_type: ResourceType, value: float) -> UtilizationLevel:
        """Get utilization level for a resource value."""
        thresholds = self.thresholds.get(resource_type, {})
        
        if value >= thresholds.get('critical', 95):
            return UtilizationLevel.CRITICAL
        elif value >= thresholds.get('high', 85):
            return UtilizationLevel.HIGH
        elif value >= thresholds.get('normal', 70):
            return UtilizationLevel.NORMAL
        else:
            return UtilizationLevel.LOW
    
    def _get_threshold_status(self, resource_type: ResourceType, value: float) -> Dict[str, Any]:
        """Get threshold status for a resource value."""
        thresholds = self.thresholds.get(resource_type, {})
        
        return {
            'normal_threshold': thresholds.get('normal', 70),
            'high_threshold': thresholds.get('high', 85),
            'critical_threshold': thresholds.get('critical', 95),
            'exceeds_normal': value >= thresholds.get('normal', 70),
            'exceeds_high': value >= thresholds.get('high', 85),
            'exceeds_critical': value >= thresholds.get('critical', 95)
        }
    
    def _cleanup_old_snapshots(self) -> None:
        """Remove snapshots older than retention period."""
        cutoff_time = datetime.now() - timedelta(hours=self.history_retention_hours)
        self.resource_history = [
            s for s in self.resource_history 
            if s.timestamp >= cutoff_time
        ]
    
    def export_resource_analysis_report(self, output_path: Path) -> None:
        """Export comprehensive resource analysis report."""
        with self.trace_operation("export_resource_analysis_report"):
            trends = self.analyze_resource_trends()
            predictions = self.predict_capacity_requirements()
            bottlenecks = self.identify_resource_bottlenecks()
            recommendations = self.generate_optimization_recommendations(bottlenecks, trends)
            current_status = self.get_current_resource_status()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'analysis_period': {
                    'snapshots_analyzed': len(self.resource_history),
                    'oldest_snapshot': self.resource_history[0].timestamp.isoformat() if self.resource_history else None,
                    'newest_snapshot': self.resource_history[-1].timestamp.isoformat() if self.resource_history else None
                },
                'current_status': current_status,
                'trends': [asdict(trend) for trend in trends],
                'capacity_predictions': [asdict(pred) for pred in predictions],
                'bottlenecks': [asdict(bottleneck) for bottleneck in bottlenecks],
                'recommendations': [asdict(rec) for rec in recommendations],
                'summary': {
                    'trends_identified': len(trends),
                    'capacity_predictions': len(predictions),
                    'bottlenecks_found': len(bottlenecks),
                    'recommendations_generated': len(recommendations),
                    'high_priority_recommendations': len([r for r in recommendations if r.priority == 'HIGH']),
                    'critical_resources': len([t for t in trends if t.current_level == UtilizationLevel.CRITICAL])
                }
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(
                f"Exported resource analysis report to {output_path}",
                extra={'report_size': len(json.dumps(report))}
            )