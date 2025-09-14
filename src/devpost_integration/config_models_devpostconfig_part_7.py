
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {'api_base_url': 'https://devpost.com/api', 'api_version': 'v1', 'timeout_seconds': 30, 'retry_attempts': 3, 'debug_mode': False, 'auto_sync': True, 'sync_interval_minutes': 60}
