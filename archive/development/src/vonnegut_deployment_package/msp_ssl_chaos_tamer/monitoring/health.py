"""
Health monitoring system for MSP SSL Chaos Tamer

Provides comprehensive health monitoring, alerting, and system status reporting
for all components with integration into the Beast Mode observability framework.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

from ..core.interfaces import ReflectiveModule


class HealthStatus(Enum):
    """System health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthMonitor(ReflectiveModule):
    """
    Comprehensive health monitoring for MSP SSL Chaos Tamer
    
    Monitors all system components, provides health scoring,
    and integrates with alerting systems for proactive monitoring.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        self.logger = logging.getLogger("msp_ssl.health_monitor")
        
        # Component registry
        self.components: Dict[str, Any] = {}
        self.health_checks: Dict[str, callable] = {}
        
        # Health thresholds
        self.health_check_interval = self.config.get("health_check_interval", 60)
        self.degraded_threshold = self.config.get("degraded_threshold", 0.8)
        self.unhealthy_threshold = self.config.get("unhealthy_threshold", 0.5)
        
        self.logger.info("Health monitor initialized")
    
    def register_component(self, name: str, component: Any, 
                          health_check: Optional[callable] = None) -> bool:
        """
        Register component for health monitoring
        
        Args:
            name: Component name
            component: Component instance
            health_check: Optional custom health check function
            
        Returns:
            bool: True if registration successful
        """
        try:
            self.components[name] = {
                "component": component,
                "registered_at": datetime.utcnow(),
                "last_check": None,
                "status": HealthStatus.UNKNOWN,
                "error_count": 0,
                "last_error": None
            }
            
            if health_check:
                self.health_checks[name] = health_check
            
            self.logger.info(f"Registered component for health monitoring: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register component {name}: {e}")
            return False
    
    def check_component_health(self, name: str) -> Dict[str, Any]:
        """
        Check health of a specific component
        
        Args:
            name: Component name
            
        Returns:
            Dict containing health status and details
        """
        if name not in self.components:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "error": f"Component {name} not registered"
            }
        
        component_info = self.components[name]
        component = component_info["component"]
        
        try:
            # Use custom health check if available
            if name in self.health_checks:
                health_result = self.health_checks[name](component)
            else:
                # Use ReflectiveModule health check if available
                if hasattr(component, 'get_health_status'):
                    health_result = component.get_health_status()
                else:
                    # Basic health check
                    health_result = {"status": "healthy"}
            
            # Update component info
            component_info["last_check"] = datetime.utcnow()
            component_info["status"] = HealthStatus(health_result.get("status", "unknown"))
            
            if health_result.get("status") != "healthy":
                component_info["error_count"] += 1
                component_info["last_error"] = health_result.get("error")
            
            return {
                "component": name,
                "status": health_result.get("status", "unknown"),
                "last_check": component_info["last_check"].isoformat(),
                "error_count": component_info["error_count"],
                "details": health_result
            }
            
        except Exception as e:
            component_info["error_count"] += 1
            component_info["last_error"] = str(e)
            component_info["status"] = HealthStatus.UNHEALTHY
            
            self.logger.error(f"Health check failed for {name}: {e}")
            
            return {
                "component": name,
                "status": HealthStatus.UNHEALTHY.value,
                "last_check": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def check_all_components(self) -> Dict[str, Any]:
        """
        Check health of all registered components
        
        Returns:
            Dict containing overall health status and component details
        """
        component_results = {}
        healthy_count = 0
        total_count = len(self.components)
        
        for name in self.components:
            result = self.check_component_health(name)
            component_results[name] = result
            
            if result["status"] == HealthStatus.HEALTHY.value:
                healthy_count += 1
        
        # Calculate overall health score
        health_score = healthy_count / total_count if total_count > 0 else 1.0
        
        # Determine overall status
        if health_score >= self.degraded_threshold:
            overall_status = HealthStatus.HEALTHY
        elif health_score >= self.unhealthy_threshold:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        return {
            "overall_status": overall_status.value,
            "health_score": health_score,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "components": component_results,
            "check_timestamp": datetime.utcnow().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health_check = self.check_all_components()
        
        return {
            "system": {
                "status": health_check["overall_status"],
                "health_score": health_check["health_score"],
                "uptime": self._get_uptime(),
                "version": "1.0.0"
            },
            "components": health_check["components"],
            "timestamp": health_check["check_timestamp"]
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        # This would track actual uptime
        # For now, return placeholder
        return "0d 0h 0m"
    
    # ReflectiveModule implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get health monitor module information"""
        return {
            "module_name": "health_monitor",
            "module_type": "monitoring",
            "version": "1.0.0",
            "description": "Comprehensive health monitoring for MSP SSL components"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get health monitor capabilities"""
        return [
            {"name": "component_health_monitoring", "enabled": True},
            {"name": "system_health_scoring", "enabled": True},
            {"name": "health_check_automation", "enabled": True},
            {"name": "error_tracking", "enabled": True}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health monitor status"""
        return {
            "status": "healthy",
            "registered_components": len(self.components),
            "health_check_interval": self.health_check_interval,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for health monitor"""
        return {
            "degradation_applied": False,
            "fallback_mode": None,
            "message": "Health monitor operating normally"
        }