"""
Alert management system for MSP SSL Chaos Tamer

Provides alerting capabilities for certificate expiration, system health,
and emergency scenarios with integration to MSP notification systems.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from ..core.interfaces import ReflectiveModule


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertManager(ReflectiveModule):
    """
    Alert management for MSP SSL operations
    
    Manages alerts for certificate expiration, system health issues,
    and emergency scenarios with MSP-specific notification workflows.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        self.logger = logging.getLogger("msp_ssl.alert_manager")
        
        # Alert configuration
        self.alert_channels = self.config.get("alert_channels", [])
        self.alert_thresholds = self.config.get("alert_thresholds", {
            "certificate_expiry_days": [7, 14, 30],
            "system_health_score": 0.8,
            "ca_plugin_failures": 3
        })
        
        # Alert history
        self.alert_history: List[Dict[str, Any]] = []
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Alert manager initialized")
    
    def create_alert(self, alert_type: str, severity: AlertSeverity, 
                    message: str, details: Dict[str, Any] = None) -> str:
        """
        Create new alert
        
        Args:
            alert_type: Type of alert (certificate_expiry, system_health, etc.)
            severity: Alert severity level
            message: Alert message
            details: Additional alert details
            
        Returns:
            str: Alert ID
        """
        alert_id = f"{alert_type}_{int(datetime.utcnow().timestamp())}"
        
        alert = {
            "id": alert_id,
            "type": alert_type,
            "severity": severity.value,
            "message": message,
            "details": details or {},
            "created_at": datetime.utcnow(),
            "acknowledged": False,
            "resolved": False
        }
        
        # Add to active alerts
        self.active_alerts[alert_id] = alert
        
        # Add to history
        self.alert_history.append(alert.copy())
        
        self.logger.warning(f"Alert created: {alert_type} - {message}")
        
        # Send notifications
        self._send_notifications(alert)
        
        return alert_id
    
    def _send_notifications(self, alert: Dict[str, Any]) -> None:
        """Send alert notifications to configured channels"""
        # This would integrate with actual notification systems
        # For now, just log the alert
        self.logger.info(f"Alert notification: {alert['message']}")
    
    # ReflectiveModule implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get alert manager module information"""
        return {
            "module_name": "alert_manager",
            "module_type": "monitoring",
            "version": "1.0.0",
            "description": "Alert management for MSP SSL operations"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get alert manager capabilities"""
        return [
            {"name": "alert_creation", "enabled": True},
            {"name": "alert_notifications", "enabled": True},
            {"name": "alert_history", "enabled": True}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get alert manager health status"""
        return {
            "status": "healthy",
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "last_check": datetime.utcnow().isoformat()
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for alert manager"""
        return {
            "degradation_applied": False,
            "fallback_mode": None,
            "message": "Alert manager operating normally"
        }