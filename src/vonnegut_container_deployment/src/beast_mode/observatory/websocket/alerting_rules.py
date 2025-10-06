"""
WebSocket Alerting Rules and Notification System

Implements comprehensive alerting rules for WebSocket connectivity issues
with support for multiple notification channels and escalation policies.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Set
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

from .comprehensive_monitor import WebSocketAlert, AlertSeverity, MonitoringDimension

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    DISCORD = "discord"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    CONSOLE = "console"


class EscalationLevel(Enum):
    """Escalation levels."""
    IMMEDIATE = "immediate"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


@dataclass
class AlertRule:
    """Alert rule configuration."""
    rule_id: str
    name: str
    condition: str
    severity: AlertSeverity
    escalation_level: EscalationLevel
    notification_channels: List[NotificationChannel]
    cooldown_minutes: int = 5
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'condition': self.condition,
            'severity': self.severity.value,
            'escalation_level': self.escalation_level.value,
            'notification_channels': [ch.value for ch in self.notification_channels],
            'cooldown_minutes': self.cooldown_minutes,
            'enabled': self.enabled,
            'metadata': self.metadata
        }


@dataclass
class NotificationConfig:
    """Notification configuration."""
    email_config: Optional[Dict[str, Any]] = None
    webhook_config: Optional[Dict[str, Any]] = None
    discord_config: Optional[Dict[str, Any]] = None
    slack_config: Optional[Dict[str, Any]] = None
    pagerduty_config: Optional[Dict[str, Any]] = None


class WebSocketAlertingSystem:
    """
    Comprehensive WebSocket alerting system with multiple notification channels
    and escalation policies.
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """Initialize alerting system."""
        self.config = config or NotificationConfig()
        self._alert_rules: Dict[str, AlertRule] = {}
        self._alert_history: List[WebSocketAlert] = []
        self._last_notification_times: Dict[str, datetime] = {}
        self._escalation_callbacks: Set[Callable[[WebSocketAlert, EscalationLevel], None]] = set()
        
        # Initialize default alert rules
        self._initialize_default_rules()
        
        self._log_action("alerting_system_initialized", {
            "notification_channels": len(NotificationChannel),
            "default_rules": len(self._alert_rules)
        })
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add custom alert rule."""
        self._alert_rules[rule.rule_id] = rule
        
        self._log_action("alert_rule_added", {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "severity": rule.severity.value,
            "channels": [ch.value for ch in rule.notification_channels]
        })
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove alert rule."""
        if rule_id in self._alert_rules:
            del self._alert_rules[rule_id]
            self._log_action("alert_rule_removed", {"rule_id": rule_id})
            return True
        return False
    
    def enable_rule(self, rule_id: str) -> bool:
        """Enable alert rule."""
        if rule_id in self._alert_rules:
            self._alert_rules[rule_id].enabled = True
            self._log_action("alert_rule_enabled", {"rule_id": rule_id})
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable alert rule."""
        if rule_id in self._alert_rules:
            self._alert_rules[rule_id].enabled = False
            self._log_action("alert_rule_disabled", {"rule_id": rule_id})
            return True
        return False
    
    async def process_alert(self, alert: WebSocketAlert) -> None:
        """Process WebSocket alert and trigger notifications."""
        self._log_action("alert_processing_started", {
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value
        })
        
        # Store alert in history
        self._alert_history.append(alert)
        if len(self._alert_history) > 1000:  # Keep last 1000 alerts
            self._alert_history = self._alert_history[-1000:]
        
        # Find matching alert rules
        matching_rules = self._find_matching_rules(alert)
        
        if not matching_rules:
            self._log_action("no_matching_rules", {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type
            })
            return
        
        # Process each matching rule
        for rule in matching_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown period
            if self._is_in_cooldown(rule.rule_id, rule.cooldown_minutes):
                continue
            
            # Trigger notifications
            await self._trigger_notifications(alert, rule)
            
            # Update last notification time
            self._last_notification_times[rule.rule_id] = datetime.utcnow()
            
            # Trigger escalation callbacks
            await self._trigger_escalation_callbacks(alert, rule.escalation_level)
        
        self._log_action("alert_processing_completed", {
            "alert_id": alert.alert_id,
            "matching_rules": len(matching_rules),
            "notifications_sent": len(matching_rules)
        })
    
    async def send_test_notification(self, channel: NotificationChannel, message: str = "Test notification") -> bool:
        """Send test notification to verify channel configuration."""
        test_alert = WebSocketAlert(
            alert_id="test_alert",
            endpoint="test",
            alert_type="test",
            severity=AlertSeverity.LOW,
            message=message
        )
        
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email_notification(test_alert, [])
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook_notification(test_alert, [])
            elif channel == NotificationChannel.DISCORD:
                return await self._send_discord_notification(test_alert, [])
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack_notification(test_alert, [])
            elif channel == NotificationChannel.PAGERDUTY:
                return await self._send_pagerduty_notification(test_alert, [])
            elif channel == NotificationChannel.CONSOLE:
                return await self._send_console_notification(test_alert, [])
            else:
                return False
        except Exception as e:
            logger.error(f"Test notification failed for {channel.value}: {e}")
            return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        total_alerts = len(self._alert_history)
        
        # Count alerts by severity
        severity_counts = {severity.value: 0 for severity in AlertSeverity}
        for alert in self._alert_history:
            severity_counts[alert.severity.value] += 1
        
        # Count alerts by type
        alert_type_counts = {}
        for alert in self._alert_history:
            alert_type_counts[alert.alert_type] = alert_type_counts.get(alert.alert_type, 0) + 1
        
        # Count notifications sent
        notifications_sent = len(self._last_notification_times)
        
        return {
            "total_alerts": total_alerts,
            "severity_distribution": severity_counts,
            "alert_type_distribution": alert_type_counts,
            "notifications_sent": notifications_sent,
            "active_rules": len([r for r in self._alert_rules.values() if r.enabled]),
            "total_rules": len(self._alert_rules),
            "recent_alerts": [alert.to_dict() for alert in self._alert_history[-10:]]
        }
    
    def add_escalation_callback(self, callback: Callable[[WebSocketAlert, EscalationLevel], None]) -> None:
        """Add escalation callback."""
        self._escalation_callbacks.add(callback)
    
    def remove_escalation_callback(self, callback: Callable[[WebSocketAlert, EscalationLevel], None]) -> None:
        """Remove escalation callback."""
        self._escalation_callbacks.discard(callback)
    
    def _find_matching_rules(self, alert: WebSocketAlert) -> List[AlertRule]:
        """Find alert rules that match the alert."""
        matching_rules = []
        
        for rule in self._alert_rules.values():
            if self._rule_matches_alert(rule, alert):
                matching_rules.append(rule)
        
        return matching_rules
    
    def _rule_matches_alert(self, rule: AlertRule, alert: WebSocketAlert) -> bool:
        """Check if rule matches alert."""
        # Simple condition matching - in production, use a proper expression evaluator
        try:
            if rule.condition == "severity == critical":
                return alert.severity == AlertSeverity.CRITICAL
            elif rule.condition == "severity == high":
                return alert.severity == AlertSeverity.HIGH
            elif rule.condition == "alert_type == connection_failure":
                return alert.alert_type == "connection_failure"
            elif rule.condition == "alert_type == high_latency":
                return alert.alert_type == "high_latency"
            elif rule.condition == "alert_type == tunnel_health_degraded":
                return alert.alert_type == "tunnel_health_degraded"
            elif rule.condition == "alert_type == error_1033_detected":
                return alert.alert_type == "error_1033_detected"
            elif rule.condition == "alert_type == bot_protection_triggers":
                return alert.alert_type == "excessive_bot_protection_triggers"
            else:
                # Custom condition evaluation
                return self._evaluate_custom_condition(rule.condition, alert)
        except Exception as e:
            logger.error(f"Error evaluating rule condition '{rule.condition}': {e}")
            return False
    
    def _evaluate_custom_condition(self, condition: str, alert: WebSocketAlert) -> bool:
        """Evaluate custom condition string."""
        # This is a simplified condition evaluator
        # In production, use a proper expression evaluator like pyparsing or similar
        
        try:
            # Create evaluation context
            context = {
                "alert_type": alert.alert_type,
                "severity": alert.severity.value,
                "endpoint": alert.endpoint,
                "message": alert.message
            }
            
            # Add dimension data
            for dim, data in alert.dimensions.items():
                context[f"dim_{dim.value}"] = data
            
            # Add metadata
            context.update(alert.metadata)
            
            # Simple condition evaluation (not safe for arbitrary code)
            if "severity" in condition:
                return eval(condition.replace("severity", f"'{alert.severity.value}'"))
            elif "alert_type" in condition:
                return eval(condition.replace("alert_type", f"'{alert.alert_type}'"))
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating custom condition '{condition}': {e}")
            return False
    
    async def _trigger_notifications(self, alert: WebSocketAlert, rule: AlertRule) -> None:
        """Trigger notifications for alert rule."""
        for channel in rule.notification_channels:
            try:
                success = False
                
                if channel == NotificationChannel.EMAIL:
                    success = await self._send_email_notification(alert, rule.notification_channels)
                elif channel == NotificationChannel.WEBHOOK:
                    success = await self._send_webhook_notification(alert, rule.notification_channels)
                elif channel == NotificationChannel.DISCORD:
                    success = await self._send_discord_notification(alert, rule.notification_channels)
                elif channel == NotificationChannel.SLACK:
                    success = await self._send_slack_notification(alert, rule.notification_channels)
                elif channel == NotificationChannel.PAGERDUTY:
                    success = await self._send_pagerduty_notification(alert, rule.notification_channels)
                elif channel == NotificationChannel.CONSOLE:
                    success = await self._send_console_notification(alert, rule.notification_channels)
                
                if success:
                    self._log_action("notification_sent", {
                        "alert_id": alert.alert_id,
                        "channel": channel.value,
                        "rule_id": rule.rule_id
                    })
                else:
                    self._log_action("notification_failed", {
                        "alert_id": alert.alert_id,
                        "channel": channel.value,
                        "rule_id": rule.rule_id
                    })
                    
            except Exception as e:
                logger.error(f"Error sending notification via {channel.value}: {e}")
    
    async def _send_email_notification(self, alert: WebSocketAlert, channels: List[NotificationChannel]) -> bool:
        """Send email notification."""
        if not self.config.email_config:
            return False
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.config.email_config['from_email']
            msg['To'] = self.config.email_config['to_email']
            msg['Subject'] = f"WebSocket Alert: {alert.alert_type}"
            
            body = self._format_email_body(alert)
            msg.attach(MimeText(body, 'html'))
            
            server = smtplib.SMTP(
                self.config.email_config['smtp_host'],
                self.config.email_config['smtp_port']
            )
            server.starttls()
            server.login(
                self.config.email_config['username'],
                self.config.email_config['password']
            )
            
            text = msg.as_string()
            server.sendmail(
                self.config.email_config['from_email'],
                self.config.email_config['to_email'],
                text
            )
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
    
    async def _send_webhook_notification(self, alert: WebSocketAlert, channels: List[NotificationChannel]) -> bool:
        """Send webhook notification."""
        if not self.config.webhook_config:
            return False
        
        try:
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "websocket_monitoring"
            }
            
            response = requests.post(
                self.config.webhook_config['url'],
                json=payload,
                headers=self.config.webhook_config.get('headers', {}),
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False
    
    async def _send_discord_notification(self, alert: WebSocketAlert, channels: List[NotificationChannel]) -> bool:
        """Send Discord notification."""
        if not self.config.discord_config:
            return False
        
        try:
            embed = {
                "title": f"WebSocket Alert: {alert.alert_type}",
                "description": alert.message,
                "color": self._get_discord_color(alert.severity),
                "fields": [
                    {"name": "Severity", "value": alert.severity.value.upper(), "inline": True},
                    {"name": "Endpoint", "value": alert.endpoint, "inline": True},
                    {"name": "Timestamp", "value": alert.triggered_at.isoformat(), "inline": False}
                ],
                "timestamp": alert.triggered_at.isoformat()
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.config.discord_config['webhook_url'],
                json=payload,
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")
            return False
    
    async def _send_slack_notification(self, alert: WebSocketAlert, channels: List[NotificationChannel]) -> bool:
        """Send Slack notification."""
        if not self.config.slack_config:
            return False
        
        try:
            color = self._get_slack_color(alert.severity)
            
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"WebSocket Alert: {alert.alert_type}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                            {"title": "Endpoint", "value": alert.endpoint, "short": True},
                            {"title": "Timestamp", "value": alert.triggered_at.isoformat(), "short": False}
                        ],
                        "ts": int(alert.triggered_at.timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.config.slack_config['webhook_url'],
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False
    
    async def _send_pagerduty_notification(self, alert: WebSocketAlert, channels: List[NotificationChannel]) -> bool:
        """Send PagerDuty notification."""
        if not self.config.pagerduty_config:
            return False
        
        try:
            payload = {
                "routing_key": self.config.pagerduty_config['routing_key'],
                "event_action": "trigger",
                "dedup_key": alert.alert_id,
                "payload": {
                    "summary": f"WebSocket Alert: {alert.alert_type}",
                    "source": alert.endpoint,
                    "severity": alert.severity.value,
                    "custom_details": {
                        "message": alert.message,
                        "alert_type": alert.alert_type,
                        "dimensions": {dim.value: data for dim, data in alert.dimensions.items()},
                        "metadata": alert.metadata
                    }
                }
            }
            
            response = requests.post(
                "https://events.pagerduty.com/v2/enqueue",
                json=payload,
                timeout=10
            )
            
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"PagerDuty notification failed: {e}")
            return False
    
    async def _send_console_notification(self, alert: WebSocketAlert, channels: List[NotificationChannel]) -> bool:
        """Send console notification."""
        try:
            print(f"\n🚨 WEBSOCKET ALERT 🚨")
            print(f"Type: {alert.alert_type}")
            print(f"Severity: {alert.severity.value.upper()}")
            print(f"Endpoint: {alert.endpoint}")
            print(f"Message: {alert.message}")
            print(f"Timestamp: {alert.triggered_at.isoformat()}")
            print(f"Dimensions: {len(alert.dimensions)}")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Console notification failed: {e}")
            return False
    
    def _format_email_body(self, alert: WebSocketAlert) -> str:
        """Format email body."""
        html = f"""
        <html>
        <body>
            <h2>WebSocket Alert</h2>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Alert Type</strong></td><td>{alert.alert_type}</td></tr>
                <tr><td><strong>Severity</strong></td><td>{alert.severity.value.upper()}</td></tr>
                <tr><td><strong>Endpoint</strong></td><td>{alert.endpoint}</td></tr>
                <tr><td><strong>Message</strong></td><td>{alert.message}</td></tr>
                <tr><td><strong>Timestamp</strong></td><td>{alert.triggered_at.isoformat()}</td></tr>
            </table>
            
            <h3>Dimensions</h3>
            <ul>
        """
        
        for dim, data in alert.dimensions.items():
            html += f"<li><strong>{dim.value}:</strong> {data}</li>"
        
        html += """
            </ul>
            
            <h3>Metadata</h3>
            <ul>
        """
        
        for key, value in alert.metadata.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        
        html += """
            </ul>
        </body>
        </html>
        """
        
        return html
    
    def _get_discord_color(self, severity: AlertSeverity) -> int:
        """Get Discord embed color for severity."""
        colors = {
            AlertSeverity.LOW: 0x00ff00,      # Green
            AlertSeverity.MEDIUM: 0xffff00,    # Yellow
            AlertSeverity.HIGH: 0xff8800,      # Orange
            AlertSeverity.CRITICAL: 0xff0000   # Red
        }
        return colors.get(severity, 0x808080)  # Gray default
    
    def _get_slack_color(self, severity: AlertSeverity) -> str:
        """Get Slack color for severity."""
        colors = {
            AlertSeverity.LOW: "good",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.HIGH: "danger",
            AlertSeverity.CRITICAL: "danger"
        }
        return colors.get(severity, "good")
    
    def _is_in_cooldown(self, rule_id: str, cooldown_minutes: int) -> bool:
        """Check if rule is in cooldown period."""
        if rule_id not in self._last_notification_times:
            return False
        
        last_time = self._last_notification_times[rule_id]
        cooldown_period = timedelta(minutes=cooldown_minutes)
        
        return (datetime.utcnow() - last_time) < cooldown_period
    
    async def _trigger_escalation_callbacks(self, alert: WebSocketAlert, escalation_level: EscalationLevel) -> None:
        """Trigger escalation callbacks."""
        for callback in self._escalation_callbacks:
            try:
                callback(alert, escalation_level)
            except Exception as e:
                logger.error(f"Escalation callback error: {e}")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="critical_alerts",
                name="Critical WebSocket Alerts",
                condition="severity == critical",
                severity=AlertSeverity.CRITICAL,
                escalation_level=EscalationLevel.IMMEDIATE,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.PAGERDUTY, NotificationChannel.CONSOLE],
                cooldown_minutes=0
            ),
            AlertRule(
                rule_id="high_alerts",
                name="High Severity WebSocket Alerts",
                condition="severity == high",
                severity=AlertSeverity.HIGH,
                escalation_level=EscalationLevel.LEVEL_1,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.CONSOLE],
                cooldown_minutes=5
            ),
            AlertRule(
                rule_id="connection_failures",
                name="WebSocket Connection Failures",
                condition="alert_type == connection_failure",
                severity=AlertSeverity.HIGH,
                escalation_level=EscalationLevel.LEVEL_1,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.DISCORD, NotificationChannel.CONSOLE],
                cooldown_minutes=10
            ),
            AlertRule(
                rule_id="high_latency",
                name="High WebSocket Latency",
                condition="alert_type == high_latency",
                severity=AlertSeverity.MEDIUM,
                escalation_level=EscalationLevel.LEVEL_2,
                notification_channels=[NotificationChannel.SLACK, NotificationChannel.CONSOLE],
                cooldown_minutes=15
            ),
            AlertRule(
                rule_id="tunnel_health",
                name="Tunnel Health Degradation",
                condition="alert_type == tunnel_health_degraded",
                severity=AlertSeverity.CRITICAL,
                escalation_level=EscalationLevel.IMMEDIATE,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.PAGERDUTY, NotificationChannel.CONSOLE],
                cooldown_minutes=0
            ),
            AlertRule(
                rule_id="error_1033",
                name="Error 1033 Detection",
                condition="alert_type == error_1033_detected",
                severity=AlertSeverity.CRITICAL,
                escalation_level=EscalationLevel.IMMEDIATE,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.PAGERDUTY, NotificationChannel.CONSOLE],
                cooldown_minutes=0
            ),
            AlertRule(
                rule_id="bot_protection",
                name="Bot Protection Triggers",
                condition="alert_type == bot_protection_triggers",
                severity=AlertSeverity.MEDIUM,
                escalation_level=EscalationLevel.LEVEL_2,
                notification_channels=[NotificationChannel.SLACK, NotificationChannel.CONSOLE],
                cooldown_minutes=30
            )
        ]
        
        for rule in default_rules:
            self._alert_rules[rule.rule_id] = rule
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '5.0',
            'action': f'alerting_system_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))


# Global alerting system instance
_global_alerting_system: Optional[WebSocketAlertingSystem] = None


async def get_global_alerting_system() -> WebSocketAlertingSystem:
    """Get global alerting system instance."""
    global _global_alerting_system
    if _global_alerting_system is None:
        _global_alerting_system = WebSocketAlertingSystem()
    return _global_alerting_system


async def process_global_alert(alert: WebSocketAlert) -> None:
    """Process alert through global alerting system."""
    alerting_system = await get_global_alerting_system()
    await alerting_system.process_alert(alert)