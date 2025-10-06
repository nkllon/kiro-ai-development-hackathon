"""
Makefile Health Monitor

Monitors makefile validation and governance health with Beast Mode integration.
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth


class HealthMetricType(Enum):
    """Types of health metrics."""
    VALIDATION_SUCCESS_RATE = "validation_success_rate"
    REPAIR_SUCCESS_RATE = "repair_success_rate"
    GOVERNANCE_COMPLIANCE_RATE = "governance_compliance_rate"
    ERROR_RATE = "error_rate"
    AVERAGE_RESPONSE_TIME = "average_response_time"
    SYSTEM_UPTIME = "system_uptime"


@dataclass
class HealthMetric:
    """Represents a health metric."""
    metric_type: HealthMetricType
    value: float
    timestamp: datetime
    threshold_warning: float = 0.7
    threshold_critical: float = 0.5
    unit: str = ""


@dataclass
class HealthAlert:
    """Represents a health alert."""
    alert_id: str
    metric_type: HealthMetricType
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: ModuleStatus
    health_score: float
    metrics: List[HealthMetric]
    alerts: List[HealthAlert]
    recommendations: List[str]
    last_updated: datetime


class MakefileHealthMonitor(ReflectiveModule):
    """
    Health monitor for makefile validation and governance systems.
    
    Provides comprehensive health monitoring, alerting, and recovery
    capabilities integrated with Beast Mode observability framework.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "makefile_health_monitor"
        self._logger = logging.getLogger(__name__)
        
        # Health tracking
        self._metrics_history: Dict[HealthMetricType, List[HealthMetric]] = {}
        self._active_alerts: List[HealthAlert] = []
        self._resolved_alerts: List[HealthAlert] = []
        
        # Statistics
        self._total_validations = 0
        self._successful_validations = 0
        self._total_repairs = 0
        self._successful_repairs = 0
        self._total_governance_checks = 0
        self._compliant_governance_checks = 0
        self._total_errors = 0
        self._response_times: List[float] = []
        
        # Configuration
        self._max_history_size = 1000
        self._alert_retention_days = 30
        self._metric_collection_interval = 60  # seconds
        
        # Initialize metrics
        self._initialize_metrics()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Makefile Health Monitor",
            "version": "1.0.0",
            "description": "Monitors makefile validation and governance health",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "statistics": {
                "total_validations": self._total_validations,
                "successful_validations": self._successful_validations,
                "total_repairs": self._total_repairs,
                "successful_repairs": self._successful_repairs,
                "total_governance_checks": self._total_governance_checks,
                "compliant_governance_checks": self._compliant_governance_checks,
                "total_errors": self._total_errors,
                "active_alerts": len(self._active_alerts),
                "resolved_alerts": len(self._resolved_alerts)
            },
            "health_metrics": {
                metric_type.value: len(self._metrics_history.get(metric_type, []))
                for metric_type in HealthMetricType
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        # Calculate overall health score
        current_metrics = self._collect_current_metrics()
        health_score = self._calculate_overall_health_score(current_metrics)
        
        # Determine status based on health score and active alerts
        critical_alerts = [a for a in self._active_alerts if a.severity == "critical"]
        warning_alerts = [a for a in self._active_alerts if a.severity == "warning"]
        
        if critical_alerts or health_score < 0.5:
            status = ModuleStatus.ERROR
        elif warning_alerts or health_score < 0.7:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.HEALTHY
        
        # Collect issues
        issues = []
        for alert in self._active_alerts:
            issues.append(f"{alert.severity.upper()}: {alert.message}")
        
        if health_score < 0.7:
            issues.append(f"Overall health score below threshold: {health_score:.2f}")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._total_errors,
            warning_count=len(warning_alerts)
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        # In degraded mode, reduce monitoring frequency
        self._metric_collection_interval = 300  # 5 minutes instead of 1 minute
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
            remaining_capabilities=[ModuleCapability.MONITORING, ModuleCapability.CORE_FUNCTIONALITY],
            error_message=None
        )
    
    def record_validation_result(self, success: bool, response_time: float) -> None:
        """
        Record the result of a makefile validation operation.
        
        Args:
            success: Whether the validation was successful
            response_time: Time taken for the validation in seconds
        """
        with self.trace_operation("record_validation_result", success=success, response_time=response_time):
            self._total_validations += 1
            if success:
                self._successful_validations += 1
            else:
                self._total_errors += 1
            
            self._response_times.append(response_time)
            
            # Keep response times list bounded
            if len(self._response_times) > self._max_history_size:
                self._response_times = self._response_times[-self._max_history_size:]
            
            self._update_activity()
            self._check_and_update_alerts()
    
    def record_repair_result(self, success: bool, response_time: float) -> None:
        """
        Record the result of a makefile repair operation.
        
        Args:
            success: Whether the repair was successful
            response_time: Time taken for the repair in seconds
        """
        with self.trace_operation("record_repair_result", success=success, response_time=response_time):
            self._total_repairs += 1
            if success:
                self._successful_repairs += 1
            else:
                self._total_errors += 1
            
            self._response_times.append(response_time)
            
            # Keep response times list bounded
            if len(self._response_times) > self._max_history_size:
                self._response_times = self._response_times[-self._max_history_size:]
            
            self._update_activity()
            self._check_and_update_alerts()
    
    def record_governance_result(self, compliant: bool, response_time: float) -> None:
        """
        Record the result of a governance validation operation.
        
        Args:
            compliant: Whether the makefile was governance compliant
            response_time: Time taken for the governance check in seconds
        """
        with self.trace_operation("record_governance_result", compliant=compliant, response_time=response_time):
            self._total_governance_checks += 1
            if compliant:
                self._compliant_governance_checks += 1
            
            self._response_times.append(response_time)
            
            # Keep response times list bounded
            if len(self._response_times) > self._max_history_size:
                self._response_times = self._response_times[-self._max_history_size:]
            
            self._update_activity()
            self._check_and_update_alerts()
    
    def get_system_health(self) -> SystemHealth:
        """
        Get comprehensive system health status.
        
        Returns:
            SystemHealth with current metrics, alerts, and recommendations
        """
        with self.trace_operation("get_system_health") as trace:
            current_metrics = self._collect_current_metrics()
            health_score = self._calculate_overall_health_score(current_metrics)
            
            # Determine overall status
            critical_alerts = [a for a in self._active_alerts if a.severity == "critical"]
            warning_alerts = [a for a in self._active_alerts if a.severity == "warning"]
            
            if critical_alerts or health_score < 0.5:
                status = ModuleStatus.ERROR
            elif warning_alerts or health_score < 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.HEALTHY
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(current_metrics, self._active_alerts)
            
            system_health = SystemHealth(
                status=status,
                health_score=health_score,
                metrics=current_metrics,
                alerts=self._active_alerts.copy(),
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
            trace.output_result = {
                "status": status.value,
                "health_score": health_score,
                "metric_count": len(current_metrics),
                "active_alerts": len(self._active_alerts),
                "recommendations": len(recommendations)
            }
            
            return system_health
    
    def get_metrics_history(self, metric_type: HealthMetricType, hours: int = 24) -> List[HealthMetric]:
        """
        Get historical metrics for a specific type.
        
        Args:
            metric_type: Type of metric to retrieve
            hours: Number of hours of history to retrieve
            
        Returns:
            List of historical metrics
        """
        if metric_type not in self._metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self._metrics_history[metric_type]
            if metric.timestamp >= cutoff_time
        ]
    
    def get_active_alerts(self) -> List[HealthAlert]:
        """Get all active health alerts."""
        return self._active_alerts.copy()
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Manually resolve a health alert.
        
        Args:
            alert_id: ID of the alert to resolve
            
        Returns:
            True if alert was found and resolved, False otherwise
        """
        for alert in self._active_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolution_timestamp = datetime.now()
                self._active_alerts.remove(alert)
                self._resolved_alerts.append(alert)
                
                # Clean up old resolved alerts
                self._cleanup_old_alerts()
                
                return True
        
        return False
    
    def _initialize_metrics(self) -> None:
        """Initialize metrics history storage."""
        for metric_type in HealthMetricType:
            self._metrics_history[metric_type] = []
    
    def _collect_current_metrics(self) -> List[HealthMetric]:
        """Collect current health metrics."""
        now = datetime.now()
        metrics = []
        
        # Validation success rate
        if self._total_validations > 0:
            validation_rate = self._successful_validations / self._total_validations
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.VALIDATION_SUCCESS_RATE,
                value=validation_rate,
                timestamp=now,
                unit="%"
            ))
        
        # Repair success rate
        if self._total_repairs > 0:
            repair_rate = self._successful_repairs / self._total_repairs
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.REPAIR_SUCCESS_RATE,
                value=repair_rate,
                timestamp=now,
                unit="%"
            ))
        
        # Governance compliance rate
        if self._total_governance_checks > 0:
            compliance_rate = self._compliant_governance_checks / self._total_governance_checks
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.GOVERNANCE_COMPLIANCE_RATE,
                value=compliance_rate,
                timestamp=now,
                unit="%"
            ))
        
        # Error rate
        total_operations = self._total_validations + self._total_repairs + self._total_governance_checks
        if total_operations > 0:
            error_rate = self._total_errors / total_operations
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.ERROR_RATE,
                value=error_rate,
                timestamp=now,
                threshold_warning=0.1,
                threshold_critical=0.2,
                unit="%"
            ))
        
        # Average response time
        if self._response_times:
            avg_response_time = sum(self._response_times) / len(self._response_times)
            metrics.append(HealthMetric(
                metric_type=HealthMetricType.AVERAGE_RESPONSE_TIME,
                value=avg_response_time,
                timestamp=now,
                threshold_warning=5.0,
                threshold_critical=10.0,
                unit="seconds"
            ))
        
        # System uptime
        uptime_seconds = (now - self._start_time).total_seconds()
        uptime_hours = uptime_seconds / 3600
        metrics.append(HealthMetric(
            metric_type=HealthMetricType.SYSTEM_UPTIME,
            value=uptime_hours,
            timestamp=now,
            unit="hours"
        ))
        
        # Store metrics in history
        for metric in metrics:
            if metric.metric_type not in self._metrics_history:
                self._metrics_history[metric.metric_type] = []
            
            self._metrics_history[metric.metric_type].append(metric)
            
            # Keep history bounded
            if len(self._metrics_history[metric.metric_type]) > self._max_history_size:
                self._metrics_history[metric.metric_type] = self._metrics_history[metric.metric_type][-self._max_history_size:]
        
        return metrics
    
    def _calculate_overall_health_score(self, metrics: List[HealthMetric]) -> float:
        """Calculate overall health score from current metrics."""
        if not metrics:
            return 1.0
        
        # Weight different metrics
        metric_weights = {
            HealthMetricType.VALIDATION_SUCCESS_RATE: 0.3,
            HealthMetricType.REPAIR_SUCCESS_RATE: 0.2,
            HealthMetricType.GOVERNANCE_COMPLIANCE_RATE: 0.2,
            HealthMetricType.ERROR_RATE: 0.2,
            HealthMetricType.AVERAGE_RESPONSE_TIME: 0.1,
            HealthMetricType.SYSTEM_UPTIME: 0.0  # Don't penalize for uptime
        }
        
        weighted_scores = []
        
        for metric in metrics:
            weight = metric_weights.get(metric.metric_type, 0.0)
            if weight == 0.0:
                continue
            
            # Calculate normalized score (0-1, higher is better)
            if metric.metric_type == HealthMetricType.ERROR_RATE:
                # For error rate, lower is better
                if metric.value <= metric.threshold_critical:
                    score = 0.0
                elif metric.value <= metric.threshold_warning:
                    score = 0.5
                else:
                    score = 1.0
            elif metric.metric_type == HealthMetricType.AVERAGE_RESPONSE_TIME:
                # For response time, lower is better
                if metric.value >= metric.threshold_critical:
                    score = 0.0
                elif metric.value >= metric.threshold_warning:
                    score = 0.5
                else:
                    score = 1.0
            else:
                # For success rates, higher is better
                if metric.value >= metric.threshold_warning:
                    score = 1.0
                elif metric.value >= metric.threshold_critical:
                    score = 0.7
                else:
                    score = 0.3
            
            weighted_scores.append(score * weight)
        
        if not weighted_scores:
            return 1.0
        
        return sum(weighted_scores) / sum(metric_weights[m.metric_type] for m in metrics if m.metric_type in metric_weights)
    
    def _check_and_update_alerts(self) -> None:
        """Check metrics and update alerts."""
        current_metrics = self._collect_current_metrics()
        
        for metric in current_metrics:
            # Check for threshold violations
            if metric.value < metric.threshold_critical:
                severity = "critical"
            elif metric.value < metric.threshold_warning:
                severity = "warning"
            else:
                # Metric is healthy, resolve any existing alerts
                self._resolve_metric_alerts(metric.metric_type)
                continue
            
            # Check if alert already exists
            existing_alert = next(
                (a for a in self._active_alerts 
                 if a.metric_type == metric.metric_type and a.severity == severity),
                None
            )
            
            if not existing_alert:
                # Create new alert
                alert_id = f"{metric.metric_type.value}_{severity}_{int(time.time())}"
                message = self._generate_alert_message(metric, severity)
                
                alert = HealthAlert(
                    alert_id=alert_id,
                    metric_type=metric.metric_type,
                    severity=severity,
                    message=message,
                    timestamp=datetime.now()
                )
                
                self._active_alerts.append(alert)
                self._logger.warning(f"Health alert created: {message}")
    
    def _resolve_metric_alerts(self, metric_type: HealthMetricType) -> None:
        """Resolve all alerts for a specific metric type."""
        alerts_to_resolve = [a for a in self._active_alerts if a.metric_type == metric_type]
        
        for alert in alerts_to_resolve:
            alert.resolved = True
            alert.resolution_timestamp = datetime.now()
            self._active_alerts.remove(alert)
            self._resolved_alerts.append(alert)
            
            self._logger.info(f"Health alert resolved: {alert.message}")
        
        self._cleanup_old_alerts()
    
    def _generate_alert_message(self, metric: HealthMetric, severity: str) -> str:
        """Generate alert message for a metric."""
        metric_name = metric.metric_type.value.replace('_', ' ').title()
        
        if metric.metric_type == HealthMetricType.ERROR_RATE:
            return f"{metric_name} is {severity}: {metric.value:.2%} (threshold: {metric.threshold_warning:.2%})"
        elif metric.metric_type == HealthMetricType.AVERAGE_RESPONSE_TIME:
            return f"{metric_name} is {severity}: {metric.value:.2f}s (threshold: {metric.threshold_warning:.2f}s)"
        else:
            return f"{metric_name} is {severity}: {metric.value:.2%} (threshold: {metric.threshold_warning:.2%})"
    
    def _generate_health_recommendations(self, metrics: List[HealthMetric], alerts: List[HealthAlert]) -> List[str]:
        """Generate health recommendations based on metrics and alerts."""
        recommendations = []
        
        # Analyze metrics for recommendations
        for metric in metrics:
            if metric.metric_type == HealthMetricType.VALIDATION_SUCCESS_RATE and metric.value < 0.8:
                recommendations.append("Consider reviewing makefile validation logic for improved accuracy")
            
            elif metric.metric_type == HealthMetricType.REPAIR_SUCCESS_RATE and metric.value < 0.7:
                recommendations.append("Review repair algorithms to improve success rate")
            
            elif metric.metric_type == HealthMetricType.GOVERNANCE_COMPLIANCE_RATE and metric.value < 0.8:
                recommendations.append("Consider updating governance rules or providing better documentation")
            
            elif metric.metric_type == HealthMetricType.ERROR_RATE and metric.value > 0.1:
                recommendations.append("Investigate and fix recurring errors to improve system stability")
            
            elif metric.metric_type == HealthMetricType.AVERAGE_RESPONSE_TIME and metric.value > 3.0:
                recommendations.append("Optimize performance to reduce response times")
        
        # Alert-specific recommendations
        critical_alerts = [a for a in alerts if a.severity == "critical"]
        if critical_alerts:
            recommendations.append("Address critical alerts immediately to restore system health")
        
        warning_alerts = [a for a in alerts if a.severity == "warning"]
        if len(warning_alerts) > 3:
            recommendations.append("Multiple warning alerts detected - consider system maintenance")
        
        return recommendations
    
    def _cleanup_old_alerts(self) -> None:
        """Clean up old resolved alerts."""
        cutoff_time = datetime.now() - timedelta(days=self._alert_retention_days)
        
        self._resolved_alerts = [
            alert for alert in self._resolved_alerts
            if alert.resolution_timestamp and alert.resolution_timestamp >= cutoff_time
        ]