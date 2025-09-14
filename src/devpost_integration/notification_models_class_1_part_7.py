from src.rm_ddd.core.health import ModuleHealth

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default notification settings."""
        return {'enabled': True, 'timing': NotificationTiming.DAILY, 'channels': ['email'], 'quiet_hours': {'start': '22:00', 'end': '08:00'}, 'max_notifications_per_day': 10, 'digest_mode': True}
