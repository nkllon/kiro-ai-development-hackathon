class NotificationMessage(ReflectiveModule):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
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
    """
    Manages notification messages and delivery.
    
    This class handles individual notification messages
    including content, recipients, and delivery status.
    """

    def __init__(self, message_data: Dict[str, Any]=None):
        """Initialize notification message."""
        super().__init__()
        self.module_id = 'notification_message'
        self.version = '1.0.0'
        self.message_data = message_data or {}
        self.message_id = self.message_data.get('id', '')
        self.title = self.message_data.get('title', '')
        self.content = self.message_data.get('content', '')
        self.recipients = self.message_data.get('recipients', [])
        self.priority = self.message_data.get('priority', 'normal')
        self.status = self.message_data.get('status', 'pending')
        self.created_at = datetime.now()
        self.sent_at = None
        self._operation_count = 0
        self._errors = 0
        register_module(self)

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'message_id': self.message_id, 'title': self.title, 'status': self.status, 'recipient_count': len(self.recipients)}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.MESSAGE_MANAGEMENT, ModuleCapability.DELIVERY_TRACKING, ModuleCapability.RECIPIENT_MANAGEMENT]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['reflective_module', 'datetime', 'typing']

    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} internal errors occurred')
        if not self.message_id:
            issues.append('No message ID specified')
        if not self.title:
            issues.append('No message title specified')
        if not self.content:
            issues.append('No message content specified')
        if not self.recipients:
            issues.append('No recipients specified')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if not self.message_id:
            score -= 0.3
        if not self.title:
            score -= 0.2
        if not self.content:
            score -= 0.2
        if not self.recipients:
            score -= 0.2
        return max(0.0, score)

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.message_id:
            issues.append('Missing message ID')
        if not self.title:
            issues.append('Missing message title')
        if not self.content:
            issues.append('Missing message content')
        if not self.recipients:
            issues.append('Missing recipients')
        return issues

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'max_title_length': 200, 'max_content_length': 5000, 'max_recipients': 100, 'valid_priorities': ['low', 'normal', 'high', 'urgent'], 'valid_statuses': ['pending', 'sent', 'failed', 'cancelled']}

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'message_id': self.message_id, 'status': self.status, 'recipient_count': len(self.recipients), 'priority': self.priority, 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0

    def mark_as_sent(self) -> bool:
        """Mark message as sent."""
        try:
            self.status = 'sent'
            self.sent_at = datetime.now()
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to mark as sent: {e}')
            self._errors += 1
            return False

    def mark_as_failed(self) -> bool:
        """Mark message as failed."""
        try:
            self.status = 'failed'
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to mark as failed: {e}')
            self._errors += 1
            return False

    def add_recipient(self, recipient: str) -> bool:
        """Add recipient to message."""
        try:
            if recipient not in self.recipients:
                self.recipients.append(recipient)
                self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to add recipient: {e}')
            self._errors += 1
            return False

    def remove_recipient(self, recipient: str) -> bool:
        """Remove recipient from message."""
        try:
            if recipient in self.recipients:
                self.recipients.remove(recipient)
                self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to remove recipient: {e}')
            self._errors += 1
            return False

    def get_message_summary(self) -> Dict[str, Any]:
        """Get message summary."""
        return {'message_id': self.message_id, 'title': self.title, 'content': self.content[:100] + '...' if len(self.content) > 100 else self.content, 'status': self.status, 'priority': self.priority, 'recipient_count': len(self.recipients), 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'Notification message: {operation}')

