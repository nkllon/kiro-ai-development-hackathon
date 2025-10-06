"""
Patch Lifecycle Management System.

This module implements comprehensive lifecycle management for technical debt patches,
including creation tracking, expiration monitoring, automated notifications, and
escalation workflows with dashboard alerts.

Requirements Coverage:
- 7.1: Patch creation dates and expected resolution timeframes
- 7.2: Automated notifications when patches approach expiration
- 7.3: Escalation for patches exceeding intended lifespan
- 7.4: Documentation and verification of patch cleanup completion
- 7.5: Validation of cleanup process through testing
"""

import json
import smtplib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set
from pathlib import Path
from enum import Enum

# Email imports with fallback
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    MimeText = None
    MimeMultipart = None

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import PatchAnnotation, DebtLevel, ValidationResult


class PatchStatus(Enum):
    """Lifecycle status of patches."""
    ACTIVE = "Active"                    # Patch is active and within expected timeframe
    APPROACHING_EXPIRATION = "Approaching_Expiration"  # Patch is near expiration date
    EXPIRED = "Expired"                  # Patch has exceeded expected resolution date
    ESCALATED = "Escalated"             # Patch has been escalated for immediate attention
    CLEANUP_PLANNED = "Cleanup_Planned"  # Cleanup has been scheduled
    CLEANUP_IN_PROGRESS = "Cleanup_In_Progress"  # Cleanup is actively being worked on
    RESOLVED = "Resolved"               # Patch has been successfully removed
    VALIDATED = "Validated"             # Cleanup has been verified through testing


class NotificationType(Enum):
    """Types of notifications for patch lifecycle events."""
    EXPIRATION_WARNING = "Expiration_Warning"
    EXPIRATION_ALERT = "Expiration_Alert"
    ESCALATION = "Escalation"
    CLEANUP_REMINDER = "Cleanup_Reminder"
    RESOLUTION_CONFIRMATION = "Resolution_Confirmation"


@dataclass
class NotificationConfig:
    """Configuration for patch lifecycle notifications."""
    email_enabled: bool = True
    slack_enabled: bool = False
    dashboard_alerts_enabled: bool = True
    
    # Email configuration
    smtp_server: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = "patches@company.com"
    
    # Slack configuration
    slack_webhook_url: str = ""
    slack_channel: str = "#technical-debt"
    
    # Notification timing
    warning_days_before_expiration: int = 7
    alert_days_before_expiration: int = 3
    escalation_days_after_expiration: int = 5
    cleanup_reminder_interval_days: int = 14


@dataclass
class LifecycleEvent:
    """Record of a lifecycle event for a patch."""
    event_id: str
    patch_id: str
    event_type: str
    timestamp: datetime
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""


@dataclass
class EscalationRule:
    """Rule for escalating overdue patches."""
    name: str
    condition: Callable[[PatchAnnotation, datetime], bool]
    escalation_level: int  # 1=team lead, 2=manager, 3=director
    notification_template: str
    dashboard_priority: str = "high"


