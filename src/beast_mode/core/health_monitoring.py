"""
Beast Mode Framework - Health Monitoring System
Implements 99.9% uptime design with comprehensive health tracking
Requirements: C-06 (99.9% uptime), UC-11 (System Health Monitoring), C-01 (RM compliance)
"""

import time
import threading
import queue
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

from .reflective_module import ReflectiveModule, HealthStatus, HealthIndicator
from ..utils.enum_serialization import SerializationHandler, make_enum_json_serializable

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class HealthAlert:
    module_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metric_value: float
    threshold_value: float
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate health alert parameters after initialization"""
        if not isinstance(self.metric_value, (int, float)):
            raise ValueError(f"metric_value must be a number, got {type(self.metric_value)}")
        if not isinstance(self.threshold_value, (int, float)):
            raise ValueError(f"threshold_value must be a number, got {type(self.threshold_value)}")
        if self.metric_value < 0:
            raise ValueError(f"metric_value must be non-negative, got {self.metric_value}")
        if self.threshold_value < 0:
            raise ValueError(f"threshold_value must be non-negative, got {self.threshold_value}")

@dataclass
class UptimeMetrics:
    total_uptime_seconds: float
    downtime_events: List[Dict[str, Any]] = field(default_factory=list)
    availability_percentage: float = 0.0
    mttr_seconds: float = 0.0  # Mean Time To Recovery
    mtbf_seconds: float = 0.0  # Mean Time Between Failures

class HealthMonitoringSystem(ReflectiveModule):
    """
    Comprehensive health monitoring for 99.9% uptime requirement
    Tracks all Beast Mode components and enables graceful degradation
    """
    
    def __init__(self):
        super().__init__("health_monitoring_system")
        
        # 99.9% uptime tracking
        self.start_time = datetime.now()
        self.uptime_target = 0.999  # 99.9%
        self.downtime_events = []
        self.current_downtime_start = None
        
        # Component health tracking
        self.registered_components = {}
        self.component_health_history = {}
        self.health_check_interval = 5.0  # seconds
        
        # Alert system
        self.alerts = queue.Queue()
        self.active_alerts = []
        self.alert_handlers = []
        
        # Graceful degradation
        self.degraded_components = set()
        self.critical_components = {
            'baseline_metrics_engine',
            'makefile_health_manager', 
            'health_monitoring_system'
        }
        
        # Monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self._update_health_indicator(
            "uptime_monitoring",
            HealthStatus.HEALTHY,
            "99.9%",
            "Uptime monitoring active"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for 99.9% uptime system"""
        uptime_metrics = self.calculate_uptime_metrics()
        
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "uptime_percentage": uptime_metrics.availability_percentage,
            "uptime_target": self.uptime_target * 100,
            "registered_components": len(self.registered_components),
            "degraded_components": len(self.degraded_components),
            "active_alerts": len(self.active_alerts),
            "monitoring_active": self.monitoring_active,
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for monitoring system"""
        uptime_metrics = self.calculate_uptime_metrics()
        uptime_ok = uptime_metrics.availability_percentage >= (self.uptime_target * 100)
        monitoring_ok = self.monitoring_active
        critical_components_ok = all(
            comp_name not in self.degraded_components 
            for comp_name in self.critical_components
        )
        
        return uptime_ok and monitoring_ok and critical_components_ok and not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for 99.9% uptime monitoring"""
        uptime_metrics = self.calculate_uptime_metrics()
        
        return {
            "uptime_compliance": {
                "status": "healthy" if uptime_metrics.availability_percentage >= 99.9 else "degraded",
                "current_uptime": uptime_metrics.availability_percentage,
                "target_uptime": 99.9,
                "downtime_events": len(uptime_metrics.downtime_events)
            },
            "component_health": {
                "status": "healthy" if len(self.degraded_components) == 0 else "degraded",
                "total_components": len(self.registered_components),
                "healthy_components": len(self.registered_components) - len(self.degraded_components),
                "degraded_components": len(self.degraded_components)
            },
            "alert_system": {
                "status": "healthy" if len(self.active_alerts) < 5 else "degraded",
                "active_alerts": len(self.active_alerts),
                "alert_queue_size": self.alerts.qsize()
            },
            "monitoring_system": {
                "status": "healthy" if self.monitoring_active else "unhealthy",
                "monitoring_active": self.monitoring_active,
                "check_interval": self.health_check_interval
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: System health monitoring and uptime management"""
        return "system_health_monitoring_and_uptime_management"
        
    def register_component(self, component: ReflectiveModule) -> bool:
        """
        Register a component for health monitoring
        Required for 99.9% uptime tracking of all Beast Mode components
        """
        try:
            component_name = component.module_name
            self.registered_components[component_name] = component
            self.component_health_history[component_name] = []
            
            self.logger.info(f"Registered component for monitoring: {component_name}")
            
            # Initial health check
            self._check_component_health(component)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register component {component.module_name}: {e}")
            return False
            
    def _monitoring_loop(self):
        """Continuous monitoring loop for 99.9% uptime"""
        while self.monitoring_active:
            try:
                # Check all registered components
                for component_name, component in self.registered_components.items():
                    self._check_component_health(component)
                    
                # Process alerts
                self._process_alerts()
                
                # Update uptime metrics
                self._update_uptime_tracking()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(1.0)  # Brief pause before retry
                
    def _check_component_health(self, component: ReflectiveModule):
        """Check individual component health"""
        try:
            component_name = component.module_name
            is_healthy = component.is_healthy()
            health_indicators = component.get_health_indicators()
            
            # Record health history
            health_record = {
                "timestamp": datetime.now(),
                "is_healthy": is_healthy,
                "indicators": health_indicators
            }
            
            self.component_health_history[component_name].append(health_record)
            
            # Keep only last 100 records per component
            if len(self.component_health_history[component_name]) > 100:
                self.component_health_history[component_name] = self.component_health_history[component_name][-100:]
                
            # Handle component degradation
            if not is_healthy and component_name not in self.degraded_components:
                self._handle_component_degradation(component_name, component)
            elif is_healthy and component_name in self.degraded_components:
                self._handle_component_recovery(component_name, component)
                
        except Exception as e:
            self.logger.error(f"Health check failed for {component.module_name}: {e}")
            self._handle_component_degradation(component.module_name, component, str(e))
            
    def _handle_component_degradation(self, component_name: str, component: ReflectiveModule, error: str = None):
        """Handle component degradation with graceful degradation"""
        self.degraded_components.add(component_name)
        
        # Trigger graceful degradation
        failure_context = {
            "component": component_name,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "monitoring_system": "health_monitoring_system"
        }
        
        try:
            degradation_result = component.degrade_gracefully(failure_context)
            
            # Create alert with health metrics
            severity = AlertSeverity.CRITICAL if component_name in self.critical_components else AlertSeverity.WARNING
            
            # Calculate health metric values
            health_score = 0.0  # Component is degraded, so health score is 0
            health_threshold = 0.5  # Threshold for healthy component
            
            alert = HealthAlert(
                module_name=component_name,
                severity=severity,
                message=f"Component degraded: {error or 'Health check failed'}. Graceful degradation applied.",
                timestamp=datetime.now(),
                metric_value=health_score,
                threshold_value=health_threshold
            )
            
            self.alerts.put(alert)
            self.active_alerts.append(alert)
            
            self.logger.warning(f"Component {component_name} degraded. Graceful degradation: {degradation_result.degradation_applied}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle degradation for {component_name}: {e}")
            
    def _handle_component_recovery(self, component_name: str, component: ReflectiveModule):
        """Handle component recovery"""
        self.degraded_components.discard(component_name)
        
        # Resolve related alerts
        for alert in self.active_alerts:
            if alert.module_name == component_name and not alert.resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                
        self.logger.info(f"Component {component_name} recovered")
        
    def _process_alerts(self):
        """Process alert queue"""
        while not self.alerts.empty():
            try:
                alert = self.alerts.get_nowait()
                
                # Call alert handlers
                for handler in self.alert_handlers:
                    try:
                        handler(alert)
                    except Exception as e:
                        self.logger.error(f"Alert handler failed: {e}")
                        
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Alert processing error: {e}")
                
    def _update_uptime_tracking(self):
        """Update uptime metrics for 99.9% compliance"""
        # Check if system is currently down (critical components degraded)
        critical_degraded = any(comp in self.degraded_components for comp in self.critical_components)
        
        if critical_degraded and self.current_downtime_start is None:
            # Start downtime event
            self.current_downtime_start = datetime.now()
            
        elif not critical_degraded and self.current_downtime_start is not None:
            # End downtime event
            downtime_duration = (datetime.now() - self.current_downtime_start).total_seconds()
            
            downtime_event = {
                "start_time": self.current_downtime_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": downtime_duration,
                "affected_components": list(self.degraded_components)
            }
            
            self.downtime_events.append(downtime_event)
            self.current_downtime_start = None
            
            self.logger.info(f"Downtime event ended: {downtime_duration:.2f}s")
            
    def calculate_uptime_metrics(self) -> UptimeMetrics:
        """Calculate comprehensive uptime metrics"""
        total_runtime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate total downtime
        total_downtime = 0.0
        for event in self.downtime_events:
            total_downtime += event["duration_seconds"]
            
        # Add current downtime if ongoing
        if self.current_downtime_start:
            current_downtime = (datetime.now() - self.current_downtime_start).total_seconds()
            total_downtime += current_downtime
            
        # Calculate availability percentage
        if total_runtime > 0:
            availability_percentage = ((total_runtime - total_downtime) / total_runtime) * 100
        else:
            availability_percentage = 100.0
            
        # Calculate MTTR and MTBF
        mttr = 0.0
        mtbf = 0.0
        
        if self.downtime_events:
            mttr = sum(event["duration_seconds"] for event in self.downtime_events) / len(self.downtime_events)
            
            if len(self.downtime_events) > 1:
                time_between_failures = []
                for i in range(1, len(self.downtime_events)):
                    prev_end = datetime.fromisoformat(self.downtime_events[i-1]["end_time"])
                    curr_start = datetime.fromisoformat(self.downtime_events[i]["start_time"])
                    time_between_failures.append((curr_start - prev_end).total_seconds())
                    
                if time_between_failures:
                    mtbf = sum(time_between_failures) / len(time_between_failures)
                    
        return UptimeMetrics(
            total_uptime_seconds=total_runtime - total_downtime,
            downtime_events=self.downtime_events.copy(),
            availability_percentage=availability_percentage,
            mttr_seconds=mttr,
            mtbf_seconds=mtbf
        )
        
    def add_alert_handler(self, handler: Callable[[HealthAlert], None]):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
        
    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        uptime_metrics = self.calculate_uptime_metrics()
        
        component_summary = {}
        for name, component in self.registered_components.items():
            try:
                component_summary[name] = {
                    "healthy": component.is_healthy(),
                    "degraded": name in self.degraded_components,
                    "critical": name in self.critical_components,
                    "status": component.get_module_status()
                }
            except Exception as e:
                component_summary[name] = {
                    "healthy": False,
                    "degraded": True,
                    "critical": name in self.critical_components,
                    "error": str(e)
                }
                
        return {
            "system_overview": {
                "uptime_percentage": uptime_metrics.availability_percentage,
                "uptime_target_met": uptime_metrics.availability_percentage >= 99.9,
                "total_components": len(self.registered_components),
                "healthy_components": len(self.registered_components) - len(self.degraded_components),
                "degraded_components": len(self.degraded_components),
                "active_alerts": len(self.active_alerts)
            },
            "uptime_metrics": {
                "availability_percentage": uptime_metrics.availability_percentage,
                "total_uptime_hours": uptime_metrics.total_uptime_seconds / 3600,
                "downtime_events": len(uptime_metrics.downtime_events),
                "mttr_minutes": uptime_metrics.mttr_seconds / 60,
                "mtbf_hours": uptime_metrics.mtbf_seconds / 3600
            },
            "component_health": component_summary,
            "recent_alerts": [
                {
                    "module": alert.module_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved
                }
                for alert in self.active_alerts[-10:]  # Last 10 alerts
            ]
        }
        
    def shutdown(self):
        """Graceful shutdown of monitoring system"""
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
            
        # Save final health report
        final_report = self.get_system_health_report()
        report_file = Path("beast_mode_final_health_report.json")
        
        try:
            with open(report_file, 'w') as f:
                # Use enum-aware serialization for health reports
                serialized_report = SerializationHandler.safe_serialize(final_report, indent=2)
                f.write(serialized_report)
            self.logger.info(f"Final health report saved to {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save final health report: {e}")


# Ensure AlertSeverity enum is JSON serializable
make_enum_json_serializable(AlertSeverity)