from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def enable_real_time_analytics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
        Enable real-time competitive analytics using TiDB.
        
        Args:
            metrics: Analytics metrics configuration
            
        Returns:
            Dict containing analytics engine results
        """
    logger.info('Enabling real-time analytics on TiDB')
    try:
        tiflash_config = self._configure_tiflash(metrics)
        pipeline_config = self._setup_data_pipeline(metrics)
        queries_config = self._configure_analytics_queries(metrics)
        self.analytics_active = True
        result = {'active': True, 'tiflash_configured': tiflash_config['success'], 'pipeline_active': pipeline_config['active'], 'queries_configured': len(queries_config['queries']), 'latency_ms': pipeline_config['latency_ms']}
        logger.info(f"Real-time analytics enabled: {pipeline_config['latency_ms']}ms latency")
        return result
    except Exception as e:
        logger.error(f'Real-time analytics setup failed: {e}')
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

