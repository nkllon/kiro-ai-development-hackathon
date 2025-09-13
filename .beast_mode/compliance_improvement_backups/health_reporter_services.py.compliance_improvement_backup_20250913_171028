"""
Health Reporter Services

This module was extracted from health_reporter.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
from .base import DomainSystemComponent
from .models import Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics, IssueSeverity, IssueCategory, HealthStatusCollection
from .exceptions import HealthReportError, AlertingError
from .config import get_config
from ..utils.enum_serialization import SerializationHandler
from ..utils.enum_serialization import make_enum_json_serializable

class AlertManager:
    """
    Manages health alerting with configurable rules and channels
    """

    def __init__(self, config: Optional[Dict[str, Any]]=None):
        self.config = config or {}
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_history = []
        self.cooldown_tracker = {}
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default alerting rules"""
        default_rules = [AlertRule(name='critical_health_score', condition='threshold', severity=AlertSeverity.CRITICAL, channels=[AlertChannel.LOG, AlertChannel.CONSOLE], threshold_value=0.3, metric_name='overall_health_score', cooldown_minutes=30), AlertRule(name='degrading_trend', condition='trend', severity=AlertSeverity.HIGH, channels=[AlertChannel.LOG], cooldown_minutes=120), AlertRule(name='circular_dependencies', condition='pattern', severity=AlertSeverity.HIGH, channels=[AlertChannel.LOG, AlertChannel.CONSOLE], cooldown_minutes=60)]
        self.alert_rules.extend(default_rules)

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules.append(rule)

    def evaluate_alerts(self, health_statuses: HealthStatusCollection, trends: Dict[str, List[HealthTrend]]) -> List[Alert]:
        """Evaluate all alert rules and generate alerts"""
        new_alerts = []
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            if self._is_in_cooldown(rule.name):
                continue
            if rule.condition == 'threshold':
                alerts = self._evaluate_threshold_rule(rule, health_statuses)
            elif rule.condition == 'trend':
                alerts = self._evaluate_trend_rule(rule, trends)
            elif rule.condition == 'pattern':
                alerts = self._evaluate_pattern_rule(rule, health_statuses)
            else:
                continue
            new_alerts.extend(alerts)
            if alerts:
                self.cooldown_tracker[rule.name] = datetime.now()
        for alert in new_alerts:
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
        return new_alerts

    def _evaluate_threshold_rule(self, rule: AlertRule, health_statuses: HealthStatusCollection) -> List[Alert]:
        """Evaluate threshold-based alert rule"""
        alerts = []
        for domain_name, health_status in health_statuses.items():
            if rule.domain_pattern and rule.domain_pattern not in domain_name:
                continue
            metric_value = self._get_metric_value(health_status, rule.metric_name)
            if metric_value is None:
                continue
            if rule.threshold_value is not None and metric_value < rule.threshold_value:
                alert = Alert(id=f'{rule.name}_{domain_name}_{int(time.time())}', rule_name=rule.name, severity=rule.severity, title=f'Health threshold exceeded: {domain_name}', description=f'{rule.metric_name} is {metric_value:.2f}, below threshold {rule.threshold_value}', domain_name=domain_name, metric_value=metric_value, threshold_value=rule.threshold_value, created_at=datetime.now())
                alerts.append(alert)
        return alerts

    def _evaluate_trend_rule(self, rule: AlertRule, trends: Dict[str, List[HealthTrend]]) -> List[Alert]:
        """Evaluate trend-based alert rule"""
        alerts = []
        for domain_name, domain_trends in trends.items():
            if rule.domain_pattern and rule.domain_pattern not in domain_name:
                continue
            degrading_trends = [t for t in domain_trends if t.trend_direction == 'degrading' and t.trend_strength > 0.2]
            if degrading_trends:
                trend_metrics = [t.metric_name for t in degrading_trends]
                avg_trend_strength = sum((t.trend_strength for t in degrading_trends)) / len(degrading_trends)
                alert = Alert(id=f'{rule.name}_{domain_name}_{int(time.time())}', rule_name=rule.name, severity=rule.severity, title=f'Degrading health trend: {domain_name}', description=f"Degrading trends detected in: {', '.join(trend_metrics)}", domain_name=domain_name, metric_value=avg_trend_strength, threshold_value=0.2, created_at=datetime.now())
                alerts.append(alert)
        return alerts

    def _evaluate_pattern_rule(self, rule: AlertRule, health_statuses: HealthStatusCollection) -> List[Alert]:
        """Evaluate pattern-based alert rule"""
        alerts = []
        if rule.name == 'circular_dependencies':
            for domain_name, health_status in health_statuses.items():
                circular_issues = [issue for issue in health_status.issues if 'circular' in issue.description.lower()]
                if circular_issues:
                    issue_count = len(circular_issues)
                    alert = Alert(id=f'{rule.name}_{domain_name}_{int(time.time())}', rule_name=rule.name, severity=rule.severity, title=f'Circular dependencies detected: {domain_name}', description=f'Found {issue_count} circular dependency issues', domain_name=domain_name, metric_value=float(issue_count), threshold_value=1.0, created_at=datetime.now())
                    alerts.append(alert)
        return alerts

    def _get_metric_value(self, health_status: HealthStatus, metric_name: str) -> Optional[float]:
        """Extract metric value from health status"""
        if not metric_name:
            return None
        metrics = health_status.metrics
        metric_map = {'overall_health_score': metrics.overall_health_score, 'dependency_health_score': metrics.dependency_health_score, 'pattern_coverage_score': metrics.pattern_coverage_score, 'file_accessibility_score': metrics.file_accessibility_score, 'makefile_integration_score': metrics.makefile_integration_score}
        return metric_map.get(metric_name)

    def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if rule is in cooldown period"""
        if rule_name not in self.cooldown_tracker:
            return False
        rule = next((r for r in self.alert_rules if r.name == rule_name), None)
        if not rule:
            return False
        last_alert_time = self.cooldown_tracker[rule_name]
        cooldown_end = last_alert_time + timedelta(minutes=rule.cooldown_minutes)
        return datetime.now() < cooldown_end

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an active alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged_at = datetime.now()
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            return True
        return False

    def get_active_alerts(self, severity: Optional[AlertSeverity]=None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)
