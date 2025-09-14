from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def ensure_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Path:
    """
        Ensure path is relative to base directory, handling absolute/relative conflicts.
        
        This method safely converts a path to be relative to a base directory,
        handling cases where the paths might be a mix of absolute and relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path: Path relative to base directory
            
        Raises:
            ValueError: If path cannot be made relative to base
            
        Example:
            >>> PathNormalizer.ensure_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.ensure_relative_to("/project/root/src/main.py", "/project/root")
            PosixPath('src/main.py')
        """
    normalized_path = PathNormalizer.normalize_path(path)
    normalized_base = PathNormalizer.normalize_path(base)
    try:
        return normalized_path.relative_to(normalized_base)
    except ValueError as e:
        path_obj = Path(path)
        if not path_obj.is_absolute():
            return path_obj
        else:
            raise ValueError(f"Path '{path}' cannot be made relative to '{base}'. Normalized path '{normalized_path}' is not under normalized base '{normalized_base}'") from e

@staticmethod