def __init__(self, settings_data: Dict[str, Any]=None):
    """Initialize notification settings."""
    super().__init__()
    self.module_id = 'notification_settings'
    self.version = '1.0.0'
    self.settings_data = settings_data or self._get_default_settings()
    self.enabled = self.settings_data.get('enabled', True)
    self.timing = self.settings_data.get('timing', NotificationTiming.DAILY)
    self.channels = self.settings_data.get('channels', ['email'])
    self.quiet_hours = self.settings_data.get('quiet_hours', {'start': '22:00', 'end': '08:00'})
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def _get_default_settings(self) -> Dict[str, Any]:
    """Get default notification settings."""
    return {'enabled': True, 'timing': NotificationTiming.DAILY, 'channels': ['email'], 'quiet_hours': {'start': '22:00', 'end': '08:00'}, 'max_notifications_per_day': 10, 'digest_mode': True}

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channel_count': len(self.channels)}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.SETTINGS_MANAGEMENT, ModuleCapability.TIMING_CONTROL, ModuleCapability.CHANNEL_MANAGEMENT, ModuleCapability.PREFERENCE_CONTROL]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing', 'enum_models']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.channels:
        score -= 0.3
    if self.enabled and (not self.channels):
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.channels:
        issues.append('No notification channels')
    if self.enabled and (not self.channels):
        issues.append('Enabled but no channels')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return self.settings_data.copy()

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        self.settings_data.update(config)
        if 'enabled' in config:
            self.enabled = config['enabled']
        if 'timing' in config:
            self.timing = config['timing']
        if 'channels' in config:
            self.channels = config['channels']
        if 'quiet_hours' in config:
            self.quiet_hours = config['quiet_hours']
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        self._errors += 1
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'enabled': self.enabled, 'channel_count': len(self.channels), 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing)}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def enable_notifications(self) -> bool:
    """Enable notifications."""
    try:
        self.enabled = True
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to enable notifications: {e}')
        self._errors += 1
        return False

def disable_notifications(self) -> bool:
    """Disable notifications."""
    try:
        self.enabled = False
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to disable notifications: {e}')
        self._errors += 1
        return False

def add_channel(self, channel: str) -> bool:
    """Add notification channel."""
    try:
        if channel not in self.channels:
            self.channels.append(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add channel: {e}')
        self._errors += 1
        return False

def remove_channel(self, channel: str) -> bool:
    """Remove notification channel."""
    try:
        if channel in self.channels:
            self.channels.remove(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove channel: {e}')
        self._errors += 1
        return False

def set_timing(self, timing: NotificationTiming) -> bool:
    """Set notification timing."""
    try:
        self.timing = timing
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set timing: {e}')
        self._errors += 1
        return False

def get_settings_summary(self) -> Dict[str, Any]:
    """Get settings summary."""
    return {'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channels': self.channels, 'quiet_hours': self.quiet_hours}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Notification settings: {operation}')

def __init__(self, message_data: Dict[str, Any]=None):
    """Initialize notification message."""
    super().__init__()
    self.module_id = 'notification_message'
    self.version = '1.0.0'
    self.message_data = message_data or {}
    self.message_id = self.message_data.get('id', '')
    self.title = self.message_data.get('title', '')
    self.content = self.message_data.get('content', '')
    self.recipients = self.message_data.get('recipients', [])
    self.priority = self.message_data.get('priority', 'normal')
    self.status = self.message_data.get('status', 'pending')
    self.created_at = datetime.now()
    self.sent_at = None
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'message_id': self.message_id, 'title': self.title, 'status': self.status, 'recipient_count': len(self.recipients)}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.MESSAGE_MANAGEMENT, ModuleCapability.DELIVERY_TRACKING, ModuleCapability.RECIPIENT_MANAGEMENT]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.message_id:
        score -= 0.3
    if not self.title:
        score -= 0.2
    if not self.content:
        score -= 0.2
    if not self.recipients:
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.message_id:
        issues.append('Missing message ID')
    if not self.title:
        issues.append('Missing message title')
    if not self.content:
        issues.append('Missing message content')
    if not self.recipients:
        issues.append('Missing recipients')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_title_length': 200, 'max_content_length': 5000, 'max_recipients': 100, 'valid_priorities': ['low', 'normal', 'high', 'urgent'], 'valid_statuses': ['pending', 'sent', 'failed', 'cancelled']}

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'message_id': self.message_id, 'status': self.status, 'recipient_count': len(self.recipients), 'priority': self.priority, 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def mark_as_sent(self) -> bool:
    """Mark message as sent."""
    try:
        self.status = 'sent'
        self.sent_at = datetime.now()
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as sent: {e}')
        self._errors += 1
        return False

def mark_as_failed(self) -> bool:
    """Mark message as failed."""
    try:
        self.status = 'failed'
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as failed: {e}')
        self._errors += 1
        return False

def add_recipient(self, recipient: str) -> bool:
    """Add recipient to message."""
    try:
        if recipient not in self.recipients:
            self.recipients.append(recipient)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add recipient: {e}')
        self._errors += 1
        return False

def remove_recipient(self, recipient: str) -> bool:
    """Remove recipient from message."""
    try:
        if recipient in self.recipients:
            self.recipients.remove(recipient)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove recipient: {e}')
        self._errors += 1
        return False

