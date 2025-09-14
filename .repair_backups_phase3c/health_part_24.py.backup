from src.rm_ddd.core.health import ModuleHealth

    def _calculate_health_trend(self) -> str:
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Calculate health trend based on recent history."""
        if len(self._health_history) < 3:
            return 'stable'
        recent_statuses = [h.status for h in self._health_history[-5:]]
        healthy_count = sum((1 for status in recent_statuses if status == ModuleStatus.AVAILABLE))
        degraded_count = sum((1 for status in recent_statuses if status == ModuleStatus.DEGRADED))
        if healthy_count > degraded_count * 2:
            return 'improving'
        elif degraded_count > healthy_count:
            return 'degrading'
        else:
            return 'stable'

    async def collect_health_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive health metrics.
        
        Returns:
            Dictionary containing all health metrics and indicators
        """
        current_health = await self.get_current_health()
        health_indicators = await self.get_health_indicators()
        return {'module_id': self.module_id, 'uptime': self._calculate_uptime(), 'current_health': current_health.to_dict() if current_health else None, 'health_indicators': {name: {'status': indicator.status, 'value': indicator.value, 'threshold': indicator.threshold, 'message': indicator.message, 'timestamp': indicator.timestamp.isoformat()} for name, indicator in health_indicators.items()}, 'health_history_count': len(self._health_history), 'monitoring_active': self._monitoring_active, 'check_interval_seconds': self._check_interval.total_seconds()}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

