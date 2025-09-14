from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def cleanup_expired_help_requests(self) -> int:
        """
        Clean up expired help requests.
        
        Returns:
            int: Number of requests cleaned up
        """
        return self.help_system.cleanup_expired_requests()
