from src.rm_ddd.core.health import ModuleHealth

def get_config_value(self, key: str, default: Any=None) -> Any:
    """Get configuration value by key."""
    try:
        return self.config_data.get(key, default)
    except Exception as e:
        logger.error(f'Failed to get config value: {e}')
        self._errors += 1
        return default
