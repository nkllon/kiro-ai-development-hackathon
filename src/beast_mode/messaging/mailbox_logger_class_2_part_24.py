from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class ExitClass:
    """Auto-generated class for functions."""

    def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit"""
    self.stop()
