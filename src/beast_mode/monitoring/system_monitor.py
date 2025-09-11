"""
Integrated system monitoring for Beast Mode Agent Collaboration Network.

Combines health monitoring, metrics collection, alerting, and recovery
into a unified monitoring system for comprehensive observability.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from .health_monitor import HealthMonitor, HealthStatus, ComponentHealth
from .metrics_collector import MetricsCollector, MetricType
from .alerting import AlertManager, Alert, AlertSeverity
from .recovery import RecoveryManager, RecoveryResult


@dataclass
class SystemStatus:
    """Overall system status summary."""
    overall_health: HealthStatus
    active_alerts: int
    critical_alerts: int
    active_recoveries: int
    message_throughput: float
    error_rate: float
    avg_latency_ms: float
    timestamp: datetime


class SystemMonitor:
    """
    Integrated monitoring system for Beast Mode Agent Collaboration Network.
    
    Provides unified monitoring, alerting, and recovery capabilities with
    automatic integration between health checks, metrics, alerts, and recovery.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.logger = logging.getLogger(__name__)
        
        # Initialize monitoring components
        self.health_monitor = HealthMonitor(redis_url)
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.recovery_manager = RecoveryManager(redis_url)
        
        # System state
        self.monitoring_active = False
        self.integration_task: Optional[asyncio.Task] = None
        
        # Callbacks for external integration
        self.status_callbacks: List[Callable] = []
        
    async def start_monitoring(self) -> None:
        """Start the integrated monitoring system."""
        if self.monitoring_active:
            self.logger.warning("System monitoring already active")
            return
            
        self.monitoring_active = True
        
        # Start all monitoring components
        await self.health_monitor.start_monitoring()
        await self.metrics_collector.start_collection()
        await self.alert_manager.start_alerting()
        await self.recovery_manager.start_recovery_system()
        
        # Set up integrations
        await self._setup_integrations()
        
        # Start integration task
        self.integration_task = asyncio.create_task(self._integration_loop())
        
        self.logger.info("Integrated system monitoring started")
        
    async def stop_monitoring(self) -> None:
        """Stop the integrated monitoring system."""
        self.monitoring_active = False
        
        # Stop integration task
        if self.integration_task:
            self.integration_task.cancel()
            try:
                await self.integration_task
            except asyncio.CancelledError:
                pass
                
        # Stop all monitoring components
        await self.recovery_manager.stop_recovery_system()
        await self.alert_manager.stop_alerting()
        await self.metrics_collector.stop_collection()
        await self.health_monitor.stop_monitoring()
        
        self.logger.info("Integrated system monitoring stopped")
        
    def add_status_callback(self, callback: Callable) -> None:
        """Add a callback for system status updates."""
        self.status_callbacks.append(callback)
        
    async def get_system_status(self) -> SystemStatus:
        """Get comprehensive system status."""
        # Get health summary
        health_summary = await self.health_monitor.get_health_summary()
        overall_health = HealthStatus(health_summary["overall_status"])
        
        # Get alert summary
        alert_summary = self.alert_manager.get_alert_summary()
        active_alerts = alert_summary["active_alerts"]
        critical_alerts = len(self.alert_manager.get_alerts_by_severity(AlertSeverity.CRITICAL))
        
        # Get recovery summary
        recovery_summary = self.recovery_manager.get_recovery_summary()
        active_recoveries = recovery_summary["active_recoveries"]
        
        # Get performance metrics
        performance_report = self.metrics_collector.get_performance_report()
        kpis = performance_report.get("kpis", {})
        
        message_throughput = kpis.get("message_throughput", {}).get("total_messages", 0)
        error_rate = kpis.get("error_rate", {}).get("error_rate_percent", 0)
        avg_latency = kpis.get("message_latency", {}).get("avg_ms", 0)
        
        return SystemStatus(
            overall_health=overall_health,
            active_alerts=active_alerts,
            critical_alerts=critical_alerts,
            active_recoveries=active_recoveries,
            message_throughput=message_throughput,
            error_rate=error_rate,
            avg_latency_ms=avg_latency,
            timestamp=datetime.now()
        )
        
    async def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get a comprehensive monitoring report."""
        system_status = await self.get_system_status()
        
        return {
            "system_status": system_status.__dict__,
            "health": await self.health_monitor.get_health_summary(),
            "component_health": await self.health_monitor.get_system_health(),
            "metrics": self.metrics_collector.get_performance_report(),
            "alerts": {
                "summary": self.alert_manager.get_alert_summary(),
                "active": [alert.__dict__ for alert in self.alert_manager.get_active_alerts()],
                "recent": [alert.__dict__ for alert in self.alert_manager.get_alert_history(24)]
            },
            "recovery": {
                "summary": self.recovery_manager.get_recovery_summary(),
                "active": [attempt.__dict__ for attempt in self.recovery_manager.get_active_recoveries()],
                "recent": [attempt.__dict__ for attempt in self.recovery_manager.get_recovery_history(24)]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    # Metric recording methods for external use
    
    def record_message_sent(self, latency_ms: Optional[float] = None) -> None:
        """Record a message sent event."""
        self.metrics_collector.increment_counter("messages_sent")
        self.metrics_collector.increment_counter("operations")
        
        if latency_ms is not None:
            self.metrics_collector.record_timer("message_latency", latency_ms)
            
    def record_message_received(self, processing_time_ms: Optional[float] = None) -> None:
        """Record a message received event."""
        self.metrics_collector.increment_counter("messages_received")
        self.metrics_collector.increment_counter("operations")
        
        if processing_time_ms is not None:
            self.metrics_collector.record_timer("message_processing_time", processing_time_ms)
            
    def record_error(self, error_type: str = "general") -> None:
        """Record an error event."""
        self.metrics_collector.increment_counter("errors", labels={"type": error_type})
        
    def record_agent_connection(self, agent_id: str, connected: bool) -> None:
        """Record agent connection status."""
        if connected:
            self.metrics_collector.increment_counter("agent_connections")
        else:
            self.metrics_collector.increment_counter("agent_disconnections")
            
        # Update active connections gauge
        current_connections = self.metrics_collector.get_gauge_value("active_connections") or 0
        if connected:
            current_connections += 1
        else:
            current_connections = max(0, current_connections - 1)
            
        self.metrics_collector.set_gauge("active_connections", current_connections)
        
    async def report_component_failure(
        self, 
        component: str, 
        failure_type: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report a component failure for recovery consideration."""
        # Record error metric
        self.record_error(f"{component}_{failure_type}")
        
        # Report to recovery manager
        await self.recovery_manager.report_failure(component, failure_type, details)
        
    async def _setup_integrations(self) -> None:
        """Set up integrations between monitoring components."""
        # Set up alert handlers
        self.alert_manager.add_alert_handler(self._handle_alert)
        
        # Set up recovery callbacks
        self.recovery_manager.add_recovery_callback(self._handle_recovery_event)
        
        # Register integrated alert rules
        await self._register_integrated_alert_rules()
        
        self.logger.info("Monitoring integrations configured")
        
    async def _integration_loop(self) -> None:
        """Main integration loop for cross-component coordination."""
        self.logger.info("Starting monitoring integration loop")
        
        while self.monitoring_active:
            try:
                # Check for health-based alerts
                await self._check_health_alerts()
                
                # Check for metric-based alerts
                await self._check_metric_alerts()
                
                # Update system status
                await self._update_system_status()
                
                # Sleep before next iteration
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in integration loop: {e}")
                await asyncio.sleep(60)
                
    async def _register_integrated_alert_rules(self) -> None:
        """Register alert rules that integrate health and metrics."""
        # Component health alert
        await self.alert_manager.register_alert_rule(
            name="component_unhealthy",
            description="One or more components are unhealthy",
            severity=AlertSeverity.HIGH,
            condition_function=self._check_component_health_alert,
            evaluation_interval_seconds=60
        )
        
        # System performance alert
        await self.alert_manager.register_alert_rule(
            name="system_performance_degraded",
            description="System performance is degraded",
            severity=AlertSeverity.MEDIUM,
            condition_function=self._check_performance_alert,
            evaluation_interval_seconds=120
        )
        
        # Recovery failure alert
        await self.alert_manager.register_alert_rule(
            name="recovery_failures",
            description="Multiple recovery attempts have failed",
            severity=AlertSeverity.CRITICAL,
            condition_function=self._check_recovery_failure_alert,
            evaluation_interval_seconds=300
        )
        
    async def _check_health_alerts(self) -> None:
        """Check health status and trigger alerts if needed."""
        health_summary = await self.health_monitor.get_health_summary()
        
        if health_summary["unhealthy"] > 0:
            await self.alert_manager.fire_alert(
                name="unhealthy_components",
                message=f"{health_summary['unhealthy']} components are unhealthy",
                severity=AlertSeverity.HIGH,
                source_component="health_monitor",
                details=health_summary
            )
            
    async def _check_metric_alerts(self) -> None:
        """Check metrics and trigger alerts if needed."""
        performance_report = self.metrics_collector.get_performance_report()
        kpis = performance_report.get("kpis", {})
        
        # Check error rate
        error_rate = kpis.get("error_rate", {}).get("error_rate_percent", 0)
        if error_rate > 10:  # 10% error rate threshold
            await self.alert_manager.fire_alert(
                name="high_error_rate",
                message=f"Error rate is {error_rate}%",
                severity=AlertSeverity.HIGH,
                source_component="metrics_collector",
                details={"error_rate": error_rate}
            )
            
        # Check latency
        latency = kpis.get("message_latency", {}).get("avg_ms", 0)
        if latency > 1000:  # 1 second threshold
            await self.alert_manager.fire_alert(
                name="high_latency",
                message=f"Average latency is {latency}ms",
                severity=AlertSeverity.MEDIUM,
                source_component="metrics_collector",
                details={"latency_ms": latency}
            )
            
    async def _update_system_status(self) -> None:
        """Update system status and notify callbacks."""
        try:
            status = await self.get_system_status()
            
            # Notify status callbacks
            for callback in self.status_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(status)
                    else:
                        callback(status)
                except Exception as e:
                    self.logger.error(f"Error in status callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error updating system status: {e}")
            
    async def _handle_alert(self, alert: Alert) -> None:
        """Handle alert events for potential recovery triggers."""
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            # Determine if recovery should be triggered
            recovery_action = None
            
            if "redis" in alert.name.lower():
                recovery_action = "redis_reconnect"
            elif "error_rate" in alert.name.lower():
                recovery_action = "reset_message_counters"
            elif "performance" in alert.name.lower():
                recovery_action = "enable_degraded_mode"
                
            if recovery_action:
                self.logger.info(f"Triggering recovery {recovery_action} for alert {alert.name}")
                await self.recovery_manager.trigger_recovery(
                    recovery_action, 
                    {"alert_id": alert.id, "alert_details": alert.details}
                )
                
    async def _handle_recovery_event(self, recovery_attempt) -> None:
        """Handle recovery events for metrics and alerting."""
        # Record recovery metrics
        if recovery_attempt.result:
            self.metrics_collector.increment_counter(
                "recovery_attempts",
                labels={"action": recovery_attempt.action_name, "result": recovery_attempt.result.value}
            )
            
        # Fire alert for failed recoveries
        if recovery_attempt.result == RecoveryResult.FAILED:
            await self.alert_manager.fire_alert(
                name="recovery_failed",
                message=f"Recovery action {recovery_attempt.action_name} failed",
                severity=AlertSeverity.HIGH,
                source_component="recovery_manager",
                details=recovery_attempt.__dict__
            )
            
    # Alert condition functions
    
    async def _check_component_health_alert(self, rule) -> Dict[str, Any]:
        """Check component health for alerting."""
        health_summary = await self.health_monitor.get_health_summary()
        
        unhealthy_count = health_summary.get("unhealthy", 0)
        
        return {
            "should_alert": unhealthy_count > 0,
            "should_resolve": unhealthy_count == 0,
            "message": f"{unhealthy_count} components are unhealthy" if unhealthy_count > 0 else "All components healthy",
            "component": "health_monitor",
            "details": health_summary
        }
        
    async def _check_performance_alert(self, rule) -> Dict[str, Any]:
        """Check system performance for alerting."""
        performance_report = self.metrics_collector.get_performance_report()
        kpis = performance_report.get("kpis", {})
        
        # Check multiple performance indicators
        issues = []
        
        error_rate = kpis.get("error_rate", {}).get("error_rate_percent", 0)
        if error_rate > 5:
            issues.append(f"Error rate: {error_rate}%")
            
        latency = kpis.get("message_latency", {}).get("avg_ms", 0)
        if latency > 500:
            issues.append(f"High latency: {latency}ms")
            
        should_alert = len(issues) > 0
        
        return {
            "should_alert": should_alert,
            "should_resolve": not should_alert,
            "message": f"Performance issues: {', '.join(issues)}" if should_alert else "Performance normal",
            "component": "metrics_collector",
            "details": kpis
        }
        
    async def _check_recovery_failure_alert(self, rule) -> Dict[str, Any]:
        """Check for recovery failures."""
        recovery_summary = self.recovery_manager.get_recovery_summary()
        recent_attempts = self.recovery_manager.get_recovery_history(1)  # Last hour
        
        failed_attempts = [
            attempt for attempt in recent_attempts 
            if attempt.result == RecoveryResult.FAILED
        ]
        
        should_alert = len(failed_attempts) >= 3  # 3 failures in an hour
        
        return {
            "should_alert": should_alert,
            "should_resolve": len(failed_attempts) < 3,
            "message": f"{len(failed_attempts)} recovery failures in the last hour" if should_alert else "Recovery operations normal",
            "component": "recovery_manager",
            "details": {"failed_attempts": len(failed_attempts), "total_attempts": len(recent_attempts)}
        }