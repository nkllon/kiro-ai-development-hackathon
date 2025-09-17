from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> Dict[str, Any]:
    """Detailed health metrics for operational visibility"""
    return {'timeout_management': {'status': 'healthy' if len(self.active_timeouts) < 10 else 'degraded', 'active_operations': len(self.active_timeouts), 'timeout_strategy': self.timeout_config.strategy.value}, 'timeout_compliance': {'status': 'healthy' if self.hard_timeouts / max(1, self.total_operations) < 0.05 else 'degraded', 'primary_timeout_seconds': self.timeout_config.primary_timeout_seconds, 'hard_timeout_rate': self.hard_timeouts / max(1, self.total_operations), 'compliance_rate': 1.0 - self.hard_timeouts / max(1, self.total_operations)}, 'graceful_degradation': {'status': 'healthy' if self.successful_degradations / max(1, self.graceful_timeouts) > 0.8 else 'degraded', 'degradation_success_rate': self.successful_degradations / max(1, self.graceful_timeouts), 'graceful_timeout_rate': self.graceful_timeouts / max(1, self.total_operations), 'max_degradation_levels': self.timeout_config.max_degradation_levels}}

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

