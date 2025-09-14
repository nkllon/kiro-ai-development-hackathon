
def _get_overall_component_health(self) -> float:
    """Calculate overall component health score"""
    if not self.component_health:
        return 1.0
    healthy_count = sum((1 for metrics in self.component_health.values() if metrics.is_healthy))
    return healthy_count / len(self.component_health)
