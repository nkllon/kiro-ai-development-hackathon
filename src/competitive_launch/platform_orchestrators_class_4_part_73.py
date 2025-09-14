from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def _analyze_scaling_demand(self, demand: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze current demand to determine scaling needs."""
    return {'scale_up': demand.get('cpu_usage', 0) > 0.8, 'scale_down': demand.get('cpu_usage', 0) < 0.3, 'target_replicas': max(1, int(demand.get('current_replicas', 1) * 1.5))}
