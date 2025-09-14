from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def get_next_available_collaboration_slot(self, agent_id: str, duration_minutes: int=30) -> Optional[datetime]:
        """Find the next available collaboration slot for an agent"""
        return self.collaboration_scheduler.get_next_available_slot(agent_id, duration_minutes)
