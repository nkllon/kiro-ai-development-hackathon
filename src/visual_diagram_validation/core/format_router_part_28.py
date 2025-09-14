from datetime import datetime
from typing import Dict, List, Any

    def __init__(self, supported_formats: List[str]):
        """Initialize with supported format list."""
        self._supported_formats = [fmt.lower() for fmt in supported_formats]
    
    @property