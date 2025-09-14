from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def monitor_cloud_costs(self) -> Dict[str, Any]:
    """
        Monitor and optimize GKE costs with FMH accountability.
        
        Returns:
            Dict containing cost monitoring results
        """
    logger.info('Monitoring GKE cloud costs')
    try:
        cost_metrics = self._get_cost_metrics()
        efficiency_analysis = self._analyze_cost_efficiency(cost_metrics)
        recommendations = self._generate_cost_recommendations(efficiency_analysis)
        self.cost_monitoring_active = True
        result = {'active': True, 'current_costs': cost_metrics, 'efficiency_score': efficiency_analysis['score'], 'recommendations': recommendations, 'accountability_chain': self._create_accountability_chain()}
        logger.info(f"Cost monitoring active: {efficiency_analysis['score']:.2%} efficiency")
        return result
    except Exception as e:
        logger.error(f'Cost monitoring setup failed: {e}')
        return {'active': False, 'error': str(e)}

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

