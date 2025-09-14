from datetime import datetime
from typing import Dict, List, Any

    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    