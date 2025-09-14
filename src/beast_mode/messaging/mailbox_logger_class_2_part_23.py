from src.rm_ddd.core.registry import register_module

def __enter__(self):
    """Context manager entry"""
    self.start()
    return self
