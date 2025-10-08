"""WebSocket connection quality metrics collection and analysis."""

import asyncio
import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import time

from .health_validator import QualityMetrics, FailureIndicator

logger = logging.getLogger(__name__)


@dataclass
class MetricsSnapshot:
    """Snapshot of metrics at a specific time."""
    timestamp: datetime
    endpoint: str
    response_time_ms: float
    connection_time_ms: float
    message_latency_ms: float
    throughput_bytes_per_sec: float
    error_rate: float
    uptime_percentage: float
    active_connections: int = 0
    message_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'endpoint': self.endpoint,
            'response_time_ms': self.response_time_ms,
            'connection_time_ms': self.connection_time_ms,
            'message_latency_ms': self.message_latency_ms,
            'throughput_bytes_per_sec': self.throughput_bytes_per_sec,
            'error_rate': self.error_rate,
            'uptime_percentage': self.uptime_percentage,
            'active_connections': self.active_connections,
            'message_count': self.message_count,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received
        }


@dataclass
class MetricsAggregation:
    """Aggregated metrics over a time period."""
    endpoint: str
    period_start: datetime
    period_end: datetime
    sample_count: int
    
    # Response time statistics
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    
    # Connection time statistics
    avg_connection_time_ms: float
    min_connection_time_ms: float
    max_connection_time_ms: float
    
    # Message latency statistics
    avg_message_latency_ms: float
    min_message_latency_ms: float
    max_message_latency_ms: float
    
    # Throughput statistics
    avg_throughput_bytes_per_sec: float
    max_throughput_bytes_per_sec: float
    total_bytes_transferred: int
    
    # Reliability statistics
    avg_error_rate: float
    max_error_rate: float
    avg_uptime_percentage: float
    min_uptime_percentage: float
    
    # Connection statistics
    avg_active_connections: float
    max_active_connections: int
    total_connections: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'endpoint': self.endpoint,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'sample_count': self.sample_count,
            'response_time': {
                'avg_ms': self.avg_response_time_ms,
                'min_ms': self.min_response_time_ms,
                'max_ms': self.max_response_time_ms,
                'p95_ms': self.p95_response_time_ms,
                'p99_ms': self.p99_response_time_ms
            },
            'connection_time': {
                'avg_ms': self.avg_connection_time_ms,
                'min_ms': self.min_connection_time_ms,
                'max_ms': self.max_connection_time_ms
            },
            'message_latency': {
                'avg_ms': self.avg_message_latency_ms,
                'min_ms': self.min_message_latency_ms,
                'max_ms': self.max_message_latency_ms
            },
            'throughput': {
                'avg_bytes_per_sec': self.avg_throughput_bytes_per_sec,
                'max_bytes_per_sec': self.max_throughput_bytes_per_sec,
                'total_bytes': self.total_bytes_transferred
            },
            'reliability': {
                'avg_error_rate': self.avg_error_rate,
                'max_error_rate': self.max_error_rate,
                'avg_uptime_percentage': self.avg_uptime_percentage,
                'min_uptime_percentage': self.min_uptime_percentage
            },
            'connections': {
                'avg_active': self.avg_active_connections,
                'max_active': self.max_active_connections,
                'total': self.total_connections
            }
        }


@dataclass
class QualityThresholds:
    """Quality thresholds for metrics evaluation."""
    response_time_ms: float = 1000.0
    connection_time_ms: float = 5000.0
    message_latency_ms: float = 100.0
    throughput_bytes_per_sec: float = 1000.0
    error_rate: float = 0.05
    uptime_percentage: float = 95.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'response_time_ms': self.response_time_ms,
            'connection_time_ms': self.connection_time_ms,
            'message_latency_ms': self.message_latency_ms,
            'throughput_bytes_per_sec': self.throughput_bytes_per_sec,
            'error_rate': self.error_rate,
            'uptime_percentage': self.uptime_percentage
        }


