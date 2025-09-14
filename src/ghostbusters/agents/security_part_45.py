from datetime import datetime
from typing import Dict, List, Any

def get_capabilities(self) -> List[str]:
    """Return list of security analysis capabilities"""
    return self._capabilities.copy()
