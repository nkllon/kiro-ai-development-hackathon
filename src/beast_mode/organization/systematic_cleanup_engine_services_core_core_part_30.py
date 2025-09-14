from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> Dict[str, Any]:
    """Get health indicators for the cleanup engine"""
    return {'cleanup_plans_created': len(self.cleanup_history), 'entropy_metrics_tracked': len(self.entropy_metrics), 'last_cleanup_timestamp': self.cleanup_history[-1].plan_id if self.cleanup_history else None, 'engine_status': 'active'}
