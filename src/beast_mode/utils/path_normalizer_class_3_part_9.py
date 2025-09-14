from src.rm_ddd.core.registry import register_module

def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """Convenience function for PathNormalizer.safe_relative_to()"""
    return PathNormalizer.safe_relative_to(path, base)

@staticmethod