def get_message_summary(self) -> Dict[str, Any]:
    """Get message summary."""
    return {'message_id': self.message_id, 'title': self.title, 'content': self.content[:100] + '...' if len(self.content) > 100 else self.content, 'status': self.status, 'priority': self.priority, 'recipient_count': len(self.recipients), 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Notification message: {operation}')

def __init__(self, settings_data: Dict[str, Any]=None):
    """Initialize notification settings."""
    super().__init__()
    self.module_id = 'notification_settings'
    self.version = '1.0.0'
    self.settings_data = settings_data or self._get_default_settings()
    self.enabled = self.settings_data.get('enabled', True)
    self.timing = self.settings_data.get('timing', NotificationTiming.DAILY)
    self.channels = self.settings_data.get('channels', ['email'])
    self.quiet_hours = self.settings_data.get('quiet_hours', {'start': '22:00', 'end': '08:00'})
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def _get_default_settings(self) -> Dict[str, Any]:
    """Get default notification settings."""
    return {'enabled': True, 'timing': NotificationTiming.DAILY, 'channels': ['email'], 'quiet_hours': {'start': '22:00', 'end': '08:00'}, 'max_notifications_per_day': 10, 'digest_mode': True}

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channel_count': len(self.channels)}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.SETTINGS_MANAGEMENT, ModuleCapability.TIMING_CONTROL, ModuleCapability.CHANNEL_MANAGEMENT, ModuleCapability.PREFERENCE_CONTROL]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing', 'enum_models']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.channels:
        score -= 0.3
    if self.enabled and (not self.channels):
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.channels:
        issues.append('No notification channels')
    if self.enabled and (not self.channels):
        issues.append('Enabled but no channels')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return self.settings_data.copy()

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        self.settings_data.update(config)
        if 'enabled' in config:
            self.enabled = config['enabled']
        if 'timing' in config:
            self.timing = config['timing']
        if 'channels' in config:
            self.channels = config['channels']
        if 'quiet_hours' in config:
            self.quiet_hours = config['quiet_hours']
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        self._errors += 1
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'enabled': self.enabled, 'channel_count': len(self.channels), 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing)}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def enable_notifications(self) -> bool:
    """Enable notifications."""
    try:
        self.enabled = True
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to enable notifications: {e}')
        self._errors += 1
        return False

def disable_notifications(self) -> bool:
    """Disable notifications."""
    try:
        self.enabled = False
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to disable notifications: {e}')
        self._errors += 1
        return False

def add_channel(self, channel: str) -> bool:
    """Add notification channel."""
    try:
        if channel not in self.channels:
            self.channels.append(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add channel: {e}')
        self._errors += 1
        return False

def remove_channel(self, channel: str) -> bool:
    """Remove notification channel."""
    try:
        if channel in self.channels:
            self.channels.remove(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove channel: {e}')
        self._errors += 1
        return False

def set_timing(self, timing: NotificationTiming) -> bool:
    """Set notification timing."""
    try:
        self.timing = timing
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set timing: {e}')
        self._errors += 1
        return False

def get_settings_summary(self) -> Dict[str, Any]:
    """Get settings summary."""
    return {'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channels': self.channels, 'quiet_hours': self.quiet_hours}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Notification settings: {operation}')

def __init__(self, message_data: Dict[str, Any]=None):
    """Initialize notification message."""
    super().__init__()
    self.module_id = 'notification_message'
    self.version = '1.0.0'
    self.message_data = message_data or {}
    self.message_id = self.message_data.get('id', '')
    self.title = self.message_data.get('title', '')
    self.content = self.message_data.get('content', '')
    self.recipients = self.message_data.get('recipients', [])
    self.priority = self.message_data.get('priority', 'normal')
    self.status = self.message_data.get('status', 'pending')
    self.created_at = datetime.now()
    self.sent_at = None
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'message_id': self.message_id, 'title': self.title, 'status': self.status, 'recipient_count': len(self.recipients)}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.MESSAGE_MANAGEMENT, ModuleCapability.DELIVERY_TRACKING, ModuleCapability.RECIPIENT_MANAGEMENT]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.message_id:
        score -= 0.3
    if not self.title:
        score -= 0.2
    if not self.content:
        score -= 0.2
    if not self.recipients:
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.message_id:
        issues.append('Missing message ID')
    if not self.title:
        issues.append('Missing message title')
    if not self.content:
        issues.append('Missing message content')
    if not self.recipients:
        issues.append('Missing recipients')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_title_length': 200, 'max_content_length': 5000, 'max_recipients': 100, 'valid_priorities': ['low', 'normal', 'high', 'urgent'], 'valid_statuses': ['pending', 'sent', 'failed', 'cancelled']}

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'message_id': self.message_id, 'status': self.status, 'recipient_count': len(self.recipients), 'priority': self.priority, 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def mark_as_sent(self) -> bool:
    """Mark message as sent."""
    try:
        self.status = 'sent'
        self.sent_at = datetime.now()
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as sent: {e}')
        self._errors += 1
        return False

