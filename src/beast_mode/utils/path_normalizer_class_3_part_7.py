from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class NormalizepathClass:
    """Auto-generated class for functions."""

    def normalize_path(path: Union[str, Path]) -> Path:
    """Convenience function for PathNormalizer.normalize_path()"""
    return PathNormalizer.normalize_path(path)
