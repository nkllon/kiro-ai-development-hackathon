from src.rm_ddd.core.health import ModuleHealth

def set_setting(self, key: str, value: Any) -> bool:
    """Set setting value by key."""
    try:
        self.settings_data[key] = value
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to set setting: {e}')
        self._errors += 1
        return False
