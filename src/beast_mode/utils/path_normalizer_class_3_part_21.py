from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


def is_safe_path(path: Union[str, Path], base: Union[str, Path]) -> bool:
    """
        Check if a path is safe relative to a base directory.
        
        This method validates that a path doesn't attempt to escape
        the base directory using ".." or other techniques.
        
        Args:
            path: Path to validate
            base: Base directory that should contain the path
            
        Returns:
            bool: True if path is safe, False otherwise
        """
    try:
        normalized_path = PathNormalizer.normalize_path(path)
        normalized_base = PathNormalizer.normalize_path(base)
        normalized_path.relative_to(normalized_base)
        path_str = str(normalized_path)
        if '..' in path_str or path_str.startswith('/..'):
            return False
        return True
    except (ValueError, OSError):
        return False

@staticmethod