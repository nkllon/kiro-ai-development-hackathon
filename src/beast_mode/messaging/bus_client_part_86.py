from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def update_agent_collaboration_score(self, agent_id: str, score_delta: float) -> None:
    """
        Update an agent's collaboration score.
        
        Args:
            agent_id: Agent to update
            score_delta: Change in score (positive for successful collaboration)
        """
    if self.discovery_enabled:
        self.agent_registry.update_collaboration_score(agent_id, score_delta)
