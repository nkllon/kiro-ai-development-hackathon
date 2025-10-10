"""
Alert Manager

Real-time alert management for WebSocket health monitoring with configurable thresholds
and notification channels. Provides intelligent alerting with deduplication and escalation.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Represents an alert"""
    id: str
    endpoint: str
    alert_type: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    created_at: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolution_notes: Optional[str] = None


@dataclass
class AlertRule:
    """Defines an alert rule"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_sec: int = 300  # 5 minutes default
    max_alerts_per_hour: int = 10
    enabled: bool = True


class AlertManager:
    """
    Manages alerts for WebSocket health monitoring.
    
    Provides configurable alerting with deduplication, cooldown periods,
    and multiple notification channels for different severity levels.
    """

    def __init__(self):
        """Initialize the alert manager"""
        self._alerts: Dict[str, Alert] = {}
        self._alert_rules: Dict[str, AlertRule] = {}
        self._alert_history: deque = deque(maxlen=1000)
        
        # Alert tracking
        self._alert_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._last_alert_times: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._suppressed_alerts: Set[str] = set()
        
        # Notification channels
        self._notification_channels: Dict[AlertSeverity, List[Callable]] = {
            AlertSeverity.INFO: [],
            AlertSeverity.WARNING: [],
            AlertSeverity.CRITICAL: [],
            AlertSeverity.EMERGENCY: []
        }
        
        # Default alert rules
        self._setup_default_rules()
        
        # Alert ID counter
        self._alert_id_counter = 0

    def _setup_default_rules(self) -> None:
        """Setup default alert rules"""
        # High error rate rule
        self.add_alert_rule(
            name="high_error_rate",
            condition=lambda metrics: metrics.get('error_rate', 0) > 0.1,
            severity=AlertSeverity.WARNING,
            message_template="High error rate detected: {error_rate:.2%}",
            cooldown_sec=300
        )
        
        # Critical error rate rule
        self.add_alert_rule(
            name="critical_error_rate",
            condition=lambda metrics: metrics.get('error_rate', 0) > 0.25,
            severity=AlertSeverity.CRITICAL,
            message_template="Critical error rate: {error_rate:.2%}",
            cooldown_sec=60
        )
        
        # High latency rule
        self.add_alert_rule(
            name="high_latency",
            condition=lambda metrics: metrics.get('avg_latency_ms', 0) > 2000,
            severity=AlertSeverity.WARNING,
            message_template="High latency detected: {avg_latency_ms:.1f}ms",
            cooldown_sec=300
        )
        
        # Critical latency rule
        self.add_alert_rule(
            name="critical_latency",
            condition=lambda metrics: metrics.get('avg_latency_ms', 0) > 5000,
            severity=AlertSeverity.CRITICAL,
            message_template="Critical latency: {avg_latency_ms:.1f}ms",
            cooldown_sec=60
        )
        
        # Low throughput rule
        self.add_alert_rule(
            name="low_throughput",
            condition=lambda metrics: metrics.get('throughput_msgs_per_sec', 0) < 0.1,
            severity=AlertSeverity.WARNING,
            message_template="Low throughput: {throughput_msgs_per_sec:.2f} msgs/sec",
            cooldown_sec=600
        )
        
        # Connection failure rule
        self.add_alert_rule(
            name="connection_failure",
            condition=lambda metrics: metrics.get('connection_failures', 0) > 0,
            severity=AlertSeverity.CRITICAL,
            message_template="Connection failure detected",
            cooldown_sec=60
        )

    def add_alert_rule(self, name: str, condition: Callable[[Dict[str, Any]], bool],
                      severity: AlertSeverity, message_template: str,
                      cooldown_sec: int = 300, max_alerts_per_hour: int = 10,
                      enabled: bool = True) -> None:
        """
        Add a new alert rule.
        
        Args:
            name: Rule name
            condition: Function that takes metrics and returns True if alert should trigger
            severity: Alert severity level
            message_template: Message template with placeholders
            cooldown_sec: Minimum time between alerts of this type
            max_alerts_per_hour: Maximum alerts per hour for this rule
            enabled: Whether the rule is enabled
        """
        rule = AlertRule(
            name=name,
            condition=condition,
            severity=severity,
            message_template=message_template,
            cooldown_sec=cooldown_sec,
            max_alerts_per_hour=max_alerts_per_hour,
            enabled=enabled
        )
        
        self._alert_rules[name] = rule
        
        self._log_action("alert_rule_added", {
            "rule_name": name,
            "severity": severity.value,
            "cooldown_sec": cooldown_sec,
            "enabled": enabled
        })

    def add_notification_channel(self, severity: AlertSeverity, 
                               callback: Callable[[Alert], None]) -> None:
        """
        Add a notification channel for alerts.
        
        Args:
            severity: Severity level for this channel
            callback: Function to call when alert is triggered
        """
        self._notification_channels[severity].append(callback)
        
        self._log_action("notification_channel_added", {
            "severity": severity.value,
            "channel_count": len(self._notification_channels[severity])
        })

    async def trigger_alert(self, endpoint: str, alert_type: str, 
                           details: List[str], severity: Optional[AlertSeverity] = None) -> Optional[Alert]:
        """
        Trigger an alert for an endpoint.
        
        Args:
            endpoint: The WebSocket endpoint
            alert_type: Type of alert
            details: List of issue details
            severity: Optional severity override
            
        Returns:
            Alert object if created, None if suppressed
        """
        # Check if alert is suppressed
        alert_key = f"{endpoint}:{alert_type}"
        if alert_key in self._suppressed_alerts:
            return None
        
        # Check cooldown
        current_time = time.time()
        if alert_key in self._last_alert_times[endpoint]:
            last_time = self._last_alert_times[endpoint][alert_key]
            rule = self._alert_rules.get(alert_type)
            if rule and (current_time - last_time) < rule.cooldown_sec:
                return None
        
        # Check rate limiting
        hour_key = f"{alert_type}:{int(current_time // 3600)}"
        if self._alert_counts[endpoint][hour_key] >= self._alert_rules.get(alert_type, AlertRule("", lambda x: False, AlertSeverity.INFO, "")).max_alerts_per_hour:
            return None
        
        # Determine severity
        if severity is None:
            rule = self._alert_rules.get(alert_type)
            severity = rule.severity if rule else AlertSeverity.WARNING
        
        # Create alert
        alert_id = f"alert_{self._alert_id_counter}"
        self._alert_id_counter += 1
        
        alert = Alert(
            id=alert_id,
            endpoint=endpoint,
            alert_type=alert_type,
            severity=severity,
            message=f"{alert_type} alert for {endpoint}",
            details={"issues": details},
            created_at=datetime.now()
        )
        
        # Store alert
        self._alerts[alert_id] = alert
        self._alert_history.append(alert)
        
        # Update tracking
        self._last_alert_times[endpoint][alert_key] = current_time
        self._alert_counts[endpoint][hour_key] += 1
        
        # Send notifications
        await self._send_notifications(alert)
        
        self._log_action("alert_triggered", {
            "alert_id": alert_id,
            "endpoint": endpoint,
            "alert_type": alert_type,
            "severity": severity.value,
            "details": details
        })
        
        return alert

    async def check_metrics_alerts(self, endpoint: str, metrics: Dict[str, Any]) -> List[Alert]:
        """
        Check metrics against all alert rules and trigger alerts if needed.
        
        Args:
            endpoint: The WebSocket endpoint
            metrics: Current metrics for the endpoint
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        for rule_name, rule in self._alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                if rule.condition(metrics):
                    # Format message
                    message = rule.message_template.format(**metrics)
                    
                    # Trigger alert
                    alert = await self.trigger_alert(
                        endpoint=endpoint,
                        alert_type=rule_name,
                        details=[message],
                        severity=rule.severity
                    )
                    
                    if alert:
                        triggered_alerts.append(alert)
            
            except Exception as e:
                self._log_action("alert_rule_error", {
                    "rule_name": rule_name,
                    "endpoint": endpoint,
                    "error": str(e),
                    "status": "error"
                })
        
        return triggered_alerts

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str,
                              notes: Optional[str] = None) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID to acknowledge
            acknowledged_by: Who acknowledged the alert
            notes: Optional acknowledgment notes
            
        Returns:
            True if acknowledged, False if not found
        """
        if alert_id not in self._alerts:
            return False
        
        alert = self._alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by
        alert.resolution_notes = notes
        
        self._log_action("alert_acknowledged", {
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by,
            "notes": notes
        })
        
        return True

    async def resolve_alert(self, alert_id: str, resolution_notes: Optional[str] = None) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID to resolve
            resolution_notes: Optional resolution notes
            
        Returns:
            True if resolved, False if not found
        """
        if alert_id not in self._alerts:
            return False
        
        alert = self._alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.resolution_notes = resolution_notes
        
        self._log_action("alert_resolved", {
            "alert_id": alert_id,
            "resolution_notes": resolution_notes
        })
        
        return True

    def suppress_alert(self, endpoint: str, alert_type: str, duration_sec: int = 3600) -> None:
        """
        Suppress alerts for a specific endpoint and type.
        
        Args:
            endpoint: The WebSocket endpoint
            alert_type: Type of alert to suppress
            duration_sec: Suppression duration in seconds
        """
        alert_key = f"{endpoint}:{alert_type}"
        self._suppressed_alerts.add(alert_key)
        
        # Schedule removal of suppression
        asyncio.create_task(self._remove_suppression_after_delay(alert_key, duration_sec))
        
        self._log_action("alert_suppressed", {
            "endpoint": endpoint,
            "alert_type": alert_type,
            "duration_sec": duration_sec
        })

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self._alerts.values() 
                if alert.status == AlertStatus.ACTIVE]

    def get_alerts_by_endpoint(self, endpoint: str) -> List[Alert]:
        """Get all alerts for a specific endpoint"""
        return [alert for alert in self._alerts.values() 
                if alert.endpoint == endpoint]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get all alerts of a specific severity"""
        return [alert for alert in self._alerts.values() 
                if alert.severity == severity]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of all alerts"""
        total_alerts = len(self._alerts)
        active_alerts = len(self.get_active_alerts())
        
        severity_counts = defaultdict(int)
        for alert in self._alerts.values():
            severity_counts[alert.severity.value] += 1
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'acknowledged_alerts': len([a for a in self._alerts.values() 
                                      if a.status == AlertStatus.ACKNOWLEDGED]),
            'resolved_alerts': len([a for a in self._alerts.values() 
                                  if a.status == AlertStatus.RESOLVED]),
            'severity_breakdown': dict(severity_counts),
            'suppressed_alerts': len(self._suppressed_alerts),
            'alert_rules': len(self._alert_rules)
        }

    async def _send_notifications(self, alert: Alert) -> None:
        """Send notifications for an alert"""
        channels = self._notification_channels[alert.severity]
        
        for channel in channels:
            try:
                await channel(alert)
            except Exception as e:
                self._log_action("notification_error", {
                    "alert_id": alert.id,
                    "severity": alert.severity.value,
                    "error": str(e),
                    "status": "error"
                })

    async def _remove_suppression_after_delay(self, alert_key: str, delay_sec: int) -> None:
        """Remove alert suppression after delay"""
        await asyncio.sleep(delay_sec)
        self._suppressed_alerts.discard(alert_key)
        
        self._log_action("alert_suppression_removed", {
            "alert_key": alert_key
        })

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format to stdout"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.1",
            "action": f"alert_manager_{action}",
            "status": "in_progress",
            "details": details
        }
        
        print(json.dumps(log_entry))