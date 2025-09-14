from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def get_common_base(paths: List[Union[str, Path]]) -> Optional[Path]:
    """
        Find the common base directory for a list of paths.
        
        This method finds the deepest common directory that contains all the given paths.
        
        Args:
            paths: List of paths to find common base for
            
        Returns:
            Path or None: Common base directory, or None if no common base exists
            
        Example:
            >>> paths = ["/project/src/main.py", "/project/tests/test.py", "/project/docs/readme.md"]
            >>> PathNormalizer.get_common_base(paths)
            PosixPath('/project')
        """
    if not paths:
        return None
    try:
        normalized_paths = [PathNormalizer.normalize_path(p) for p in paths]
        common_parts = list(normalized_paths[0].parts)
        for path in normalized_paths[1:]:
            path_parts = list(path.parts)
            new_common = []
            for i, (common_part, path_part) in enumerate(zip(common_parts, path_parts)):
                if common_part == path_part:
                    new_common.append(common_part)
                else:
                    break
            common_parts = new_common
            if not common_parts:
                return None
        if common_parts:
            return Path(*common_parts)
        else:
            return None
    except (ValueError, OSError):
        return None

@staticmethod