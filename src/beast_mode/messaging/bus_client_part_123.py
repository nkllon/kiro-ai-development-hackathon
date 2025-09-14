from datetime import datetime
from typing import Dict, List, Any

def get_help_system_stats(self) -> Dict[str, Any]:
    """Get help system statistics"""
    return self.help_system.get_help_system_stats()
