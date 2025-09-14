from datetime import datetime
from typing import Dict, List, Any

def is_agent_available_for_collaboration(self, agent_id: str, at_time: Optional[datetime]=None) -> bool:
    """Check if an agent is available for collaboration"""
    return self.collaboration_scheduler.is_agent_available(agent_id, at_time)
