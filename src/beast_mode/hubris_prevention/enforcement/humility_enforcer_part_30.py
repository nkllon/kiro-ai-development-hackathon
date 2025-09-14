from datetime import datetime
from typing import Dict, List, Any

    def list_interfaces(self) -> List[str]:
        """List all registered interfaces"""
        return list(self.interfaces.keys())
    