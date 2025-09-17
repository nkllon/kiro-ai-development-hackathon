from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def __enter__(self):
    """Context manager entry"""
    self.start()
    return self
