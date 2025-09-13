"""
Enhanced Observability Manager Services

This module was extracted from enhanced_observability_manager.py
as part of RM-DDD compliance refactoring.
"""

import time
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus
from .comprehensive_monitoring_system import ComprehensiveMonitoringSystem

class EnhancedObservabilityManager(ReflectiveModule):
    """
    Enhanced observability manager with actionable alerts and distributed tracing
    Extends comprehensive monitoring with advanced observability features
    """

    def __init__(self):
        super().__init__('enhanced_observability_manager')
        self.monitoring_system = ComprehensiveMonitoringSystem()
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = []
        self.notification_handlers = {}
        self.active_traces = {}
        self.trace_history = []
        self.trace_sampling_rate = 0.1
        self.dashboards = {}
        self.dashboard_configs = {}
        self.observability_metrics = {'alerts_triggered': 0, 'alerts_resolved': 0, 'traces_created': 0, 'average_alert_resolution_time': 0.0, 'dashboard_views': 0}
        self.alert_evaluation_interval = 60
        self.trace_retention_hours = 24
        self.alert_retention_days = 30
        self._initialize_default_alert_rules()
        self._start_alert_evaluation()
        self._update_health_indicator('enhanced_observability_manager', HealthStatus.HEALTHY, 'operational', 'Enhanced observability manager ready for advanced monitoring')

    def get_module_status(self) -> Dict[str, Any]:
        """Enhanced observability manager status"""
        return {'module_name': self.module_name, 'status': 'operational' if self.is_healthy() else 'degraded', 'active_alerts': len([a for a in self.active_alerts.values() if a.status == AlertStatus.ACTIVE]), 'alert_rules': len(self.alert_rules), 'active_traces': len(self.active_traces), 'dashboards': len(self.dashboards), 'alerts_triggered': self.observability_metrics['alerts_triggered'], 'traces_created': self.observability_metrics['traces_created']}

    def is_healthy(self) -> bool:
        """Health assessment for enhanced observability"""
        return self.monitoring_system.is_healthy() and len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]) == 0 and (not self._degradation_active)

    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for enhanced observability"""
        return {'alert_status': {'total_rules': len(self.alert_rules), 'active_alerts': len([a for a in self.active_alerts.values() if a.status == AlertStatus.ACTIVE]), 'critical_alerts': len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]), 'unacknowledged_alerts': len([a for a in self.active_alerts.values() if a.status == AlertStatus.ACTIVE])}, 'tracing_status': {'active_traces': len(self.active_traces), 'sampling_rate': self.trace_sampling_rate, 'traces_per_hour': len([t for t in self.trace_history if (datetime.now() - t.start_time).total_seconds() < 3600])}, 'dashboard_status': {'total_dashboards': len(self.dashboards), 'dashboard_views': self.observability_metrics['dashboard_views']}, 'performance_metrics': self.observability_metrics}

    def _get_primary_responsibility(self) -> str:
        """Single responsibility: enhanced observability and actionable alerting"""
        return 'enhanced_observability_and_actionable_alerting'

    def create_alert_rule(self, rule: AlertRule) -> Dict[str, Any]:
        """
        Create new alert rule for monitoring metrics
        Implements actionable alerting with resolution guidance
        """
        if not self._validate_alert_rule(rule):
            raise ValueError(f'Invalid alert rule configuration: {rule.rule_id}')
        self.alert_rules[rule.rule_id] = rule
        self.logger.info(f'Alert rule created: {rule.name} ({rule.rule_id})')
        return {'success': True, 'rule_id': rule.rule_id, 'name': rule.name, 'severity': rule.severity.value, 'enabled': rule.enabled}

    def trigger_alert(self, rule_id: str, metric_value: float, context: Dict[str, Any]=None) -> Dict[str, Any]:
        """
        Trigger alert based on rule evaluation
        """
        if rule_id not in self.alert_rules:
            raise ValueError(f'Alert rule not found: {rule_id}')
        rule = self.alert_rules[rule_id]
        existing_alert = self._find_active_alert(rule_id)
        if existing_alert:
            return {'message': 'Alert already active', 'alert_id': existing_alert.alert_id}
        alert = Alert(alert_id=str(uuid.uuid4()), rule_id=rule_id, title=f'{rule.name} - Threshold Exceeded', description=f'{rule.description} (Value: {metric_value}, Threshold: {rule.threshold_value})', severity=rule.severity, status=AlertStatus.ACTIVE, triggered_at=datetime.now(), metric_value=metric_value, threshold_value=rule.threshold_value, resolution_guidance=self._generate_resolution_guidance(rule, metric_value, context), tags=rule.tags.copy())
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        self.observability_metrics['alerts_triggered'] += 1
        self._send_alert_notifications(alert)
        self.logger.warning(f'Alert triggered: {alert.title} (ID: {alert.alert_id})')
        return {'success': True, 'alert_id': alert.alert_id, 'severity': alert.severity.value, 'resolution_guidance': alert.resolution_guidance}

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str, notes: str='') -> Dict[str, Any]:
        """
        Acknowledge active alert
        """
        if alert_id not in self.active_alerts:
            return {'error': 'Alert not found or already resolved'}
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by
        if notes:
            alert.logs.append({'timestamp': datetime.now().isoformat(), 'type': 'acknowledgment', 'message': notes, 'user': acknowledged_by})
        self.logger.info(f'Alert acknowledged: {alert.title} by {acknowledged_by}')
        return {'success': True, 'alert_id': alert_id, 'acknowledged_by': acknowledged_by, 'acknowledged_at': alert.acknowledged_at.isoformat()}

    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str='') -> Dict[str, Any]:
        """
        Resolve active alert
        """
        if alert_id not in self.active_alerts:
            return {'error': 'Alert not found'}
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        resolution_time = (alert.resolved_at - alert.triggered_at).total_seconds()
        self._update_resolution_metrics(resolution_time)
        alert.logs.append({'timestamp': datetime.now().isoformat(), 'type': 'resolution', 'message': resolution_notes, 'user': resolved_by, 'resolution_time_seconds': resolution_time})
        del self.active_alerts[alert_id]
        self.observability_metrics['alerts_resolved'] += 1
        self.logger.info(f'Alert resolved: {alert.title} by {resolved_by} (Resolution time: {resolution_time:.1f}s)')
        return {'success': True, 'alert_id': alert_id, 'resolved_by': resolved_by, 'resolution_time_seconds': resolution_time}

    def start_trace(self, operation_name: str, service_name: str, parent_span_id: Optional[str]=None, tags: Dict[str, Any]=None) -> str:
        """
        Start new distributed trace span
        """
        if not self._should_sample_trace():
            return ''
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id or str(uuid.uuid4())
        span = TraceSpan(span_id=span_id, trace_id=trace_id, parent_span_id=parent_span_id, operation_name=operation_name, service_name=service_name, start_time=datetime.now(), tags=tags or {})
        self.active_traces[span_id] = span
        self.observability_metrics['traces_created'] += 1
        return span_id

    def finish_trace(self, span_id: str, status: str='ok', tags: Dict[str, Any]=None) -> Dict[str, Any]:
        """
        Finish distributed trace span
        """
        if not span_id or span_id not in self.active_traces:
            return {'error': 'Trace span not found'}
        span = self.active_traces[span_id]
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        if tags:
            span.tags.update(tags)
        self.trace_history.append(span)
        del self.active_traces[span_id]
        self._cleanup_old_traces()
        return {'success': True, 'span_id': span_id, 'duration_ms': span.duration_ms, 'status': status}

    def add_trace_log(self, span_id: str, level: str, message: str, fields: Dict[str, Any]=None) -> Dict[str, Any]:
        """
        Add log entry to trace span
        """
        if not span_id or span_id not in self.active_traces:
            return {'error': 'Trace span not found'}
        span = self.active_traces[span_id]
        log_entry = {'timestamp': datetime.now().isoformat(), 'level': level, 'message': message, 'fields': fields or {}}
        span.logs.append(log_entry)
        return {'success': True, 'log_added': True}

    def create_dashboard(self, dashboard_id: str, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create operational dashboard configuration
        """
        dashboard_config = {'id': dashboard_id, 'name': name, 'created_at': datetime.now().isoformat(), 'panels': config.get('panels', []), 'refresh_interval': config.get('refresh_interval', 30), 'time_range': config.get('time_range', '1h'), 'tags': config.get('tags', [])}
        self.dashboard_configs[dashboard_id] = dashboard_config
        dashboard_data = self._generate_dashboard_data(dashboard_config)
        self.dashboards[dashboard_id] = dashboard_data
        self.logger.info(f'Dashboard created: {name} ({dashboard_id})')
        return {'success': True, 'dashboard_id': dashboard_id, 'name': name, 'panels': len(dashboard_config['panels'])}

    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get current dashboard data
        """
        if dashboard_id not in self.dashboard_configs:
            return {'error': 'Dashboard not found'}
        self.observability_metrics['dashboard_views'] += 1
        config = self.dashboard_configs[dashboard_id]
        dashboard_data = self._generate_dashboard_data(config)
        self.dashboards[dashboard_id] = dashboard_data
        return dashboard_data

    def get_observability_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive observability analytics
        """
        return {'alert_analytics': {'total_rules': len(self.alert_rules), 'active_alerts': len([a for a in self.active_alerts.values() if a.status == AlertStatus.ACTIVE]), 'alerts_by_severity': self._get_alerts_by_severity(), 'average_resolution_time': self.observability_metrics['average_alert_resolution_time'], 'alert_trends': self._analyze_alert_trends()}, 'tracing_analytics': {'total_traces': self.observability_metrics['traces_created'], 'active_traces': len(self.active_traces), 'sampling_rate': self.trace_sampling_rate, 'average_trace_duration': self._calculate_average_trace_duration(), 'trace_error_rate': self._calculate_trace_error_rate()}, 'dashboard_analytics': {'total_dashboards': len(self.dashboards), 'dashboard_views': self.observability_metrics['dashboard_views'], 'most_viewed_dashboards': self._get_most_viewed_dashboards()}, 'system_health_overview': {'overall_health_score': self._calculate_overall_health_score(), 'critical_issues': self._get_critical_issues(), 'performance_trends': self._analyze_performance_trends(), 'recommendations': self._generate_observability_recommendations()}}
