from src.rm_ddd.core.health import ModuleHealth

def is_healthy(self) -> bool:
    """Health assessment for test failure detection capability"""
    return not self._degradation_active
