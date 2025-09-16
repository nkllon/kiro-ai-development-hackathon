"""
Alert System - Real-time alerting for critical issues
"""

import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    """Alert notification"""
    id: str
    timestamp: datetime
    level: AlertLevel
    source: str
    message: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    level: AlertLevel
    message_template: str
    cooldown_seconds: int = 300  # 5 minutes default cooldown
    enabled: bool = True


class AlertSystem:
    """Real-time alerting system for health monitoring"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Initialize default alert rules
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default alert rules"""
        
        # High CPU usage
        self.add_rule(AlertRule(
            name="high_cpu_usage",
            condition=lambda metrics: metrics.get('cpu_percent', 0) > 90,
            level=AlertLevel.CRITICAL,
            message_template="High CPU usage detected: {cpu_percent}%",
            cooldown_seconds=300
        ))
        
        # High memory usage
        self.add_rule(AlertRule(
            name="high_memory_usage",
            condition=lambda metrics: metrics.get('memory_percent', 0) > 85,
            level=AlertLevel.WARNING,
            message_template="High memory usage detected: {memory_percent}%",
            cooldown_seconds=300
        ))
        
        # Low disk space
        self.add_rule(AlertRule(
            name="low_disk_space",
            condition=lambda metrics: metrics.get('disk_usage_percent', 0) > 95,
            level=AlertLevel.CRITICAL,
            message_template="Low disk space: {disk_usage_percent}% used",
            cooldown_seconds=600
        ))
        
        # Poor Makefile health
        self.add_rule(AlertRule(
            name="poor_makefile_health",
            condition=lambda metrics: metrics.get('health_score', 1.0) < 0.5,
            level=AlertLevel.WARNING,
            message_template="Poor Makefile health: {health_score}",
            cooldown_seconds=600
        ))
        
        # Critical Makefile health
        self.add_rule(AlertRule(
            name="critical_makefile_health",
            condition=lambda metrics: metrics.get('health_score', 1.0) < 0.3,
            level=AlertLevel.CRITICAL,
            message_template="Critical Makefile health: {health_score}",
            cooldown_seconds=300
        ))
        
        # Circular dependencies detected
        self.add_rule(AlertRule(
            name="circular_dependencies",
            condition=lambda metrics: metrics.get('cycle_count', 0) > 0,
            level=AlertLevel.WARNING,
            message_template="Circular dependencies detected: {cycle_count} cycles",
            cooldown_seconds=900
        ))
        
        # High analysis time
        self.add_rule(AlertRule(
            name="slow_analysis",
            condition=lambda metrics: metrics.get('analysis_time_ms', 0) > 5000,
            level=AlertLevel.WARNING,
            message_template="Slow analysis performance: {analysis_time_ms}ms",
            cooldown_seconds=600
        ))
        
        # Memory leak detection
        self.add_rule(AlertRule(
            name="memory_leak",
            condition=lambda metrics: metrics.get('memory_usage_mb', 0) > 1000,
            level=AlertLevel.WARNING,
            message_template="High memory usage: {memory_usage_mb}MB",
            cooldown_seconds=300
        ))
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add a new alert rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove an alert rule by name"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against alert rules and generate alerts"""
        new_alerts = []
        current_time = datetime.now()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            last_alert_time = self.last_alert_times.get(rule.name)
            if last_alert_time:
                time_since_last = (current_time - last_alert_time).total_seconds()
                if time_since_last < rule.cooldown_seconds:
                    continue
            
            # Check condition
            try:
                if rule.condition(metrics):
                    alert = self._create_alert(rule, metrics, current_time)
                    new_alerts.append(alert)
                    self.last_alert_times[rule.name] = current_time
            except Exception as e:
                print(f"Error checking alert rule {rule.name}: {e}")
        
        # Store new alerts
        self.alerts.extend(new_alerts)
        self.alert_history.extend(new_alerts)
        
        # Keep only last 1000 alerts in history
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        return new_alerts
    
    def _create_alert(self, rule: AlertRule, metrics: Dict[str, Any], 
                     timestamp: datetime) -> Alert:
        """Create a new alert from rule and metrics"""
        alert_id = f"{rule.name}_{int(timestamp.timestamp())}"
        
        # Format message with metrics
        try:
            message = rule.message_template.format(**metrics)
        except KeyError:
            message = rule.message_template
        
        return Alert(
            id=alert_id,
            timestamp=timestamp,
            level=rule.level,
            source=rule.name,
            message=message,
            details=metrics.copy()
        )
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all unresolved alerts"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts filtered by severity level"""
        return [alert for alert in self.alerts if alert.level == level and not alert.resolved]
    
    def get_critical_alerts(self) -> List[Alert]:
        """Get all critical and emergency alerts"""
        return [alert for alert in self.alerts 
                if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY] 
                and not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alert status"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "total_active_alerts": len(active_alerts),
            "alerts_by_level": {},
            "alerts_by_source": {},
            "oldest_alert": None,
            "newest_alert": None
        }
        
        # Count by level
        for level in AlertLevel:
            count = len([a for a in active_alerts if a.level == level])
            summary["alerts_by_level"][level.value] = count
        
        # Count by source
        for alert in active_alerts:
            source = alert.source
            summary["alerts_by_source"][source] = summary["alerts_by_source"].get(source, 0) + 1
        
        # Find oldest and newest
        if active_alerts:
            sorted_alerts = sorted(active_alerts, key=lambda a: a.timestamp)
            summary["oldest_alert"] = {
                "id": sorted_alerts[0].id,
                "timestamp": sorted_alerts[0].timestamp.isoformat(),
                "message": sorted_alerts[0].message
            }
            summary["newest_alert"] = {
                "id": sorted_alerts[-1].id,
                "timestamp": sorted_alerts[-1].timestamp.isoformat(),
                "message": sorted_alerts[-1].message
            }
        
        return summary
    
    def clear_resolved_alerts(self) -> int:
        """Remove all resolved alerts and return count of removed alerts"""
        resolved_count = len([a for a in self.alerts if a.resolved])
        self.alerts = [alert for alert in self.alerts if not alert.resolved]
        return resolved_count
    
    def export_alerts(self, output_path: str, include_resolved: bool = False) -> bool:
        """Export alerts to file"""
        try:
            alerts_to_export = self.alerts
            if include_resolved:
                alerts_to_export = self.alert_history
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_alerts": len(alerts_to_export),
                "include_resolved": include_resolved,
                "alerts": [asdict(alert) for alert in alerts_to_export]
            }
            
            # Convert datetime objects to strings for JSON serialization
            for alert in export_data["alerts"]:
                alert["timestamp"] = alert["timestamp"].isoformat() if isinstance(alert["timestamp"], datetime) else alert["timestamp"]
                if alert.get("resolved_at"):
                    alert["resolved_at"] = alert["resolved_at"].isoformat() if isinstance(alert["resolved_at"], datetime) else alert["resolved_at"]
                alert["level"] = alert["level"].value if hasattr(alert["level"], 'value') else alert["level"]
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting alerts: {e}")
            return False
    
    def get_alert_statistics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics over time window"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        recent_alerts = [alert for alert in self.alert_history 
                        if alert.timestamp >= cutoff_time]
        
        if not recent_alerts:
            return {"error": f"No alerts in last {time_window_hours} hours"}
        
        # Calculate statistics
        total_alerts = len(recent_alerts)
        resolved_alerts = len([a for a in recent_alerts if a.resolved])
        
        stats = {
            "time_window_hours": time_window_hours,
            "total_alerts": total_alerts,
            "resolved_alerts": resolved_alerts,
            "unresolved_alerts": total_alerts - resolved_alerts,
            "resolution_rate": (resolved_alerts / total_alerts) * 100 if total_alerts > 0 else 0,
            "alerts_by_level": {},
            "alerts_by_source": {},
            "hourly_distribution": {}
        }
        
        # Count by level
        for level in AlertLevel:
            count = len([a for a in recent_alerts if a.level == level])
            stats["alerts_by_level"][level.value] = count
        
        # Count by source
        for alert in recent_alerts:
            source = alert.source
            stats["alerts_by_source"][source] = stats["alerts_by_source"].get(source, 0) + 1
        
        # Hourly distribution
        for alert in recent_alerts:
            hour = alert.timestamp.hour
            stats["hourly_distribution"][str(hour)] = stats["hourly_distribution"].get(str(hour), 0) + 1
        
        return stats
