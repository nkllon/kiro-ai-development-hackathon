
def update_configuration(self, config: Dict[str, Any]) -> bool:
    """Update module configuration."""
    try:
        self.settings_data.update(config)
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to update settings: {e}')
        self._errors += 1
        return False
