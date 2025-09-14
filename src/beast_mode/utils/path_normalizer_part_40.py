from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """
        Safely attempt to make path relative to base, returning None if not possible.
        
        This is a non-throwing version of ensure_relative_to that returns None
        instead of raising an exception when the path cannot be made relative.
        
        Args:
            path: Path to make relative
            base: Base directory path
            
        Returns:
            Path or None: Path relative to base directory, or None if not possible
            
        Example:
            >>> PathNormalizer.safe_relative_to("src/main.py", "/project/root")
            PosixPath('src/main.py')
            
            >>> PathNormalizer.safe_relative_to("/other/project/file.py", "/project/root")
            None
        """
    try:
        return PathNormalizer.ensure_relative_to(path, base)
    except ValueError:
        return None

@staticmethod