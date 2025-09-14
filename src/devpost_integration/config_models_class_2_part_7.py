from src.rm_ddd.core.health import ModuleHealth

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default global settings."""
        return {'log_level': 'INFO', 'max_file_size_mb': 100, 'auto_backup': True, 'backup_retention_days': 30, 'ui_theme': 'default', 'language': 'en'}
