from src.rm_ddd.core.health import ModuleHealth

def get_health_indicators(self) -> List[HealthIndicator]:
    """Get current health indicators."""
    swarm_health = 'healthy'
    if self.active_swarms:
        error_rates = [swarm.performance_metrics.error_rate for swarm in self.active_swarms.values()]
        avg_error_rate = sum(error_rates) / len(error_rates)
        if avg_error_rate > 0.1:
            swarm_health = 'warning'
        if avg_error_rate > 0.3:
            swarm_health = 'critical'
    performance_indicator = self.create_health_indicator('swarm_performance', swarm_health, f'Managing {len(self.active_swarms)} active swarms', {'active_swarms': len(self.active_swarms), 'total_swarms_launched': self.performance_metrics['swarms_launched'], 'tasks_distributed': self.performance_metrics['tasks_distributed']})
    return self._health_indicators + [performance_indicator]
