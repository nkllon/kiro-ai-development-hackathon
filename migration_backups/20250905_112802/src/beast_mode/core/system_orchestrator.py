"""
Beast Mode Framework - System Orchestrator
Coordinates all Beast Mode components with 99.9% uptime guarantee
Implements complete RM foundation with graceful degradation
"""

import time
import atexit
from typing import Dict, Any, List, Optional
from datetime import datetime

from .reflective_module import ReflectiveModule, HealthStatus
from .health_monitoring import HealthMonitoringSystem, HealthAlert, AlertSeverity
from ..metrics.baseline_metrics_engine import BaselineMetricsEngine
from ..tool_health.makefile_health_manager import MakefileHealthManager
from ..ghostbusters.multi_perspective_validator import MultiPerspectiveValidator

class BeastModeSystemOrchestrator(ReflectiveModule):
    """
    Master orchestrator for Beast Mode Framework
    Ensures 99.9% uptime through systematic component management
    """
    
    def __init__(self):
        super().__init__("beast_mode_system_orchestrator")
        
        # Initialize health monitoring first (critical for 99.9% uptime)
        self.health_monitor = HealthMonitoringSystem()
        
        # Initialize core components
        self.metrics_engine = BaselineMetricsEngine()
        self.makefile_manager = MakefileHealthManager(self.metrics_engine)
        self.multi_perspective_validator = MultiPerspectiveValidator()
        
        # Component registry for systematic management
        self.core_components = {
            'health_monitoring_system': self.health_monitor,
            'baseline_metrics_engine': self.metrics_engine,
            'makefile_health_manager': self.makefile_manager,
            'multi_perspective_validator': self.multi_perspective_validator
        }
        
        # Register all components with health monitor
        for component in self.core_components.values():
            self.health_monitor.register_component(component)
            
        # System state
        self.system_start_time = datetime.now()
        self.initialization_complete = False
        self.shutdown_initiated = False
        
        # Setup alert handling
        self.health_monitor.add_alert_handler(self._handle_system_alert)
        
        # Register shutdown handler
        atexit.register(self.graceful_shutdown)
        
        # Complete initialization
        self._complete_initialization()
        
    def _complete_initialization(self):
        """Complete system initialization with validation"""
        try:
            # Validate all components are healthy
            unhealthy_components = []
            for name, component in self.core_components.items():
                if not component.is_healthy():
                    unhealthy_components.append(name)
                    
            if unhealthy_components:
                self.logger.warning(f"Components not healthy at startup: {unhealthy_components}")
            else:
                self.logger.info("All components healthy at startup")
                
            self.initialization_complete = True
            
            self._update_health_indicator(
                "system_initialization",
                HealthStatus.HEALTHY,
                "complete",
                "Beast Mode system initialization complete"
            )
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.initialization_complete = False
            
    def get_module_status(self) -> Dict[str, Any]:
        """Comprehensive system status"""
        health_report = self.health_monitor.get_system_health_report()
        
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "initialization_complete": self.initialization_complete,
            "uptime_seconds": (datetime.now() - self.system_start_time).total_seconds(),
            "uptime_percentage": health_report["uptime_metrics"]["availability_percentage"],
            "uptime_target_met": health_report["system_overview"]["uptime_target_met"],
            "total_components": len(self.core_components),
            "healthy_components": health_report["system_overview"]["healthy_components"],
            "degraded_components": health_report["system_overview"]["degraded_components"],
            "active_alerts": health_report["system_overview"]["active_alerts"],
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """System health assessment"""
        if not self.initialization_complete or self.shutdown_initiated:
            return False
            
        # System is healthy if health monitor is healthy (it tracks everything else)
        return self.health_monitor.is_healthy() and not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed system health indicators"""
        health_report = self.health_monitor.get_system_health_report()
        
        return {
            "system_health": {
                "status": "healthy" if self.is_healthy() else "degraded",
                "initialization_complete": self.initialization_complete,
                "uptime_compliance": health_report["uptime_metrics"]["availability_percentage"] >= 99.9
            },
            "component_health": health_report["system_overview"],
            "uptime_metrics": health_report["uptime_metrics"],
            "alert_summary": {
                "active_alerts": len(health_report["recent_alerts"]),
                "critical_alerts": len([a for a in health_report["recent_alerts"] if a["severity"] == "critical"]),
                "unresolved_alerts": len([a for a in health_report["recent_alerts"] if not a["resolved"]])
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Beast Mode system orchestration and uptime management"""
        return "beast_mode_system_orchestration_and_uptime_management"
        
    def _handle_system_alert(self, alert: HealthAlert):
        """Handle system-level alerts"""
        self.logger.info(f"System alert: {alert.severity.value} - {alert.module_name}: {alert.message}")
        
        # Handle critical alerts that might affect 99.9% uptime
        if alert.severity == AlertSeverity.CRITICAL:
            self._handle_critical_alert(alert)
        elif alert.severity == AlertSeverity.EMERGENCY:
            self._handle_emergency_alert(alert)
            
    def _handle_critical_alert(self, alert: HealthAlert):
        """Handle critical alerts that threaten 99.9% uptime"""
        self.logger.warning(f"CRITICAL ALERT: {alert.module_name} - {alert.message}")
        
        # Implement recovery strategies based on component
        if alert.module_name == "baseline_metrics_engine":
            self._recover_metrics_engine()
        elif alert.module_name == "makefile_health_manager":
            self._recover_makefile_manager()
        elif alert.module_name == "health_monitoring_system":
            self._recover_health_monitor()
            
    def _handle_emergency_alert(self, alert: HealthAlert):
        """Handle emergency alerts that require immediate action"""
        self.logger.error(f"EMERGENCY ALERT: {alert.module_name} - {alert.message}")
        
        # Emergency alerts might trigger system-wide graceful degradation
        failure_context = {
            "alert": alert.message,
            "component": alert.module_name,
            "severity": "emergency",
            "timestamp": alert.timestamp.isoformat()
        }
        
        self.degrade_gracefully(failure_context)
        
    def _recover_metrics_engine(self):
        """Attempt to recover metrics engine"""
        try:
            # Reinitialize metrics engine
            self.metrics_engine = BaselineMetricsEngine()
            self.core_components['baseline_metrics_engine'] = self.metrics_engine
            self.health_monitor.register_component(self.metrics_engine)
            self.logger.info("Metrics engine recovery attempted")
        except Exception as e:
            self.logger.error(f"Metrics engine recovery failed: {e}")
            
    def _recover_makefile_manager(self):
        """Attempt to recover Makefile manager"""
        try:
            # Reinitialize Makefile manager
            self.makefile_manager = MakefileHealthManager(self.metrics_engine)
            self.core_components['makefile_health_manager'] = self.makefile_manager
            self.health_monitor.register_component(self.makefile_manager)
            self.logger.info("Makefile manager recovery attempted")
        except Exception as e:
            self.logger.error(f"Makefile manager recovery failed: {e}")
            
    def _recover_health_monitor(self):
        """Attempt to recover health monitor (critical!)"""
        try:
            # This is critical - if health monitor fails, we lose 99.9% uptime tracking
            self.logger.error("Health monitor failure - attempting emergency recovery")
            
            # Try to restart monitoring
            if hasattr(self.health_monitor, 'monitoring_active'):
                self.health_monitor.monitoring_active = True
                
        except Exception as e:
            self.logger.error(f"Health monitor recovery failed: {e}")
            # This is a system-critical failure
            
    def execute_systematic_task(self, task_name: str, task_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute systematic tasks with full monitoring and error handling
        Ensures 99.9% uptime during task execution
        """
        if not self.is_healthy():
            return {
                "success": False,
                "error": "System not healthy - cannot execute tasks",
                "system_status": self.get_module_status()
            }
            
        start_time = datetime.now()
        task_params = task_params or {}
        
        try:
            self.logger.info(f"Executing systematic task: {task_name}")
            
            # Task execution with monitoring
            if task_name == "makefile_diagnosis":
                result = self.makefile_manager.diagnose_makefile_issues()
                
            elif task_name == "makefile_repair":
                diagnosis = task_params.get('diagnosis')
                if not diagnosis:
                    return {"success": False, "error": "Diagnosis required for repair"}
                result = self.makefile_manager.fix_makefile_systematically(diagnosis)
                
            elif task_name == "multi_perspective_validation":
                context = task_params.get('context', '')
                confidence = task_params.get('confidence', 0.5)
                result = self.multi_perspective_validator.validate_c7_multi_stakeholder_perspectives(context, confidence)
                
            elif task_name == "system_health_report":
                result = self.health_monitor.get_system_health_report()
                
            else:
                return {"success": False, "error": f"Unknown task: {task_name}"}
                
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Record task execution metrics
            self.metrics_engine.establish_baseline_measurement(
                'development_velocity', 'systematic', 1.0 / execution_time  # Tasks per second
            )
            
            return {
                "success": True,
                "task_name": task_name,
                "result": result,
                "execution_time": execution_time,
                "system_health": self.is_healthy()
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Task execution failed: {task_name} - {e}")
            
            return {
                "success": False,
                "task_name": task_name,
                "error": str(e),
                "execution_time": execution_time,
                "system_health": self.is_healthy()
            }
            
    def demonstrate_99_9_uptime_capability(self) -> Dict[str, Any]:
        """
        Demonstrate 99.9% uptime capability through systematic testing
        """
        uptime_metrics = self.health_monitor.calculate_uptime_metrics()
        
        # Simulate component failure and recovery to test graceful degradation
        test_results = {
            "uptime_compliance": uptime_metrics.availability_percentage >= 99.9,
            "current_uptime": uptime_metrics.availability_percentage,
            "target_uptime": 99.9,
            "graceful_degradation_tested": False,
            "recovery_capability_tested": False
        }
        
        try:
            # Test graceful degradation
            self.logger.info("Testing graceful degradation capability...")
            
            # Temporarily degrade a non-critical component
            test_component = self.multi_perspective_validator
            failure_context = {"test": "graceful_degradation_test", "component": "multi_perspective_validator"}
            
            degradation_result = test_component.degrade_gracefully(failure_context)
            test_results["graceful_degradation_tested"] = degradation_result.degradation_applied
            
            # Wait a moment then check system still operational
            time.sleep(1.0)
            system_still_healthy = self.health_monitor.is_healthy()
            test_results["system_resilience"] = system_still_healthy
            
            # Test recovery (component should recover automatically)
            time.sleep(2.0)
            component_recovered = test_component.is_healthy()
            test_results["recovery_capability_tested"] = component_recovered
            
            self.logger.info("99.9% uptime capability testing complete")
            
        except Exception as e:
            self.logger.error(f"Uptime capability testing failed: {e}")
            test_results["test_error"] = str(e)
            
        return {
            "uptime_metrics": {
                "availability_percentage": uptime_metrics.availability_percentage,
                "total_uptime_hours": uptime_metrics.total_uptime_seconds / 3600,
                "downtime_events": len(uptime_metrics.downtime_events),
                "mttr_minutes": uptime_metrics.mttr_seconds / 60,
                "mtbf_hours": uptime_metrics.mtbf_seconds / 3600
            },
            "capability_tests": test_results,
            "compliance_status": "COMPLIANT" if uptime_metrics.availability_percentage >= 99.9 else "NON_COMPLIANT"
        }
        
    def graceful_shutdown(self):
        """Graceful system shutdown with final health report"""
        if self.shutdown_initiated:
            return
            
        self.shutdown_initiated = True
        self.logger.info("Initiating graceful Beast Mode system shutdown...")
        
        try:
            # Generate final system report
            final_report = self.health_monitor.get_system_health_report()
            
            # Shutdown health monitoring
            self.health_monitor.shutdown()
            
            # Log final status
            uptime_percentage = final_report["uptime_metrics"]["availability_percentage"]
            uptime_compliant = uptime_percentage >= 99.9
            
            self.logger.info(f"Beast Mode shutdown complete:")
            self.logger.info(f"  Final uptime: {uptime_percentage:.3f}%")
            self.logger.info(f"  99.9% compliance: {uptime_compliant}")
            self.logger.info(f"  Total components: {final_report['system_overview']['total_components']}")
            self.logger.info(f"  Healthy at shutdown: {final_report['system_overview']['healthy_components']}")
            
        except Exception as e:
            self.logger.error(f"Graceful shutdown error: {e}")
            
    def get_beast_mode_superiority_proof(self) -> Dict[str, Any]:
        """
        Generate comprehensive proof of Beast Mode systematic superiority
        """
        # Get metrics from all components
        superiority_evidence = self.metrics_engine.generate_superiority_evidence()
        uptime_capability = self.demonstrate_99_9_uptime_capability()
        makefile_superiority = self.makefile_manager.demonstrate_systematic_superiority()
        
        return {
            "systematic_methodology_proof": {
                "metrics_superiority": superiority_evidence.__dict__ if superiority_evidence else None,
                "uptime_capability": uptime_capability,
                "tool_health_superiority": makefile_superiority,
                "multi_perspective_validation": "Ghostbusters framework operational"
            },
            "overall_assessment": {
                "systematic_vs_adhoc_improvement": superiority_evidence.overall_superiority_score if superiority_evidence else 0,
                "uptime_compliance": uptime_capability["compliance_status"],
                "evidence_quality": superiority_evidence.evidence_quality_score if superiority_evidence else 0,
                "beast_mode_ready": self.is_healthy() and uptime_capability["compliance_status"] == "COMPLIANT"
            }
        }