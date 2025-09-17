from src.rm_ddd.core.health import ModuleHealth

def get_service_usage_patterns(self) -> Dict[str, Any]:
    """
        Get service usage patterns and effectiveness metrics
        Documents service usage patterns and effectiveness for optimization
        """
    return {'service_usage_distribution': self.service_metrics['service_usage_patterns'], 'peak_usage_times': self._analyze_peak_usage_times(), 'team_expertise_correlation': self._analyze_expertise_service_correlation(), 'service_effectiveness': {'pdca_cycle': self._calculate_service_effectiveness(ServiceType.PDCA_CYCLE), 'model_driven_building': self._calculate_service_effectiveness(ServiceType.MODEL_DRIVEN_BUILDING), 'tool_health_management': self._calculate_service_effectiveness(ServiceType.TOOL_HEALTH_MANAGEMENT), 'quality_assurance': self._calculate_service_effectiveness(ServiceType.QUALITY_ASSURANCE)}, 'optimization_recommendations': self._generate_service_optimization_recommendations(), 'analysis_timestamp': datetime.now().isoformat()}

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