def mark_as_failed(self) -> bool:
    """Mark message as failed."""
    try:
        self.status = 'failed'
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as failed: {e}')
        self._errors += 1
        return False

def add_recipient(self, recipient: str) -> bool:
    """Add recipient to message."""
    try:
        if recipient not in self.recipients:
            self.recipients.append(recipient)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add recipient: {e}')
        self._errors += 1
        return False

def remove_recipient(self, recipient: str) -> bool:
    """Remove recipient from message."""
    try:
        if recipient in self.recipients:
            self.recipients.remove(recipient)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove recipient: {e}')
        self._errors += 1
        return False

def get_message_summary(self) -> Dict[str, Any]:
    """Get message summary."""
    return {'message_id': self.message_id, 'title': self.title, 'content': self.content[:100] + '...' if len(self.content) > 100 else self.content, 'status': self.status, 'priority': self.priority, 'recipient_count': len(self.recipients), 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Notification message: {operation}')

def __init__(self, settings_data: Dict[str, Any]=None):
    """Initialize notification settings."""
    super().__init__()
    self.module_id = 'notification_settings'
    self.version = '1.0.0'
    self.settings_data = settings_data or self._get_default_settings()
    self.enabled = self.settings_data.get('enabled', True)
    self.timing = self.settings_data.get('timing', NotificationTiming.DAILY)
    self.channels = self.settings_data.get('channels', ['email'])
    self.quiet_hours = self.settings_data.get('quiet_hours', {'start': '22:00', 'end': '08:00'})
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def _get_default_settings(self) -> Dict[str, Any]:
    """Get default notification settings."""
    return {'enabled': True, 'timing': NotificationTiming.DAILY, 'channels': ['email'], 'quiet_hours': {'start': '22:00', 'end': '08:00'}, 'max_notifications_per_day': 10, 'digest_mode': True}

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channel_count': len(self.channels)}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.SETTINGS_MANAGEMENT, ModuleCapability.TIMING_CONTROL, ModuleCapability.CHANNEL_MANAGEMENT, ModuleCapability.PREFERENCE_CONTROL]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing', 'enum_models']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.channels:
        score -= 0.3
    if self.enabled and (not self.channels):
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.channels:
        issues.append('No notification channels')
    if self.enabled and (not self.channels):
        issues.append('Enabled but no channels')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return self.settings_data.copy()

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        self.settings_data.update(config)
        if 'enabled' in config:
            self.enabled = config['enabled']
        if 'timing' in config:
            self.timing = config['timing']
        if 'channels' in config:
            self.channels = config['channels']
        if 'quiet_hours' in config:
            self.quiet_hours = config['quiet_hours']
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        self._errors += 1
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'enabled': self.enabled, 'channel_count': len(self.channels), 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing)}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def enable_notifications(self) -> bool:
    """Enable notifications."""
    try:
        self.enabled = True
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to enable notifications: {e}')
        self._errors += 1
        return False

def disable_notifications(self) -> bool:
    """Disable notifications."""
    try:
        self.enabled = False
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to disable notifications: {e}')
        self._errors += 1
        return False

