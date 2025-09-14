from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def validate_path_length(path: Union[str, Path], max_length: int=260) -> bool:
        """
        Validate that a path doesn't exceed maximum length.
        
        Args:
            path: Path to validate
            max_length: Maximum allowed path length (default 260 for Windows compatibility)
            
        Returns:
            bool: True if path length is acceptable, False otherwise
        """
        return len(str(path)) <= max_length
