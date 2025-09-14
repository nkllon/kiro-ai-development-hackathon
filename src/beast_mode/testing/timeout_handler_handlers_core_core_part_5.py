from src.rm_ddd.core.health import ModuleHealth

def _get_primary_responsibility(self) -> str:
    """Single responsibility: RCA timeout handling and graceful degradation"""
    return 'rca_timeout_handling_and_graceful_degradation'

@contextmanager