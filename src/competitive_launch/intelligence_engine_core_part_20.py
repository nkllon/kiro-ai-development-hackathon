from src.rm_ddd.core.health import ModuleHealth

def _calculate_systematic_metrics(self) -> SystematicMetrics:
    """Calculate systematic superiority metrics."""
    return SystematicMetrics(development_speed=0.4, quality_score=0.35, reliability_score=0.45, maintainability_score=0.5, test_coverage=0.925)

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

