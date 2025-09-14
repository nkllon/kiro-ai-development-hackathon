from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for RCA capability"""
    return not self._degradation_active and len(self.pattern_library) > 0
