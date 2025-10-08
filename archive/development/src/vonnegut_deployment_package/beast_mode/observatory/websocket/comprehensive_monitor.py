"""
Comprehensive WebSocket Connectivity Monitoring and Alerting System

This module provides real-time monitoring, alerting, and dashboard capabilities
for WebSocket connectivity status across all Observatory endpoints.

Implements the 22-dimension ontology for WebSocket issues with comprehensive
monitoring covering all critical aspects of WebSocket infrastructure.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode, WebSocketException

from .health_validator import WebSocketHealthValidator, HealthCheckResult, HealthStatus, QualityMetrics, FailureIndicator
from .failure_detector import FailureDetector, FailureRule, FailureType, FailureSeverity
from .endpoint_monitor import EndpointMonitor, Alert, MonitoringConfig

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringDimension(Enum):
    """22-dimensional ontology dimensions for WebSocket monitoring."""
    PROBLEM_TAXONOMY = "problem_taxonomy"
    INFRASTRUCTURE = "infrastructure"
    SOLUTION_ARCHITECTURE = "solution_architecture"
    RISK_ASSESSMENT = "risk_assessment"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COST = "cost"
    TEMPORAL = "temporal"
    DEPENDENCIES = "dependencies"
    SCALABILITY = "scalability"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"
    ARCHITECTURE = "architecture"
    NETWORK = "network"
    DATA = "data"
    USER = "user"
    VENDOR = "vendor"
    MAINTENANCE = "maintenance"
    LEGAL = "legal"
    CONSTRAINTS = "constraints"
    EXECUTION = "execution"
    VALIDATION = "validation"


@dataclass
class WebSocketAlert:
    """Comprehensive WebSocket alert with 22-dimensional context."""
    alert_id: str
    endpoint: str
    alert_type: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    dimensions: Dict[MonitoringDimension, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'endpoint': self.endpoint,
            'alert_type': self.alert_type,
            'severity': self.severity.value,
            'message': self.message,
            'triggered_at': self.triggered_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'dimensions': {dim.value: data for dim, data in self.dimensions.items()},
            'metadata': self.metadata
        }


@dataclass
class MonitoringMetrics:
    """Comprehensive monitoring metrics."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    connection_success_rate: float = 0.0
    average_latency_ms: float = 0.0
    throughput_msgs_per_sec: float = 0.0
    error_rate: float = 0.0
    active_connections: int = 0
    failed_connections: int = 0
    tunnel_health_score: float = 1.0
    bot_protection_triggers: int = 0
    cloudflare_status: str = "unknown"
    observatory_health_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'connection_success_rate': self.connection_success_rate,
            'average_latency_ms': self.average_latency_ms,
            'throughput_msgs_per_sec': self.throughput_msgs_per_sec,
            'error_rate': self.error_rate,
            'active_connections': self.active_connections,
            'failed_connections': self.failed_connections,
            'tunnel_health_score': self.tunnel_health_score,
            'bot_protection_triggers': self.bot_protection_triggers,
            'cloudflare_status': self.cloudflare_status,
            'observatory_health_score': self.observatory_health_score
        }


