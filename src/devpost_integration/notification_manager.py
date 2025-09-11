#!/usr/bin/env python3
"""
Devpost Notification Manager

Handles desktop notifications, email alerts, and status change notifications
for hackathon deadlines and submission updates.

Requirements: 4.2, 4.4
"""

import json
import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    import plyer
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

from .models import NotificationSettings


@dataclass
class NotificationConfig:
    """Notification configuration settings."""
    enabled: bool = True
    desktop_notifications: bool = True
    email_notifications: bool = False
    email_address: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    deadline_warning_hours: int = 24
    status_change_notifications: bool = True


class NotificationManager:
    """
    Manages notifications for deadline reminders and status changes.
    
    Provides comprehensive notification delivery with:
    - Desktop notifications using plyer
    - Email notifications via SMTP
    - Submission status change alerts
    - Configurable notification preferences
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize notification manager.
        
        Args:
            config_file: Path to notification configuration file
        """
        self.config_file = config_file or Path.cwd() / '.devpost' / 'notifications.json'
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Notification history for deduplication
        self._notification_history: List[Dict[str, Any]] = []
        self._history_file = self.config_file.parent / 'notification_history.json'
        self._load_notification_history()
    
    def _load_config(self) -> NotificationConfig:
        """Load notification configuration from file."""
        try:
            if self.config_file.exists():
                config_data = json.loads(self.config_file.read_text())
                return NotificationConfig(**config_data)
            else:
                # Create default configuration
                default_config = NotificationConfig()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"Failed to load notification config: {e}")
            return NotificationConfig()
    
    def _save_config(self, config: NotificationConfig) -> None:
        """Save notification configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(asdict(config), indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save notification config: {e}")
    
    def _load_notification_history(self) -> None:
        """Load notification history for deduplication."""
        try:
            if self._history_file.exists():
                self._notification_history = json.loads(self._history_file.read_text())
            else:
                self._notification_history = []
        except Exception as e:
            self.logger.error(f"Failed to load notification history: {e}")
            self._notification_history = []
    
    def _save_notification_history(self) -> None:
        """Save notification history to file."""
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Keep only recent notifications (last 30 days)
            cutoff_date = datetime.now().timestamp() - (30 * 24 * 3600)
            recent_notifications = [
                n for n in self._notification_history 
                if n.get('timestamp', 0) > cutoff_date
            ]
            
            self._history_file.write_text(json.dumps(recent_notifications, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save notification history: {e}")
    
    def configure_notifications(self, config_updates: Dict[str, Any]) -> None:
        """
        Update notification configuration.
        
        Args:
            config_updates: Dictionary of configuration updates
        """
        try:
            # Update configuration
            for key, value in config_updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Save updated configuration
            self._save_config(self.config)
            
            self.logger.info("Notification configuration updated")
            
        except Exception as e:
            self.logger.error(f"Failed to configure notifications: {e}")
            raise
    
    def disable_notifications(self) -> None:
        """Disable all notifications."""
        self.config.enabled = False
        self._save_config(self.config)
        self.logger.info("Notifications disabled")
    
    def send_deadline_notification(
        self,
        hackathon_name: str,
        deadline_date: datetime,
        time_remaining: str,
        requirements: List[Dict[str, Any]],
        message: Optional[str] = None
    ) -> bool:
        """
        Send deadline reminder notification.
        
        Args:
            hackathon_name: Name of the hackathon
            deadline_date: Deadline date and time
            time_remaining: Formatted time remaining string
            requirements: List of submission requirements
            message: Custom notification message
            
        Returns:
            True if notification was sent successfully
        """
        if not self.config.enabled:
            return False
        
        try:
            # Check for duplicate notifications
            notification_key = f"deadline_{hackathon_name}_{deadline_date.isoformat()}"
            if self._is_duplicate_notification(notification_key):
                return False
            
            # Create notification content
            title = f"⏰ Deadline Alert: {hackathon_name}"
            
            if message:
                content = message
            else:
                content = f"Deadline: {deadline_date.strftime('%Y-%m-%d %H:%M')}\n"
                content += f"Time remaining: {time_remaining}\n"
                
                unmet_requirements = [r for r in requirements if not r.get('is_met', False)]
                if unmet_requirements:
                    content += f"\nOutstanding requirements: {len(unmet_requirements)}"
            
            # Send desktop notification
            desktop_success = False
            if self.config.desktop_notifications:
                desktop_success = self._send_desktop_notification(title, content)
            
            # Send email notification
            email_success = False
            if self.config.email_notifications and self.config.email_address:
                email_success = self._send_email_notification(title, content)
            
            # Record notification in history
            if desktop_success or email_success:
                self._record_notification(notification_key, {
                    'type': 'deadline',
                    'hackathon_name': hackathon_name,
                    'deadline_date': deadline_date.isoformat(),
                    'title': title,
                    'content': content
                })
            
            return desktop_success or email_success
            
        except Exception as e:
            self.logger.error(f"Failed to send deadline notification: {e}")
            return False
    
    def send_status_change_notification(
        self,
        project_name: str,
        old_status: str,
        new_status: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Send notification for submission status changes.
        
        Args:
            project_name: Name of the project
            old_status: Previous status
            new_status: New status
            details: Additional details about the change
            
        Returns:
            True if notification was sent successfully
        """
        if not self.config.enabled or not self.config.status_change_notifications:
            return False
        
        try:
            # Check for duplicate notifications
            notification_key = f"status_{project_name}_{new_status}_{datetime.now().date().isoformat()}"
            if self._is_duplicate_notification(notification_key):
                return False
            
            # Create notification content
            title = f"📝 Status Update: {project_name}"
            content = f"Status changed from '{old_status}' to '{new_status}'"
            
            if details:
                content += f"\n\nDetails: {details}"
            
            # Send desktop notification
            desktop_success = False
            if self.config.desktop_notifications:
                desktop_success = self._send_desktop_notification(title, content)
            
            # Send email notification
            email_success = False
            if self.config.email_notifications and self.config.email_address:
                email_success = self._send_email_notification(title, content)
            
            # Record notification in history
            if desktop_success or email_success:
                self._record_notification(notification_key, {
                    'type': 'status_change',
                    'project_name': project_name,
                    'old_status': old_status,
                    'new_status': new_status,
                    'title': title,
                    'content': content
                })
            
            return desktop_success or email_success
            
        except Exception as e:
            self.logger.error(f"Failed to send status change notification: {e}")
            return False
    
    def send_validation_notification(
        self,
        project_name: str,
        validation_errors: List[str],
        validation_warnings: List[str],
        completion_percentage: float
    ) -> bool:
        """
        Send notification for validation results.
        
        Args:
            project_name: Name of the project
            validation_errors: List of validation errors
            validation_warnings: List of validation warnings
            completion_percentage: Project completion percentage
            
        Returns:
            True if notification was sent successfully
        """
        if not self.config.enabled:
            return False
        
        try:
            # Only send if there are significant issues or low completion
            if not validation_errors and completion_percentage > 80:
                return False
            
            # Check for duplicate notifications
            notification_key = f"validation_{project_name}_{len(validation_errors)}_{datetime.now().date().isoformat()}"
            if self._is_duplicate_notification(notification_key):
                return False
            
            # Create notification content
            if validation_errors:
                title = f"❌ Validation Issues: {project_name}"
                content = f"Found {len(validation_errors)} critical issues:\n"
                content += "\n".join(f"• {error}" for error in validation_errors[:3])
                
                if len(validation_errors) > 3:
                    content += f"\n... and {len(validation_errors) - 3} more"
            else:
                title = f"⚠️ Validation Warnings: {project_name}"
                content = f"Found {len(validation_warnings)} warnings"
            
            content += f"\n\nCompletion: {completion_percentage:.1f}%"
            
            # Send desktop notification
            desktop_success = False
            if self.config.desktop_notifications:
                desktop_success = self._send_desktop_notification(title, content)
            
            # Send email notification
            email_success = False
            if self.config.email_notifications and self.config.email_address:
                email_success = self._send_email_notification(title, content)
            
            # Record notification in history
            if desktop_success or email_success:
                self._record_notification(notification_key, {
                    'type': 'validation',
                    'project_name': project_name,
                    'error_count': len(validation_errors),
                    'warning_count': len(validation_warnings),
                    'completion_percentage': completion_percentage,
                    'title': title,
                    'content': content
                })
            
            return desktop_success or email_success
            
        except Exception as e:
            self.logger.error(f"Failed to send validation notification: {e}")
            return False
    
    def _send_desktop_notification(self, title: str, message: str) -> bool:
        """Send desktop notification using plyer."""
        if not PLYER_AVAILABLE:
            self.logger.warning("Plyer not available for desktop notifications")
            return False
        
        try:
            plyer.notification.notify(
                title=title,
                message=message,
                app_name="Devpost Integration",
                timeout=10
            )
            
            self.logger.info(f"Sent desktop notification: {title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send desktop notification: {e}")
            return False
    
    def _send_email_notification(self, subject: str, body: str) -> bool:
        """Send email notification via SMTP."""
        if not all([self.config.email_address, self.config.smtp_server, 
                   self.config.smtp_username, self.config.smtp_password]):
            self.logger.warning("Email configuration incomplete")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = self.config.email_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Sent email notification: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _is_duplicate_notification(self, notification_key: str) -> bool:
        """Check if notification was already sent recently."""
        # Check if same notification was sent in the last hour
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour
        
        for notification in self._notification_history:
            if (notification.get('key') == notification_key and
                notification.get('timestamp', 0) > cutoff_time):
                return True
        
        return False
    
    def _record_notification(self, key: str, data: Dict[str, Any]) -> None:
        """Record notification in history."""
        notification_record = {
            'key': key,
            'timestamp': datetime.now().timestamp(),
            'data': data
        }
        
        self._notification_history.append(notification_record)
        self._save_notification_history()
    
    def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent notification history.
        
        Args:
            limit: Maximum number of notifications to return
            
        Returns:
            List of recent notifications
        """
        # Sort by timestamp (most recent first)
        sorted_history = sorted(
            self._notification_history,
            key=lambda n: n.get('timestamp', 0),
            reverse=True
        )
        
        return sorted_history[:limit]
    
    def test_notifications(self) -> Dict[str, bool]:
        """
        Test notification delivery methods.
        
        Returns:
            Dictionary with test results for each method
        """
        results = {}
        
        # Test desktop notification
        if self.config.desktop_notifications:
            results['desktop'] = self._send_desktop_notification(
                "Test Notification",
                "This is a test desktop notification from Devpost Integration"
            )
        
        # Test email notification
        if self.config.email_notifications and self.config.email_address:
            results['email'] = self._send_email_notification(
                "Test Email Notification",
                "This is a test email notification from Devpost Integration"
            )
        
        return results