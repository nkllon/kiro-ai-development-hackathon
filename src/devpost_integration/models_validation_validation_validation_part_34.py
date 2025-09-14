
def validate_settings(self) -> bool:
    """Validate global settings"""
    try:
        self._update_metrics('validate_settings')
        required_keys = ['system_name', 'version', 'log_level']
        for key in required_keys:
            if key not in self.settings_data or not self.settings_data[key]:
                self._logger.warning(f'Missing required setting: {key}')
                return False
        if not isinstance(self.settings_data.get('debug_mode'), bool):
            self._logger.warning('debug_mode must be a boolean')
            return False
        if not isinstance(self.settings_data.get('max_file_size'), int):
            self._logger.warning('max_file_size must be an integer')
            return False
        self._logger.info('Settings validation passed')
        return True
    except Exception as e:
        self._logger.error(f'Settings validation failed: {e}')
        self._metrics['error_count'] += 1
        return False