class PatchLifecycleManager(ReflectiveModule):
    """
    Comprehensive patch lifecycle management system.
    
    Provides automated tracking, monitoring, notifications, and escalation
    workflows for technical debt patches throughout their entire lifecycle.
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        Initialize the patch lifecycle manager.
        
        Args:
            config: Notification configuration settings
        """
        super().__init__()
        self.config = config or NotificationConfig()
        self.patches: Dict[str, PatchAnnotation] = {}
        self.lifecycle_events: List[LifecycleEvent] = []
        self.escalation_rules: List[EscalationRule] = []
        self.notification_handlers: Dict[NotificationType, List[Callable]] = {
            notification_type: [] for notification_type in NotificationType
        }
        
        # Initialize default escalation rules
        self._setup_default_escalation_rules()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Metrics tracking
        self.metrics = {
            'patches_tracked': 0,
            'notifications_sent': 0,
            'escalations_triggered': 0,
            'patches_resolved': 0,
            'average_resolution_time_days': 0.0
        }
    
    def track_patch(self, patch: PatchAnnotation) -> None:
        """
        Start tracking a patch in the lifecycle management system.
        
        Args:
            patch: PatchAnnotation to track
            
        Requirements: 7.1 - Track creation dates and expected resolution timeframes
        """
        self.patches[patch.patch_id] = patch
        self.metrics['patches_tracked'] += 1
        
        # Record lifecycle event
        event = LifecycleEvent(
            event_id=f"EVENT-{len(self.lifecycle_events):06d}",
            patch_id=patch.patch_id,
            event_type="PATCH_CREATED",
            timestamp=patch.created_date,
            description=f"Patch {patch.patch_id} created and added to lifecycle tracking",
            metadata={
                'debt_level': patch.debt_level.value,
                'component': patch.component,
                'expected_resolution': patch.expected_resolution.isoformat() if patch.expected_resolution else None
            },
            created_by=patch.created_by
        )
        self.lifecycle_events.append(event)
        
        self.logger.info(f"Started tracking patch {patch.patch_id} in component {patch.component}")
    
    def check_patch_deadlines(self) -> Dict[str, List[PatchAnnotation]]:
        """
        Check all tracked patches for approaching or exceeded deadlines.
        
        Returns:
            Dictionary categorizing patches by their deadline status
            
        Requirements: 7.2 - Automated deadline monitoring
        """
        now = datetime.now()
        categorized_patches = {
            'approaching_expiration': [],
            'expired': [],
            'escalated': [],
            'active': []
        }
        
        for patch in self.patches.values():
            if not patch.expected_resolution:
                categorized_patches['active'].append(patch)
                continue
            
            days_until_expiration = (patch.expected_resolution - now).days
            days_since_expiration = (now - patch.expected_resolution).days
            
            if days_since_expiration > self.config.escalation_days_after_expiration:
                categorized_patches['escalated'].append(patch)
                self._trigger_escalation(patch, days_since_expiration)
            elif days_since_expiration > 0:
                categorized_patches['expired'].append(patch)
                self._send_expiration_alert(patch, days_since_expiration)
            elif days_until_expiration <= self.config.warning_days_before_expiration:
                categorized_patches['approaching_expiration'].append(patch)
                self._send_expiration_warning(patch, days_until_expiration)
            else:
                categorized_patches['active'].append(patch)
        
        return categorized_patches
    
    def send_notifications(self, notification_type: NotificationType, patches: List[PatchAnnotation]) -> int:
        """
        Send notifications for patches based on their lifecycle status.
        
        Args:
            notification_type: Type of notification to send
            patches: List of patches to notify about
            
        Returns:
            Number of notifications successfully sent
            
        Requirements: 7.2 - Automated notifications to responsible teams
        """
        notifications_sent = 0
        
        for patch in patches:
            try:
                # Email notifications
                if self.config.email_enabled:
                    self._send_email_notification(notification_type, patch)
                    notifications_sent += 1
                
                # Slack notifications
                if self.config.slack_enabled and self.config.slack_webhook_url:
                    self._send_slack_notification(notification_type, patch)
                
                # Dashboard alerts
                if self.config.dashboard_alerts_enabled:
                    self._create_dashboard_alert(notification_type, patch)
                
                # Record notification event
                self._record_notification_event(notification_type, patch)
                
            except Exception as e:
                self.logger.error(f"Failed to send {notification_type.value} notification for patch {patch.patch_id}: {e}")
        
        self.metrics['notifications_sent'] += notifications_sent
        return notifications_sent
    
    def escalate_overdue_patches(self) -> List[PatchAnnotation]:
        """
        Escalate patches that have exceeded their intended lifespan.
        
        Returns:
            List of patches that were escalated
            
        Requirements: 7.3 - Escalation for patches exceeding intended lifespan
        """
        now = datetime.now()
        escalated_patches = []
        
        for patch in self.patches.values():
            if not patch.expected_resolution:
                continue
            
            days_overdue = (now - patch.expected_resolution).days
            
            if days_overdue > self.config.escalation_days_after_expiration:
                # Check if already escalated recently
                recent_escalation = any(
                    event.patch_id == patch.patch_id and 
                    event.event_type == "ESCALATED" and
                    (now - event.timestamp).days < 7
                    for event in self.lifecycle_events
                )
                
                if not recent_escalation:
                    self._trigger_escalation(patch, days_overdue)
                    escalated_patches.append(patch)
        
        return escalated_patches
    
    def document_patch_resolution(self, patch_id: str, resolution_notes: str, resolved_by: str) -> bool:
        """
        Document the completion of patch cleanup with verification details.
        
        Args:
            patch_id: ID of the resolved patch
            resolution_notes: Details about how the patch was resolved
            resolved_by: Developer who completed the cleanup
            
        Returns:
            True if resolution was successfully documented
            
        Requirements: 7.4 - Document and verify patch cleanup completion
        """
        if patch_id not in self.patches:
            self.logger.error(f"Cannot document resolution for unknown patch: {patch_id}")
            return False
        
        patch = self.patches[patch_id]
        
        # Record resolution event
        event = LifecycleEvent(
            event_id=f"EVENT-{len(self.lifecycle_events):06d}",
            patch_id=patch_id,
            event_type="PATCH_RESOLVED",
            timestamp=datetime.now(),
            description=f"Patch {patch_id} resolved: {resolution_notes}",
            metadata={
                'resolution_notes': resolution_notes,
                'resolved_by': resolved_by,
                'original_debt_level': patch.debt_level.value,
                'days_to_resolution': (datetime.now() - patch.created_date).days
            },
            created_by=resolved_by
        )
        self.lifecycle_events.append(event)
        
        # Update metrics
        self.metrics['patches_resolved'] += 1
        self._update_average_resolution_time()
        
        # Send resolution confirmation
        if self.config.email_enabled:
            self._send_resolution_confirmation(patch, resolution_notes, resolved_by)
        
        self.logger.info(f"Documented resolution of patch {patch_id} by {resolved_by}")
        return True
    
    def validate_patch_cleanup(self, patch_id: str, validation_results: Dict[str, Any]) -> ValidationResult:
        """
        Validate that patch cleanup was completed successfully through testing.
        
        Args:
            patch_id: ID of the patch to validate
            validation_results: Results from cleanup validation tests
            
        Returns:
            ValidationResult indicating whether cleanup was successful
            
        Requirements: 7.5 - Validate cleanup process through testing
        """
        if patch_id not in self.patches:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown patch ID: {patch_id}"]
            )
        
        patch = self.patches[patch_id]
        errors = []
        warnings = []
        
        # Check if validation criteria were met
        if patch.validation_criteria:
            for criterion in patch.validation_criteria:
                if criterion not in validation_results:
                    errors.append(f"Validation criterion not tested: {criterion}")
                elif not validation_results[criterion]:
                    errors.append(f"Validation criterion failed: {criterion}")
        else:
            warnings.append("No validation criteria specified for this patch")
        
        # Check for required validation fields
        required_fields = ['tests_passed', 'functionality_verified', 'no_regressions']
        for field in required_fields:
            if field not in validation_results:
                warnings.append(f"Recommended validation field missing: {field}")
        
        is_valid = len(errors) == 0
        
        # Record validation event
        event = LifecycleEvent(
            event_id=f"EVENT-{len(self.lifecycle_events):06d}",
            patch_id=patch_id,
            event_type="PATCH_VALIDATED" if is_valid else "VALIDATION_FAILED",
            timestamp=datetime.now(),
            description=f"Patch {patch_id} validation {'passed' if is_valid else 'failed'}",
            metadata={
                'validation_results': validation_results,
                'validation_passed': is_valid,
                'errors_count': len(errors),
                'warnings_count': len(warnings)
            }
        )
        self.lifecycle_events.append(event)
        
        if is_valid:
            # Mark patch as validated and remove from active tracking
            del self.patches[patch_id]
            self.logger.info(f"Patch {patch_id} successfully validated and removed from tracking")
        else:
            self.logger.warning(f"Patch {patch_id} validation failed with {len(errors)} errors")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata={
                'patch_id': patch_id,
                'validation_timestamp': datetime.now().isoformat(),
                'validation_results': validation_results
            }
        )
    
    def get_lifecycle_report(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive lifecycle report for patches.
        
        Args:
            component: Optional component filter
            
        Returns:
            Dictionary containing lifecycle statistics and patch status
        """
        now = datetime.now()
        patches_to_analyze = [
            patch for patch in self.patches.values()
            if not component or patch.component == component
        ]
        
        # Categorize patches by status
        status_counts = {status.value: 0 for status in PatchStatus}
        debt_level_counts = {level.value: 0 for level in DebtLevel}
        
        overdue_patches = []
        approaching_expiration = []
        
        for patch in patches_to_analyze:
            debt_level_counts[patch.debt_level.value] += 1
            
            if patch.expected_resolution:
                days_until_expiration = (patch.expected_resolution - now).days
                if days_until_expiration < 0:
                    overdue_patches.append(patch)
                    if abs(days_until_expiration) > self.config.escalation_days_after_expiration:
                        status_counts[PatchStatus.ESCALATED.value] += 1
                    else:
                        status_counts[PatchStatus.EXPIRED.value] += 1
                elif days_until_expiration <= self.config.warning_days_before_expiration:
                    approaching_expiration.append(patch)
                    status_counts[PatchStatus.APPROACHING_EXPIRATION.value] += 1
                else:
                    status_counts[PatchStatus.ACTIVE.value] += 1
            else:
                status_counts[PatchStatus.ACTIVE.value] += 1
        
        # Calculate metrics
        total_patches = len(patches_to_analyze)
        resolved_patches = len([e for e in self.lifecycle_events if e.event_type == "PATCH_RESOLVED"])
        
        return {
            'summary': {
                'total_active_patches': total_patches,
                'total_resolved_patches': resolved_patches,
                'overdue_patches': len(overdue_patches),
                'approaching_expiration': len(approaching_expiration),
                'average_resolution_time_days': self.metrics['average_resolution_time_days']
            },
            'status_breakdown': status_counts,
            'debt_level_breakdown': debt_level_counts,
            'overdue_patches': [
                {
                    'patch_id': p.patch_id,
                    'component': p.component,
                    'debt_level': p.debt_level.value,
                    'days_overdue': (now - p.expected_resolution).days if p.expected_resolution else 0,
                    'assigned_to': p.assigned_to
                }
                for p in overdue_patches
            ],
            'metrics': self.metrics,
            'component_filter': component,
            'report_timestamp': now.isoformat()
        }
    
    def _setup_default_escalation_rules(self) -> None:
        """Setup default escalation rules for overdue patches."""
        self.escalation_rules = [
            EscalationRule(
                name="Critical Debt Escalation",
                condition=lambda patch, now: (
                    patch.debt_level == DebtLevel.CRITICAL and
                    patch.expected_resolution and
                    (now - patch.expected_resolution).days > 1
                ),
                escalation_level=3,
                notification_template="Critical technical debt patch {patch_id} is {days_overdue} days overdue",
                dashboard_priority="critical"
            ),
            EscalationRule(
                name="High Debt Escalation",
                condition=lambda patch, now: (
                    patch.debt_level == DebtLevel.HIGH and
                    patch.expected_resolution and
                    (now - patch.expected_resolution).days > 3
                ),
                escalation_level=2,
                notification_template="High priority patch {patch_id} is {days_overdue} days overdue",
                dashboard_priority="high"
            ),
            EscalationRule(
                name="Standard Escalation",
                condition=lambda patch, now: (
                    patch.expected_resolution and
                    (now - patch.expected_resolution).days > self.config.escalation_days_after_expiration
                ),
                escalation_level=1,
                notification_template="Patch {patch_id} is {days_overdue} days overdue",
                dashboard_priority="medium"
            )
        ]
    
    def _trigger_escalation(self, patch: PatchAnnotation, days_overdue: int) -> None:
        """Trigger escalation workflow for an overdue patch."""
        now = datetime.now()
        
        # Find applicable escalation rules
        applicable_rules = [
            rule for rule in self.escalation_rules
            if rule.condition(patch, now)
        ]
        
        if not applicable_rules:
            return
        
        # Use the highest escalation level
        escalation_rule = max(applicable_rules, key=lambda r: r.escalation_level)
        
        # Record escalation event
        event = LifecycleEvent(
            event_id=f"EVENT-{len(self.lifecycle_events):06d}",
            patch_id=patch.patch_id,
            event_type="ESCALATED",
            timestamp=now,
            description=f"Patch {patch.patch_id} escalated: {days_overdue} days overdue",
            metadata={
                'escalation_level': escalation_rule.escalation_level,
                'escalation_rule': escalation_rule.name,
                'days_overdue': days_overdue,
                'dashboard_priority': escalation_rule.dashboard_priority
            }
        )
        self.lifecycle_events.append(event)
        
        self.metrics['escalations_triggered'] += 1
        self.logger.warning(f"Escalated patch {patch.patch_id} ({days_overdue} days overdue)")
    
    def _send_email_notification(self, notification_type: NotificationType, patch: PatchAnnotation) -> None:
        """Send email notification for patch lifecycle event."""
        if not self.config.smtp_server or not patch.assigned_to:
            return
            
        if not EMAIL_AVAILABLE:
            self.logger.warning("Email functionality not available - skipping email notification")
            return
        
        subject_templates = {
            NotificationType.EXPIRATION_WARNING: f"Patch Expiration Warning: {patch.patch_id}",
            NotificationType.EXPIRATION_ALERT: f"Patch Expiration Alert: {patch.patch_id}",
            NotificationType.ESCALATION: f"ESCALATED: Overdue Patch {patch.patch_id}",
            NotificationType.CLEANUP_REMINDER: f"Cleanup Reminder: {patch.patch_id}",
            NotificationType.RESOLUTION_CONFIRMATION: f"Patch Resolved: {patch.patch_id}"
        }
        
        body_templates = {
            NotificationType.EXPIRATION_WARNING: f"""
Patch {patch.patch_id} is approaching its expected resolution date.

Component: {patch.component}
Debt Level: {patch.debt_level.value}
Expected Resolution: {patch.expected_resolution}
Reason: {patch.reason}
Cleanup Task: {patch.cleanup_task}

Please prioritize cleanup of this patch to prevent technical debt accumulation.
            """,
            NotificationType.EXPIRATION_ALERT: f"""
ALERT: Patch {patch.patch_id} has expired or is about to expire.

Component: {patch.component}
Debt Level: {patch.debt_level.value}
Expected Resolution: {patch.expected_resolution}
Reason: {patch.reason}
Cleanup Task: {patch.cleanup_task}

Immediate action required to resolve this technical debt.
            """,
            NotificationType.ESCALATION: f"""
ESCALATION: Patch {patch.patch_id} is significantly overdue and requires immediate attention.

Component: {patch.component}
Debt Level: {patch.debt_level.value}
Expected Resolution: {patch.expected_resolution}
Days Overdue: {(datetime.now() - patch.expected_resolution).days if patch.expected_resolution else 'N/A'}
Reason: {patch.reason}
Cleanup Task: {patch.cleanup_task}

This patch has been escalated due to extended overdue status.
            """
        }
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.config.from_email
            msg['To'] = patch.assigned_to
            msg['Subject'] = subject_templates.get(notification_type, f"Patch Notification: {patch.patch_id}")
            
            body = body_templates.get(notification_type, f"Notification for patch {patch.patch_id}")
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            if self.config.smtp_username:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    def _send_slack_notification(self, notification_type: NotificationType, patch: PatchAnnotation) -> None:
        """Send Slack notification for patch lifecycle event."""
        # Implementation would use Slack webhook API
        # Placeholder for Slack integration
        self.logger.info(f"Slack notification sent for patch {patch.patch_id}: {notification_type.value}")
    
    def _create_dashboard_alert(self, notification_type: NotificationType, patch: PatchAnnotation) -> None:
        """Create dashboard alert for patch lifecycle event."""
        # Implementation would integrate with dashboard system
        # Placeholder for dashboard integration
        self.logger.info(f"Dashboard alert created for patch {patch.patch_id}: {notification_type.value}")
    
    def _record_notification_event(self, notification_type: NotificationType, patch: PatchAnnotation) -> None:
        """Record notification event in lifecycle history."""
        event = LifecycleEvent(
            event_id=f"EVENT-{len(self.lifecycle_events):06d}",
            patch_id=patch.patch_id,
            event_type=f"NOTIFICATION_{notification_type.value.upper()}",
            timestamp=datetime.now(),
            description=f"Sent {notification_type.value} notification for patch {patch.patch_id}",
            metadata={
                'notification_type': notification_type.value,
                'recipient': patch.assigned_to
            }
        )
        self.lifecycle_events.append(event)
    
    def _send_expiration_warning(self, patch: PatchAnnotation, days_until_expiration: int) -> None:
        """Send warning notification for approaching patch expiration."""
        self.send_notifications(NotificationType.EXPIRATION_WARNING, [patch])
    
    def _send_expiration_alert(self, patch: PatchAnnotation, days_since_expiration: int) -> None:
        """Send alert notification for expired patch."""
        self.send_notifications(NotificationType.EXPIRATION_ALERT, [patch])
    
    def _send_resolution_confirmation(self, patch: PatchAnnotation, resolution_notes: str, resolved_by: str) -> None:
        """Send confirmation notification for resolved patch."""
        self.send_notifications(NotificationType.RESOLUTION_CONFIRMATION, [patch])
    
    def _update_average_resolution_time(self) -> None:
        """Update average resolution time metric."""
        resolution_events = [
            event for event in self.lifecycle_events
            if event.event_type == "PATCH_RESOLVED"
        ]
        
        if not resolution_events:
            return
        
        total_days = 0
        for event in resolution_events:
            if 'days_to_resolution' in event.metadata:
                total_days += event.metadata['days_to_resolution']
        
        self.metrics['average_resolution_time_days'] = total_days / len(resolution_events)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the lifecycle manager."""
        return {
            'status': 'healthy',
            'patches_tracked': len(self.patches),
            'lifecycle_events': len(self.lifecycle_events),
            'notifications_sent': self.metrics['notifications_sent'],
            'escalations_triggered': self.metrics['escalations_triggered'],
            'patches_resolved': self.metrics['patches_resolved']
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for ReflectiveModule compliance."""
        return {
            'module_name': 'PatchLifecycleManager',
            'version': '1.0.0',
            'description': 'Comprehensive patch lifecycle management system',
            'capabilities': [
                'patch_tracking',
                'deadline_monitoring', 
                'automated_notifications',
                'escalation_workflows',
                'resolution_documentation',
                'cleanup_validation'
            ],
            'dependencies': ['email', 'smtplib', 'datetime'],
            'configuration': {
                'email_enabled': self.config.email_enabled,
                'slack_enabled': self.config.slack_enabled,
                'dashboard_alerts_enabled': self.config.dashboard_alerts_enabled
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities for ReflectiveModule compliance."""
        return [
            'patch_tracking',
            'deadline_monitoring',
            'automated_notifications', 
            'escalation_workflows',
            'resolution_documentation',
            'cleanup_validation',
            'lifecycle_reporting',
            'health_monitoring'
        ]
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation for ReflectiveModule compliance."""
        self.logger.error(f"Lifecycle manager error: {error}")
        
        # Disable non-essential features during degradation
        degraded_config = NotificationConfig(
            email_enabled=False,
            slack_enabled=False,
            dashboard_alerts_enabled=False
        )
        
        return {
            'status': 'degraded',
            'error': str(error),
            'degradation_actions': [
                'Disabled email notifications',
                'Disabled Slack notifications', 
                'Disabled dashboard alerts',
                'Core tracking functionality maintained'
            ],
            'core_functionality_available': True,
            'degraded_features': ['notifications', 'external_integrations']
        }