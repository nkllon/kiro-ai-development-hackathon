
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration for RM pattern"""
        return {'integration_mode': self.integration_mode, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60, 'config_keys': list(self.config.keys())}
