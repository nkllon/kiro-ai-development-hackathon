"""
Health Reporting and Alerting System

This module provides comprehensive health reporting with detailed issue categorization,
health status aggregation, trend analysis, and configurable alerting for critical issues.
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
from .models import (
    Domain, HealthStatus, HealthStatusType, HealthIssue, HealthMetrics,
    IssueSeverity, IssueCategory, HealthStatusCollection
)
from .exceptions import HealthReportError, AlertingError
from .config import get_config


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert delivery channels"""
    LOG = "log"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class HealthTrend:
    """Health trend data over time"""
    domain_name: str
    metric_name: str
    values: List[float]
    timestamps: List[datetime]
    trend_direction: str  # "improving", "degrading", "stable"
    trend_strength: float  # 0.0 to 1.0
    
    
@dataclass
class AlertRule:
    """Configuration for health alerting rules"""
    name: str
    condition: str  # "threshold", "trend", "pattern"
    severity: AlertSeverity
    channels: List[AlertChannel]
    threshold_value: Optional[float] = None
    metric_name: Optional[str] = None
    domain_pattern: Optional[str] = None
    cooldown_minutes: int = 60
    enabled: bool = True


@dataclass
class Alert:
    """Individual health alert"""
    id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    description: str
    domain_name: Optional[str]
    metric_value: Optional[float]
    threshold_value: Optional[float]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

@dataclass
class HealthReport:
    """Comprehensive health report with categorized issues"""
    report_id: str
    generated_at: datetime
    report_type: str  # "full", "summary", "domain_specific", "trend"
    
    # Overall metrics
    total_domains: int
    healthy_domains: int
    degraded_domains: int
    failed_domains: int
    overall_health_score: float
    
    # Issue categorization
    critical_issues: List[HealthIssue]
    warning_issues: List[HealthIssue]
    info_issues: List[HealthIssue]
    
    # Domain-specific data
    domain_health_statuses: Dict[str, HealthStatus]
    domain_trends: Dict[str, List[HealthTrend]]
    
    # Recommendations
    recommendations: List[Dict[str, Any]]
    
    # Metadata
    generation_time_ms: float
    data_freshness: Dict[str, datetime]
    report_config: Dict[str, Any]


class HealthTrendAnalyzer:
    """
    Analyzes health trends over time for predictive insights
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.trend_window_days = self.config.get("trend_window_days", 7)
        self.min_data_points = self.config.get("min_trend_data_points", 3)
        self.trend_threshold = self.config.get("trend_significance_threshold", 0.1)
        
        # Historical data storage (in production, this would be a database)
        self.historical_data = defaultdict(lambda: defaultdict(list))
    
    def record_health_metrics(self, domain_name: str, metrics: HealthMetrics):
        """Record health metrics for trend analysis"""
        timestamp = datetime.now()
        
        # Store key metrics
        metric_values = {
            "overall_health_score": metrics.overall_health_score,
            "dependency_health_score": metrics.dependency_health_score,
            "pattern_coverage_score": metrics.pattern_coverage_score,
            "file_accessibility_score": metrics.file_accessibility_score,
            "makefile_integration_score": metrics.makefile_integration_score
        }
        
        for metric_name, value in metric_values.items():
            self.historical_data[domain_name][metric_name].append((timestamp, value))
            
            # Keep only recent data within trend window
            cutoff_time = timestamp - timedelta(days=self.trend_window_days)
            self.historical_data[domain_name][metric_name] = [
                (ts, val) for ts, val in self.historical_data[domain_name][metric_name]
                if ts >= cutoff_time
            ]
    
    def analyze_domain_trends(self, domain_name: str) -> List[HealthTrend]:
        """Analyze trends for a specific domain"""
        trends = []
        
        if domain_name not in self.historical_data:
            return trends
        
        for metric_name, data_points in self.historical_data[domain_name].items():
            if len(data_points) < self.min_data_points:
                continue
            
            # Extract timestamps and values
            timestamps = [ts for ts, _ in data_points]
            values = [val for _, val in data_points]
            
            # Calculate trend
            trend_direction, trend_strength = self._calculate_trend(values)
            
            trend = HealthTrend(
                domain_name=domain_name,
                metric_name=metric_name,
                values=values,
                timestamps=timestamps,
                trend_direction=trend_direction,
                trend_strength=trend_strength
            )
            trends.append(trend)
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate trend direction and strength using linear regression"""
        if len(values) < 2:
            return "stable", 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        # Calculate linear regression slope
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        
        # Determine trend direction and strength
        abs_slope = abs(slope)
        
        if abs_slope < self.trend_threshold:
            return "stable", abs_slope
        elif slope > 0:
            return "improving", min(abs_slope, 1.0)
        else:
            return "degrading", min(abs_slope, 1.0)
    
    def get_trending_domains(self, trend_type: str = "degrading") -> List[Tuple[str, float]]:
        """Get domains with significant trends"""
        trending_domains = []
        
        for domain_name in self.historical_data:
            trends = self.analyze_domain_trends(domain_name)
            
            # Calculate average trend strength for the domain
            relevant_trends = [t for t in trends if t.trend_direction == trend_type]
            if relevant_trends:
                avg_strength = sum(t.trend_strength for t in relevant_trends) / len(relevant_trends)
                if avg_strength > self.trend_threshold:
                    trending_domains.append((domain_name, avg_strength))
        
        # Sort by trend strength
        trending_domains.sort(key=lambda x: x[1], reverse=True)
        return trending_domains


