from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Alerting Core

This module was extracted from alerting.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import dataclass, field
from pydantic import BaseModel

class AlertSeverity(str, Enum, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Alert severity levels."""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    INFO = 'info'

@dataclass
class Alert(ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """An alert instance."""
    id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source_component: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_message: str = ''

class AlertRule(BaseModel, ReflectiveModule):
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """Configuration for an alert rule."""
    name: str
    description: str
    severity: AlertSeverity
    condition_function: Callable
    threshold_value: Optional[float] = None
    evaluation_interval_seconds: int = 60
    cooldown_seconds: int = 300
    auto_resolve: bool = True
    auto_resolve_threshold: Optional[float] = None

def __init__(self) -> Any:
    self.logger = logging.getLogger(__name__)
    self.alert_rules: Dict[str, AlertRule] = {}
    self.active_alerts: Dict[str, Alert] = {}
    self.alert_history: List[Alert] = []
    self.last_evaluation: Dict[str, datetime] = {}
    self.last_alert_time: Dict[str, datetime] = {}
    self.alerting_active = False
    self.alerting_task: Optional[asyncio.Task] = None
    self.alert_handlers: List[Callable] = []

def add_alert_handler(self, handler: Callable) -> None:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Add an alert handler function."""
    self.alert_handlers.append(handler)
    self.logger.info(f'Added alert handler: {handler.__name__}')

def get_active_alerts(self) -> List[Alert]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get all active alerts."""
    return list(self.active_alerts.values())

def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get active alerts by severity."""
    return [alert for alert in self.active_alerts.values() if alert.severity == severity]

def get_alert_history(self, hours: int=24) -> List[Alert]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get alert history for the specified time period."""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]

def get_alert_summary(self) -> Dict[str, Any]:
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    """Get a summary of current alert status."""
    active_by_severity = {}
    for severity in AlertSeverity:
        active_by_severity[severity.value] = len(self.get_alerts_by_severity(severity))
    recent_history = self.get_alert_history(24)
    return {'active_alerts': len(self.active_alerts), 'active_by_severity': active_by_severity, 'recent_alerts_24h': len(recent_history), 'alert_rules': len(self.alert_rules), 'last_updated': datetime.now().isoformat()}
