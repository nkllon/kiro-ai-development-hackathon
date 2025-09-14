from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def register_agent(self, agent: Agent) -> None:
        """Register an agent for task execution."""
        self.agent_manager.register_agent(agent)
    