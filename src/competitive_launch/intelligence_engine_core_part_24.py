from src.rm_ddd.core.health import ModuleHealth

def _calculate_time_to_market_advantage(self) -> TimeToMarketAdvantage:
    """Calculate time-to-market competitive advantage."""
    return TimeToMarketAdvantage(development_velocity=0.5, deployment_speed=0.6, feature_delivery=0.4, market_response=0.7)

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

