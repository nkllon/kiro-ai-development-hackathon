from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_collaboration_recommendations(self) -> List[Dict[str, Any]]:
        """Get collaboration recommendations based on patterns"""
        return self.collaboration_scheduler.get_collaboration_recommendations(self.agent_id)
