
    def validate_configuration(self) -> bool:
        """Validate configuration values."""
        try:
            required_keys = ['api_base_url', 'api_version', 'timeout_seconds']
            for key in required_keys:
                if key not in self.config_data:
                    return False
            timeout = self.config_data.get('timeout_seconds', 0)
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                return False
            return True
        except Exception as e:
            logger.error(f'Configuration validation failed: {e}')
            self._errors += 1
            return False
