from datetime import datetime
from typing import Dict, List, Any

    def get_collaboration_sessions(self) -> List:
        """Get all collaboration sessions"""
        return [session.__dict__ for session in self.help_system.get_collaboration_sessions()]
