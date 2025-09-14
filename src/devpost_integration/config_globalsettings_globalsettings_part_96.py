from src.rm_ddd.core.health import ModuleHealth

def reset_to_defaults(self) -> bool:
    """Reset configuration to defaults."""
    try:
        self.config_data = self._get_default_config()
        self._operation_count += 1
        return True
    except Exception as e:
        logger.error(f'Failed to reset to defaults: {e}')
        self._errors += 1
        return False
