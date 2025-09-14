
def validate_notification_settings(self) -> bool:
    """Validate notification settings"""
    try:
        self._update_metrics('validate_notification_settings')
        required_keys = ['email_enabled', 'push_notifications_enabled', 'notification_frequency']
        for key in required_keys:
            if key not in self.settings_data:
                self._logger.warning(f'Missing required setting: {key}')
                return False
        if self.settings_data.get('email_enabled') and (not self.settings_data.get('email_address')):
            self._logger.warning('Email enabled but no email address provided')
            return False
        if self.settings_data.get('quiet_hours_enabled'):
            start_time = self.settings_data.get('quiet_hours_start')
            end_time = self.settings_data.get('quiet_hours_end')
            if not start_time or not end_time:
                self._logger.warning('Quiet hours enabled but times not specified')
                return False
        self._logger.info('Notification settings validation passed')
        return True
    except Exception as e:
        self._logger.error(f'Notification settings validation failed: {e}')
        self._metrics['error_count'] += 1
        return False
