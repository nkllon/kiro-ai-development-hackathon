"""
Agent management and assignment logic.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

@dataclass
class Agent:
    id: str
    name: str
    capabilities: List[str]
    max_concurrent_tasks: int = 1
    current_tasks: int = 0
    is_available: bool = True

class AgentManager:
    """Manages agent pool and task assignments."""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_agent(self, agent: Agent) -> None:
        """Register a new agent."""
        self.agents[agent.id] = agent
        self.logger.info(f"Registered agent: {agent.id}")
    
    def get_available_agents(self) -> List[Agent]:
        """Get agents that are available for new tasks."""
        return [
            agent for agent in self.agents.values()
            if agent.is_available and agent.current_tasks < agent.max_concurrent_tasks
        ]
    
    def find_best_agent(self, task, available_agents: List[Agent]) -> Optional[Agent]:
        """Find the best agent for a given task based on capabilities."""
        # Simple capability matching - in reality this would be more sophisticated
        for agent in available_agents:
            if self._agent_can_handle_task(agent, task):
                return agent
        return None
    
    def _agent_can_handle_task(self, agent: Agent, task) -> bool:
        """Check if an agent can handle a specific task."""
        # Simple check - could be enhanced with more sophisticated matching
        return len(agent.capabilities) > 0  # Basic availability check
    
    def assign_task(self, agent_id: str, task_id: str) -> bool:
        """Assign a task to an agent."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.current_tasks >= agent.max_concurrent_tasks:
            return False
        
        agent.current_tasks += 1
        self.logger.info(f"Assigned task {task_id} to agent {agent_id}")
        return True
    
    def release_agent(self, agent_id: str) -> bool:
        """Release an agent from a completed task."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.current_tasks > 0:
            agent.current_tasks -= 1
        
        self.logger.info(f"Released agent {agent_id}")
        return True