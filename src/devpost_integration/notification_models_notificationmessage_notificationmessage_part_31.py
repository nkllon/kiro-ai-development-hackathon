
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
