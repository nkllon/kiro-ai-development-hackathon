from datetime import datetime
from typing import Dict, List, Any

def normalize_path(path: Union[str, Path]) -> Path:
    """Convenience function for PathNormalizer.normalize_path()"""
    return PathNormalizer.normalize_path(path)
