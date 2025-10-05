#!/usr/bin/env python3
"""
Integration Health Monitor for DAG Orchestration
===============================================

Comprehensive health monitoring and diagnostics for all integration
layer components including ACE Reporter, AI Memory Palace, System
Integration Framework, and Task List Converter.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


class HealthCheckType(Enum):
    """Types of health checks."""
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health monitoring alert."""
    component: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


@dataclass
class IntegrationHealthReport:
    """Comprehensive integration health report."""
    timestamp: datetime
    overall_health_score: float
    component_health: Dict[str, ModuleHealth]
    active_alerts: List[HealthAlert]
    performance_metrics: Dict[str, Any]
    recommendations: List[str]
    system_status: str


class IntegrationHealthMonitor(ReflectiveModule):
    """
    Comprehensive health monitoring for DAG orchestration integration layer.
    
    Monitors:
    - ACE Reporter Integration
    - AI Memory Palace Integration  
    - System Integration Framework
    - Task List Converter
    - Cross-component integration health
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "IntegrationHealthMonitor"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Health monitoring state
        self._monitored_components: Dict[str, Any] = {}
        self._health_history: List[IntegrationHealthReport] = []
        self._active_alerts: List[HealthAlert] = []
        self._performance_baselines: Dict[str, float] = {}
        
        # Configuration
        self._check_interval_seconds = 60
        self._alert_thresholds = {
            "health_score_warning": 0.8,
            "health_score_error": 0.6,
            "health_score_critical": 0.4,
            "response_time_warning": 1.0,
            "response_time_error": 5.0,
            "error_rate_warning": 0.05,
            "error_rate_error": 0.15
        }
        
        # Statistics
        self._total_health_checks = 0
        self._total_alerts_generated = 0
        self._total_alerts_resolved = 0
        
        self._logger.info("Integration Health Monitor initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "Integration Health Monitor",
            "version": "1.0.0",
            "description": "Comprehensive health monitoring for integration layer",
            "configuration": {
                "monitored_components": len(self._monitored_components),
                "check_interval_seconds": self._check_interval_seconds,
                "alert_thresholds": self._alert_thresholds
            },
            "statistics": {
                "total_health_checks": self._total_health_checks,
                "total_alerts_generated": self._total_alerts_generated,
                "total_alerts_resolved": self._total_alerts_resolved,
                "active_alerts": len(self._active_alerts),
                "health_history_count": len(self._health_history)
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            issues = []
            health_score = 1.0
            
            # Check alert levels
            critical_alerts = [a for a in self._active_alerts if a.severity == AlertSeverity.CRITICAL]
            error_alerts = [a for a in self._active_alerts if a.severity == AlertSeverity.ERROR]
            warning_alerts = [a for a in self._active_alerts if a.severity == AlertSeverity.WARNING]
            
            if critical_alerts:
                issues.append(f"{len(critical_alerts)} critical alerts active")
                health_score *= 0.3
            
            if error_alerts:
                issues.append(f"{len(error_alerts)} error alerts active")
                health_score *= 0.6
            
            if warning_alerts:
                issues.append(f"{len(warning_alerts)} warning alerts active")
                health_score *= 0.8
            
            # Check monitoring coverage
            if len(self._monitored_components) == 0:
                issues.append("No components being monitored")
                health_score *= 0.5
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, continue basic monitoring but reduce frequency
            self._check_interval_seconds = 300  # Reduce to 5-minute intervals
            
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION,
                ModuleCapability.API_INTEGRATION
            ]
            
            # Clear non-critical alerts to reduce processing load
            self._active_alerts = [
                alert for alert in self._active_alerts 
                if alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def register_component(self, component_name: str, component_instance: Any) -> bool:
        """
        Register a component for health monitoring.
        
        Args:
            component_name: Name of the component
            component_instance: Component instance to monitor
            
        Returns:
            bool: True if registration successful
        """
        with self.trace_operation("register_component", 
                                component_name=component_name) as trace:
            try:
                # Validate component has required health methods
                required_methods = ['get_health_status', 'get_module_info']
                for method in required_methods:
                    if not hasattr(component_instance, method):
                        raise ValueError(f"Component {component_name} missing required method: {method}")
                
                self._monitored_components[component_name] = {
                    'instance': component_instance,
                    'registered_at': datetime.now(),
                    'last_check': None,
                    'check_count': 0,
                    'error_count': 0
                }
                
                trace.output_result = {
                    'registered': True,
                    'component_name': component_name,
                    'total_components': len(self._monitored_components)
                }
                
                self._logger.info(f"Registered component for monitoring: {component_name}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to register component {component_name}: {e}")
                trace.output_result = {'registered': False, 'error': str(e)}
                return False
    
    def unregister_component(self, component_name: str) -> bool:
        """
        Unregister a component from health monitoring.
        
        Args:
            component_name: Name of the component to unregister
            
        Returns:
            bool: True if unregistration successful
        """
        with self.trace_operation("unregister_component", 
                                component_name=component_name) as trace:
            try:
                if component_name in self._monitored_components:
                    del self._monitored_components[component_name]
                    
                    # Remove alerts for this component
                    self._active_alerts = [
                        alert for alert in self._active_alerts 
                        if alert.component != component_name
                    ]
                    
                    trace.output_result = {
                        'unregistered': True,
                        'component_name': component_name,
                        'remaining_components': len(self._monitored_components)
                    }
                    
                    self._logger.info(f"Unregistered component from monitoring: {component_name}")
                    return True
                else:
                    trace.output_result = {'unregistered': False, 'reason': 'Component not found'}
                    return False
                    
            except Exception as e:
                self._logger.error(f"Failed to unregister component {component_name}: {e}")
                trace.output_result = {'unregistered': False, 'error': str(e)}
                return False
    
    async def perform_health_check(self, check_type: HealthCheckType = HealthCheckType.BASIC) -> IntegrationHealthReport:
        """
        Perform comprehensive health check of all monitored components.
        
        Args:
            check_type: Type of health check to perform
            
        Returns:
            IntegrationHealthReport: Comprehensive health report
        """
        with self.trace_operation("perform_health_check", 
                                check_type=check_type.value) as trace:
            try:
                self._total_health_checks += 1
                
                component_health = {}
                performance_metrics = {}
                new_alerts = []
                
                # Check each monitored component
                for component_name, component_info in self._monitored_components.items():
                    try:
                        component_instance = component_info['instance']
                        
                        # Get component health
                        health = component_instance.get_health_status()
                        component_health[component_name] = health
                        
                        # Update component tracking
                        component_info['last_check'] = datetime.now()
                        component_info['check_count'] += 1
                        
                        # Check for health issues
                        if health.health_score < self._alert_thresholds['health_score_critical']:
                            new_alerts.append(HealthAlert(
                                component=component_name,
                                severity=AlertSeverity.CRITICAL,
                                message=f"Critical health score: {health.health_score:.2f}",
                                timestamp=datetime.now(),
                                details={'health_score': health.health_score, 'issues': health.issues}
                            ))
                        elif health.health_score < self._alert_thresholds['health_score_error']:
                            new_alerts.append(HealthAlert(
                                component=component_name,
                                severity=AlertSeverity.ERROR,
                                message=f"Low health score: {health.health_score:.2f}",
                                timestamp=datetime.now(),
                                details={'health_score': health.health_score, 'issues': health.issues}
                            ))
                        elif health.health_score < self._alert_thresholds['health_score_warning']:
                            new_alerts.append(HealthAlert(
                                component=component_name,
                                severity=AlertSeverity.WARNING,
                                message=f"Degraded health score: {health.health_score:.2f}",
                                timestamp=datetime.now(),
                                details={'health_score': health.health_score, 'issues': health.issues}
                            ))
                        
                        # Collect performance metrics if available
                        if hasattr(component_instance, 'get_performance_metrics'):
                            metrics = component_instance.get_performance_metrics()
                            performance_metrics[component_name] = metrics
                        
                        # Component-specific checks
                        if check_type in [HealthCheckType.COMPREHENSIVE, HealthCheckType.PERFORMANCE]:
                            await self._perform_component_specific_checks(
                                component_name, component_instance, new_alerts
                            )
                        
                    except Exception as e:
                        component_info['error_count'] += 1
                        self._logger.error(f"Health check failed for {component_name}: {e}")
                        
                        new_alerts.append(HealthAlert(
                            component=component_name,
                            severity=AlertSeverity.ERROR,
                            message=f"Health check failed: {str(e)}",
                            timestamp=datetime.now(),
                            details={'error': str(e)}
                        ))
                
                # Add new alerts
                self._active_alerts.extend(new_alerts)
                self._total_alerts_generated += len(new_alerts)
                
                # Calculate overall health score
                if component_health:
                    overall_health_score = sum(h.health_score for h in component_health.values()) / len(component_health)
                else:
                    overall_health_score = 0.0
                
                # Generate recommendations
                recommendations = self._generate_recommendations(component_health, new_alerts)
                
                # Determine system status
                if overall_health_score >= 0.9:
                    system_status = "HEALTHY"
                elif overall_health_score >= 0.7:
                    system_status = "WARNING"
                elif overall_health_score >= 0.5:
                    system_status = "DEGRADED"
                else:
                    system_status = "CRITICAL"
                
                # Create health report
                health_report = IntegrationHealthReport(
                    timestamp=datetime.now(),
                    overall_health_score=overall_health_score,
                    component_health=component_health,
                    active_alerts=self._active_alerts.copy(),
                    performance_metrics=performance_metrics,
                    recommendations=recommendations,
                    system_status=system_status
                )
                
                # Store in history
                self._health_history.append(health_report)
                
                # Limit history size
                if len(self._health_history) > 100:
                    self._health_history = self._health_history[-100:]
                
                trace.output_result = {
                    'health_check_completed': True,
                    'overall_health_score': overall_health_score,
                    'system_status': system_status,
                    'components_checked': len(component_health),
                    'new_alerts': len(new_alerts)
                }
                
                self._logger.info(f"Health check completed: {system_status} (score: {overall_health_score:.2f})")
                return health_report
                
            except Exception as e:
                self._logger.error(f"Health check failed: {e}")
                
                # Return error report
                error_report = IntegrationHealthReport(
                    timestamp=datetime.now(),
                    overall_health_score=0.0,
                    component_health={},
                    active_alerts=[HealthAlert(
                        component="health_monitor",
                        severity=AlertSeverity.CRITICAL,
                        message=f"Health check system failure: {str(e)}",
                        timestamp=datetime.now(),
                        details={'error': str(e)}
                    )],
                    performance_metrics={},
                    recommendations=["Investigate health monitoring system failure"],
                    system_status="CRITICAL"
                )
                
                trace.output_result = {'health_check_completed': False, 'error': str(e)}
                return error_report
    
    async def _perform_component_specific_checks(self, component_name: str, 
                                               component_instance: Any,
                                               alerts: List[HealthAlert]) -> None:
        """Perform component-specific health checks."""
        try:
            # ACE Reporter specific checks
            if hasattr(component_instance, 'get_broadcast_statistics'):
                stats = component_instance.get_broadcast_statistics()
                broadcast_stats = stats.get('broadcast_statistics', {})
                
                success_rate = broadcast_stats.get('success_rate', 1.0)
                if success_rate < 0.9:
                    alerts.append(HealthAlert(
                        component=component_name,
                        severity=AlertSeverity.WARNING,
                        message=f"Low broadcast success rate: {success_rate:.1%}",
                        timestamp=datetime.now(),
                        details={'success_rate': success_rate}
                    ))
            
            # AI Memory Palace specific checks
            if hasattr(component_instance, 'get_learning_statistics'):
                stats = component_instance.get_learning_statistics()
                
                if not stats.get('learning_enabled', True):
                    alerts.append(HealthAlert(
                        component=component_name,
                        severity=AlertSeverity.WARNING,
                        message="Learning is disabled",
                        timestamp=datetime.now(),
                        details={'learning_enabled': False}
                    ))
            
            # System Integration Framework specific checks
            if hasattr(component_instance, 'get_integration_statistics'):
                stats = component_instance.get_integration_statistics()
                integration_stats = stats.get('integration_statistics', {})
                
                success_rate = integration_stats.get('integration_success_rate', 1.0)
                if success_rate < 0.8:
                    alerts.append(HealthAlert(
                        component=component_name,
                        severity=AlertSeverity.ERROR,
                        message=f"Low integration success rate: {success_rate:.1%}",
                        timestamp=datetime.now(),
                        details={'integration_success_rate': success_rate}
                    ))
            
        except Exception as e:
            self._logger.error(f"Component-specific check failed for {component_name}: {e}")
    
    def _generate_recommendations(self, component_health: Dict[str, ModuleHealth], 
                                alerts: List[HealthAlert]) -> List[str]:
        """Generate health recommendations based on current state."""
        recommendations = []
        
        # Check for components with low health scores
        for component_name, health in component_health.items():
            if health.health_score < 0.7:
                recommendations.append(f"Investigate {component_name} health issues: {', '.join(health.issues)}")
        
        # Check for high alert counts
        error_alerts = [a for a in alerts if a.severity == AlertSeverity.ERROR]
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        
        if critical_alerts:
            recommendations.append("Address critical alerts immediately to prevent system failure")
        
        if len(error_alerts) > 3:
            recommendations.append("High number of error alerts - consider system maintenance")
        
        # Check for unmonitored components
        if len(self._monitored_components) < 4:
            recommendations.append("Ensure all integration components are registered for monitoring")
        
        return recommendations
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an active alert.
        
        Args:
            alert_id: ID of the alert to resolve
            
        Returns:
            bool: True if alert was resolved
        """
        with self.trace_operation("resolve_alert", alert_id=alert_id) as trace:
            try:
                # Find alert by timestamp (using as ID)
                for alert in self._active_alerts:
                    if str(alert.timestamp) == alert_id:
                        alert.resolved = True
                        alert.resolution_timestamp = datetime.now()
                        self._total_alerts_resolved += 1
                        
                        trace.output_result = {'resolved': True, 'alert_id': alert_id}
                        self._logger.info(f"Resolved alert: {alert.message}")
                        return True
                
                trace.output_result = {'resolved': False, 'reason': 'Alert not found'}
                return False
                
            except Exception as e:
                self._logger.error(f"Failed to resolve alert {alert_id}: {e}")
                trace.output_result = {'resolved': False, 'error': str(e)}
                return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        if not self._health_history:
            return {"status": "No health data available"}
        
        latest_report = self._health_history[-1]
        
        return {
            "overall_status": latest_report.system_status,
            "overall_health_score": latest_report.overall_health_score,
            "last_check": latest_report.timestamp.isoformat(),
            "monitored_components": len(self._monitored_components),
            "active_alerts": {
                "total": len(self._active_alerts),
                "critical": len([a for a in self._active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "error": len([a for a in self._active_alerts if a.severity == AlertSeverity.ERROR]),
                "warning": len([a for a in self._active_alerts if a.severity == AlertSeverity.WARNING])
            },
            "component_health": {
                name: {
                    "status": health.status.value,
                    "health_score": health.health_score,
                    "issues": health.issues
                }
                for name, health in latest_report.component_health.items()
            },
            "recommendations": latest_report.recommendations,
            "statistics": {
                "total_health_checks": self._total_health_checks,
                "total_alerts_generated": self._total_alerts_generated,
                "total_alerts_resolved": self._total_alerts_resolved
            }
        }
    
    def export_health_report(self, output_path: str) -> bool:
        """
        Export comprehensive health report to file.
        
        Args:
            output_path: Path to export the report
            
        Returns:
            bool: True if export successful
        """
        with self.trace_operation("export_health_report", output_path=output_path) as trace:
            try:
                health_summary = self.get_health_summary()
                
                # Add detailed history
                health_summary["health_history"] = [
                    {
                        "timestamp": report.timestamp.isoformat(),
                        "overall_health_score": report.overall_health_score,
                        "system_status": report.system_status,
                        "component_count": len(report.component_health),
                        "alert_count": len(report.active_alerts)
                    }
                    for report in self._health_history[-10:]  # Last 10 reports
                ]
                
                with open(output_path, 'w') as f:
                    json.dump(health_summary, f, indent=2, default=str)
                
                trace.output_result = {'exported': True, 'output_path': output_path}
                self._logger.info(f"Health report exported to {output_path}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to export health report: {e}")
                trace.output_result = {'exported': False, 'error': str(e)}
                return False


def create_integration_health_monitor() -> IntegrationHealthMonitor:
    """Factory function to create Integration Health Monitor."""
    return IntegrationHealthMonitor()


# Auto-registration function for all integration components
async def setup_integration_monitoring() -> IntegrationHealthMonitor:
    """
    Set up comprehensive monitoring for all integration components.
    
    Returns:
        IntegrationHealthMonitor: Configured health monitor
    """
    monitor = create_integration_health_monitor()
    
    try:
        # Import and register all integration components
        from .ace_reporter_integration import create_ace_reporter_integration
        from .ai_memory_palace_integration import create_ai_memory_palace_integration
        from .system_integration_framework import create_system_integration_framework
        from .task_list_converter import create_task_list_converter
        
        # Create and register components
        ace_reporter = create_ace_reporter_integration()
        monitor.register_component("ace_reporter", ace_reporter)
        
        memory_palace = create_ai_memory_palace_integration()
        monitor.register_component("memory_palace", memory_palace)
        
        system_framework = create_system_integration_framework()
        monitor.register_component("system_framework", system_framework)
        
        task_converter = create_task_list_converter()
        monitor.register_component("task_converter", task_converter)
        
        logging.getLogger(__name__).info("Integration monitoring setup completed successfully")
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to setup integration monitoring: {e}")
    
    return monitor


if __name__ == "__main__":
    # Example usage
    async def main():
        monitor = await setup_integration_monitoring()
        
        # Perform initial health check
        report = await monitor.perform_health_check(HealthCheckType.COMPREHENSIVE)
        
        print(f"Integration Health Status: {report.system_status}")
        print(f"Overall Health Score: {report.overall_health_score:.2f}")
        print(f"Components Monitored: {len(report.component_health)}")
        print(f"Active Alerts: {len(report.active_alerts)}")
        
        # Export report
        monitor.export_health_report("integration_health_report.json")
    
    asyncio.run(main())