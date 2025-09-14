
    def get_metrics(self) -> Dict[str, Any]:
        """Get operational metrics for RM pattern"""
        return {'integration_mode': self.integration_mode, 'openflow_assets_available': OPENFLOW_ASSETS_AVAILABLE, 'cache_valid': self._is_cache_valid(), 'last_update': self.last_update.isoformat() if self.last_update else None, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60}
