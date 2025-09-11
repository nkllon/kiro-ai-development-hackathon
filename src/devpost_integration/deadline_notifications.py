#!/usr/bin/env python3
"""
Deadline Notifications - Notification management for deadlines

Extracted from deadline_tracker.py for RM-DDD compliance.
Single responsibility: Deadline notification management and delivery.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from .deadline_models import DeadlineInfo, DeadlineAlert, DeadlineConfiguration
from .notification_manager import NotificationManager
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Deadline Notifications',
            'description': 'deadline_notifications module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class DeadlineNotificationManager(ReflectiveModule):
    """Manages deadline notifications and alerts"""
    
    def __init__(self, config: Optional[DeadlineConfiguration] = None, 
        super().__init__(module_id="deadline_notifications", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

                 notification_manager: Optional[NotificationManager] = None):
        """Initialize deadline notification manager"""
        self.config = config or DeadlineConfiguration()
        self.notification_manager = notification_manager or NotificationManager()
        self.alerts: List[DeadlineAlert] = []
        self.alert_history: List[DeadlineAlert] = []
        
        # Notification settings
        self.alert_storage_path = Path("deadline_alerts.json")
        self.max_alert_history = 1000
        
        # Statistics
        self.stats = {
            'alerts_created': 0,
            'alerts_sent': 0,
            'alerts_failed': 0,
            'alerts_retried': 0,
            'last_alert_time': None
        }
        
        # Load existing alerts
        self._load_alerts()
    
    def create_deadline_alert(self, deadline: DeadlineInfo, 
                             alert_type: str = "email",
                             custom_message: Optional[str] = None) -> Optional[DeadlineAlert]:
        """Create a deadline alert"""
        try:
            # Generate alert ID
            alert_id = f"alert_{deadline.hackathon_id}_{int(datetime.now().timestamp())}"
            
            # Generate message
            if custom_message:
                message = custom_message
            else:
                if deadline.is_overdue:
                    message = f"🚨 OVERDUE: {deadline.hackathon_name} deadline has passed!"
                elif deadline.is_soon:
                    message = f"⚠️ URGENT: {deadline.hackathon_name} deadline in {deadline.time_remaining}"
                else:
                    message = f"📅 REMINDER: {deadline.hackathon_name} deadline in {deadline.time_remaining}"
            
            # Create alert
            alert = DeadlineAlert(
                alert_id=alert_id,
                deadline_id=deadline.hackathon_id,
                alert_time=datetime.now(),
                alert_type=alert_type,
                message=message
            )
            
            # Add to alerts list
            self.alerts.append(alert)
            self.stats['alerts_created'] += 1
            
            # Save alerts
            self._save_alerts()
            
            logger.info(f"Created deadline alert: {alert_id}")
            return alert
            
        except Exception as e:
            logger.error(f"Error creating deadline alert: {e}")
            return None
    
    def send_deadline_alert(self, alert: DeadlineAlert) -> bool:
        """Send a deadline alert"""
        try:
            if not self.config.enable_notifications:
                logger.info("Notifications disabled, skipping alert")
                return True
            
            # Check if alert type is enabled
            if alert.alert_type not in self.config.notification_types:
                logger.info(f"Alert type {alert.alert_type} not enabled")
                return True
            
            # Send notification based on type
            success = False
            if alert.alert_type == "email":
                success = self._send_email_alert(alert)
            elif alert.alert_type == "push":
                success = self._send_push_alert(alert)
            elif alert.alert_type == "sms":
                success = self._send_sms_alert(alert)
            elif alert.alert_type == "in_app":
                success = self._send_in_app_alert(alert)
            else:
                logger.warning(f"Unknown alert type: {alert.alert_type}")
                return False
            
            if success:
                alert.mark_sent()
                self.stats['alerts_sent'] += 1
                self.stats['last_alert_time'] = datetime.now().isoformat()
                logger.info(f"Sent deadline alert: {alert.alert_id}")
            else:
                self.stats['alerts_failed'] += 1
                logger.error(f"Failed to send deadline alert: {alert.alert_id}")
            
            # Save alerts
            self._save_alerts()
            return success
            
        except Exception as e:
            logger.error(f"Error sending deadline alert: {e}")
            self.stats['alerts_failed'] += 1
            return False
    
    def process_deadline_alerts(self, deadlines: List[DeadlineInfo]) -> int:
        """Process all deadline alerts"""
        try:
            alerts_sent = 0
            
            for deadline in deadlines:
                # Check if we should create an alert
                if self._should_create_alert(deadline):
                    alert = self.create_deadline_alert(deadline)
                    if alert:
                        if self.send_deadline_alert(alert):
                            alerts_sent += 1
            
            logger.info(f"Processed deadline alerts: {alerts_sent} sent")
            return alerts_sent
            
        except Exception as e:
            logger.error(f"Error processing deadline alerts: {e}")
            return 0
    
    def retry_failed_alerts(self) -> int:
        """Retry failed alerts"""
        try:
            retried_count = 0
            
            for alert in self.alerts:
                if not alert.is_sent and alert.can_retry():
                    if self.send_deadline_alert(alert):
                        retried_count += 1
                    else:
                        alert.increment_retry()
                        self.stats['alerts_retried'] += 1
            
            logger.info(f"Retried failed alerts: {retried_count} successful")
            return retried_count
            
        except Exception as e:
            logger.error(f"Error retrying failed alerts: {e}")
            return 0
    
    def get_pending_alerts(self) -> List[DeadlineAlert]:
        """Get pending alerts that need to be sent"""
        return [alert for alert in self.alerts if not alert.is_sent]
    
    def get_sent_alerts(self) -> List[DeadlineAlert]:
        """Get sent alerts"""
        return [alert for alert in self.alerts if alert.is_sent]
    
    def get_failed_alerts(self) -> List[DeadlineAlert]:
        """Get failed alerts"""
        return [alert for alert in self.alerts if not alert.is_sent and not alert.can_retry()]
    
    def clear_old_alerts(self, days_old: int = 30) -> int:
        """Clear old alerts from history"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            old_alerts = [alert for alert in self.alerts if alert.alert_time < cutoff_date]
            
            # Remove old alerts
            self.alerts = [alert for alert in self.alerts if alert.alert_time >= cutoff_date]
            
            # Add to history
            self.alert_history.extend(old_alerts)
            if len(self.alert_history) > self.max_alert_history:
                self.alert_history = self.alert_history[-self.max_alert_history:]
            
            # Save alerts
            self._save_alerts()
            
            logger.info(f"Cleared {len(old_alerts)} old alerts")
            return len(old_alerts)
            
        except Exception as e:
            logger.error(f"Error clearing old alerts: {e}")
            return 0
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return {
            'notification_stats': self.stats.copy(),
            'total_alerts': len(self.alerts),
            'pending_alerts': len(self.get_pending_alerts()),
            'sent_alerts': len(self.get_sent_alerts()),
            'failed_alerts': len(self.get_failed_alerts()),
            'alert_history_size': len(self.alert_history),
            'notifications_enabled': self.config.enable_notifications,
            'notification_types': self.config.notification_types
        }
    
    def _should_create_alert(self, deadline: DeadlineInfo) -> bool:
        """Check if alert should be created for deadline"""
        try:
            # Don't alert for completed deadlines
            if deadline.is_completed:
                return False
            
            # Always alert for overdue deadlines
            if deadline.is_overdue:
                return True
            
            # Check if deadline is soon
            if deadline.is_soon:
                # Check if we've already created an alert recently
                recent_alerts = [
                    alert for alert in self.alerts 
                    if alert.deadline_id == deadline.hackathon_id 
                    and alert.alert_time > datetime.now() - timedelta(hours=1)
                ]
                return len(recent_alerts) == 0
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert condition: {e}")
            return False
    
    def _send_email_alert(self, alert: DeadlineAlert) -> bool:
        """Send email alert"""
        try:
            # Use notification manager to send email
            return self.notification_manager.send_notification(
                notification_type="email",
                title="Deadline Alert",
                message=alert.message,
                priority="high"
            )
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def _send_push_alert(self, alert: DeadlineAlert) -> bool:
        """Send push notification alert"""
        try:
            # Use notification manager to send push notification
            return self.notification_manager.send_notification(
                notification_type="push",
                title="Deadline Alert",
                message=alert.message,
                priority="high"
            )
        except Exception as e:
            logger.error(f"Error sending push alert: {e}")
            return False
    
    def _send_sms_alert(self, alert: DeadlineAlert) -> bool:
        """Send SMS alert"""
        try:
            # Use notification manager to send SMS
            return self.notification_manager.send_notification(
                notification_type="sms",
                title="Deadline Alert",
                message=alert.message,
                priority="high"
            )
        except Exception as e:
            logger.error(f"Error sending SMS alert: {e}")
            return False
    
    def _send_in_app_alert(self, alert: DeadlineAlert) -> bool:
        """Send in-app notification alert"""
        try:
            # Use notification manager to send in-app notification
            return self.notification_manager.send_notification(
                notification_type="in_app",
                title="Deadline Alert",
                message=alert.message,
                priority="high"
            )
        except Exception as e:
            logger.error(f"Error sending in-app alert: {e}")
            return False
    
    def _load_alerts(self) -> None:
        """Load alerts from storage"""
        try:
            if not self.alert_storage_path.exists():
                return
            
            with open(self.alert_storage_path, 'r') as f:
                data = json.load(f)
            
            # Load alerts
            self.alerts = [DeadlineAlert.from_dict(alert_data) for alert_data in data.get('alerts', [])]
            self.alert_history = [DeadlineAlert.from_dict(alert_data) for alert_data in data.get('alert_history', [])]
            
            logger.info(f"Loaded {len(self.alerts)} alerts from storage")
            
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
    
    def _save_alerts(self) -> None:
        """Save alerts to storage"""
        try:
            data = {
                'alerts': [alert.to_dict() for alert in self.alerts],
                'alert_history': [alert.to_dict() for alert in self.alert_history],
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.alert_storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")
    
    def is_healthy(self) -> bool:
        """Check if notification manager is healthy"""
        try:
            # Check if notification manager is healthy
            if not self.notification_manager.is_healthy():
                return False
            
            # Check if we can access alert storage
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'notification_manager_healthy': self.is_healthy(),
                'notification_manager_health': self.notification_manager.get_health_indicators(),
                'config': self.config.to_dict(),
                'stats': self.stats,
                'total_alerts': len(self.alerts),
                'storage_accessible': self.alert_storage_path.parent.exists()
            }
        except Exception as e:
            return {
                'notification_manager_healthy': False,
                'error': str(e)
            }
