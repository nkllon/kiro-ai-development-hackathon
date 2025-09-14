from datetime import datetime
from typing import Dict, List, Any

    def get_metadata(self, name: str) -> Optional[InterfaceMetadata]:
        """Get interface metadata"""
        return self.interfaces.get(name)
    