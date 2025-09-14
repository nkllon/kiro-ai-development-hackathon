from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def generate_superiority_metrics(self) -> List[SuperiorityMetric]:
    """Generate comprehensive superiority metrics."""
    logger.info('Generating systematic superiority metrics')
    try:
        self.metrics.clear()
        metric_types = [MetricType.DEVELOPMENT_VELOCITY, MetricType.QUALITY_IMPROVEMENT, MetricType.TECHNICAL_DEBT_REDUCTION, MetricType.COST_EFFICIENCY, MetricType.RISK_MITIGATION, MetricType.CUSTOMER_SATISFACTION, MetricType.TIME_TO_MARKET, MetricType.MAINTENANCE_EFFICIENCY]
        for metric_type in metric_types:
            metric = self._calculate_metric(metric_type)
            if metric:
                self.metrics.append(metric)
        logger.info(f'Generated {len(self.metrics)} superiority metrics')
        return self.metrics
    except Exception as e:
        logger.error(f'Failed to generate superiority metrics: {e}')
        return []

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

