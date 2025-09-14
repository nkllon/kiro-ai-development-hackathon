from src.rm_ddd.core.health import ModuleHealth

    def get_setting(self, key: str, default: Any=None) -> Any:
        """Get setting value by key."""
        try:
            return self.settings_data.get(key, default)
        except Exception as e:
            logger.error(f'Failed to get setting: {e}')
            self._errors += 1
            return default