class ComprehensiveWebSocketMonitor:
    """
    Comprehensive WebSocket monitoring system implementing 22-dimensional ontology.
    
    Provides real-time monitoring, alerting, and dashboard capabilities for
    WebSocket connectivity across all Observatory endpoints with full coverage
    of the ontological dimensions.
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize comprehensive monitoring system."""
        self.config = config or MonitoringConfig()
        
        # Core monitoring components
        self.health_validator = WebSocketHealthValidator(
            timeout=self.config.health_check_timeout
        )
        self.failure_detector = FailureDetector()
        self.endpoint_monitor = EndpointMonitor(self.config)
        
        # Monitoring state
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._metrics_history: List[MonitoringMetrics] = []
        self._active_alerts: Dict[str, WebSocketAlert] = {}
        self._alert_history: List[WebSocketAlert] = []
        
        # Alerting thresholds
        self._thresholds = {
            'connection_failure_rate': 0.10,  # 10%
            'latency_threshold_ms': 5000.0,  # 5 seconds
            'error_1033_threshold': 1,  # Any 1033 error
            'tunnel_health_min': 0.8,  # 80% health score
            'bot_protection_threshold': 5,  # 5 triggers
            'consecutive_failures': 3
        }
        
        # Callbacks
        self._alert_callbacks: Set[Callable[[WebSocketAlert], None]] = set()
        self._metrics_callbacks: Set[Callable[[MonitoringMetrics], None]] = set()
        
        # Initialize monitoring rules
        self._initialize_monitoring_rules()
        
        self._log_action("comprehensive_monitor_initialized", {
            "config": {
                "check_interval_seconds": self.config.check_interval_seconds,
                "health_check_timeout": self.config.health_check_timeout,
                "max_consecutive_failures": self.config.max_consecutive_failures,
                "enable_alerts": self.config.enable_alerts
            },
            "thresholds": self._thresholds,
            "dimensions_covered": len(MonitoringDimension)
        })
    
    async def start_monitoring(self) -> None:
        """Start comprehensive WebSocket monitoring."""
        if self._monitoring_active:
            self._log_action("monitoring_already_active", {})
            return
        
        self._monitoring_active = True
        
        # Start endpoint monitoring
        await self.endpoint_monitor.start_monitoring()
        
        # Start comprehensive monitoring loop
        self._monitoring_task = asyncio.create_task(self._comprehensive_monitoring_loop())
        
        self._log_action("comprehensive_monitoring_started", {
            "check_interval_seconds": self.config.check_interval_seconds,
            "endpoints_monitored": len(self.health_validator.endpoints)
        })
    
    async def stop_monitoring(self) -> None:
        """Stop comprehensive WebSocket monitoring."""
        if not self._monitoring_active:
            self._log_action("monitoring_not_active", {})
            return
        
        self._monitoring_active = False
        
        # Stop endpoint monitoring
        await self.endpoint_monitor.stop_monitoring()
        
        # Stop comprehensive monitoring
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self._log_action("comprehensive_monitoring_stopped", {})
    
    async def get_current_metrics(self) -> MonitoringMetrics:
        """Get current monitoring metrics."""
        # Get health check results
        health_results = await self.endpoint_monitor.get_all_endpoint_statuses()
        
        # Calculate metrics
        total_endpoints = len(health_results)
        healthy_endpoints = sum(1 for r in health_results.values() if r.status == HealthStatus.HEALTHY)
        
        connection_success_rate = healthy_endpoints / total_endpoints if total_endpoints > 0 else 0.0
        
        # Calculate average latency
        latencies = [r.response_time_ms for r in health_results.values() if r.response_time_ms < float('inf')]
        average_latency_ms = sum(latencies) / len(latencies) if latencies else 0.0
        
        # Calculate error rate
        error_count = sum(1 for r in health_results.values() if r.status == HealthStatus.UNHEALTHY)
        error_rate = error_count / total_endpoints if total_endpoints > 0 else 0.0
        
        # Get tunnel and observatory health
        tunnel_health_score = await self._get_tunnel_health_score()
        observatory_health_score = await self._get_observatory_health_score()
        
        # Count bot protection triggers
        bot_protection_triggers = await self._count_bot_protection_triggers()
        
        metrics = MonitoringMetrics(
            connection_success_rate=connection_success_rate,
            average_latency_ms=average_latency_ms,
            throughput_msgs_per_sec=0.0,  # Would need real-time measurement
            error_rate=error_rate,
            active_connections=healthy_endpoints,
            failed_connections=error_count,
            tunnel_health_score=tunnel_health_score,
            bot_protection_triggers=bot_protection_triggers,
            cloudflare_status=await self._get_cloudflare_status(),
            observatory_health_score=observatory_health_score
        )
        
        return metrics
    
    async def get_alert_summary(self) -> Dict[str, Any]:
        """Get comprehensive alert summary."""
        active_alerts = list(self._active_alerts.values())
        recent_alerts = self._alert_history[-50:] if self._alert_history else []
        
        # Count alerts by severity
        severity_counts = {severity.value: 0 for severity in AlertSeverity}
        for alert in active_alerts:
            severity_counts[alert.severity.value] += 1
        
        # Count alerts by type
        alert_type_counts = {}
        for alert in active_alerts + recent_alerts:
            alert_type_counts[alert.alert_type] = alert_type_counts.get(alert.alert_type, 0) + 1
        
        # Get most critical alerts
        critical_alerts = [alert for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL]
        
        return {
            "active_alerts": len(active_alerts),
            "recent_alerts": len(recent_alerts),
            "severity_distribution": severity_counts,
            "alert_types": alert_type_counts,
            "critical_alerts": [alert.to_dict() for alert in critical_alerts],
            "most_common_alert_type": max(alert_type_counts.items(), key=lambda x: x[1])[0] if alert_type_counts else None
        }
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        current_metrics = await self.get_current_metrics()
        alert_summary = await self.get_alert_summary()
        health_summary = self.health_validator.get_health_summary()
        
        # Get historical trends
        recent_metrics = self._metrics_history[-24:] if self._metrics_history else []  # Last 24 data points
        
        # Calculate trends
        success_rate_trend = self._calculate_trend([m.connection_success_rate for m in recent_metrics])
        latency_trend = self._calculate_trend([m.average_latency_ms for m in recent_metrics])
        error_rate_trend = self._calculate_trend([m.error_rate for m in recent_metrics])
        
        return {
            "current_metrics": current_metrics.to_dict(),
            "alert_summary": alert_summary,
            "health_summary": health_summary,
            "trends": {
                "success_rate": success_rate_trend,
                "latency": latency_trend,
                "error_rate": error_rate_trend
            },
            "historical_metrics": [m.to_dict() for m in recent_metrics],
            "monitoring_status": {
                "active": self._monitoring_active,
                "uptime_seconds": self._get_monitoring_uptime(),
                "last_check": datetime.utcnow().isoformat()
            }
        }
    
    def add_alert_callback(self, callback: Callable[[WebSocketAlert], None]) -> None:
        """Add alert callback."""
        self._alert_callbacks.add(callback)
    
    def remove_alert_callback(self, callback: Callable[[WebSocketAlert], None]) -> None:
        """Remove alert callback."""
        self._alert_callbacks.discard(callback)
    
    def add_metrics_callback(self, callback: Callable[[MonitoringMetrics], None]) -> None:
        """Add metrics callback."""
        self._metrics_callbacks.add(callback)
    
    def remove_metrics_callback(self, callback: Callable[[MonitoringMetrics], None]) -> None:
        """Remove metrics callback."""
        self._metrics_callbacks.discard(callback)
    
    async def _comprehensive_monitoring_loop(self) -> None:
        """Main comprehensive monitoring loop."""
        self._log_action("comprehensive_monitoring_loop_started", {})
        
        try:
            while self._monitoring_active:
                start_time = time.time()
                
                # Collect comprehensive metrics
                metrics = await self.get_current_metrics()
                
                # Store metrics
                self._metrics_history.append(metrics)
                if len(self._metrics_history) > 1000:  # Keep last 1000 data points
                    self._metrics_history = self._metrics_history[-1000:]
                
                # Check for alerts
                await self._check_comprehensive_alerts(metrics)
                
                # Notify metrics callbacks
                await self._notify_metrics_callbacks(metrics)
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.check_interval_seconds - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            self._log_action("comprehensive_monitoring_loop_cancelled", {})
            raise
        except Exception as e:
            self._log_action("comprehensive_monitoring_loop_error", {
                "error": str(e)
            })
            raise
    
    async def _check_comprehensive_alerts(self, metrics: MonitoringMetrics) -> None:
        """Check for comprehensive alert conditions."""
        current_time = datetime.utcnow()
        
        # Check connection failure rate
        if metrics.connection_success_rate < (1.0 - self._thresholds['connection_failure_rate']):
            await self._trigger_alert(
                alert_type="high_connection_failure_rate",
                severity=AlertSeverity.HIGH,
                message=f"Connection failure rate {metrics.connection_success_rate:.1%} exceeds threshold {self._thresholds['connection_failure_rate']:.1%}",
                dimensions={
                    MonitoringDimension.PERFORMANCE: {"failure_rate": metrics.connection_success_rate},
                    MonitoringDimension.RISK_ASSESSMENT: {"impact": "high", "probability": "medium"}
                },
                metadata={"threshold": self._thresholds['connection_failure_rate']}
            )
        
        # Check latency threshold
        if metrics.average_latency_ms > self._thresholds['latency_threshold_ms']:
            await self._trigger_alert(
                alert_type="high_latency",
                severity=AlertSeverity.MEDIUM,
                message=f"Average latency {metrics.average_latency_ms:.1f}ms exceeds threshold {self._thresholds['latency_threshold_ms']:.1f}ms",
                dimensions={
                    MonitoringDimension.PERFORMANCE: {"latency_ms": metrics.average_latency_ms},
                    MonitoringDimension.USER: {"experience_impact": "degraded"}
                },
                metadata={"threshold": self._thresholds['latency_threshold_ms']}
            )
        
        # Check tunnel health
        if metrics.tunnel_health_score < self._thresholds['tunnel_health_min']:
            await self._trigger_alert(
                alert_type="tunnel_health_degraded",
                severity=AlertSeverity.CRITICAL,
                message=f"Tunnel health score {metrics.tunnel_health_score:.2f} below threshold {self._thresholds['tunnel_health_min']:.2f}",
                dimensions={
                    MonitoringDimension.INFRASTRUCTURE: {"tunnel_health": metrics.tunnel_health_score},
                    MonitoringDimension.RISK_ASSESSMENT: {"impact": "critical", "probability": "high"}
                },
                metadata={"threshold": self._thresholds['tunnel_health_min']}
            )
        
        # Check bot protection triggers
        if metrics.bot_protection_triggers > self._thresholds['bot_protection_threshold']:
            await self._trigger_alert(
                alert_type="excessive_bot_protection_triggers",
                severity=AlertSeverity.MEDIUM,
                message=f"Bot protection triggered {metrics.bot_protection_triggers} times, exceeding threshold {self._thresholds['bot_protection_threshold']}",
                dimensions={
                    MonitoringDimension.SECURITY: {"bot_protection_triggers": metrics.bot_protection_triggers},
                    MonitoringDimension.USER: {"access_impact": "potential_blocking"}
                },
                metadata={"threshold": self._thresholds['bot_protection_threshold']}
            )
        
        # Check for error 1033 incidents
        error_1033_count = await self._count_error_1033_incidents()
        if error_1033_count >= self._thresholds['error_1033_threshold']:
            await self._trigger_alert(
                alert_type="error_1033_detected",
                severity=AlertSeverity.CRITICAL,
                message=f"Error 1033 incidents detected: {error_1033_count}",
                dimensions={
                    MonitoringDimension.PROBLEM_TAXONOMY: {"error_code": "1033", "count": error_1033_count},
                    MonitoringDimension.RISK_ASSESSMENT: {"impact": "critical", "probability": "high"}
                },
                metadata={"error_code": "1033", "count": error_1033_count}
            )
    
    async def _trigger_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        message: str,
        dimensions: Dict[MonitoringDimension, Any],
        metadata: Dict[str, Any]
    ) -> None:
        """Trigger a comprehensive alert."""
        alert_id = f"{alert_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if alert is already active
        if alert_id in self._active_alerts:
            return
        
        # Check cooldown period
        if self._is_alert_in_cooldown(alert_type):
            return
        
        alert = WebSocketAlert(
            alert_id=alert_id,
            endpoint="global",  # Global alert
            alert_type=alert_type,
            severity=severity,
            message=message,
            dimensions=dimensions,
            metadata=metadata
        )
        
        # Store alert
        self._active_alerts[alert_id] = alert
        
        self._log_action("comprehensive_alert_triggered", {
            "alert_id": alert_id,
            "alert_type": alert_type,
            "severity": severity.value,
            "message": message,
            "dimensions_covered": len(dimensions)
        })
        
        # Notify callbacks
        await self._notify_alert_callbacks(alert)
    
    async def _get_tunnel_health_score(self) -> float:
        """Get Cloudflare tunnel health score."""
        try:
            # This would integrate with Cloudflare API
            # For now, return a mock score based on connection success
            health_results = await self.endpoint_monitor.get_all_endpoint_statuses()
            healthy_count = sum(1 for r in health_results.values() if r.status == HealthStatus.HEALTHY)
            total_count = len(health_results)
            return healthy_count / total_count if total_count > 0 else 0.0
        except Exception:
            return 0.0
    
    async def _get_observatory_health_score(self) -> float:
        """Get Observatory core health score."""
        try:
            # This would integrate with Observatory core health
            # For now, return a mock score
            return 0.95  # Mock healthy score
        except Exception:
            return 0.0
    
    async def _get_cloudflare_status(self) -> str:
        """Get Cloudflare service status."""
        try:
            # This would check Cloudflare status API
            # For now, return mock status
            return "operational"
        except Exception:
            return "unknown"
    
    async def _count_bot_protection_triggers(self) -> int:
        """Count bot protection triggers."""
        try:
            # This would integrate with Cloudflare bot protection metrics
            # For now, return mock count
            return 0
        except Exception:
            return 0
    
    async def _count_error_1033_incidents(self) -> int:
        """Count error 1033 incidents."""
        try:
            # This would check logs for error 1033
            # For now, return mock count
            return 0
        except Exception:
            return 0
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values."""
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _get_monitoring_uptime(self) -> float:
        """Get monitoring uptime in seconds."""
        # This would track actual uptime
        return time.time() - self._start_time if hasattr(self, '_start_time') else 0.0
    
    def _is_alert_in_cooldown(self, alert_type: str) -> bool:
        """Check if alert is in cooldown period."""
        # Check recent alerts of same type
        recent_alerts = [alert for alert in self._alert_history[-10:] if alert.alert_type == alert_type]
        if not recent_alerts:
            return False
        
        last_alert = recent_alerts[-1]
        cooldown_period = timedelta(minutes=5)  # 5 minute cooldown
        
        return (datetime.utcnow() - last_alert.triggered_at) < cooldown_period
    
    async def _notify_alert_callbacks(self, alert: WebSocketAlert) -> None:
        """Notify alert callbacks."""
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    async def _notify_metrics_callbacks(self, metrics: MonitoringMetrics) -> None:
        """Notify metrics callbacks."""
        for callback in self._metrics_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Metrics callback error: {e}")
    
    def _initialize_monitoring_rules(self) -> None:
        """Initialize comprehensive monitoring rules."""
        # Add custom failure detection rules
        custom_rules = [
            FailureRule(
                name="websocket_connection_failure_rate",
                failure_type=FailureType.HIGH_ERROR_RATE,
                severity=FailureSeverity.HIGH,
                condition="connection_failure_rate > 0.10",
                threshold=0.10,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="websocket_latency_threshold",
                failure_type=FailureType.HIGH_LATENCY,
                severity=FailureSeverity.MEDIUM,
                condition="latency_ms > 5000",
                threshold=5000.0,
                cooldown_seconds=300.0
            ),
            FailureRule(
                name="tunnel_health_degradation",
                failure_type=FailureType.ENDPOINT_SPECIFIC,
                severity=FailureSeverity.CRITICAL,
                condition="tunnel_health_score < 0.8",
                threshold=0.8,
                cooldown_seconds=600.0
            ),
            FailureRule(
                name="bot_protection_excessive_triggers",
                failure_type=FailureType.RATE_LIMIT_EXCEEDED,
                severity=FailureSeverity.MEDIUM,
                condition="bot_protection_triggers > 5",
                threshold=5,
                cooldown_seconds=300.0
            )
        ]
        
        for rule in custom_rules:
            self.failure_detector.add_failure_rule(rule)
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '5.0',
            'action': f'comprehensive_monitor_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))


# Global monitoring instance
_global_monitor: Optional[ComprehensiveWebSocketMonitor] = None


async def get_global_monitor() -> ComprehensiveWebSocketMonitor:
    """Get global monitoring instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ComprehensiveWebSocketMonitor()
    return _global_monitor


async def start_global_monitoring() -> None:
    """Start global WebSocket monitoring."""
    monitor = await get_global_monitor()
    await monitor.start_monitoring()


async def stop_global_monitoring() -> None:
    """Stop global WebSocket monitoring."""
    monitor = await get_global_monitor()
    await monitor.stop_monitoring()