class QualityMetricsCollector:
    """Collects and analyzes WebSocket connection quality metrics."""
    
    def __init__(self, max_history_size: int = 10000):
        self.max_history_size = max_history_size
        self._metrics_history: Dict[str, List[MetricsSnapshot]] = {}
        self._quality_thresholds = QualityThresholds()
        
        self._log_action("collector_initialized", {
            "max_history_size": self.max_history_size,
            "thresholds": self._quality_thresholds.to_dict()
        })
    
    async def collect_metrics(self, endpoint: str, quality_metrics: QualityMetrics, additional_data: Optional[Dict[str, Any]] = None) -> MetricsSnapshot:
        """Collect metrics snapshot for an endpoint."""
        additional_data = additional_data or {}
        
        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            endpoint=endpoint,
            response_time_ms=quality_metrics.response_time_ms,
            connection_time_ms=quality_metrics.connection_time_ms,
            message_latency_ms=quality_metrics.message_latency_ms,
            throughput_bytes_per_sec=quality_metrics.throughput_bytes_per_sec,
            error_rate=quality_metrics.error_rate,
            uptime_percentage=quality_metrics.uptime_percentage,
            active_connections=additional_data.get('active_connections', 0),
            message_count=additional_data.get('message_count', 0),
            bytes_sent=additional_data.get('bytes_sent', 0),
            bytes_received=additional_data.get('bytes_received', 0)
        )
        
        # Store in history
        if endpoint not in self._metrics_history:
            self._metrics_history[endpoint] = []
        
        self._metrics_history[endpoint].append(snapshot)
        
        # Maintain history size limit
        if len(self._metrics_history[endpoint]) > self.max_history_size:
            self._metrics_history[endpoint] = self._metrics_history[endpoint][-self.max_history_size:]
        
        self._log_action("metrics_collected", {
            "endpoint": endpoint,
            "response_time_ms": quality_metrics.response_time_ms,
            "connection_time_ms": quality_metrics.connection_time_ms,
            "message_latency_ms": quality_metrics.message_latency_ms,
            "throughput_bytes_per_sec": quality_metrics.throughput_bytes_per_sec,
            "error_rate": quality_metrics.error_rate,
            "uptime_percentage": quality_metrics.uptime_percentage
        })
        
        return snapshot
    
    async def get_metrics_history(self, endpoint: str, limit: Optional[int] = None) -> List[MetricsSnapshot]:
        """Get metrics history for an endpoint."""
        if endpoint not in self._metrics_history:
            return []
        
        history = self._metrics_history[endpoint]
        if limit:
            return history[-limit:]
        return history
    
    async def get_aggregated_metrics(
        self, 
        endpoint: str, 
        period_minutes: int = 60,
        end_time: Optional[datetime] = None
    ) -> Optional[MetricsAggregation]:
        """Get aggregated metrics for a time period."""
        if endpoint not in self._metrics_history:
            return None
        
        end_time = end_time or datetime.utcnow()
        start_time = end_time - timedelta(minutes=period_minutes)
        
        # Filter metrics within the time period
        period_metrics = [
            m for m in self._metrics_history[endpoint]
            if start_time <= m.timestamp <= end_time
        ]
        
        if not period_metrics:
            return None
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in period_metrics]
        connection_times = [m.connection_time_ms for m in period_metrics]
        message_latencies = [m.message_latency_ms for m in period_metrics]
        throughputs = [m.throughput_bytes_per_sec for m in period_metrics]
        error_rates = [m.error_rate for m in period_metrics]
        uptime_percentages = [m.uptime_percentage for m in period_metrics]
        active_connections = [m.active_connections for m in period_metrics]
        
        # Calculate percentiles for response time
        response_times_sorted = sorted(response_times)
        p95_response_time = self._percentile(response_times_sorted, 95)
        p99_response_time = self._percentile(response_times_sorted, 99)
        
        # Calculate total bytes transferred
        total_bytes = sum(m.bytes_sent + m.bytes_received for m in period_metrics)
        
        aggregation = MetricsAggregation(
            endpoint=endpoint,
            period_start=start_time,
            period_end=end_time,
            sample_count=len(period_metrics),
            
            # Response time statistics
            avg_response_time_ms=statistics.mean(response_times),
            min_response_time_ms=min(response_times),
            max_response_time_ms=max(response_times),
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            
            # Connection time statistics
            avg_connection_time_ms=statistics.mean(connection_times),
            min_connection_time_ms=min(connection_times),
            max_connection_time_ms=max(connection_times),
            
            # Message latency statistics
            avg_message_latency_ms=statistics.mean(message_latencies),
            min_message_latency_ms=min(message_latencies),
            max_message_latency_ms=max(message_latencies),
            
            # Throughput statistics
            avg_throughput_bytes_per_sec=statistics.mean(throughputs),
            max_throughput_bytes_per_sec=max(throughputs),
            total_bytes_transferred=total_bytes,
            
            # Reliability statistics
            avg_error_rate=statistics.mean(error_rates),
            max_error_rate=max(error_rates),
            avg_uptime_percentage=statistics.mean(uptime_percentages),
            min_uptime_percentage=min(uptime_percentages),
            
            # Connection statistics
            avg_active_connections=statistics.mean(active_connections),
            max_active_connections=max(active_connections),
            total_connections=sum(1 for m in period_metrics if m.active_connections > 0)
        )
        
        self._log_action("metrics_aggregated", {
            "endpoint": endpoint,
            "period_minutes": period_minutes,
            "sample_count": len(period_metrics),
            "avg_response_time_ms": aggregation.avg_response_time_ms,
            "avg_error_rate": aggregation.avg_error_rate,
            "avg_uptime_percentage": aggregation.avg_uptime_percentage
        })
        
        return aggregation
    
    async def evaluate_quality(self, endpoint: str, period_minutes: int = 60) -> Dict[str, Any]:
        """Evaluate endpoint quality based on metrics."""
        aggregation = await self.get_aggregated_metrics(endpoint, period_minutes)
        
        if not aggregation:
            return {
                "endpoint": endpoint,
                "quality_score": 0.0,
                "status": "insufficient_data",
                "issues": ["No metrics data available"],
                "recommendations": []
            }
        
        # Calculate quality score (0-1)
        quality_score = self._calculate_quality_score(aggregation)
        
        # Identify issues
        issues = self._identify_quality_issues(aggregation)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(aggregation, issues)
        
        # Determine overall status
        if quality_score >= 0.9:
            status = "excellent"
        elif quality_score >= 0.7:
            status = "good"
        elif quality_score >= 0.5:
            status = "fair"
        elif quality_score >= 0.3:
            status = "poor"
        else:
            status = "critical"
        
        evaluation = {
            "endpoint": endpoint,
            "quality_score": quality_score,
            "status": status,
            "period_minutes": period_minutes,
            "issues": issues,
            "recommendations": recommendations,
            "aggregated_metrics": aggregation.to_dict(),
            "thresholds": self._quality_thresholds.to_dict()
        }
        
        self._log_action("quality_evaluated", {
            "endpoint": endpoint,
            "quality_score": quality_score,
            "status": status,
            "issue_count": len(issues)
        })
        
        return evaluation
    
    async def detect_quality_degradation(self, endpoint: str, comparison_period_minutes: int = 60) -> List[Dict[str, Any]]:
        """Detect quality degradation by comparing current metrics with historical baseline."""
        if endpoint not in self._metrics_history or len(self._metrics_history[endpoint]) < 10:
            return []
        
        # Get current period metrics
        current_aggregation = await self.get_aggregated_metrics(endpoint, comparison_period_minutes)
        
        # Get baseline metrics (previous period of same length)
        baseline_end_time = datetime.utcnow() - timedelta(minutes=comparison_period_minutes)
        baseline_aggregation = await self.get_aggregated_metrics(
            endpoint, 
            comparison_period_minutes, 
            baseline_end_time
        )
        
        if not current_aggregation or not baseline_aggregation:
            return []
        
        degradations = []
        
        # Check response time degradation
        if current_aggregation.avg_response_time_ms > baseline_aggregation.avg_response_time_ms * 1.5:
            degradations.append({
                "metric": "response_time",
                "severity": "high",
                "current_value": current_aggregation.avg_response_time_ms,
                "baseline_value": baseline_aggregation.avg_response_time_ms,
                "degradation_percentage": ((current_aggregation.avg_response_time_ms - baseline_aggregation.avg_response_time_ms) / baseline_aggregation.avg_response_time_ms) * 100,
                "description": f"Response time increased by {((current_aggregation.avg_response_time_ms - baseline_aggregation.avg_response_time_ms) / baseline_aggregation.avg_response_time_ms) * 100:.1f}%"
            })
        
        # Check error rate degradation
        if current_aggregation.avg_error_rate > baseline_aggregation.avg_error_rate * 2:
            degradations.append({
                "metric": "error_rate",
                "severity": "critical",
                "current_value": current_aggregation.avg_error_rate,
                "baseline_value": baseline_aggregation.avg_error_rate,
                "degradation_percentage": ((current_aggregation.avg_error_rate - baseline_aggregation.avg_error_rate) / baseline_aggregation.avg_error_rate) * 100,
                "description": f"Error rate increased by {((current_aggregation.avg_error_rate - baseline_aggregation.avg_error_rate) / baseline_aggregation.avg_error_rate) * 100:.1f}%"
            })
        
        # Check uptime degradation
        if current_aggregation.avg_uptime_percentage < baseline_aggregation.avg_uptime_percentage - 5:
            degradations.append({
                "metric": "uptime",
                "severity": "medium",
                "current_value": current_aggregation.avg_uptime_percentage,
                "baseline_value": baseline_aggregation.avg_uptime_percentage,
                "degradation_percentage": ((baseline_aggregation.avg_uptime_percentage - current_aggregation.avg_uptime_percentage) / baseline_aggregation.avg_uptime_percentage) * 100,
                "description": f"Uptime decreased by {((baseline_aggregation.avg_uptime_percentage - current_aggregation.avg_uptime_percentage) / baseline_aggregation.avg_uptime_percentage) * 100:.1f}%"
            })
        
        # Check throughput degradation
        if current_aggregation.avg_throughput_bytes_per_sec < baseline_aggregation.avg_throughput_bytes_per_sec * 0.7:
            degradations.append({
                "metric": "throughput",
                "severity": "medium",
                "current_value": current_aggregation.avg_throughput_bytes_per_sec,
                "baseline_value": baseline_aggregation.avg_throughput_bytes_per_sec,
                "degradation_percentage": ((baseline_aggregation.avg_throughput_bytes_per_sec - current_aggregation.avg_throughput_bytes_per_sec) / baseline_aggregation.avg_throughput_bytes_per_sec) * 100,
                "description": f"Throughput decreased by {((baseline_aggregation.avg_throughput_bytes_per_sec - current_aggregation.avg_throughput_bytes_per_sec) / baseline_aggregation.avg_throughput_bytes_per_sec) * 100:.1f}%"
            })
        
        if degradations:
            self._log_action("quality_degradation_detected", {
                "endpoint": endpoint,
                "degradation_count": len(degradations),
                "metrics_affected": [d["metric"] for d in degradations]
            })
        
        return degradations
    
    def update_quality_thresholds(self, thresholds: QualityThresholds) -> None:
        """Update quality thresholds."""
        self._quality_thresholds = thresholds
        
        self._log_action("thresholds_updated", {
            "thresholds": thresholds.to_dict()
        })
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get metrics collection statistics."""
        total_metrics = sum(len(metrics) for metrics in self._metrics_history.values())
        endpoint_counts = {endpoint: len(metrics) for endpoint, metrics in self._metrics_history.items()}
        
        return {
            "total_metrics_collected": total_metrics,
            "endpoints_tracked": len(self._metrics_history),
            "metrics_per_endpoint": endpoint_counts,
            "max_history_size": self.max_history_size,
            "quality_thresholds": self._quality_thresholds.to_dict()
        }
    
    def _calculate_quality_score(self, aggregation: MetricsAggregation) -> float:
        """Calculate overall quality score (0-1)."""
        # Response time score (0-1, lower is better)
        response_score = max(0, 1 - (aggregation.avg_response_time_ms / self._quality_thresholds.response_time_ms))
        
        # Error rate score (0-1, lower is better)
        error_score = max(0, 1 - (aggregation.avg_error_rate / self._quality_thresholds.error_rate))
        
        # Uptime score (0-1, higher is better)
        uptime_score = min(1, aggregation.avg_uptime_percentage / 100)
        
        # Throughput score (0-1, higher is better)
        throughput_score = min(1, aggregation.avg_throughput_bytes_per_sec / self._quality_thresholds.throughput_bytes_per_sec)
        
        # Weighted average
        quality_score = (
            response_score * 0.3 +
            error_score * 0.3 +
            uptime_score * 0.3 +
            throughput_score * 0.1
        )
        
        return min(1.0, max(0.0, quality_score))
    
    def _identify_quality_issues(self, aggregation: MetricsAggregation) -> List[str]:
        """Identify quality issues based on thresholds."""
        issues = []
        
        if aggregation.avg_response_time_ms > self._quality_thresholds.response_time_ms:
            issues.append(f"High response time: {aggregation.avg_response_time_ms:.2f}ms (threshold: {self._quality_thresholds.response_time_ms}ms)")
        
        if aggregation.avg_connection_time_ms > self._quality_thresholds.connection_time_ms:
            issues.append(f"Slow connection time: {aggregation.avg_connection_time_ms:.2f}ms (threshold: {self._quality_thresholds.connection_time_ms}ms)")
        
        if aggregation.avg_message_latency_ms > self._quality_thresholds.message_latency_ms:
            issues.append(f"High message latency: {aggregation.avg_message_latency_ms:.2f}ms (threshold: {self._quality_thresholds.message_latency_ms}ms)")
        
        if aggregation.avg_error_rate > self._quality_thresholds.error_rate:
            issues.append(f"High error rate: {aggregation.avg_error_rate:.2%} (threshold: {self._quality_thresholds.error_rate:.2%})")
        
        if aggregation.avg_uptime_percentage < self._quality_thresholds.uptime_percentage:
            issues.append(f"Low uptime: {aggregation.avg_uptime_percentage:.1f}% (threshold: {self._quality_thresholds.uptime_percentage:.1f}%)")
        
        return issues
    
    def _generate_recommendations(self, aggregation: MetricsAggregation, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        
        if aggregation.avg_response_time_ms > self._quality_thresholds.response_time_ms:
            recommendations.append("Consider optimizing server response time or increasing server capacity")
        
        if aggregation.avg_connection_time_ms > self._quality_thresholds.connection_time_ms:
            recommendations.append("Check network connectivity and server load during connection establishment")
        
        if aggregation.avg_message_latency_ms > self._quality_thresholds.message_latency_ms:
            recommendations.append("Optimize message processing pipeline and reduce message queue backlog")
        
        if aggregation.avg_error_rate > self._quality_thresholds.error_rate:
            recommendations.append("Investigate error sources and implement better error handling")
        
        if aggregation.avg_uptime_percentage < self._quality_thresholds.uptime_percentage:
            recommendations.append("Implement redundancy and improve fault tolerance")
        
        if aggregation.max_active_connections > aggregation.avg_active_connections * 2:
            recommendations.append("Consider implementing connection pooling or rate limiting")
        
        return recommendations
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '2.3',
            'action': f'quality_metrics_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))