class AlertManager:
    """
    Manages health alerting with configurable rules and channels
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_history = []
        self.cooldown_tracker = {}
        
        # Load default alert rules
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default alerting rules"""
        default_rules = [
            AlertRule(
                name="critical_health_score",
                condition="threshold",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                threshold_value=0.3,
                metric_name="overall_health_score",
                cooldown_minutes=30
            ),
            AlertRule(
                name="degrading_trend",
                condition="trend",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.LOG],
                cooldown_minutes=120
            ),
            AlertRule(
                name="circular_dependencies",
                condition="pattern",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                cooldown_minutes=60
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules.append(rule)
    
    def evaluate_alerts(self, health_statuses: HealthStatusCollection, 
                       trends: Dict[str, List[HealthTrend]]) -> List[Alert]:
        """Evaluate all alert rules and generate alerts"""
        new_alerts = []
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            if self._is_in_cooldown(rule.name):
                continue
            
            # Evaluate rule based on condition type
            if rule.condition == "threshold":
                alerts = self._evaluate_threshold_rule(rule, health_statuses)
            elif rule.condition == "trend":
                alerts = self._evaluate_trend_rule(rule, trends)
            elif rule.condition == "pattern":
                alerts = self._evaluate_pattern_rule(rule, health_statuses)
            else:
                continue
            
            new_alerts.extend(alerts)
            
            # Update cooldown tracker
            if alerts:
                self.cooldown_tracker[rule.name] = datetime.now()
        
        # Store new alerts
        for alert in new_alerts:
            self.active_alerts[alert.id] = alert
            self.alert_history.append(alert)
        
        return new_alerts
    
    def _evaluate_threshold_rule(self, rule: AlertRule, 
                                health_statuses: HealthStatusCollection) -> List[Alert]:
        """Evaluate threshold-based alert rule"""
        alerts = []
        
        for domain_name, health_status in health_statuses.items():
            if rule.domain_pattern and rule.domain_pattern not in domain_name:
                continue
            
            # Get metric value
            metric_value = self._get_metric_value(health_status, rule.metric_name)
            if metric_value is None:
                continue
            
            # Check threshold
            if rule.threshold_value is not None and metric_value < rule.threshold_value:
                alert = Alert(
                    id=f"{rule.name}_{domain_name}_{int(time.time())}",
                    rule_name=rule.name,
                    severity=rule.severity,
                    title=f"Health threshold exceeded: {domain_name}",
                    description=f"{rule.metric_name} is {metric_value:.2f}, below threshold {rule.threshold_value}",
                    domain_name=domain_name,
                    metric_value=metric_value,
                    threshold_value=rule.threshold_value,
                    created_at=datetime.now()
                )
                alerts.append(alert)
        
        return alerts
    
    def _evaluate_trend_rule(self, rule: AlertRule, 
                           trends: Dict[str, List[HealthTrend]]) -> List[Alert]:
        """Evaluate trend-based alert rule"""
        alerts = []
        
        for domain_name, domain_trends in trends.items():
            if rule.domain_pattern and rule.domain_pattern not in domain_name:
                continue
            
            # Check for degrading trends
            degrading_trends = [t for t in domain_trends 
                              if t.trend_direction == "degrading" and t.trend_strength > 0.2]
            
            if degrading_trends:
                trend_metrics = [t.metric_name for t in degrading_trends]
                alert = Alert(
                    id=f"{rule.name}_{domain_name}_{int(time.time())}",
                    rule_name=rule.name,
                    severity=rule.severity,
                    title=f"Degrading health trend: {domain_name}",
                    description=f"Degrading trends detected in: {', '.join(trend_metrics)}",
                    domain_name=domain_name,
                    created_at=datetime.now()
                )
                alerts.append(alert)
        
        return alerts
    
    def _evaluate_pattern_rule(self, rule: AlertRule, 
                             health_statuses: HealthStatusCollection) -> List[Alert]:
        """Evaluate pattern-based alert rule"""
        alerts = []
        
        # Check for circular dependency patterns
        if rule.name == "circular_dependencies":
            for domain_name, health_status in health_statuses.items():
                circular_issues = [issue for issue in health_status.issues 
                                 if "circular" in issue.description.lower()]
                
                if circular_issues:
                    alert = Alert(
                        id=f"{rule.name}_{domain_name}_{int(time.time())}",
                        rule_name=rule.name,
                        severity=rule.severity,
                        title=f"Circular dependencies detected: {domain_name}",
                        description=f"Found {len(circular_issues)} circular dependency issues",
                        domain_name=domain_name,
                        created_at=datetime.now()
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _get_metric_value(self, health_status: HealthStatus, metric_name: str) -> Optional[float]:
        """Extract metric value from health status"""
        if not metric_name:
            return None
        
        metrics = health_status.metrics
        metric_map = {
            "overall_health_score": metrics.overall_health_score,
            "dependency_health_score": metrics.dependency_health_score,
            "pattern_coverage_score": metrics.pattern_coverage_score,
            "file_accessibility_score": metrics.file_accessibility_score,
            "makefile_integration_score": metrics.makefile_integration_score
        }
        
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
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)
class
 HealthReportGenerator(DomainSystemComponent):
    """
    Generates comprehensive health reports with detailed issue categorization
    """
    
    def __init__(self, health_monitor=None, dependency_analyzer=None, config: Optional[Dict[str, Any]] = None):
        super().__init__("health_report_generator", config)
        
        # Dependencies
        self.health_monitor = health_monitor
        self.dependency_analyzer = dependency_analyzer
        
        # Components
        self.trend_analyzer = HealthTrendAnalyzer(config)
        self.alert_manager = AlertManager(config)
        
        # Configuration
        self.config_obj = get_config()
        self.report_retention_days = self.config_obj.get("report_retention_days", 30)
        self.auto_alert_enabled = self.config_obj.get("auto_alerting_enabled", True)
        
        # Report storage (in production, this would be a database)
        self.report_history = []
        
        self.logger.info("Initialized HealthReportGenerator")
    
    def generate_full_health_report(self) -> HealthReport:
        """Generate comprehensive health report for all domains"""
        with self._time_operation("generate_full_report"):
            start_time = time.time()
            
            try:
                # Get current health statuses
                if not self.health_monitor:
                    raise HealthReportError("Health monitor not available")
                
                health_statuses = self.health_monitor.check_all_domains()
                
                # Get dependency analysis if available
                dependency_analysis = {}
                if self.dependency_analyzer:
                    dependency_analysis = self.dependency_analyzer.perform_comprehensive_analysis()
                
                # Analyze trends
                domain_trends = {}
                for domain_name in health_statuses.keys():
                    # Record current metrics for trend analysis
                    if domain_name in health_statuses:
                        self.trend_analyzer.record_health_metrics(
                            domain_name, health_statuses[domain_name].metrics
                        )
                    
                    # Get trends
                    domain_trends[domain_name] = self.trend_analyzer.analyze_domain_trends(domain_name)
                
                # Categorize issues
                critical_issues, warning_issues, info_issues = self._categorize_all_issues(health_statuses)
                
                # Calculate overall metrics
                total_domains = len(health_statuses)
                healthy_count = sum(1 for status in health_statuses.values() 
                                  if status.status == HealthStatusType.HEALTHY)
                degraded_count = sum(1 for status in health_statuses.values() 
                                   if status.status == HealthStatusType.DEGRADED)
                failed_count = sum(1 for status in health_statuses.values() 
                                 if status.status == HealthStatusType.FAILED)
                
                overall_health_score = self._calculate_overall_health_score(health_statuses)
                
                # Generate recommendations
                recommendations = self._generate_comprehensive_recommendations(
                    health_statuses, dependency_analysis, domain_trends
                )
                
                # Create report
                report = HealthReport(
                    report_id=f"full_report_{int(time.time())}",
                    generated_at=datetime.now(),
                    report_type="full",
                    total_domains=total_domains,
                    healthy_domains=healthy_count,
                    degraded_domains=degraded_count,
                    failed_domains=failed_count,
                    overall_health_score=overall_health_score,
                    critical_issues=critical_issues,
                    warning_issues=warning_issues,
                    info_issues=info_issues,
                    domain_health_statuses=health_statuses,
                    domain_trends=domain_trends,
                    recommendations=recommendations,
                    generation_time_ms=(time.time() - start_time) * 1000,
                    data_freshness={
                        "health_data": datetime.now(),
                        "dependency_data": datetime.now() if dependency_analysis else None
                    },
                    report_config=self.config
                )
                
                # Store report
                self._store_report(report)
                
                # Generate alerts if enabled
                if self.auto_alert_enabled:
                    alerts = self.alert_manager.evaluate_alerts(health_statuses, domain_trends)
                    if alerts:
                        self._process_alerts(alerts)
                
                return report
                
            except Exception as e:
                self._handle_error(e, "generate_full_report")
                raise HealthReportError(f"Failed to generate health report: {str(e)}")
    
    def generate_domain_report(self, domain_name: str) -> HealthReport:
        """Generate detailed report for a specific domain"""
        with self._time_operation("generate_domain_report"):
            start_time = time.time()
            
            try:
                if not self.health_monitor:
                    raise HealthReportError("Health monitor not available")
                
                # Get domain health status
                domain_health = self.health_monitor.check_domain_health(domain_name)
                health_statuses = {domain_name: domain_health}
                
                # Get domain-specific dependency analysis
                dependency_analysis = {}
                if self.dependency_analyzer:
                    dependency_analysis = self.dependency_analyzer.analyze_domain_impact(domain_name)
                
                # Get domain trends
                domain_trends = {domain_name: self.trend_analyzer.analyze_domain_trends(domain_name)}
                
                # Categorize issues
                critical_issues, warning_issues, info_issues = self._categorize_all_issues(health_statuses)
                
                # Generate domain-specific recommendations
                recommendations = self._generate_domain_recommendations(
                    domain_name, domain_health, dependency_analysis, domain_trends[domain_name]
                )
                
                # Create report
                report = HealthReport(
                    report_id=f"domain_report_{domain_name}_{int(time.time())}",
                    generated_at=datetime.now(),
                    report_type="domain_specific",
                    total_domains=1,
                    healthy_domains=1 if domain_health.status == HealthStatusType.HEALTHY else 0,
                    degraded_domains=1 if domain_health.status == HealthStatusType.DEGRADED else 0,
                    failed_domains=1 if domain_health.status == HealthStatusType.FAILED else 0,
                    overall_health_score=domain_health.metrics.overall_health_score,
                    critical_issues=critical_issues,
                    warning_issues=warning_issues,
                    info_issues=info_issues,
                    domain_health_statuses=health_statuses,
                    domain_trends=domain_trends,
                    recommendations=recommendations,
                    generation_time_ms=(time.time() - start_time) * 1000,
                    data_freshness={"health_data": datetime.now()},
                    report_config=self.config
                )
                
                self._store_report(report)
                return report
                
            except Exception as e:
                self._handle_error(e, "generate_domain_report")
                raise HealthReportError(f"Failed to generate domain report: {str(e)}")
    
    def generate_trend_report(self, days: int = 7) -> HealthReport:
        """Generate trend analysis report"""
        with self._time_operation("generate_trend_report"):
            start_time = time.time()
            
            try:
                # Get trending domains
                degrading_domains = self.trend_analyzer.get_trending_domains("degrading")
                improving_domains = self.trend_analyzer.get_trending_domains("improving")
                
                # Get trends for all domains with data
                all_trends = {}
                for domain_name in self.trend_analyzer.historical_data.keys():
                    all_trends[domain_name] = self.trend_analyzer.analyze_domain_trends(domain_name)
                
                # Generate trend-specific recommendations
                recommendations = self._generate_trend_recommendations(degrading_domains, improving_domains)
                
                # Create report
                report = HealthReport(
                    report_id=f"trend_report_{int(time.time())}",
                    generated_at=datetime.now(),
                    report_type="trend",
                    total_domains=len(all_trends),
                    healthy_domains=len(improving_domains),
                    degraded_domains=len(degrading_domains),
                    failed_domains=0,
                    overall_health_score=0.0,  # Not applicable for trend reports
                    critical_issues=[],
                    warning_issues=[],
                    info_issues=[],
                    domain_health_statuses={},
                    domain_trends=all_trends,
                    recommendations=recommendations,
                    generation_time_ms=(time.time() - start_time) * 1000,
                    data_freshness={"trend_data": datetime.now()},
                    report_config={"trend_window_days": days}
                )
                
                self._store_report(report)
                return report
                
            except Exception as e:
                self._handle_error(e, "generate_trend_report")
                raise HealthReportError(f"Failed to generate trend report: {str(e)}")
    
    def _categorize_all_issues(self, health_statuses: HealthStatusCollection) -> Tuple[List[HealthIssue], List[HealthIssue], List[HealthIssue]]:
        """Categorize all issues by severity"""
        critical_issues = []
        warning_issues = []
        info_issues = []
        
        for domain_name, health_status in health_statuses.items():
            for issue in health_status.issues:
                if issue.severity == IssueSeverity.CRITICAL:
                    critical_issues.append(issue)
                elif issue.severity == IssueSeverity.WARNING:
                    warning_issues.append(issue)
                else:
                    info_issues.append(issue)
        
        return critical_issues, warning_issues, info_issues
    
    def _calculate_overall_health_score(self, health_statuses: HealthStatusCollection) -> float:
        """Calculate overall health score across all domains"""
        if not health_statuses:
            return 0.0
        
        total_score = sum(status.metrics.overall_health_score for status in health_statuses.values())
        return total_score / len(health_statuses)
    
    def _generate_comprehensive_recommendations(self, health_statuses: HealthStatusCollection,
                                              dependency_analysis: Dict[str, Any],
                                              domain_trends: Dict[str, List[HealthTrend]]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on all available data"""
        recommendations = []
        
        # Health-based recommendations
        critical_domains = [name for name, status in health_statuses.items() 
                          if status.status == HealthStatusType.FAILED]
        
        if critical_domains:
            recommendations.append({
                "type": "critical_health",
                "priority": "high",
                "title": "Critical Health Issues Detected",
                "description": f"Immediate attention required for domains: {', '.join(critical_domains)}",
                "affected_domains": critical_domains,
                "actions": [
                    "Review critical issues in affected domains",
                    "Implement fixes for dependency and pattern issues",
                    "Monitor closely after fixes are applied"
                ]
            })
        
        # Dependency-based recommendations
        if dependency_analysis.get("circular_dependencies", {}).get("has_circular_dependencies", False):
            cycle_count = dependency_analysis["circular_dependencies"]["cycles_found"]
            recommendations.append({
                "type": "circular_dependencies",
                "priority": "high",
                "title": "Circular Dependencies Detected",
                "description": f"Found {cycle_count} circular dependency cycles that need resolution",
                "actions": [
                    "Review dependency cycles and identify breaking points",
                    "Refactor code to eliminate circular dependencies",
                    "Implement dependency injection or observer patterns"
                ]
            })
        
        # Trend-based recommendations
        degrading_domains = []
        for domain_name, trends in domain_trends.items():
            if any(t.trend_direction == "degrading" and t.trend_strength > 0.2 for t in trends):
                degrading_domains.append(domain_name)
        
        if degrading_domains:
            recommendations.append({
                "type": "degrading_trends",
                "priority": "medium",
                "title": "Degrading Health Trends",
                "description": f"Health metrics are declining for: {', '.join(degrading_domains)}",
                "affected_domains": degrading_domains,
                "actions": [
                    "Investigate root causes of health degradation",
                    "Implement preventive measures",
                    "Increase monitoring frequency for affected domains"
                ]
            })
        
        return recommendations
    
    def _generate_domain_recommendations(self, domain_name: str, health_status: HealthStatus,
                                       dependency_analysis: Dict[str, Any],
                                       trends: List[HealthTrend]) -> List[Dict[str, Any]]:
        """Generate recommendations for a specific domain"""
        recommendations = []
        
        # Issue-based recommendations
        critical_issues = [issue for issue in health_status.issues 
                          if issue.severity == IssueSeverity.CRITICAL]
        
        if critical_issues:
            recommendations.append({
                "type": "domain_critical_issues",
                "priority": "high",
                "title": f"Critical Issues in {domain_name}",
                "description": f"Found {len(critical_issues)} critical issues requiring immediate attention",
                "actions": [issue.suggested_fix for issue in critical_issues[:3]]  # Top 3 fixes
            })
        
        # Trend-based recommendations
        degrading_trends = [t for t in trends if t.trend_direction == "degrading"]
        if degrading_trends:
            trend_metrics = [t.metric_name for t in degrading_trends]
            recommendations.append({
                "type": "domain_degrading_trends",
                "priority": "medium",
                "title": f"Declining Metrics in {domain_name}",
                "description": f"Degrading trends in: {', '.join(trend_metrics)}",
                "actions": [
                    "Review recent changes that might affect these metrics",
                    "Implement monitoring for early detection",
                    "Consider refactoring if trends continue"
                ]
            })
        
        return recommendations
    
    def _generate_trend_recommendations(self, degrading_domains: List[Tuple[str, float]],
                                      improving_domains: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        if degrading_domains:
            worst_domains = [name for name, _ in degrading_domains[:5]]  # Top 5 worst
            recommendations.append({
                "type": "trend_degradation",
                "priority": "high",
                "title": "Domains with Degrading Health Trends",
                "description": f"Priority attention needed for: {', '.join(worst_domains)}",
                "affected_domains": worst_domains,
                "actions": [
                    "Conduct root cause analysis for degrading domains",
                    "Implement corrective measures",
                    "Establish monitoring alerts for continued degradation"
                ]
            })
        
        if improving_domains:
            best_domains = [name for name, _ in improving_domains[:3]]  # Top 3 best
            recommendations.append({
                "type": "trend_improvement",
                "priority": "low",
                "title": "Domains with Improving Health Trends",
                "description": f"Positive trends observed in: {', '.join(best_domains)}",
                "actions": [
                    "Document successful practices from improving domains",
                    "Consider applying similar approaches to other domains",
                    "Maintain current practices to sustain improvements"
                ]
            })
        
        return recommendations
    
    def _store_report(self, report: HealthReport):
        """Store report in history"""
        self.report_history.append(report)
        
        # Clean up old reports
        cutoff_date = datetime.now() - timedelta(days=self.report_retention_days)
        self.report_history = [r for r in self.report_history if r.generated_at >= cutoff_date]
    
    def _process_alerts(self, alerts: List[Alert]):
        """Process generated alerts through configured channels"""
        for alert in alerts:
            rule = next((r for r in self.alert_manager.alert_rules if r.name == alert.rule_name), None)
            if not rule:
                continue
            
            for channel in rule.channels:
                try:
                    if channel == AlertChannel.LOG:
                        self.logger.warning(f"ALERT [{alert.severity.value.upper()}]: {alert.title} - {alert.description}")
                    elif channel == AlertChannel.CONSOLE:
                        print(f"🚨 HEALTH ALERT: {alert.title}")
                        print(f"   Severity: {alert.severity.value.upper()}")
                        print(f"   Domain: {alert.domain_name}")
                        print(f"   Description: {alert.description}")
                        print(f"   Time: {alert.created_at}")
                    # Additional channels (email, webhook) would be implemented here
                except Exception as e:
                    self.logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    def get_report_history(self, report_type: Optional[str] = None, days: int = 7) -> List[HealthReport]:
        """Get historical reports"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        reports = [r for r in self.report_history if r.generated_at >= cutoff_date]
        
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
        
        return sorted(reports, key=lambda r: r.generated_at, reverse=True)
    
    def export_report(self, report: HealthReport, format: str = "json") -> str:
        """Export report in specified format"""
        if format == "json":
            # Convert report to JSON-serializable format
            report_dict = asdict(report)
            
            # Handle datetime serialization
            def datetime_handler(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            return json.dumps(report_dict, indent=2, default=datetime_handler)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alerts"""
        active_alerts = self.alert_manager.get_active_alerts()
        
        return {
            "total_active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
            "high_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
            "medium_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
            "low_alerts": len([a for a in active_alerts if a.severity == AlertSeverity.LOW]),
            "recent_alerts": [
                {
                    "id": alert.id,
                    "severity": alert.severity.value,
                    "title": alert.title,
                    "domain": alert.domain_name,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in active_alerts[:5]  # Most recent 5
            ]
        }