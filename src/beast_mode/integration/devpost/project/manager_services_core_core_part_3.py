
def get_project_config(self) -> DevpostConfig:
    """Get current project configuration.
        
        Returns:
            DevpostConfig instance
            
        Raises:
            ConfigurationError: If no configuration is found
        """
    if self._current_connection:
        return self._current_connection.configuration
    config = self.config_manager.load_config()
    if config:
        return config
    raise ConfigurationError('No project configuration found')
