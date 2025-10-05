"""Real-time WebSocket endpoint monitoring system."""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
import time

from .health_validator import WebSocketHealthValidator, HealthCheckResult, HealthStatus, QualityMetrics, FailureIndicator

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for endpoint monitoring."""
    check_interval_seconds: float = 30.0
    health_check_timeout: float = 5.0
    max_consecutive_failures: int = 3
    alert_cooldown_seconds: float = 300.0  # 5 minutes
    enable_quality_metrics: bool = True
    enable_failure_detection: bool = True
    enable_alerts: bool = True


@dataclass
class Alert:
    """WebSocket endpoint alert."""
    endpoint: str
    alert_type: str
    severity: str
    message: str
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'endpoint': self.endpoint,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'triggered_at': self.triggered_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.metadata
        }


class EndpointMonitor:
    """Real-time WebSocket endpoint monitoring system."""
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.health_validator = WebSocketHealthValidator(
            timeout=self.config.health_check_timeout
        )
        
        # Monitoring state
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._last_health_checks: Dict[str, HealthCheckResult] = {}
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._quality_metrics_history: Dict[str, List[QualityMetrics]] = {}
        self._failure_history: Dict[str, List[FailureIndicator]] = {}
        
        # Callbacks
        self._health_callbacks: Set[Callable[[str, HealthCheckResult], None]] = set()
        self._alert_callbacks: Set[Callable[[Alert], None]] = set()
        self._quality_callbacks: Set[Callable[[str, QualityMetrics], None]] = set()
        
        self._log_action("monitor_initialized", {
            "config": {
                "check_interval_seconds": self.config.check_interval_seconds,
                "health_check_timeout": self.config.health_check_timeout,
                "max_consecutive_failures": self.config.max_consecutive_failures,
                "enable_quality_metrics": self.config.enable_quality_metrics,
                "enable_failure_detection": self.config.enable_failure_detection,
                "enable_alerts": self.config.enable_alerts
            }
        })
    
    async def start_monitoring(self) -> None:
        """Start real-time endpoint monitoring."""
        if self._monitoring_active:
            self._log_action("monitoring_already_active", {})
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self._log_action("monitoring_started", {
            "check_interval_seconds": self.config.check_interval_seconds
        })
    
    async def stop_monitoring(self) -> None:
        """Stop real-time endpoint monitoring."""
        if not self._monitoring_active:
            self._log_action("monitoring_not_active", {})
            return
        
        self._monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self._log_action("monitoring_stopped", {})
    
    async def get_endpoint_status(self, endpoint: str) -> Optional[HealthCheckResult]:
        """Get current status of a specific endpoint."""
        return self._last_health_checks.get(endpoint)
    
    async def get_all_endpoint_statuses(self) -> Dict[str, HealthCheckResult]:
        """Get current status of all endpoints."""
        return self._last_health_checks.copy()
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get currently active alerts."""
        return list(self._active_alerts.values())
    
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self._alert_history[-limit:] if self._alert_history else []
    
    async def get_quality_metrics_history(self, endpoint: str, limit: int = 50) -> List[QualityMetrics]:
        """Get quality metrics history for an endpoint."""
        if endpoint not in self._quality_metrics_history:
            return []
        return self._quality_metrics_history[endpoint][-limit:] if self._quality_metrics_history[endpoint] else []
    
    async def get_failure_history(self, endpoint: str, limit: int = 50) -> List[FailureIndicator]:
        """Get failure history for an endpoint."""
        if endpoint not in self._failure_history:
            return []
        return self._failure_history[endpoint][-limit:] if self._failure_history[endpoint] else []
    
    async def resolve_alert(self, endpoint: str, alert_type: str) -> bool:
        """Manually resolve an alert."""
        alert_key = f"{endpoint}:{alert_type}"
        
        if alert_key in self._active_alerts:
            alert = self._active_alerts[alert_key]
            alert.resolved_at = datetime.utcnow()
            
            # Move to history
            self._alert_history.append(alert)
            del self._active_alerts[alert_key]
            
            self._log_action("alert_resolved", {
                "endpoint": endpoint,
                "alert_type": alert_type,
                "duration_seconds": (alert.resolved_at - alert.triggered_at).total_seconds()
            })
            
            return True
        
        return False
    
    def add_health_callback(self, callback: Callable[[str, HealthCheckResult], None]) -> None:
        """Add callback for health check results."""
        self._health_callbacks.add(callback)
    
    def remove_health_callback(self, callback: Callable[[str, HealthCheckResult], None]) -> None:
        """Remove health check callback."""
        self._health_callbacks.discard(callback)
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add callback for alerts."""
        self._alert_callbacks.add(callback)
    
    def remove_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Remove alert callback."""
        self._alert_callbacks.discard(callback)
    
    def add_quality_callback(self, callback: Callable[[str, QualityMetrics], None]) -> None:
        """Add callback for quality metrics."""
        self._quality_callbacks.add(callback)
    
    def remove_quality_callback(self, callback: Callable[[str, QualityMetrics], None]) -> None:
        """Remove quality callback."""
        self._quality_callbacks.discard(callback)
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        self._log_action("monitoring_loop_started", {})
        
        try:
            while self._monitoring_active:
                start_time = time.time()
                
                # Perform health checks for all endpoints
                await self._perform_health_checks()
                
                # Calculate sleep time to maintain consistent interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.check_interval_seconds - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            self._log_action("monitoring_loop_cancelled", {})
            raise
        except Exception as e:
            self._log_action("monitoring_loop_error", {
                "error": str(e)
            })
            raise
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks for all endpoints."""
        self._log_action("health_checks_started", {
            "endpoint_count": len(self.health_validator.endpoints)
        })
        
        # Get health check results for all endpoints
        health_results = await self.health_validator.validate_all_endpoints()
        
        for endpoint, result in health_results.items():
            # Update last health check
            self._last_health_checks[endpoint] = result
            
            # Store quality metrics if available
            if result.quality_metrics and self.config.enable_quality_metrics:
                await self._store_quality_metrics(endpoint, result.quality_metrics)
            
            # Store failures if available
            if result.failure_indicators and self.config.enable_failure_detection:
                await self._store_failures(endpoint, result.failure_indicators)
            
            # Check for alerts
            if self.config.enable_alerts:
                await self._check_and_trigger_alerts(endpoint, result)
            
            # Notify callbacks
            await self._notify_health_callbacks(endpoint, result)
        
        self._log_action("health_checks_completed", {
            "healthy_endpoints": sum(1 for r in health_results.values() if r.status == HealthStatus.HEALTHY),
            "degraded_endpoints": sum(1 for r in health_results.values() if r.status == HealthStatus.DEGRADED),
            "unhealthy_endpoints": sum(1 for r in health_results.values() if r.status == HealthStatus.UNHEALTHY)
        })
    
    async def _store_quality_metrics(self, endpoint: str, metrics: QualityMetrics) -> None:
        """Store quality metrics in history."""
        if endpoint not in self._quality_metrics_history:
            self._quality_metrics_history[endpoint] = []
        
        self._quality_metrics_history[endpoint].append(metrics)
        
        # Keep only last 1000 metrics
        if len(self._quality_metrics_history[endpoint]) > 1000:
            self._quality_metrics_history[endpoint] = self._quality_metrics_history[endpoint][-1000:]
        
        # Notify quality callbacks
        await self._notify_quality_callbacks(endpoint, metrics)
    
    async def _store_failures(self, endpoint: str, failures: List[FailureIndicator]) -> None:
        """Store failures in history."""
        if endpoint not in self._failure_history:
            self._failure_history[endpoint] = []
        
        self._failure_history[endpoint].extend(failures)
        
        # Keep only last 500 failures
        if len(self._failure_history[endpoint]) > 500:
            self._failure_history[endpoint] = self._failure_history[endpoint][-500:]
    
    async def _check_and_trigger_alerts(self, endpoint: str, result: HealthCheckResult) -> None:
        """Check for conditions that should trigger alerts."""
        current_time = datetime.utcnow()
        
        # Check for unhealthy status
        if result.status == HealthStatus.UNHEALTHY:
            await self._trigger_alert_if_needed(
                endpoint=endpoint,
                alert_type="endpoint_unhealthy",
                severity="critical",
                message=f"Endpoint {endpoint} is unhealthy: {result.error_message or 'Unknown error'}",
                metadata={"status": result.status.value, "response_time_ms": result.response_time_ms}
            )
        
        # Check for degraded status
        elif result.status == HealthStatus.DEGRADED:
            await self._trigger_alert_if_needed(
                endpoint=endpoint,
                alert_type="endpoint_degraded",
                severity="medium",
                message=f"Endpoint {endpoint} is degraded",
                metadata={"status": result.status.value, "failure_count": len(result.failure_indicators)}
            )
        
        # Check for high response time
        if result.response_time_ms > 2000:  # 2 seconds
            await self._trigger_alert_if_needed(
                endpoint=endpoint,
                alert_type="high_response_time",
                severity="medium",
                message=f"Endpoint {endpoint} has high response time: {result.response_time_ms:.2f}ms",
                metadata={"response_time_ms": result.response_time_ms}
            )
        
        # Check for consecutive failures
        consecutive_failures = self.health_validator._count_consecutive_failures(endpoint)
        if consecutive_failures >= self.config.max_consecutive_failures:
            await self._trigger_alert_if_needed(
                endpoint=endpoint,
                alert_type="consecutive_failures",
                severity="high",
                message=f"Endpoint {endpoint} has failed {consecutive_failures} consecutive health checks",
                metadata={"consecutive_failures": consecutive_failures}
            )
        
        # Check for critical failures
        critical_failures = [f for f in result.failure_indicators if f.severity == "critical"]
        for failure in critical_failures:
            await self._trigger_alert_if_needed(
                endpoint=endpoint,
                alert_type=f"critical_{failure.failure_type}",
                severity="critical",
                message=f"Critical failure detected on {endpoint}: {failure.description}",
                metadata=failure.metadata
            )
    
    async def _trigger_alert_if_needed(self, endpoint: str, alert_type: str, severity: str, message: str, metadata: Dict[str, Any]) -> None:
        """Trigger alert if not already active or cooldown period has passed."""
        alert_key = f"{endpoint}:{alert_type}"
        current_time = datetime.utcnow()
        
        # Check if alert is already active
        if alert_key in self._active_alerts:
            return
        
        # Check cooldown period
        if alert_key in self._active_alerts:
            last_alert = self._active_alerts[alert_key]
            if (current_time - last_alert.triggered_at).total_seconds() < self.config.alert_cooldown_seconds:
                return
        
        # Create new alert
        alert = Alert(
            endpoint=endpoint,
            alert_type=alert_type,
            severity=severity,
            message=message,
            metadata=metadata
        )
        
        # Store alert
        self._active_alerts[alert_key] = alert
        
        self._log_action("alert_triggered", {
            "endpoint": endpoint,
            "alert_type": alert_type,
            "severity": severity,
            "message": message
        })
        
        # Notify alert callbacks
        await self._notify_alert_callbacks(alert)
    
    async def _notify_health_callbacks(self, endpoint: str, result: HealthCheckResult) -> None:
        """Notify health check callbacks."""
        for callback in self._health_callbacks:
            try:
                callback(endpoint, result)
            except Exception as e:
                logger.error(f"Health callback error: {e}")
    
    async def _notify_alert_callbacks(self, alert: Alert) -> None:
        """Notify alert callbacks."""
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    async def _notify_quality_callbacks(self, endpoint: str, metrics: QualityMetrics) -> None:
        """Notify quality metrics callbacks."""
        for callback in self._quality_callbacks:
            try:
                callback(endpoint, metrics)
            except Exception as e:
                logger.error(f"Quality callback error: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        total_alerts = len(self._alert_history) + len(self._active_alerts)
        active_alerts = len(self._active_alerts)
        
        # Calculate alert statistics by severity
        alert_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for alert in self._active_alerts.values():
            alert_stats[alert.severity] += 1
        
        # Calculate endpoint health distribution
        health_stats = {"healthy": 0, "degraded": 0, "unhealthy": 0, "unknown": 0}
        for result in self._last_health_checks.values():
            health_stats[result.status.value] += 1
        
        return {
            "monitoring_active": self._monitoring_active,
            "total_endpoints": len(self.health_validator.endpoints),
            "health_stats": health_stats,
            "alert_stats": {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "by_severity": alert_stats
            },
            "quality_metrics_collected": sum(len(metrics) for metrics in self._quality_metrics_history.values()),
            "failures_detected": sum(len(failures) for failures in self._failure_history.values()),
            "callback_counts": {
                "health_callbacks": len(self._health_callbacks),
                "alert_callbacks": len(self._alert_callbacks),
                "quality_callbacks": len(self._quality_callbacks)
            }
        }
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '2.3',
            'action': f'endpoint_monitor_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))