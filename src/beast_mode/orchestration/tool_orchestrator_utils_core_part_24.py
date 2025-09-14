from src.rm_ddd.core.health import ModuleHealth

def _calculate_constraint_adherence(self) -> float:
    """Calculate systematic constraint adherence rate"""
    if not self.tool_metrics:
        return 1.0
    total_adherence = sum((metrics.systematic_compliance_rate for metrics in self.tool_metrics.values()))
    return total_adherence / len(self.tool_metrics)
