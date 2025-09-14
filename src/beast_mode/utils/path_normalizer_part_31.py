from datetime import datetime
from typing import Dict, List, Any

def safe_relative_to(path: Union[str, Path], base: Union[str, Path]) -> Optional[Path]:
    """Convenience function for PathNormalizer.safe_relative_to()"""
    return PathNormalizer.safe_relative_to(path, base)

@staticmethod