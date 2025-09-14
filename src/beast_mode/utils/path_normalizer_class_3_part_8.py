from src.rm_ddd.core.registry import register_module

def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """Convenience function for PathNormalizer.ensure_relative_to()"""
    return PathNormalizer.ensure_relative_to(path, base)
