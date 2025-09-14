
def validate_configuration(self) -> bool:
    """Validate configuration data"""
    try:
        self._update_metrics('validate_configuration')
        required_keys = ['api_base_url', 'api_version', 'timeout_seconds']
        for key in required_keys:
            if key not in self.config_data or not self.config_data[key]:
                self._logger.warning(f'Missing required config key: {key}')
                return False
        if not isinstance(self.config_data.get('timeout_seconds'), int):
            self._logger.warning('timeout_seconds must be an integer')
            return False
        if not isinstance(self.config_data.get('retry_attempts'), int):
            self._logger.warning('retry_attempts must be an integer')
            return False
        self._logger.info('Configuration validation passed')
        return True
    except Exception as e:
        self._logger.error(f'Configuration validation failed: {e}')
        self._metrics['error_count'] += 1
        return False
