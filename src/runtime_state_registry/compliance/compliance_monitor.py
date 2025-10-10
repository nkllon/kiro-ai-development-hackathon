#!/usr/bin/env python3
"""
Compliance Monitoring System - Task 11 Implementation
=====================================================

Continuous compliance monitoring system that provides:
- Continuous specification compliance monitoring
- Compliance trend tracking (IMPROVING, STABLE, DEGRADING)
- Detailed compliance reports with drift analysis
- Critical drift alerting system

This system provides ongoing surveillance of system compliance
and proactive alerting when compliance degrades.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import (
    UnifiedServiceState, ServiceState, DriftSeverity, ComplianceStatus,
    StateLayer, ServiceHealth, ConfigurationDrift
)
from .drift_detector import DriftDetector, DriftDetectionResult


class ComplianceTrend(Enum):
    """Compliance trend indicators."""
    IMPROVING = "improving"      # Compliance scores increasing
    STABLE = "stable"           # Compliance scores steady
    DEGRADING = "degrading"     # Compliance scores decreasing
    VOLATILE = "volatile"       # Compliance scores fluctuating
    UNKNOWN = "unknown"         # Insufficient data


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"       # Immediate action required
    HIGH = "high"              # Action required soon
    MEDIUM = "medium"          # Should be addressed
    LOW = "low"                # Informational
    INFO = "info"              # General information


@dataclass
class ComplianceAlert:
    """Compliance alert definition."""
    alert_id: str
    service_name: str
    alert_type: str
    severity: AlertSeverity
    message: str
    triggered_at: datetime
    compliance_score: float
    drift_severity: DriftSeverity
    remediation_actions: List[str]
    auto_resolvable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "alert_id": self.alert_id,
            "service_name": self.service_name,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "message": self.message,
            "triggered_at": self.triggered_at.isoformat(),
            "compliance_score": self.compliance_score,
            "drift_severity": self.drift_severity.value,
            "remediation_actions": self.remediation_actions,
            "auto_resolvable": self.auto_resolvable
        }


@dataclass
class ComplianceReport:
    """Detailed compliance report."""
    report_id: str
    generated_at: datetime
    reporting_period: Tuple[datetime, datetime]
    services_analyzed: int
    overall_compliance_score: float
    compliance_trend: ComplianceTrend
    service_compliance: Dict[str, float]
    drift_analysis: Dict[str, Any]
    active_alerts: List[ComplianceAlert]
    recommendations: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "reporting_period": [
                self.reporting_period[0].isoformat(),
                self.reporting_period[1].isoformat()
            ],
            "services_analyzed": self.services_analyzed,
            "overall_compliance_score": self.overall_compliance_score,
            "compliance_trend": self.compliance_trend.value,
            "service_compliance": self.service_compliance,
            "drift_analysis": self.drift_analysis,
            "active_alerts": [alert.to_dict() for alert in self.active_alerts],
            "recommendations": self.recommendations
        }


class ComplianceMonitor(ReflectiveModule):
    """
    Continuous compliance monitoring system for Runtime State Registry.
    
    Provides ongoing surveillance of system compliance with:
    - Real-time compliance score tracking
    - Trend analysis and prediction
    - Proactive alerting for compliance degradation
    - Detailed compliance reporting
    - Integration with drift detection system
    
    Features:
    - Continuous monitoring with configurable intervals
    - Multi-level alerting system
    - Historical compliance tracking
    - Predictive trend analysis
    - Automated report generation
    """
    
    def __init__(self,
                 monitoring_interval: int = 300,  # 5 minutes
                 compliance_threshold: float = 0.8,
                 critical_threshold: float = 0.5,
                 trend_analysis_window: int = 24,  # hours
                 max_alerts_per_service: int = 10):
        super().__init__()
        
        self.monitoring_interval = monitoring_interval
        self.compliance_threshold = compliance_threshold
        self.critical_threshold = critical_threshold
        self.trend_analysis_window = trend_analysis_window
        self.max_alerts_per_service = max_alerts_per_service
        
        # Initialize drift detector
        self.drift_detector = DriftDetector()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Compliance tracking
        self.compliance_history: List[Tuple[datetime, str, float]] = []  # (timestamp, service, score)
        self.active_alerts: Dict[str, ComplianceAlert] = {}  # alert_id -> alert
        self.alert_history: List[ComplianceAlert] = []
        
        # Service state cache
        self.last_service_states: Dict[str, Dict[str, Any]] = {}
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ComplianceMonitor initialized with {monitoring_interval}s interval")
    
    async def start_monitoring(self):
        """Start continuous compliance monitoring."""
        if self.is_monitoring:
            self.logger.warning("Compliance monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Compliance monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous compliance monitoring."""
        if not self.is_monitoring:
            self.logger.warning("Compliance monitoring not running")
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Compliance monitoring stopped")
    
    async def check_compliance(self, service_states: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Check compliance for all services and update tracking.
        
        Args:
            service_states: Dictionary mapping service names to their state data
            
        Returns:
            Dictionary mapping service names to compliance scores
        """
        self.logger.info(f"Checking compliance for {len(service_states)} services")
        
        compliance_scores = {}
        current_time = datetime.now()
        
        for service_name, state_data in service_states.items():
            try:
                # Detect drift for the service
                drift_result = await self.drift_detector.detect_service_drift(
                    service_name=service_name,
                    spec_state=state_data.get("spec_state"),
                    cms_state=state_data.get("cms_state"),
                    runtime_state=state_data.get("runtime_state")
                )
                
                # Calculate compliance score based on drift
                compliance_score = self._calculate_compliance_score(drift_result)
                compliance_scores[service_name] = compliance_score
                
                # Update compliance history
                self.compliance_history.append((current_time, service_name, compliance_score))
                
                # Check for alert conditions
                await self._check_alert_conditions(service_name, compliance_score, drift_result)
                
                # Update service state cache
                self.last_service_states[service_name] = state_data
                
            except Exception as e:
                self.logger.error(f"Failed to check compliance for {service_name}: {e}")
                compliance_scores[service_name] = 0.0
                
                # Create error alert
                await self._create_alert(
                    service_name=service_name,
                    alert_type="compliance_check_error",
                    severity=AlertSeverity.HIGH,
                    message=f"Compliance check failed: {e}",
                    compliance_score=0.0,
                    drift_severity=DriftSeverity.CRITICAL,
                    remediation_actions=["Investigate compliance check failure"]
                )
        
        # Clean up old history
        self._cleanup_old_data()
        
        self.logger.info(f"Compliance check completed. Average score: {statistics.mean(compliance_scores.values()):.3f}")
        return compliance_scores
    
    async def generate_compliance_report(self, 
                                        reporting_period_hours: int = 24) -> ComplianceReport:
        """
        Generate detailed compliance report.
        
        Args:
            reporting_period_hours: Hours to include in the report
            
        Returns:
            ComplianceReport with detailed analysis
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=reporting_period_hours)
        
        self.logger.info(f"Generating compliance report for period {start_time} to {end_time}")
        
        # Filter compliance history for reporting period
        period_history = [
            (timestamp, service, score) for timestamp, service, score in self.compliance_history
            if start_time <= timestamp <= end_time
        ]
        
        if not period_history:
            # Return empty report
            return ComplianceReport(
                report_id=f"compliance_report_{int(end_time.timestamp())}",
                generated_at=end_time,
                reporting_period=(start_time, end_time),
                services_analyzed=0,
                overall_compliance_score=0.0,
                compliance_trend=ComplianceTrend.UNKNOWN,
                service_compliance={},
                drift_analysis={},
                active_alerts=list(self.active_alerts.values()),
                recommendations=[]
            )
        
        # Analyze compliance data
        services_analyzed = len(set(service for _, service, _ in period_history))
        
        # Calculate overall compliance score
        all_scores = [score for _, _, score in period_history]
        overall_compliance_score = statistics.mean(all_scores)
        
        # Calculate per-service compliance
        service_compliance = {}
        for service in set(service for _, service, _ in period_history):
            service_scores = [score for _, s, score in period_history if s == service]
            service_compliance[service] = statistics.mean(service_scores)
        
        # Analyze compliance trend
        compliance_trend = self._analyze_compliance_trend(period_history)
        
        # Analyze drift patterns
        drift_analysis = await self._analyze_drift_patterns(period_history)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            service_compliance, drift_analysis, compliance_trend
        )
        
        report = ComplianceReport(
            report_id=f"compliance_report_{int(end_time.timestamp())}",
            generated_at=end_time,
            reporting_period=(start_time, end_time),
            services_analyzed=services_analyzed,
            overall_compliance_score=overall_compliance_score,
            compliance_trend=compliance_trend,
            service_compliance=service_compliance,
            drift_analysis=drift_analysis,
            active_alerts=list(self.active_alerts.values()),
            recommendations=recommendations
        )
        
        self.logger.info(f"Compliance report generated: {services_analyzed} services, {overall_compliance_score:.3f} overall score")
        return report
    
    def get_active_alerts(self, 
                         service_name: Optional[str] = None,
                         severity: Optional[AlertSeverity] = None) -> List[ComplianceAlert]:
        """
        Get active compliance alerts with optional filtering.
        
        Args:
            service_name: Filter by service name
            severity: Filter by alert severity
            
        Returns:
            List of matching active alerts
        """
        alerts = list(self.active_alerts.values())
        
        if service_name:
            alerts = [alert for alert in alerts if alert.service_name == service_name]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    def get_compliance_trends(self, 
                             service_name: Optional[str] = None,
                             hours: int = 24) -> Dict[str, Any]:
        """
        Get compliance trends for services.
        
        Args:
            service_name: Specific service to analyze (None for all)
            hours: Hours of history to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter history
        relevant_history = [
            (timestamp, service, score) for timestamp, service, score in self.compliance_history
            if timestamp >= cutoff_time
        ]
        
        if service_name:
            relevant_history = [
                (timestamp, service, score) for timestamp, service, score in relevant_history
                if service == service_name
            ]
        
        if not relevant_history:
            return {"status": "no_data", "message": "No compliance data available"}
        
        # Analyze trends
        services = set(service for _, service, _ in relevant_history)
        service_trends = {}
        
        for service in services:
            service_history = [(timestamp, score) for timestamp, s, score in relevant_history if s == service]
            service_history.sort(key=lambda x: x[0])  # Sort by timestamp
            
            if len(service_history) < 2:
                service_trends[service] = {
                    "trend": ComplianceTrend.UNKNOWN.value,
                    "current_score": service_history[0][1] if service_history else 0.0,
                    "data_points": len(service_history)
                }
                continue
            
            # Calculate trend
            scores = [score for _, score in service_history]
            timestamps = [timestamp for timestamp, _ in service_history]
            
            # Simple linear trend analysis
            if len(scores) >= 3:
                recent_avg = statistics.mean(scores[-3:])
                older_avg = statistics.mean(scores[:3])
                
                if recent_avg > older_avg + 0.05:
                    trend = ComplianceTrend.IMPROVING
                elif recent_avg < older_avg - 0.05:
                    trend = ComplianceTrend.DEGRADING
                else:
                    # Check for volatility
                    score_std = statistics.stdev(scores) if len(scores) > 1 else 0
                    if score_std > 0.1:
                        trend = ComplianceTrend.VOLATILE
                    else:
                        trend = ComplianceTrend.STABLE
            else:
                trend = ComplianceTrend.STABLE
            
            service_trends[service] = {
                "trend": trend.value,
                "current_score": scores[-1],
                "average_score": statistics.mean(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "score_std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "data_points": len(scores),
                "time_span_hours": (timestamps[-1] - timestamps[0]).total_seconds() / 3600
            }
        
        return {
            "status": "success",
            "analysis_period_hours": hours,
            "services_analyzed": len(services),
            "service_trends": service_trends,
            "overall_trend": self._calculate_overall_trend(service_trends)
        }
    
    # Private methods
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.info("Starting compliance monitoring loop")
        
        while self.is_monitoring:
            try:
                # Check if we have service states to monitor
                if self.last_service_states:
                    await self.check_compliance(self.last_service_states)
                else:
                    self.logger.debug("No service states available for monitoring")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
        
        self.logger.info("Compliance monitoring loop stopped")
    
    def _calculate_compliance_score(self, drift_result: DriftDetectionResult) -> float:
        """Calculate compliance score from drift detection result."""
        base_score = 1.0
        
        # Reduce score based on drift severity
        severity_penalties = {
            DriftSeverity.LOW: 0.05,
            DriftSeverity.MEDIUM: 0.15,
            DriftSeverity.HIGH: 0.35,
            DriftSeverity.CRITICAL: 0.60
        }
        
        penalty = severity_penalties.get(drift_result.drift_severity, 0.0)
        
        # Additional penalty for number of drifts
        drift_count_penalty = min(0.2, len(drift_result.detected_drifts) * 0.02)
        
        # Factor in confidence score
        confidence_factor = drift_result.confidence_score
        
        final_score = max(0.0, (base_score - penalty - drift_count_penalty) * confidence_factor)
        return final_score
    
    async def _check_alert_conditions(self, 
                                     service_name: str,
                                     compliance_score: float,
                                     drift_result: DriftDetectionResult):
        """Check if alert conditions are met and create alerts."""
        
        # Critical compliance threshold
        if compliance_score < self.critical_threshold:
            await self._create_alert(
                service_name=service_name,
                alert_type="critical_compliance_degradation",
                severity=AlertSeverity.CRITICAL,
                message=f"Service compliance critically low: {compliance_score:.3f}",
                compliance_score=compliance_score,
                drift_severity=drift_result.drift_severity,
                remediation_actions=[action["description"] for action in drift_result.remediation_guidance]
            )
        
        # General compliance threshold
        elif compliance_score < self.compliance_threshold:
            await self._create_alert(
                service_name=service_name,
                alert_type="compliance_degradation",
                severity=AlertSeverity.HIGH,
                message=f"Service compliance below threshold: {compliance_score:.3f}",
                compliance_score=compliance_score,
                drift_severity=drift_result.drift_severity,
                remediation_actions=[action["description"] for action in drift_result.remediation_guidance]
            )
        
        # Drift-specific alerts
        if drift_result.drift_severity == DriftSeverity.CRITICAL:
            await self._create_alert(
                service_name=service_name,
                alert_type="critical_drift_detected",
                severity=AlertSeverity.CRITICAL,
                message=f"Critical drift detected: {len(drift_result.detected_drifts)} issues",
                compliance_score=compliance_score,
                drift_severity=drift_result.drift_severity,
                remediation_actions=[action["description"] for action in drift_result.remediation_guidance]
            )
        
        # Orphaned services alert
        if drift_result.orphaned_services:
            await self._create_alert(
                service_name=service_name,
                alert_type="orphaned_services_detected",
                severity=AlertSeverity.MEDIUM,
                message=f"Orphaned services detected: {', '.join(drift_result.orphaned_services)}",
                compliance_score=compliance_score,
                drift_severity=drift_result.drift_severity,
                remediation_actions=["Review and register or terminate orphaned services"]
            )
        
        # Missing services alert
        if drift_result.missing_services:
            await self._create_alert(
                service_name=service_name,
                alert_type="missing_services_detected",
                severity=AlertSeverity.HIGH,
                message=f"Missing services detected: {', '.join(drift_result.missing_services)}",
                compliance_score=compliance_score,
                drift_severity=drift_result.drift_severity,
                remediation_actions=["Start missing services or remove from CMS"]
            )
    
    async def _create_alert(self,
                           service_name: str,
                           alert_type: str,
                           severity: AlertSeverity,
                           message: str,
                           compliance_score: float,
                           drift_severity: DriftSeverity,
                           remediation_actions: List[str]):
        """Create a new compliance alert."""
        
        alert_id = f"{service_name}_{alert_type}_{int(datetime.now().timestamp())}"
        
        # Check if we already have too many alerts for this service
        service_alerts = [alert for alert in self.active_alerts.values() 
                         if alert.service_name == service_name]
        
        if len(service_alerts) >= self.max_alerts_per_service:
            # Remove oldest alert for this service
            oldest_alert = min(service_alerts, key=lambda a: a.triggered_at)
            del self.active_alerts[oldest_alert.alert_id]
        
        alert = ComplianceAlert(
            alert_id=alert_id,
            service_name=service_name,
            alert_type=alert_type,
            severity=severity,
            message=message,
            triggered_at=datetime.now(),
            compliance_score=compliance_score,
            drift_severity=drift_severity,
            remediation_actions=remediation_actions,
            auto_resolvable=severity in [AlertSeverity.LOW, AlertSeverity.MEDIUM]
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(f"Alert created: {alert_id} - {message}")
    
    def _analyze_compliance_trend(self, 
                                 period_history: List[Tuple[datetime, str, float]]) -> ComplianceTrend:
        """Analyze compliance trend from historical data."""
        if len(period_history) < 6:  # Need minimum data points
            return ComplianceTrend.UNKNOWN
        
        # Sort by timestamp
        period_history.sort(key=lambda x: x[0])
        
        # Split into older and newer halves
        mid_point = len(period_history) // 2
        older_scores = [score for _, _, score in period_history[:mid_point]]
        newer_scores = [score for _, _, score in period_history[mid_point:]]
        
        older_avg = statistics.mean(older_scores)
        newer_avg = statistics.mean(newer_scores)
        
        # Calculate trend
        if newer_avg > older_avg + 0.05:
            return ComplianceTrend.IMPROVING
        elif newer_avg < older_avg - 0.05:
            return ComplianceTrend.DEGRADING
        else:
            # Check for volatility
            all_scores = [score for _, _, score in period_history]
            score_std = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
            
            if score_std > 0.15:
                return ComplianceTrend.VOLATILE
            else:
                return ComplianceTrend.STABLE
    
    async def _analyze_drift_patterns(self, 
                                     period_history: List[Tuple[datetime, str, float]]) -> Dict[str, Any]:
        """Analyze drift patterns from historical data."""
        # Get drift summary from drift detector
        drift_summary = self.drift_detector.get_drift_summary()
        
        # Add historical context
        services_with_issues = set()
        low_compliance_services = set()
        
        for timestamp, service, score in period_history:
            if score < self.compliance_threshold:
                services_with_issues.add(service)
            if score < self.critical_threshold:
                low_compliance_services.add(service)
        
        return {
            "drift_detector_summary": drift_summary,
            "services_with_compliance_issues": list(services_with_issues),
            "services_with_critical_compliance": list(low_compliance_services),
            "total_compliance_violations": len(services_with_issues),
            "critical_compliance_violations": len(low_compliance_services)
        }
    
    def _generate_recommendations(self,
                                 service_compliance: Dict[str, float],
                                 drift_analysis: Dict[str, Any],
                                 compliance_trend: ComplianceTrend) -> List[Dict[str, Any]]:
        """Generate recommendations based on compliance analysis."""
        recommendations = []
        
        # Overall trend recommendations
        if compliance_trend == ComplianceTrend.DEGRADING:
            recommendations.append({
                "type": "trend_analysis",
                "priority": "high",
                "title": "Compliance Degradation Detected",
                "description": "System compliance is trending downward. Immediate investigation recommended.",
                "actions": [
                    "Review recent changes and deployments",
                    "Analyze drift patterns for root causes",
                    "Implement corrective measures for critical services"
                ]
            })
        elif compliance_trend == ComplianceTrend.VOLATILE:
            recommendations.append({
                "type": "trend_analysis",
                "priority": "medium",
                "title": "Compliance Volatility Detected",
                "description": "System compliance is fluctuating significantly. Stability improvements needed.",
                "actions": [
                    "Identify sources of configuration instability",
                    "Implement configuration management best practices",
                    "Add monitoring for configuration changes"
                ]
            })
        
        # Service-specific recommendations
        critical_services = [service for service, score in service_compliance.items() 
                           if score < self.critical_threshold]
        
        if critical_services:
            recommendations.append({
                "type": "critical_services",
                "priority": "critical",
                "title": f"Critical Compliance Issues ({len(critical_services)} services)",
                "description": f"Services with critical compliance issues: {', '.join(critical_services)}",
                "actions": [
                    "Immediate investigation of critical services",
                    "Apply emergency remediation measures",
                    "Consider service isolation if necessary"
                ]
            })
        
        # Drift-based recommendations
        drift_summary = drift_analysis.get("drift_detector_summary", {})
        if drift_summary.get("orphaned_services"):
            recommendations.append({
                "type": "orphaned_services",
                "priority": "medium",
                "title": "Orphaned Services Cleanup",
                "description": f"Found {len(drift_summary['orphaned_services'])} orphaned services",
                "actions": [
                    "Review orphaned services for business value",
                    "Register valuable services in CMS",
                    "Decommission unnecessary services"
                ]
            })
        
        if drift_summary.get("missing_services"):
            recommendations.append({
                "type": "missing_services",
                "priority": "high",
                "title": "Missing Services Recovery",
                "description": f"Found {len(drift_summary['missing_services'])} missing services",
                "actions": [
                    "Start missing critical services immediately",
                    "Investigate root cause of service failures",
                    "Update service dependencies and configurations"
                ]
            })
        
        return recommendations
    
    def _calculate_overall_trend(self, service_trends: Dict[str, Dict[str, Any]]) -> str:
        """Calculate overall trend from individual service trends."""
        if not service_trends:
            return ComplianceTrend.UNKNOWN.value
        
        trend_counts = {}
        for trend_info in service_trends.values():
            trend = trend_info["trend"]
            trend_counts[trend] = trend_counts.get(trend, 0) + 1
        
        # Return most common trend
        if trend_counts:
            return max(trend_counts.items(), key=lambda x: x[1])[0]
        else:
            return ComplianceTrend.UNKNOWN.value
    
    def _cleanup_old_data(self):
        """Clean up old compliance history and alerts."""
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep 7 days of history
        
        # Clean up compliance history
        self.compliance_history = [
            (timestamp, service, score) for timestamp, service, score in self.compliance_history
            if timestamp >= cutoff_time
        ]
        
        # Clean up alert history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.triggered_at >= cutoff_time
        ]
        
        # Clean up resolved alerts from active alerts
        # (In a real implementation, alerts would be resolved through external actions)
        
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return compliance monitor capabilities."""
        return {
            "module_type": "compliance_monitor",
            "monitoring_interval_seconds": self.monitoring_interval,
            "compliance_threshold": self.compliance_threshold,
            "critical_threshold": self.critical_threshold,
            "trend_analysis_window_hours": self.trend_analysis_window,
            "max_alerts_per_service": self.max_alerts_per_service,
            "alert_severities": [sev.value for sev in AlertSeverity],
            "compliance_trends": [trend.value for trend in ComplianceTrend],
            "features": [
                "continuous_monitoring",
                "trend_analysis",
                "proactive_alerting",
                "compliance_reporting",
                "drift_integration"
            ]
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information and status."""
        return {
            "name": "ComplianceMonitor",
            "version": "2.0.0",
            "status": "monitoring" if self.is_monitoring else "stopped",
            "active_alerts": len(self.active_alerts),
            "total_alert_history": len(self.alert_history),
            "compliance_data_points": len(self.compliance_history),
            "monitored_services": len(self.last_service_states),
            "monitoring_interval": self.monitoring_interval
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation during failures."""
        self.logger.error(f"ComplianceMonitor degradation: {error}")
        
        return {
            "status": "degraded",
            "error": str(error),
            "available_functions": [
                "get_active_alerts",
                "get_compliance_trends",
                "get_module_info"
            ],
            "degraded_functions": [
                "check_compliance",
                "start_monitoring",
                "generate_compliance_report"
            ],
            "recovery_actions": [
                "Check drift detector connectivity",
                "Verify service state data availability",
                "Restart compliance monitoring"
            ]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for ReflectiveModule compliance."""
        return {
            "status": "monitoring" if self.is_monitoring else "stopped",
            "active_alerts": len(self.active_alerts),
            "compliance_data_points": len(self.compliance_history),
            "monitored_services": len(self.last_service_states),
            "monitoring_interval": self.monitoring_interval
        }


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Runtime State Registry - Compliance Monitor")
    parser.add_argument("--start", action="store_true", help="Start compliance monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop compliance monitoring")
    parser.add_argument("--report", action="store_true", help="Generate compliance report")
    parser.add_argument("--alerts", action="store_true", help="Show active alerts")
    parser.add_argument("--trends", action="store_true", help="Show compliance trends")
    parser.add_argument("--interval", type=int, default=300, help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def main():
        monitor = ComplianceMonitor(monitoring_interval=args.interval)
        
        if args.start:
            await monitor.start_monitoring()
            print("Compliance monitoring started. Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await monitor.stop_monitoring()
                print("Compliance monitoring stopped.")
        elif args.stop:
            await monitor.stop_monitoring()
        elif args.report:
            report = await monitor.generate_compliance_report()
            print(json.dumps(report.to_dict(), indent=2))
        elif args.alerts:
            alerts = monitor.get_active_alerts()
            for alert in alerts:
                print(json.dumps(alert.to_dict(), indent=2))
        elif args.trends:
            trends = monitor.get_compliance_trends()
            print(json.dumps(trends, indent=2))
        else:
            print("Use --help for usage information")
    
    asyncio.run(main())