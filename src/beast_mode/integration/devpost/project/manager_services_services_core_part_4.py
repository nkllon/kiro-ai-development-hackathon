
def update_config(self, updates: Dict[str, Any]) -> bool:
    """Update project configuration.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            True if update was successful
            
        Raises:
            ConfigurationError: If update fails
        """
    try:
        current_config = self.get_project_config()
        config_dict = current_config.model_dump()
        config_dict.update(updates)
        updated_config = DevpostConfig(**config_dict)
        if self._current_connection:
            self._current_connection.configuration = updated_config
            self.config_manager.save_connection(self._current_connection)
        else:
            self.config_manager.save_config(updated_config)
        return True
    except Exception as e:
        raise ConfigurationError(f'Failed to update configuration: {e}')