def add_channel(self, channel: str) -> bool:
    """Add notification channel."""
    try:
        if channel not in self.channels:
            self.channels.append(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add channel: {e}')
        self._errors += 1
        return False

def remove_channel(self, channel: str) -> bool:
    """Remove notification channel."""
    try:
        if channel in self.channels:
            self.channels.remove(channel)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove channel: {e}')
        self._errors += 1
        return False

def set_timing(self, timing: NotificationTiming) -> bool:
    """Set notification timing."""
    try:
        self.timing = timing
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set timing: {e}')
        self._errors += 1
        return False

def get_settings_summary(self) -> Dict[str, Any]:
    """Get settings summary."""
    return {'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channels': self.channels, 'quiet_hours': self.quiet_hours}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Notification settings: {operation}')

def __init__(self, message_data: Dict[str, Any]=None):
    """Initialize notification message."""
    super().__init__()
    self.module_id = 'notification_message'
    self.version = '1.0.0'
    self.message_data = message_data or {}
    self.message_id = self.message_data.get('id', '')
    self.title = self.message_data.get('title', '')
    self.content = self.message_data.get('content', '')
    self.recipients = self.message_data.get('recipients', [])
    self.priority = self.message_data.get('priority', 'normal')
    self.status = self.message_data.get('status', 'pending')
    self.created_at = datetime.now()
    self.sent_at = None
    self._operation_count = 0
    self._errors = 0
    register_module(self)

def get_module_info(self) -> Dict[str, Any]:
    """Get module information."""
    return {'module_id': self.module_id, 'version': self.version, 'message_id': self.message_id, 'title': self.title, 'status': self.status, 'recipient_count': len(self.recipients)}

def get_capabilities(self) -> List[ModuleCapability]:
    """Get module capabilities."""
    return [ModuleCapability.MESSAGE_MANAGEMENT, ModuleCapability.DELIVERY_TRACKING, ModuleCapability.RECIPIENT_MANAGEMENT]

def get_dependencies(self) -> List[str]:
    """Get module dependencies."""
    return ['reflective_module', 'datetime', 'typing']

def _calculate_health_score(self) -> float:
    """Calculate health score."""
    score = 1.0
    if self._errors > 0:
        score -= min(0.5, self._errors * 0.1)
    if not self.message_id:
        score -= 0.3
    if not self.title:
        score -= 0.2
    if not self.content:
        score -= 0.2
    if not self.recipients:
        score -= 0.2
    return max(0.0, score)

def _identify_health_issues(self) -> List[str]:
    """Identify health issues."""
    issues = []
    if self._errors > 0:
        issues.append(f'Internal errors: {self._errors}')
    if not self.message_id:
        issues.append('Missing message ID')
    if not self.title:
        issues.append('Missing message title')
    if not self.content:
        issues.append('Missing message content')
    if not self.recipients:
        issues.append('Missing recipients')
    return issues

def get_configuration(self) -> Dict[str, Any]:
    """Get module configuration."""
    return {'max_title_length': 200, 'max_content_length': 5000, 'max_recipients': 100, 'valid_priorities': ['low', 'normal', 'high', 'urgent'], 'valid_statuses': ['pending', 'sent', 'failed', 'cancelled']}

def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        return True
    except Exception as e:
        logger.error(f'Failed to update configuration: {e}')
        return False

def get_metrics(self) -> Dict[str, Any]:
    """Get module metrics."""
    return {'operation_count': self._operation_count, 'error_count': self._errors, 'message_id': self.message_id, 'status': self.status, 'recipient_count': len(self.recipients), 'priority': self.priority, 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

def reset_metrics(self) -> None:
    """Reset module metrics."""
    self._operation_count = 0
    self._errors = 0

def mark_as_sent(self) -> bool:
    """Mark message as sent."""
    try:
        self.status = 'sent'
        self.sent_at = datetime.now()
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as sent: {e}')
        self._errors += 1
        return False

def mark_as_failed(self) -> bool:
    """Mark message as failed."""
    try:
        self.status = 'failed'
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to mark as failed: {e}')
        self._errors += 1
        return False

def add_recipient(self, recipient: str) -> bool:
    """Add recipient to message."""
    try:
        if recipient not in self.recipients:
            self.recipients.append(recipient)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to add recipient: {e}')
        self._errors += 1
        return False

def remove_recipient(self, recipient: str) -> bool:
    """Remove recipient from message."""
    try:
        if recipient in self.recipients:
            self.recipients.remove(recipient)
            self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to remove recipient: {e}')
        self._errors += 1
        return False

def get_message_summary(self) -> Dict[str, Any]:
    """Get message summary."""
    return {'message_id': self.message_id, 'title': self.title, 'content': self.content[:100] + '...' if len(self.content) > 100 else self.content, 'status': self.status, 'priority': self.priority, 'recipient_count': len(self.recipients), 'created_at': self.created_at.isoformat(), 'sent_at': self.sent_at.isoformat() if self.sent_at else None}

def _update_metrics(self, operation: str) -> None:
    """Update internal metrics."""
    self._operation_count += 1
    logger.debug(f'Notification message: {operation}')









