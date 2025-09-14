from datetime import datetime
from typing import Dict, List, Any

    def get_supported_formats(self) -> List[str]:
        """Get list of all supported formats."""
        return list(self.processors.keys())
    