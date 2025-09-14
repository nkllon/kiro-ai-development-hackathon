from src.rm_ddd.core.health import ModuleHealth

def _record_operation_time(self, operation_time: float):
    """Record operation time for performance monitoring"""
    self._operation_times.append(operation_time * 1000)
    if len(self._operation_times) > self._max_operation_history:
        self._operation_times = self._operation_times[-self._max_operation_history:]
