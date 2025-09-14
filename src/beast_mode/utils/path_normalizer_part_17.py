from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def normalize_path(path: Union[str, Path]) -> Path:
        """
        Normalize path to consistent format.
        
        This method converts paths to absolute paths and resolves any symbolic links
        to ensure consistent path handling across the system.
        
        Args:
            path: Path to normalize (string or Path object)
            
        Returns:
            Path: Normalized absolute path
            
        Example:
            >>> PathNormalizer.normalize_path("src/main.py")
            PosixPath('/current/working/dir/src/main.py')
            
            >>> PathNormalizer.normalize_path("/absolute/path/file.py")
            PosixPath('/absolute/path/file.py')
        """
        path_obj = Path(path)
        if not path_obj.is_absolute():
            path_obj = Path.cwd() / path_obj
        return path_obj.resolve()

    @staticmethod