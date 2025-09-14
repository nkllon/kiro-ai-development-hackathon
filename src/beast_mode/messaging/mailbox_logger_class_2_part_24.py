from src.rm_ddd.core.registry import register_module

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit"""
    self.stop()
