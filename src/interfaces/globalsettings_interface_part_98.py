from src.rm_ddd.core.health import ModuleHealth


def import_configuration(self, config_export: Dict[str, Any]) -> bool:
    """Import configuration from backup."""
    try:
        if 'config_data' in config_export:
            self.config_data = config_export['config_data'].copy()
            self._operation_count += 1
            return True
        return False
    except Exception as e:
        logger.error(f'Failed to import configuration: {e}')
        self._errors += 1
        return False
