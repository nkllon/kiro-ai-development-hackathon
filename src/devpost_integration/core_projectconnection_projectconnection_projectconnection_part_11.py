
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'connection_timeout': 30, 'retry_attempts': 3, 'auto_reconnect': True}
