
def set_config_value(self, key: str, value: Any) -> bool:
    """Set configuration value by key."""
    try:
        self.config_data[key] = value
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set config value: {e}')
        self._errors += 1
        return False
