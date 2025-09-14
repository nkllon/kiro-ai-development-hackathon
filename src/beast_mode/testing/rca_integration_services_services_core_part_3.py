from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for test RCA integration capability"""
    return not self._degradation_active and self.rca_engine is not None and self.rca_engine.is_healthy() and self.performance_monitor.is_healthy() and self.timeout_handler.is_healthy()
