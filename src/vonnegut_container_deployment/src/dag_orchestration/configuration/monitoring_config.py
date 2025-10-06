#!/usr/bin/env python3
"""
Monitoring Configuration for DAG Orchestration
==============================================

Configurable monitoring system with metrics collection intervals,
reporting configurations, and alerting policies.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class MetricType(Enum):
    """Types of metrics to collect."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    YAML = "yaml"
    HTML = "html"
    CSV = "csv"
    PROMETHEUS = "prometheus"


@dataclass
class MetricDefinition:
    """Definition of a metric to collect."""
    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = field(default_factory=list)
    unit: str = ""
    enabled: bool = True
    collection_interval: float = 30.0  # seconds
    retention_period: timedelta = field(default_factory=lambda: timedelta(days=7))


@dataclass
class MetricsCollectionConfig:
    """Configuration for metrics collection."""
    enabled: bool = True
    collection_interval: float = 30.0  # seconds
    batch_size: int = 100
    buffer_size: int = 1000
    flush_interval: float = 60.0  # seconds
    compression_enabled: bool = True
    metrics: List[MetricDefinition] = field(default_factory=list)
    custom_collectors: Dict[str, Callable] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Configuration for an alert rule."""
    name: str
    description: str
    metric_name: str
    condition: str  # e.g., "> 0.8", "< 0.1", "== 0"
    severity: AlertSeverity
    threshold_duration: float = 60.0  # seconds
    cooldown_period: float = 300.0  # seconds
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class AlertingConfig:
    """Configuration for alerting system."""
    enabled: bool = True
    evaluation_interval: float = 30.0  # seconds
    notification_timeout: float = 10.0  # seconds
    max_alerts_per_minute: int = 10
    alert_rules: List[AlertRule] = field(default_factory=list)
    notification_channels: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ReportConfig:
    """Configuration for a specific report."""
    name: str
    description: str
    format: ReportFormat
    metrics: List[str]  # Metric names to include
    schedule: str  # Cron-like schedule
    output_path: str
    enabled: bool = True
    include_charts: bool = False
    template_path: Optional[str] = None


@dataclass
class ReportingConfig:
    """Configuration for reporting system."""
    enabled: bool = True
    output_directory: str = "reports"
    retention_period: timedelta = field(default_factory=lambda: timedelta(days=30))
    reports: List[ReportConfig] = field(default_factory=list)
    email_notifications: bool = False
    email_recipients: List[str] = field(default_factory=list)


@dataclass
class MonitoringConfiguration:
    """Complete monitoring system configuration."""
    name: str
    description: str
    metrics_collection: MetricsCollectionConfig
    alerting: AlertingConfig
    reporting: ReportingConfig
    dashboard_enabled: bool = True
    dashboard_port: int = 8080
    api_enabled: bool = True
    api_port: int = 8081
    created_at: datetime = field(default_factory=datetime.now)


class MonitoringConfigManager(ReflectiveModule):
    """
    Manager for monitoring system configurations.
    
    Features:
    - Configurable metrics collection intervals
    - Dynamic alerting rules
    - Flexible reporting schedules
    - Dashboard and API configuration
    - Real-time configuration updates
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "MonitoringConfigManager"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Configuration storage
        self._configurations: Dict[str, MonitoringConfiguration] = {}
        self._current_config: Optional[str] = None
        self._config_history: List[Dict[str, Any]] = []
        
        # Active monitoring state
        self._active_collectors: Dict[str, Any] = {}
        self._active_alerts: Dict[str, Any] = {}
        self._active_reports: Dict[str, Any] = {}
        
        # Initialize default configuration
        self._initialize_default_configuration()
        
        self._logger.info("MonitoringConfigManager initialized")
    
    def _initialize_default_configuration(self) -> None:
        """Initialize default monitoring configuration."""
        
        # Define default metrics
        default_metrics = [
            MetricDefinition(
                name="dag_orchestration_executions_total",
                description="Total number of DAG orchestration executions",
                metric_type=MetricType.COUNTER,
                labels=["status", "strategy"],
                collection_interval=30.0
            ),
            MetricDefinition(
                name="dag_orchestration_execution_duration_seconds",
                description="Duration of DAG orchestration executions",
                metric_type=MetricType.HISTOGRAM,
                labels=["strategy"],
                unit="seconds",
                collection_interval=30.0
            ),
            MetricDefinition(
                name="dag_orchestration_tasks_total",
                description="Total number of tasks executed",
                metric_type=MetricType.COUNTER,
                labels=["status"],
                collection_interval=30.0
            ),
            MetricDefinition(
                name="dag_orchestration_active_workers",
                description="Number of active worker threads",
                metric_type=MetricType.GAUGE,
                collection_interval=10.0
            ),
            MetricDefinition(
                name="dag_orchestration_queue_size",
                description="Number of tasks in execution queue",
                metric_type=MetricType.GAUGE,
                collection_interval=10.0
            ),
            MetricDefinition(
                name="dag_orchestration_resource_usage",
                description="Resource usage metrics",
                metric_type=MetricType.GAUGE,
                labels=["resource_type"],
                unit="percent",
                collection_interval=15.0
            ),
            MetricDefinition(
                name="llm_selection_total",
                description="Total number of LLM selections",
                metric_type=MetricType.COUNTER,
                labels=["provider", "policy"],
                collection_interval=30.0
            ),
            MetricDefinition(
                name="llm_execution_duration_seconds",
                description="Duration of LLM executions",
                metric_type=MetricType.HISTOGRAM,
                labels=["provider"],
                unit="seconds",
                collection_interval=30.0
            ),
            MetricDefinition(
                name="llm_cost_total",
                description="Total cost of LLM usage",
                metric_type=MetricType.COUNTER,
                labels=["provider"],
                unit="dollars",
                collection_interval=60.0
            )
        ]
        
        # Define default alert rules
        default_alerts = [
            AlertRule(
                name="high_execution_failure_rate",
                description="High rate of execution failures",
                metric_name="dag_orchestration_executions_total",
                condition="rate(dag_orchestration_executions_total{status='failed'}[5m]) > 0.1",
                severity=AlertSeverity.WARNING,
                threshold_duration=300.0,
                notification_channels=["email", "slack"]
            ),
            AlertRule(
                name="high_resource_usage",
                description="High resource usage detected",
                metric_name="dag_orchestration_resource_usage",
                condition="> 0.9",
                severity=AlertSeverity.CRITICAL,
                threshold_duration=120.0,
                notification_channels=["email", "slack", "pagerduty"]
            ),
            AlertRule(
                name="long_execution_duration",
                description="Execution taking longer than expected",
                metric_name="dag_orchestration_execution_duration_seconds",
                condition="> 1800",  # 30 minutes
                severity=AlertSeverity.WARNING,
                threshold_duration=60.0,
                notification_channels=["email"]
            ),
            AlertRule(
                name="high_llm_cost",
                description="LLM costs exceeding budget",
                metric_name="llm_cost_total",
                condition="rate(llm_cost_total[1h]) > 10",  # $10/hour
                severity=AlertSeverity.ERROR,
                threshold_duration=300.0,
                notification_channels=["email", "slack"]
            )
        ]
        
        # Define default reports
        default_reports = [
            ReportConfig(
                name="daily_execution_summary",
                description="Daily summary of DAG executions",
                format=ReportFormat.HTML,
                metrics=[
                    "dag_orchestration_executions_total",
                    "dag_orchestration_execution_duration_seconds",
                    "dag_orchestration_tasks_total"
                ],
                schedule="0 9 * * *",  # Daily at 9 AM
                output_path="reports/daily_summary_{date}.html",
                include_charts=True
            ),
            ReportConfig(
                name="weekly_performance_report",
                description="Weekly performance analysis",
                format=ReportFormat.HTML,
                metrics=[
                    "dag_orchestration_execution_duration_seconds",
                    "dag_orchestration_resource_usage",
                    "llm_execution_duration_seconds",
                    "llm_cost_total"
                ],
                schedule="0 9 * * 1",  # Weekly on Monday at 9 AM
                output_path="reports/weekly_performance_{date}.html",
                include_charts=True
            ),
            ReportConfig(
                name="monthly_cost_analysis",
                description="Monthly cost analysis and optimization recommendations",
                format=ReportFormat.HTML,
                metrics=[
                    "llm_cost_total",
                    "llm_selection_total"
                ],
                schedule="0 9 1 * *",  # Monthly on 1st at 9 AM
                output_path="reports/monthly_cost_{date}.html",
                include_charts=True
            )
        ]
        
        # Create default configuration
        default_config = MonitoringConfiguration(
            name="default",
            description="Default monitoring configuration for DAG orchestration",
            metrics_collection=MetricsCollectionConfig(
                enabled=True,
                collection_interval=30.0,
                batch_size=100,
                buffer_size=1000,
                flush_interval=60.0,
                compression_enabled=True,
                metrics=default_metrics
            ),
            alerting=AlertingConfig(
                enabled=True,
                evaluation_interval=30.0,
                notification_timeout=10.0,
                max_alerts_per_minute=10,
                alert_rules=default_alerts,
                notification_channels={
                    "email": {
                        "type": "email",
                        "smtp_server": "localhost",
                        "smtp_port": 587,
                        "recipients": ["admin@example.com"]
                    },
                    "slack": {
                        "type": "slack",
                        "webhook_url": "https://hooks.slack.com/services/...",
                        "channel": "#alerts"
                    }
                }
            ),
            reporting=ReportingConfig(
                enabled=True,
                output_directory="reports",
                retention_period=timedelta(days=30),
                reports=default_reports,
                email_notifications=False,
                email_recipients=["admin@example.com"]
            ),
            dashboard_enabled=True,
            dashboard_port=8080,
            api_enabled=True,
            api_port=8081
        )
        
        self.register_configuration(default_config)
        self._current_config = "default"
    
    def register_configuration(self, config: MonitoringConfiguration) -> None:
        """Register a monitoring configuration."""
        self._configurations[config.name] = config
        self._logger.info(f"Registered monitoring configuration: {config.name}")
    
    def get_configuration(self, name: str) -> MonitoringConfiguration:
        """Get monitoring configuration by name."""
        if name not in self._configurations:
            raise ValueError(f"Configuration '{name}' not found")
        
        return self._configurations[name]
    
    def set_current_configuration(self, name: str) -> None:
        """Set current monitoring configuration."""
        if name not in self._configurations:
            raise ValueError(f"Configuration '{name}' not found")
        
        old_config = self._current_config
        self._current_config = name
        
        # Record configuration change
        change_record = {
            'timestamp': datetime.now(),
            'old_config': old_config,
            'new_config': name,
            'reason': 'manual_change'
        }
        self._config_history.append(change_record)
        
        self._logger.info(f"Changed monitoring configuration from '{old_config}' to '{name}'")
    
    def get_current_configuration(self) -> MonitoringConfiguration:
        """Get current monitoring configuration."""
        if not self._current_config:
            raise ValueError("No current configuration set")
        
        return self.get_configuration(self._current_config)
    
    def update_metrics_collection(self, config_name: str, 
                                updates: Dict[str, Any]) -> None:
        """Update metrics collection configuration."""
        if config_name not in self._configurations:
            raise ValueError(f"Configuration '{config_name}' not found")
        
        config = self._configurations[config_name]
        metrics_config = config.metrics_collection
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(metrics_config, key):
                setattr(metrics_config, key, value)
        
        self._logger.info(f"Updated metrics collection for configuration '{config_name}'")
    
    def add_metric_definition(self, config_name: str, metric: MetricDefinition) -> None:
        """Add a metric definition to configuration."""
        if config_name not in self._configurations:
            raise ValueError(f"Configuration '{config_name}' not found")
        
        config = self._configurations[config_name]
        config.metrics_collection.metrics.append(metric)
        
        self._logger.info(f"Added metric '{metric.name}' to configuration '{config_name}'")
    
    def add_alert_rule(self, config_name: str, alert_rule: AlertRule) -> None:
        """Add an alert rule to configuration."""
        if config_name not in self._configurations:
            raise ValueError(f"Configuration '{config_name}' not found")
        
        config = self._configurations[config_name]
        config.alerting.alert_rules.append(alert_rule)
        
        self._logger.info(f"Added alert rule '{alert_rule.name}' to configuration '{config_name}'")
    
    def add_report_config(self, config_name: str, report_config: ReportConfig) -> None:
        """Add a report configuration."""
        if config_name not in self._configurations:
            raise ValueError(f"Configuration '{config_name}' not found")
        
        config = self._configurations[config_name]
        config.reporting.reports.append(report_config)
        
        self._logger.info(f"Added report '{report_config.name}' to configuration '{config_name}'")
    
    def enable_metric(self, config_name: str, metric_name: str) -> None:
        """Enable a specific metric."""
        config = self.get_configuration(config_name)
        
        for metric in config.metrics_collection.metrics:
            if metric.name == metric_name:
                metric.enabled = True
                self._logger.info(f"Enabled metric '{metric_name}' in configuration '{config_name}'")
                return
        
        raise ValueError(f"Metric '{metric_name}' not found in configuration '{config_name}'")
    
    def disable_metric(self, config_name: str, metric_name: str) -> None:
        """Disable a specific metric."""
        config = self.get_configuration(config_name)
        
        for metric in config.metrics_collection.metrics:
            if metric.name == metric_name:
                metric.enabled = False
                self._logger.info(f"Disabled metric '{metric_name}' in configuration '{config_name}'")
                return
        
        raise ValueError(f"Metric '{metric_name}' not found in configuration '{config_name}'")
    
    def enable_alert_rule(self, config_name: str, rule_name: str) -> None:
        """Enable a specific alert rule."""
        config = self.get_configuration(config_name)
        
        for rule in config.alerting.alert_rules:
            if rule.name == rule_name:
                rule.enabled = True
                self._logger.info(f"Enabled alert rule '{rule_name}' in configuration '{config_name}'")
                return
        
        raise ValueError(f"Alert rule '{rule_name}' not found in configuration '{config_name}'")
    
    def disable_alert_rule(self, config_name: str, rule_name: str) -> None:
        """Disable a specific alert rule."""
        config = self.get_configuration(config_name)
        
        for rule in config.alerting.alert_rules:
            if rule.name == rule_name:
                rule.enabled = False
                self._logger.info(f"Disabled alert rule '{rule_name}' in configuration '{config_name}'")
                return
        
        raise ValueError(f"Alert rule '{rule_name}' not found in configuration '{config_name}'")
    
    def get_active_metrics(self, config_name: Optional[str] = None) -> List[MetricDefinition]:
        """Get list of active (enabled) metrics."""
        config_name = config_name or self._current_config
        if not config_name:
            return []
        
        config = self.get_configuration(config_name)
        return [metric for metric in config.metrics_collection.metrics if metric.enabled]
    
    def get_active_alert_rules(self, config_name: Optional[str] = None) -> List[AlertRule]:
        """Get list of active (enabled) alert rules."""
        config_name = config_name or self._current_config
        if not config_name:
            return []
        
        config = self.get_configuration(config_name)
        return [rule for rule in config.alerting.alert_rules if rule.enabled]
    
    def get_active_reports(self, config_name: Optional[str] = None) -> List[ReportConfig]:
        """Get list of active (enabled) reports."""
        config_name = config_name or self._current_config
        if not config_name:
            return []
        
        config = self.get_configuration(config_name)
        return [report for report in config.reporting.reports if report.enabled]
    
    def create_environment_config(self, environment: str, 
                                base_config: str = "default") -> MonitoringConfiguration:
        """Create environment-specific monitoring configuration."""
        base = self.get_configuration(base_config)
        
        # Environment-specific adjustments
        if environment == "development":
            # More detailed logging, less alerting
            config = MonitoringConfiguration(
                name=f"{environment}",
                description=f"Monitoring configuration for {environment} environment",
                metrics_collection=MetricsCollectionConfig(
                    enabled=True,
                    collection_interval=15.0,  # More frequent collection
                    batch_size=50,
                    buffer_size=500,
                    flush_interval=30.0,
                    compression_enabled=False,  # Easier debugging
                    metrics=base.metrics_collection.metrics.copy()
                ),
                alerting=AlertingConfig(
                    enabled=False,  # Disable alerting in dev
                    evaluation_interval=60.0,
                    notification_timeout=10.0,
                    max_alerts_per_minute=5,
                    alert_rules=[],  # No alerts in dev
                    notification_channels={}
                ),
                reporting=ReportingConfig(
                    enabled=False,  # Disable reporting in dev
                    output_directory="dev_reports",
                    retention_period=timedelta(days=7),
                    reports=[],
                    email_notifications=False,
                    email_recipients=[]
                ),
                dashboard_enabled=True,
                dashboard_port=8080,
                api_enabled=True,
                api_port=8081
            )
        
        elif environment == "production":
            # Full monitoring with all features
            config = MonitoringConfiguration(
                name=f"{environment}",
                description=f"Monitoring configuration for {environment} environment",
                metrics_collection=base.metrics_collection,
                alerting=base.alerting,
                reporting=base.reporting,
                dashboard_enabled=True,
                dashboard_port=8080,
                api_enabled=True,
                api_port=8081
            )
        
        else:  # testing, staging, etc.
            # Moderate monitoring
            config = MonitoringConfiguration(
                name=f"{environment}",
                description=f"Monitoring configuration for {environment} environment",
                metrics_collection=MetricsCollectionConfig(
                    enabled=True,
                    collection_interval=60.0,  # Less frequent collection
                    batch_size=100,
                    buffer_size=1000,
                    flush_interval=120.0,
                    compression_enabled=True,
                    metrics=base.metrics_collection.metrics.copy()
                ),
                alerting=AlertingConfig(
                    enabled=True,
                    evaluation_interval=60.0,
                    notification_timeout=10.0,
                    max_alerts_per_minute=5,
                    alert_rules=[rule for rule in base.alerting.alert_rules 
                               if rule.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]],
                    notification_channels=base.alerting.notification_channels
                ),
                reporting=ReportingConfig(
                    enabled=True,
                    output_directory=f"{environment}_reports",
                    retention_period=timedelta(days=14),
                    reports=[base.reporting.reports[0]],  # Only daily summary
                    email_notifications=False,
                    email_recipients=[]
                ),
                dashboard_enabled=True,
                dashboard_port=8080,
                api_enabled=True,
                api_port=8081
            )
        
        self.register_configuration(config)
        return config
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of all monitoring configurations."""
        summary = {
            'total_configurations': len(self._configurations),
            'current_configuration': self._current_config,
            'configuration_changes': len(self._config_history),
            'configurations': {}
        }
        
        for name, config in self._configurations.items():
            summary['configurations'][name] = {
                'description': config.description,
                'metrics_count': len(config.metrics_collection.metrics),
                'active_metrics': len([m for m in config.metrics_collection.metrics if m.enabled]),
                'alert_rules_count': len(config.alerting.alert_rules),
                'active_alert_rules': len([r for r in config.alerting.alert_rules if r.enabled]),
                'reports_count': len(config.reporting.reports),
                'active_reports': len([r for r in config.reporting.reports if r.enabled]),
                'dashboard_enabled': config.dashboard_enabled,
                'api_enabled': config.api_enabled,
                'created_at': config.created_at.isoformat()
            }
        
        return summary


# Convenience functions
def create_monitoring_config_manager() -> MonitoringConfigManager:
    """Factory function to create monitoring configuration manager."""
    return MonitoringConfigManager()


def create_metric_definition(name: str, description: str, metric_type: MetricType,
                           labels: Optional[List[str]] = None,
                           collection_interval: float = 30.0) -> MetricDefinition:
    """Convenience function to create metric definition."""
    return MetricDefinition(
        name=name,
        description=description,
        metric_type=metric_type,
        labels=labels or [],
        collection_interval=collection_interval
    )


def create_alert_rule(name: str, description: str, metric_name: str,
                     condition: str, severity: AlertSeverity,
                     notification_channels: Optional[List[str]] = None) -> AlertRule:
    """Convenience function to create alert rule."""
    return AlertRule(
        name=name,
        description=description,
        metric_name=metric_name,
        condition=condition,
        severity=severity,
        notification_channels=notification_channels or []
    )