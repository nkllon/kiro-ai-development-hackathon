from src.rm_ddd.core.registry import register_module

def get_capabilities(self) -> List[str]:
    """Return list of security analysis capabilities"""
    return self._capabilities.copy()
