from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_help_system_stats(self) -> Dict[str, Any]:
        """Get help system statistics"""
        return self.help_system.get_help_system_stats()
