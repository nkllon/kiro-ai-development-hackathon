from src.rm_ddd.core.health import ModuleHealth

def _calculate_success_rate(self) -> float:
    """
        Calculate orchestration success rate
        """
    total = self.orchestration_metrics['total_orchestrations']
    if total == 0:
        return 0.0
    successful = self.orchestration_metrics['successful_orchestrations']
    return successful / total
