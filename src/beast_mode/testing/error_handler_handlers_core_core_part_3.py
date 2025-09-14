from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for error handling capability"""
    return not self._degradation_active and self.degradation_level.value <= DegradationLevel.MINIMAL.value and (self._get_overall_component_health() > 0.7)
