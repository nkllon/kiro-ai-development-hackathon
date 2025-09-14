from datetime import datetime
from typing import Dict, List, Any

    def extract_metadata(self, input_data: bytes) -> Dict[str, any]:
        """Default metadata extraction - subclasses should override."""
        return {
            'processor': self.__class__.__name__,
            'data_size': len(input_data)
        }