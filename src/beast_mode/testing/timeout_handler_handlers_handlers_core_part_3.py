from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for timeout handling capability"""
    if self.total_operations == 0:
        return not self._degradation_active
    hard_timeout_rate = self.hard_timeouts / max(1, self.total_operations)
    degradation_success_rate = self.successful_degradations / max(1, self.graceful_timeouts) if self.graceful_timeouts > 0 else 1.0
    return not self._degradation_active and hard_timeout_rate < 0.05 and (degradation_success_rate > 0.8)
