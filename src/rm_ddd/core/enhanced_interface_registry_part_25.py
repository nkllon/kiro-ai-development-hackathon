from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


class GetinterfaceperformancereportClass:
    """Auto-generated class for functions."""

    def get_interface_performance_report(self) -> Dict[str, Any]:
    """Generate interface performance report"""
    if not self.metrics:
    return {"message": "No metrics available"}

    total_interfaces = len(self.metrics)
    total_usage = sum(metrics.usage_count for metrics in self.metrics.values())
    avg_success_rate = sum(metrics.success_rate for metrics in self.metrics.values()) / total_interfaces

    # Top performing interfaces
    top_performers = sorted(
    self.metrics.values(),
    key=lambda x: x.performance_score * x.success_rate,
    reverse=True
    )[:5]

    # Most used interfaces
    most_used = sorted(
    self.metrics.values(),
    key=lambda x: x.usage_count,
    reverse=True
    )[:5]

    return {
    'total_interfaces': total_interfaces,
    'total_usage': total_usage,
    'average_success_rate': round(avg_success_rate, 3),
    'top_performers': [
    {
    'interface_id': metrics.interface_id,
    'performance_score': metrics.performance_score,
    'success_rate': metrics.success_rate,
    'usage_count': metrics.usage_count
    }
    for metrics in top_performers
    ],
    'most_used': [
    {
    'interface_id': metrics.interface_id,
    'usage_count': metrics.usage_count,
    'last_accessed': metrics.last_accessed.isoformat()
    }
    for metrics in most_used
    ]
    }

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

