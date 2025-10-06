"""
WebSocket Health Monitor

Core health monitoring class that provides real-time visibility into WebSocket
connection health, performance metrics, and status tracking.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import json
import logging
from datetime import datetime

from .metrics_collector import MetricsCollector
from .connection_tracker import ConnectionTracker
from .performance_analyzer import PerformanceAnalyzer
from .alert_manager import AlertManager


class HealthStatus(Enum):
    """Health status levels for WebSocket connections"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ConnectionHealth:
    """Health information for a specific connection"""
    endpoint: str
    status: HealthStatus
    last_check: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    score: float = 0.0


class WebSocketHealthMonitor:
    """
    Comprehensive WebSocket health monitoring with minimal overhead.

    Tracks connection health, collects performance metrics, and provides
    real-time monitoring capabilities for all WebSocket endpoints.
    """

    def __init__(self):
        """Initialize the health monitor with all components"""
        self.metrics = {
            'websocket_connections_active': 0,
            'websocket_connection_failures': 0,
            'websocket_message_latency_ms': [],
            'websocket_throughput_msgs_per_sec': 0.0,
            'websocket_error_rate': 0.0
        }

        # Initialize components
        self.connection_tracker = ConnectionTracker()
        self.performance_analyzer = PerformanceAnalyzer()
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()

        # Health tracking
        self._connection_health: Dict[str, ConnectionHealth] = {}
        self._monitoring_active: Set[str] = set()

        # Performance thresholds
        self._thresholds = {
            'max_latency_ms': 1000,
            'min_throughput_msgs_per_sec': 1.0,
            'max_error_rate': 0.05,
            'connection_timeout_sec': 30
        }

        self.logger = logging.getLogger(__name__)

    async def monitor_connection(self, endpoint: str, websocket) -> None:
        """
        Monitor a WebSocket connection for health and performance.

        Args:
            endpoint: The WebSocket endpoint identifier
            websocket: The WebSocket connection object
        """
        start_time = time.time()

        try:
            # Log monitoring start
            self._log_action("monitor_connection_start", {
                "endpoint": endpoint,
                "timestamp": time.time()
            })

            # Track connection
            await self.connection_tracker.track_connection(endpoint, websocket)
            self._monitoring_active.add(endpoint)

            # Initialize health status
            self._connection_health[endpoint] = ConnectionHealth(
                endpoint=endpoint,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.now()
            )

            # Start continuous monitoring
            monitor_task = asyncio.create_task(
                self._continuous_monitor(endpoint, websocket)
            )

            # Update active connections metric
            self.metrics['websocket_connections_active'] = len(self._monitoring_active)

            self._log_action("monitor_connection_established", {
                "endpoint": endpoint,
                "setup_time_ms": (time.time() - start_time) * 1000
            })

        except Exception as e:
            self.metrics['websocket_connection_failures'] += 1
            self._log_action("monitor_connection_error", {
                "endpoint": endpoint,
                "error": str(e),
                "status": "error"
            })
            raise

    async def record_message_sent(self, endpoint: str, timestamp: float) -> None:
        """Record a message sent event for performance tracking"""
        await self.performance_analyzer.record_message_sent(endpoint, timestamp)
        await self.metrics_collector.increment_counter(f"messages_sent_{endpoint}")

        self._log_action("message_sent", {
            "endpoint": endpoint,
            "timestamp": timestamp
        })

    async def record_message_received(self, endpoint: str, timestamp: float) -> None:
        """Record a message received event for performance tracking"""
        await self.performance_analyzer.record_message_received(endpoint, timestamp)
        await self.metrics_collector.increment_counter(f"messages_received_{endpoint}")

        # Calculate latency if we have a paired sent message
        latency = await self.performance_analyzer.calculate_latency(endpoint, timestamp)
        if latency is not None:
            self.metrics['websocket_message_latency_ms'].append(latency)
            # Keep only recent latency measurements
            if len(self.metrics['websocket_message_latency_ms']) > 1000:
                self.metrics['websocket_message_latency_ms'] = \
                    self.metrics['websocket_message_latency_ms'][-500:]

        self._log_action("message_received", {
            "endpoint": endpoint,
            "timestamp": timestamp,
            "latency_ms": latency
        })

    def get_health_status(self, endpoint: str) -> HealthStatus:
        """
        Get the current health status for an endpoint.

        Args:
            endpoint: The WebSocket endpoint identifier

        Returns:
            HealthStatus: Current health status
        """
        if endpoint not in self._connection_health:
            return HealthStatus.UNKNOWN

        return self._connection_health[endpoint].status

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.

        Returns:
            Dict containing all performance metrics
        """
        # Calculate derived metrics
        latencies = self.metrics['websocket_message_latency_ms']

        performance_metrics = {
            **self.metrics,
            'connection_count': len(self._monitoring_active),
            'endpoints_monitored': list(self._monitoring_active),
            'latency_stats': self._calculate_latency_stats(latencies),
            'health_summary': self._get_health_summary()
        }

        return performance_metrics

    def get_connection_health(self, endpoint: str) -> Optional[ConnectionHealth]:
        """Get detailed health information for a specific connection"""
        return self._connection_health.get(endpoint)

    def get_all_health_status(self) -> Dict[str, ConnectionHealth]:
        """Get health status for all monitored connections"""
        return self._connection_health.copy()

    async def stop_monitoring(self, endpoint: str) -> None:
        """Stop monitoring a specific endpoint"""
        if endpoint in self._monitoring_active:
            self._monitoring_active.discard(endpoint)
            await self.connection_tracker.stop_tracking(endpoint)

            # Update metrics
            self.metrics['websocket_connections_active'] = len(self._monitoring_active)

            self._log_action("monitoring_stopped", {
                "endpoint": endpoint,
                "remaining_connections": len(self._monitoring_active)
            })

    async def _continuous_monitor(self, endpoint: str, websocket) -> None:
        """Continuous monitoring loop for a WebSocket connection"""
        while endpoint in self._monitoring_active:
            try:
                # Check connection health
                await self._check_connection_health(endpoint, websocket)

                # Update performance metrics
                await self._update_performance_metrics(endpoint)

                # Check for alerts
                await self._check_alerts(endpoint)

                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(1.0)  # 1 second monitoring interval

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring for {endpoint}: {e}")
                await asyncio.sleep(5.0)  # Back off on error

    async def _check_connection_health(self, endpoint: str, websocket) -> None:
        """Check and update connection health status"""
        if endpoint not in self._connection_health:
            return

        health = self._connection_health[endpoint]
        health.last_check = datetime.now()

        # Get current metrics for this endpoint
        connection_metrics = await self.connection_tracker.get_connection_metrics(endpoint)
        performance_metrics = await self.performance_analyzer.get_endpoint_metrics(endpoint)

        # Calculate health score and status
        score = self._calculate_health_score(connection_metrics, performance_metrics)
        status = self._determine_health_status(score, connection_metrics, performance_metrics)

        health.score = score
        health.status = status
        health.metrics = {**connection_metrics, **performance_metrics}
        health.issues = self._identify_issues(connection_metrics, performance_metrics)

        self._log_action("health_check", {
            "endpoint": endpoint,
            "status": status.value,
            "score": score,
            "issues": health.issues
        })

    async def _update_performance_metrics(self, endpoint: str) -> None:
        """Update overall performance metrics"""
        # Get throughput for this endpoint
        throughput = await self.performance_analyzer.get_throughput(endpoint)

        # Update overall throughput (simple average for now)
        if self._monitoring_active:
            total_throughput = 0
            for ep in self._monitoring_active:
                ep_throughput = await self.performance_analyzer.get_throughput(ep)
                total_throughput += ep_throughput

            self.metrics['websocket_throughput_msgs_per_sec'] = \
                total_throughput / len(self._monitoring_active)

    async def _check_alerts(self, endpoint: str) -> None:
        """Check if alerts should be triggered for an endpoint"""
        if endpoint not in self._connection_health:
            return

        health = self._connection_health[endpoint]

        # Check for critical status
        if health.status == HealthStatus.CRITICAL:
            await self.alert_manager.trigger_alert(
                endpoint, "critical_health", health.issues
            )

        # Check for performance issues
        if health.metrics.get('error_rate', 0) > self._thresholds['max_error_rate']:
            await self.alert_manager.trigger_alert(
                endpoint, "high_error_rate",
                [f"Error rate: {health.metrics['error_rate']:.2%}"]
            )

    def _calculate_health_score(self, connection_metrics: Dict, performance_metrics: Dict) -> float:
        """Calculate a health score from 0-100 based on metrics"""
        score = 100.0

        # Penalize high error rate
        error_rate = connection_metrics.get('error_rate', 0)
        score -= min(error_rate * 100, 50)  # Max 50 point penalty

        # Penalize high latency
        avg_latency = performance_metrics.get('avg_latency_ms', 0)
        if avg_latency > self._thresholds['max_latency_ms']:
            penalty = min((avg_latency / self._thresholds['max_latency_ms'] - 1) * 30, 30)
            score -= penalty

        # Penalize low throughput
        throughput = performance_metrics.get('throughput_msgs_per_sec', 0)
        if throughput < self._thresholds['min_throughput_msgs_per_sec']:
            score -= 20

        return max(0.0, score)

    def _determine_health_status(self, score: float, connection_metrics: Dict,
                               performance_metrics: Dict) -> HealthStatus:
        """Determine health status based on score and metrics"""
        if score >= 80:
            return HealthStatus.HEALTHY
        elif score >= 60:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.CRITICAL

    def _identify_issues(self, connection_metrics: Dict, performance_metrics: Dict) -> List[str]:
        """Identify specific issues based on metrics"""
        issues = []

        # Check error rate
        error_rate = connection_metrics.get('error_rate', 0)
        if error_rate > self._thresholds['max_error_rate']:
            issues.append(f"High error rate: {error_rate:.2%}")

        # Check latency
        avg_latency = performance_metrics.get('avg_latency_ms', 0)
        if avg_latency > self._thresholds['max_latency_ms']:
            issues.append(f"High latency: {avg_latency:.1f}ms")

        # Check throughput
        throughput = performance_metrics.get('throughput_msgs_per_sec', 0)
        if throughput < self._thresholds['min_throughput_msgs_per_sec']:
            issues.append(f"Low throughput: {throughput:.1f} msgs/sec")

        return issues

    def _calculate_latency_stats(self, latencies: List[float]) -> Dict[str, float]:
        """Calculate latency statistics"""
        if not latencies:
            return {
                'min': 0.0, 'max': 0.0, 'avg': 0.0,
                'p95': 0.0, 'p99': 0.0, 'count': 0
            }

        sorted_latencies = sorted(latencies)
        count = len(sorted_latencies)

        return {
            'min': sorted_latencies[0],
            'max': sorted_latencies[-1],
            'avg': sum(sorted_latencies) / count,
            'p95': sorted_latencies[int(count * 0.95)] if count > 0 else 0.0,
            'p99': sorted_latencies[int(count * 0.99)] if count > 0 else 0.0,
            'count': count
        }

    def _get_health_summary(self) -> Dict[str, int]:
        """Get summary of health status across all connections"""
        summary = {status.value: 0 for status in HealthStatus}

        for health in self._connection_health.values():
            summary[health.status.value] += 1

        return summary

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.1",
            "action": action,
            "status": "in_progress",
            "details": details
        }

        print(json.dumps(log_entry))