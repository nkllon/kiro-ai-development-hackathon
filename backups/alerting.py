"""
Alerting system for Beast Mode monitoring.

Provides configurable alerting for system failures, performance degradation,
and other critical events in the Beast Mode Agent Collaboration Network.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from pydantic import BaseModel


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"    # System is down or severely impacted
    HIGH = "high"           # Major functionality affected
    MEDIUM = "medium"       # Minor functionality affected
    LOW = "low"             # Informational or warning
    INFO = "info"           # General information


@dataclass
class Alert:
    """An alert instance."""
    id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source_component: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_message: str = ""


class AlertRule(BaseModel):
    """Configuration for an alert rule."""
    name: str
    description: str
    severity: AlertSeverity
    condition_function: Callable
    threshold_value: Optional[float] = None
    evaluation_interval_seconds: int = 60
    cooldown_seconds: int = 300  # Minimum time between alerts
    auto_resolve: bool = True
    auto_resolve_threshold: Optional[float] = None


class AlertManager:
    """
    Comprehensive alerting system for Beast Mode components.
    
    Monitors system health and performance metrics, evaluates alert rules,
    and manages alert lifecycle including firing, escalation, and resolution.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_evaluation: Dict[str, datetime] = {}
        self.last_alert_time: Dict[str, datetime] = {}
        self.alerting_active = False
        self.alerting_task: Optional[asyncio.Task] = None
        
        # Alert handlers
        self.alert_handlers: List[Callable] = []
        
    async def register_alert_rule(
        self,
        name: str,
        description: str,
        severity: AlertSeverity,
        condition_function: Callable,
        threshold_value: Optional[float] = None,
        evaluation_interval_seconds: int = 60,
        cooldown_seconds: int = 300,
        auto_resolve: bool = True,
        auto_resolve_threshold: Optional[float] = None
    ) -> None:
        """Register a new alert rule."""
        self.alert_rules[name] = AlertRule(
            name=name,
            description=description,
            severity=severity,
            condition_function=condition_function,
            threshold_value=threshold_value,
            evaluation_interval_seconds=evaluation_interval_seconds,
            cooldown_seconds=cooldown_seconds,
            auto_resolve=auto_resolve,
            auto_resolve_threshold=auto_resolve_threshold
        )
        
        self.logger.info(f"Registered alert rule: {name}")
        
    def add_alert_handler(self, handler: Callable) -> None:
        """Add an alert handler function."""
        self.alert_handlers.append(handler)
        self.logger.info(f"Added alert handler: {handler.__name__}")
        
    async def start_alerting(self) -> None:
        """Start the alerting system."""
        if self.alerting_active:
            self.logger.warning("Alerting already active")
            return
            
        self.alerting_active = True
        
        # Register default alert rules
        await self._register_default_rules()
        
        # Start alerting task
        self.alerting_task = asyncio.create_task(self._alerting_loop())
        
        self.logger.info("Alerting system started")
        
    async def stop_alerting(self) -> None:
        """Stop the alerting system."""
        self.alerting_active = False
        
        if self.alerting_task:
            self.alerting_task.cancel()
            try:
                await self.alerting_task
            except asyncio.CancelledError:
                pass
                
        self.logger.info("Alerting system stopped")
        
    async def fire_alert(
        self,
        name: str,
        message: str,
        severity: AlertSeverity,
        source_component: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Manually fire an alert."""
        alert_id = f"{name}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            name=name,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            source_component=source_component,
            details=details or {}
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Notify handlers
        await self._notify_handlers(alert)
        
        self.logger.warning(f"Alert fired: {name} - {message}")
        return alert_id
        
    async def resolve_alert(
        self,
        alert_id: str,
        resolution_message: str = "Manually resolved"
    ) -> bool:
        """Resolve an active alert."""
        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.now()
        alert.resolution_message = resolution_message
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        # Notify handlers
        await self._notify_handlers(alert)
        
        self.logger.info(f"Alert resolved: {alert.name} - {resolution_message}")
        return True
        
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
        
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get active alerts by severity."""
        return [alert for alert in self.active_alerts.values() if alert.severity == severity]
        
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
        
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get a summary of current alert status."""
        active_by_severity = {}
        for severity in AlertSeverity:
            active_by_severity[severity.value] = len(self.get_alerts_by_severity(severity))
            
        recent_history = self.get_alert_history(24)
        
        return {
            "active_alerts": len(self.active_alerts),
            "active_by_severity": active_by_severity,
            "recent_alerts_24h": len(recent_history),
            "alert_rules": len(self.alert_rules),
            "last_updated": datetime.now().isoformat()
        }
        
    async def _register_default_rules(self) -> None:
        """Register default alert rules for common issues."""
        # Redis connectivity alert
        await self.register_alert_rule(
            name="redis_connectivity_failure",
            description="Redis server is not reachable",
            severity=AlertSeverity.CRITICAL,
            condition_function=self._check_redis_connectivity_alert,
            evaluation_interval_seconds=30,
            cooldown_seconds=300
        )
        
        # High error rate alert
        await self.register_alert_rule(
            name="high_error_rate",
            description="Error rate is above acceptable threshold",
            severity=AlertSeverity.HIGH,
            condition_function=self._check_error_rate_alert,
            threshold_value=5.0,  # 5% error rate
            evaluation_interval_seconds=60,
            cooldown_seconds=600
        )
        
        # High message latency alert
        await self.register_alert_rule(
            name="high_message_latency",
            description="Message latency is above acceptable threshold",
            severity=AlertSeverity.MEDIUM,
            condition_function=self._check_latency_alert,
            threshold_value=1000.0,  # 1 second
            evaluation_interval_seconds=120,
            cooldown_seconds=300
        )
        
        # System resource alert
        await self.register_alert_rule(
            name="high_resource_usage",
            description="System resource usage is critically high",
            severity=AlertSeverity.HIGH,
            condition_function=self._check_resource_usage_alert,
            threshold_value=90.0,  # 90% usage
            evaluation_interval_seconds=300,
            cooldown_seconds=600
        )
        
    async def _alerting_loop(self) -> None:
        """Main alerting evaluation loop."""
        self.logger.info("Starting alerting evaluation loop")
        
        while self.alerting_active:
            try:
                # Evaluate all alert rules
                for rule_name, rule in self.alert_rules.items():
                    # Check if it's time to evaluate this rule
                    last_eval = self.last_evaluation.get(rule_name)
                    if (not last_eval or 
                        (datetime.now() - last_eval).total_seconds() >= rule.evaluation_interval_seconds):
                        
                        await self._evaluate_rule(rule_name, rule)
                        self.last_evaluation[rule_name] = datetime.now()
                        
                # Sleep before next iteration
                await asyncio.sleep(10)  # Check every 10 seconds for due evaluations
                
            except Exception as e:
                self.logger.error(f"Error in alerting loop: {e}")
                await asyncio.sleep(30)  # Back off on error
                
    async def _evaluate_rule(self, rule_name: str, rule: AlertRule) -> None:
        """Evaluate a single alert rule."""
        try:
            # Check cooldown period
            last_alert = self.last_alert_time.get(rule_name)
            if (last_alert and 
                (datetime.now() - last_alert).total_seconds() < rule.cooldown_seconds):
                return
                
            # Evaluate condition
            result = await rule.condition_function(rule)
            
            if result.get("should_alert", False):
                # Fire alert
                alert_id = await self.fire_alert(
                    name=rule_name,
                    message=result.get("message", rule.description),
                    severity=rule.severity,
                    source_component=result.get("component", "unknown"),
                    details=result.get("details", {})
                )
                
                self.last_alert_time[rule_name] = datetime.now()
                
            elif rule.auto_resolve:
                # Check for auto-resolution
                await self._check_auto_resolve(rule_name, rule, result)
                
        except Exception as e:
            self.logger.error(f"Error evaluating alert rule {rule_name}: {e}")
            
    async def _check_auto_resolve(
        self, 
        rule_name: str, 
        rule: AlertRule, 
        result: Dict[str, Any]
    ) -> None:
        """Check if any active alerts for this rule should be auto-resolved."""
        # Find active alerts for this rule
        rule_alerts = [
            alert for alert in self.active_alerts.values() 
            if alert.name == rule_name
        ]
        
        for alert in rule_alerts:
            if result.get("should_resolve", False):
                await self.resolve_alert(
                    alert.id,
                    result.get("resolution_message", "Condition no longer met")
                )
                
    async def _notify_handlers(self, alert: Alert) -> None:
        """Notify all registered alert handlers."""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler {handler.__name__}: {e}")
                
    # Default alert condition functions
    
    async def _check_redis_connectivity_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check Redis connectivity for alerting."""
        # This would integrate with the health monitor
        # For now, return a placeholder
        return {
            "should_alert": False,
            "should_resolve": True,
            "message": "Redis connectivity OK",
            "component": "redis"
        }
        
    async def _check_error_rate_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check error rate for alerting."""
        # This would integrate with the metrics collector
        # For now, return a placeholder
        return {
            "should_alert": False,
            "should_resolve": True,
            "message": "Error rate within acceptable limits",
            "component": "messaging"
        }
        
    async def _check_latency_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check message latency for alerting."""
        # This would integrate with the metrics collector
        # For now, return a placeholder
        return {
            "should_alert": False,
            "should_resolve": True,
            "message": "Message latency within acceptable limits",
            "component": "messaging"
        }
        
    async def _check_resource_usage_alert(self, rule: AlertRule) -> Dict[str, Any]:
        """Check system resource usage for alerting."""
        # This would integrate with the health monitor
        # For now, return a placeholder
        return {
            "should_alert": False,
            "should_resolve": True,
            "message": "System resource usage normal",
            "component": "system"
        }