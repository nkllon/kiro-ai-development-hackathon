
    def get_settings_summary(self) -> Dict[str, Any]:
        """Get settings summary."""
        return {'enabled': self.enabled, 'timing': self.timing.value if hasattr(self.timing, 'value') else str(self.timing), 'channels': self.channels, 'quiet_hours': self.quiet_hours}
