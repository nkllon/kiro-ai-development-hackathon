from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def complete_collaboration(self, session_id: str, success: bool, metrics: Optional[Dict[str, Any]]=None) -> bool:
    """
        Mark a collaboration session as completed.
        
        Args:
            session_id: ID of the collaboration session
            success: Whether the collaboration was successful
            metrics: Optional success metrics
            
        Returns:
            bool: True if session was updated successfully
        """
    return self.help_system.complete_collaboration(session_id, success, metrics)
