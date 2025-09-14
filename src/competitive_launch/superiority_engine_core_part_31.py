from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _calculate_metric(self, metric_type: MetricType) -> Optional[SuperiorityMetric]:
    """Calculate specific superiority metric."""
    try:
        if metric_type == MetricType.DEVELOPMENT_VELOCITY:
            return self._calculate_development_velocity_metric()
        elif metric_type == MetricType.QUALITY_IMPROVEMENT:
            return self._calculate_quality_improvement_metric()
        elif metric_type == MetricType.TECHNICAL_DEBT_REDUCTION:
            return self._calculate_technical_debt_reduction_metric()
        elif metric_type == MetricType.COST_EFFICIENCY:
            return self._calculate_cost_efficiency_metric()
        elif metric_type == MetricType.RISK_MITIGATION:
            return self._calculate_risk_mitigation_metric()
        elif metric_type == MetricType.CUSTOMER_SATISFACTION:
            return self._calculate_customer_satisfaction_metric()
        elif metric_type == MetricType.TIME_TO_MARKET:
            return self._calculate_time_to_market_metric()
        elif metric_type == MetricType.MAINTENANCE_EFFICIENCY:
            return self._calculate_maintenance_efficiency_metric()
        else:
            return None
    except Exception as e:
        logger.error(f'Failed to calculate metric {metric_type}: {e}')
        return None

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

