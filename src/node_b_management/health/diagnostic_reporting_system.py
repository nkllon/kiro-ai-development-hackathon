"""
Diagnostic Reporting System for Node B Management

Provides comprehensive diagnostic report generation, alert management,
conversation history tracking, and resource utilization monitoring
for Node B instances with Beast Mode framework integration.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from ..core.node_b_component import NodeBComponent
from ..core.interfaces import HealthMetrics


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertCategory(Enum):
    """Alert categories"""
    PERFORMANCE = "performance"
    CONNECTIVITY = "connectivity"
    SECURITY = "security"
    RESOURCE = "resource"
    NETWORK = "network"
    SYSTEM = "system"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    node_id: str
    timestamp: str
    metric_name: str
    metric_value: Any
    threshold_value: Any
    resolved: bool = False
    resolved_at: Optional[str] = None
    acknowledged: bool = False
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None


@dataclass
class ConversationEvent:
    """Conversation event tracking"""
    event_id: str
    node_id: str
    timestamp: str
    event_type: str  # 'message_received', 'message_sent', 'conversation_started', 'conversation_ended'
    participant: str
    content_summary: str
    metadata: Dict[str, Any]


@dataclass
class NetworkParticipationEvent:
    """Network participation event tracking"""
    event_id: str
    node_id: str
    timestamp: str
    event_type: str  # 'consensus_vote', 'challenge_response', 'topology_change', 'coordination_request'
    details: Dict[str, Any]
    success: bool
    response_time_ms: float


@dataclass
class ResourceUtilizationReport:
    """Resource utilization report"""
    node_id: str
    timestamp: str
    cpu_utilization: Dict[str, float]
    memory_utilization: Dict[str, float]
    network_utilization: Dict[str, float]
    disk_utilization: Dict[str, float]
    process_metrics: Dict[str, Any]
    system_limits: Dict[str, Any]
    recommendations: List[str]


class DiagnosticReportingSystem(NodeBComponent):
    """
    Diagnostic Reporting System for Node B instances
    
    Provides comprehensive diagnostic capabilities including:
    - Alert generation for performance degradation
    - Conversation history and network participation tracking
    - Resource utilization monitoring and reporting
    - Comprehensive diagnostic report generation
    
    Requirements: 3.4, 3.5, 3.7, 6.3
    """

    def __init__(self, node_id: str = None):
        """
        Initialize Diagnostic Reporting System
        
        Args:
            node_id: Optional Node B instance ID for reporting
        """
        super().__init__("diagnostic_reporting", node_id)
        
        # Alert management
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._alert_rules: Dict[str, Dict[str, Any]] = {}
        
        # Conversation tracking
        self._conversation_events: Dict[str, List[ConversationEvent]] = {}
        self._active_conversations: Dict[str, Dict[str, Any]] = {}
        
        # Network participation tracking
        self._network_events: Dict[str, List[NetworkParticipationEvent]] = {}
        self._participation_stats: Dict[str, Dict[str, Any]] = {}
        
        # Resource utilization tracking
        self._resource_reports: Dict[str, List[ResourceUtilizationReport]] = {}
        self._utilization_thresholds: Dict[str, Dict[str, float]] = {}
        
        # Report generation settings
        self._report_retention_days = 30
        self._max_events_per_node = 1000
        
        # Initialize default alert rules and thresholds
        self._initialize_default_alert_rules()
        self._initialize_default_thresholds()
        
        self._logger.info(f"DiagnosticReportingSystem initialized for reporting")

    def _initialize_default_alert_rules(self):
        """Initialize default alert rules"""
        self._alert_rules = {
            "cpu_high": {
                "metric": "cpu_percent",
                "threshold": 80.0,
                "severity": AlertSeverity.WARNING,
                "category": AlertCategory.PERFORMANCE,
                "title": "High CPU Usage",
                "message_template": "CPU usage is {value:.1f}%, exceeding threshold of {threshold:.1f}%"
            },
            "cpu_critical": {
                "metric": "cpu_percent",
                "threshold": 95.0,
                "severity": AlertSeverity.CRITICAL,
                "category": AlertCategory.PERFORMANCE,
                "title": "Critical CPU Usage",
                "message_template": "CPU usage is {value:.1f}%, critically high"
            },
            "memory_high": {
                "metric": "memory_percent",
                "threshold": 85.0,
                "severity": AlertSeverity.WARNING,
                "category": AlertCategory.RESOURCE,
                "title": "High Memory Usage",
                "message_template": "Memory usage is {value:.1f}%, exceeding threshold of {threshold:.1f}%"
            },
            "memory_critical": {
                "metric": "memory_percent",
                "threshold": 95.0,
                "severity": AlertSeverity.CRITICAL,
                "category": AlertCategory.RESOURCE,
                "title": "Critical Memory Usage",
                "message_template": "Memory usage is {value:.1f}%, critically high"
            },
            "redis_disconnected": {
                "metric": "redis_connectivity",
                "threshold": True,
                "severity": AlertSeverity.CRITICAL,
                "category": AlertCategory.CONNECTIVITY,
                "title": "Redis Connection Lost",
                "message_template": "Redis connectivity has been lost"
            },
            "response_time_high": {
                "metric": "response_time_avg",
                "threshold": 2000.0,
                "severity": AlertSeverity.WARNING,
                "category": AlertCategory.PERFORMANCE,
                "title": "High Response Time",
                "message_template": "Average response time is {value:.1f}ms, exceeding threshold of {threshold:.1f}ms"
            },
            "error_rate_high": {
                "metric": "error_count",
                "threshold": 10,
                "severity": AlertSeverity.WARNING,
                "category": AlertCategory.SYSTEM,
                "title": "High Error Rate",
                "message_template": "Error count is {value}, exceeding threshold of {threshold}"
            }
        }

    def _initialize_default_thresholds(self):
        """Initialize default resource utilization thresholds"""
        self._utilization_thresholds = {
            "cpu": {
                "warning": 70.0,
                "critical": 90.0,
                "emergency": 98.0
            },
            "memory": {
                "warning": 75.0,
                "critical": 90.0,
                "emergency": 98.0
            },
            "disk": {
                "warning": 80.0,
                "critical": 95.0,
                "emergency": 99.0
            },
            "network": {
                "warning": 70.0,
                "critical": 90.0,
                "emergency": 98.0
            }
        }

    async def generate_alerts_from_health_metrics(self, node_id: str, health_metrics: HealthMetrics) -> List[Alert]:
        """
        Generate alerts based on health metrics
        
        Args:
            node_id: Node identifier
            health_metrics: Current health metrics
            
        Returns:
            List[Alert]: Generated alerts
            
        Requirements: 3.4, 3.5
        """
        generated_alerts = []
        
        try:
            # Check each alert rule against current metrics
            for rule_name, rule in self._alert_rules.items():
                metric_name = rule["metric"]
                threshold = rule["threshold"]
                
                # Get metric value from health metrics
                metric_value = getattr(health_metrics, metric_name, None)
                
                if metric_value is None:
                    continue
                
                # Check if alert should be triggered
                should_alert = False
                
                if metric_name == "redis_connectivity":
                    should_alert = not metric_value  # Alert if not connected
                elif isinstance(threshold, (int, float)):
                    should_alert = metric_value > threshold
                
                if should_alert:
                    # Generate alert ID
                    alert_id = self._generate_alert_id(node_id, rule_name, metric_value)
                    
                    # Check if alert already exists
                    if alert_id in self._active_alerts:
                        continue
                    
                    # Create new alert
                    alert = Alert(
                        id=alert_id,
                        severity=rule["severity"],
                        category=rule["category"],
                        title=rule["title"],
                        message=rule["message_template"].format(
                            value=metric_value,
                            threshold=threshold
                        ),
                        node_id=node_id,
                        timestamp=datetime.now().isoformat(),
                        metric_name=metric_name,
                        metric_value=metric_value,
                        threshold_value=threshold
                    )
                    
                    # Add to active alerts
                    self._active_alerts[alert_id] = alert
                    generated_alerts.append(alert)
                    
                    self._logger.warning(f"Generated alert {alert_id}: {alert.title}")
                
                else:
                    # Check if we should resolve existing alert
                    alert_id = self._generate_alert_id(node_id, rule_name, metric_value)
                    if alert_id in self._active_alerts:
                        await self.resolve_alert(alert_id)
            
            return generated_alerts
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to generate alerts for node {node_id}: {e}")
            return []

    async def track_conversation_event(self, node_id: str, event_type: str, participant: str, 
                                     content_summary: str, metadata: Dict[str, Any] = None):
        """
        Track conversation events for diagnostic reporting
        
        Args:
            node_id: Node identifier
            event_type: Type of conversation event
            participant: Conversation participant
            content_summary: Summary of conversation content
            metadata: Additional event metadata
            
        Requirements: 3.5, 3.7
        """
        try:
            event_id = f"conv_{node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            event = ConversationEvent(
                event_id=event_id,
                node_id=node_id,
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                participant=participant,
                content_summary=content_summary,
                metadata=metadata or {}
            )
            
            # Add to conversation events
            if node_id not in self._conversation_events:
                self._conversation_events[node_id] = []
            
            self._conversation_events[node_id].append(event)
            
            # Maintain event limit
            if len(self._conversation_events[node_id]) > self._max_events_per_node:
                self._conversation_events[node_id] = self._conversation_events[node_id][-self._max_events_per_node:]
            
            # Update active conversations tracking
            if event_type == "conversation_started":
                if node_id not in self._active_conversations:
                    self._active_conversations[node_id] = {}
                
                self._active_conversations[node_id][participant] = {
                    "started_at": event.timestamp,
                    "last_activity": event.timestamp,
                    "message_count": 0
                }
            
            elif event_type in ["message_received", "message_sent"]:
                if node_id in self._active_conversations and participant in self._active_conversations[node_id]:
                    conv = self._active_conversations[node_id][participant]
                    conv["last_activity"] = event.timestamp
                    conv["message_count"] += 1
            
            elif event_type == "conversation_ended":
                if node_id in self._active_conversations and participant in self._active_conversations[node_id]:
                    del self._active_conversations[node_id][participant]
            
            self._logger.debug(f"Tracked conversation event {event_id} for node {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to track conversation event for node {node_id}: {e}")

    async def track_network_participation_event(self, node_id: str, event_type: str, 
                                              details: Dict[str, Any], success: bool, 
                                              response_time_ms: float):
        """
        Track network participation events for diagnostic reporting
        
        Args:
            node_id: Node identifier
            event_type: Type of network event
            details: Event details
            success: Whether the event was successful
            response_time_ms: Response time in milliseconds
            
        Requirements: 3.5, 3.7
        """
        try:
            event_id = f"net_{node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            event = NetworkParticipationEvent(
                event_id=event_id,
                node_id=node_id,
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                details=details,
                success=success,
                response_time_ms=response_time_ms
            )
            
            # Add to network events
            if node_id not in self._network_events:
                self._network_events[node_id] = []
            
            self._network_events[node_id].append(event)
            
            # Maintain event limit
            if len(self._network_events[node_id]) > self._max_events_per_node:
                self._network_events[node_id] = self._network_events[node_id][-self._max_events_per_node:]
            
            # Update participation statistics
            if node_id not in self._participation_stats:
                self._participation_stats[node_id] = {
                    "total_events": 0,
                    "successful_events": 0,
                    "failed_events": 0,
                    "average_response_time": 0.0,
                    "event_types": {}
                }
            
            stats = self._participation_stats[node_id]
            stats["total_events"] += 1
            
            if success:
                stats["successful_events"] += 1
            else:
                stats["failed_events"] += 1
            
            # Update average response time
            total_response_time = stats["average_response_time"] * (stats["total_events"] - 1)
            stats["average_response_time"] = (total_response_time + response_time_ms) / stats["total_events"]
            
            # Update event type counts
            if event_type not in stats["event_types"]:
                stats["event_types"][event_type] = {"count": 0, "success_rate": 0.0}
            
            event_type_stats = stats["event_types"][event_type]
            event_type_stats["count"] += 1
            
            # Calculate success rate for this event type
            event_type_events = [e for e in self._network_events[node_id] if e.event_type == event_type]
            successful_events = sum(1 for e in event_type_events if e.success)
            event_type_stats["success_rate"] = successful_events / len(event_type_events)
            
            self._logger.debug(f"Tracked network participation event {event_id} for node {node_id}")
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to track network participation event for node {node_id}: {e}")

    async def generate_resource_utilization_report(self, node_id: str, 
                                                 performance_metrics: Dict[str, float]) -> ResourceUtilizationReport:
        """
        Generate resource utilization report
        
        Args:
            node_id: Node identifier
            performance_metrics: Current performance metrics
            
        Returns:
            ResourceUtilizationReport: Comprehensive resource utilization report
            
        Requirements: 3.7, 6.3
        """
        try:
            # Extract utilization metrics
            cpu_utilization = {
                "current": performance_metrics.get("cpu_percent", 0.0),
                "process": performance_metrics.get("process_cpu_percent", 0.0),
                "load_average": performance_metrics.get("load_average", 0.0)
            }
            
            memory_utilization = {
                "current_percent": performance_metrics.get("memory_percent", 0.0),
                "current_mb": performance_metrics.get("memory_mb", 0.0),
                "available_mb": performance_metrics.get("memory_available_mb", 0.0),
                "process_mb": performance_metrics.get("process_memory_mb", 0.0)
            }
            
            network_utilization = {
                "bytes_sent": performance_metrics.get("network_bytes_sent", 0),
                "bytes_recv": performance_metrics.get("network_bytes_recv", 0),
                "utilization_percent": min(100.0, 
                    (performance_metrics.get("network_bytes_sent", 0) + 
                     performance_metrics.get("network_bytes_recv", 0)) / (1024 * 1024) * 0.1)  # Rough estimate
            }
            
            disk_utilization = {
                "read_bytes": performance_metrics.get("disk_read_bytes", 0),
                "write_bytes": performance_metrics.get("disk_write_bytes", 0),
                "utilization_percent": 0.0  # Would need more sophisticated calculation
            }
            
            process_metrics = {
                "cpu_percent": performance_metrics.get("process_cpu_percent", 0.0),
                "memory_mb": performance_metrics.get("process_memory_mb", 0.0),
                "response_time_avg": performance_metrics.get("response_time_avg", 0.0)
            }
            
            system_limits = {
                "cpu_cores": performance_metrics.get("cpu_cores", 1),
                "memory_total_mb": performance_metrics.get("memory_total_mb", 1024),
                "disk_total_gb": performance_metrics.get("disk_total_gb", 100)
            }
            
            # Generate recommendations
            recommendations = self._generate_resource_recommendations(
                cpu_utilization, memory_utilization, network_utilization, disk_utilization
            )
            
            # Create report
            report = ResourceUtilizationReport(
                node_id=node_id,
                timestamp=datetime.now().isoformat(),
                cpu_utilization=cpu_utilization,
                memory_utilization=memory_utilization,
                network_utilization=network_utilization,
                disk_utilization=disk_utilization,
                process_metrics=process_metrics,
                system_limits=system_limits,
                recommendations=recommendations
            )
            
            # Store report
            if node_id not in self._resource_reports:
                self._resource_reports[node_id] = []
            
            self._resource_reports[node_id].append(report)
            
            # Cleanup old reports
            await self._cleanup_resource_reports(node_id)
            
            self._logger.debug(f"Generated resource utilization report for node {node_id}")
            return report
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to generate resource utilization report for node {node_id}: {e}")
            
            # Return minimal error report
            return ResourceUtilizationReport(
                node_id=node_id,
                timestamp=datetime.now().isoformat(),
                cpu_utilization={"error": str(e)},
                memory_utilization={"error": str(e)},
                network_utilization={"error": str(e)},
                disk_utilization={"error": str(e)},
                process_metrics={"error": str(e)},
                system_limits={"error": str(e)},
                recommendations=[f"Error generating report: {e}"]
            )

    def _generate_resource_recommendations(self, cpu_util: Dict[str, float], 
                                         memory_util: Dict[str, float],
                                         network_util: Dict[str, float], 
                                         disk_util: Dict[str, float]) -> List[str]:
        """Generate resource optimization recommendations"""
        recommendations = []
        
        # CPU recommendations
        cpu_current = cpu_util.get("current", 0.0)
        if cpu_current > self._utilization_thresholds["cpu"]["critical"]:
            recommendations.append("CRITICAL: CPU usage is very high. Consider scaling horizontally or optimizing CPU-intensive operations.")
        elif cpu_current > self._utilization_thresholds["cpu"]["warning"]:
            recommendations.append("WARNING: CPU usage is elevated. Monitor for sustained high usage and consider optimization.")
        
        # Memory recommendations
        memory_current = memory_util.get("current_percent", 0.0)
        if memory_current > self._utilization_thresholds["memory"]["critical"]:
            recommendations.append("CRITICAL: Memory usage is very high. Check for memory leaks and consider increasing available memory.")
        elif memory_current > self._utilization_thresholds["memory"]["warning"]:
            recommendations.append("WARNING: Memory usage is elevated. Monitor memory growth patterns.")
        
        # Network recommendations
        network_current = network_util.get("utilization_percent", 0.0)
        if network_current > self._utilization_thresholds["network"]["warning"]:
            recommendations.append("INFO: Network utilization is elevated. Monitor for network bottlenecks.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("INFO: Resource utilization is within normal ranges.")
        
        return recommendations

    async def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """
        Resolve an active alert
        
        Args:
            alert_id: Alert identifier
            resolved_by: Who resolved the alert
            
        Returns:
            bool: True if alert was resolved successfully
        """
        try:
            if alert_id in self._active_alerts:
                alert = self._active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                
                # Move to history
                self._alert_history.append(alert)
                del self._active_alerts[alert_id]
                
                self._logger.info(f"Resolved alert {alert_id}: {alert.title}")
                return True
            
            return False
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge an active alert
        
        Args:
            alert_id: Alert identifier
            acknowledged_by: Who acknowledged the alert
            
        Returns:
            bool: True if alert was acknowledged successfully
        """
        try:
            if alert_id in self._active_alerts:
                alert = self._active_alerts[alert_id]
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now().isoformat()
                alert.acknowledged_by = acknowledged_by
                
                self._logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
                return True
            
            return False
            
        except Exception as e:
            self._increment_error_count()
            self._logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False

    def get_active_alerts(self, node_id: str = None) -> List[Alert]:
        """Get active alerts, optionally filtered by node ID"""
        if node_id:
            return [alert for alert in self._active_alerts.values() if alert.node_id == node_id]
        return list(self._active_alerts.values())

    def get_conversation_history(self, node_id: str, limit: int = 100) -> List[ConversationEvent]:
        """Get conversation history for a node"""
        events = self._conversation_events.get(node_id, [])
        return events[-limit:] if limit else events

    def get_network_participation_history(self, node_id: str, limit: int = 100) -> List[NetworkParticipationEvent]:
        """Get network participation history for a node"""
        events = self._network_events.get(node_id, [])
        return events[-limit:] if limit else events

    def get_resource_utilization_history(self, node_id: str, limit: int = 50) -> List[ResourceUtilizationReport]:
        """Get resource utilization history for a node"""
        reports = self._resource_reports.get(node_id, [])
        return reports[-limit:] if limit else reports

    def get_participation_statistics(self, node_id: str) -> Dict[str, Any]:
        """Get network participation statistics for a node"""
        return self._participation_stats.get(node_id, {})

    def _generate_alert_id(self, node_id: str, rule_name: str, metric_value: Any) -> str:
        """Generate unique alert ID"""
        content = f"{node_id}_{rule_name}_{datetime.now().strftime('%Y%m%d')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    async def _cleanup_resource_reports(self, node_id: str):
        """Clean up old resource reports"""
        if node_id not in self._resource_reports:
            return
        
        cutoff_time = datetime.now() - timedelta(days=self._report_retention_days)
        
        self._resource_reports[node_id] = [
            report for report in self._resource_reports[node_id]
            if datetime.fromisoformat(report.timestamp) > cutoff_time
        ]

    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """Get diagnostic system summary"""
        return {
            "active_alerts_count": len(self._active_alerts),
            "alert_history_count": len(self._alert_history),
            "monitored_nodes": list(set(
                list(self._conversation_events.keys()) +
                list(self._network_events.keys()) +
                list(self._resource_reports.keys())
            )),
            "conversation_events_total": sum(len(events) for events in self._conversation_events.values()),
            "network_events_total": sum(len(events) for events in self._network_events.values()),
            "resource_reports_total": sum(len(reports) for reports in self._resource_reports.values()),
            "active_conversations": sum(len(convs) for convs in self._active_conversations.values()),
            "alert_rules_count": len(self._alert_rules),
            "system_status": "operational"
        }