from src.rm_ddd.core.health import ModuleHealth

def _get_avg_operation_time(self) -> float:
    """Get average operation time in milliseconds"""
    if not self._operation_times:
        return 0.0
    return sum(self._operation_times) / len(self._operation_times)
