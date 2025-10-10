"""Agent pool management for Constellation Orchestrator."""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog

from ..core.config import ConstellationConfig
from .claude_agent import ClaudeAgent


class AgentManager:
    """Manages pool of Claude CLI agents with dynamic scaling."""
    
    def __init__(self, config: ConstellationConfig):
        """Initialize agent manager."""
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Agent pool
        self.agents: Dict[str, ClaudeAgent] = {}
        self.agent_counter = 0
        
        # Scaling state
        self.last_scale_time = 0
        self.scale_cooldown = config.scale_cooldown
        self.scale_threshold = config.scale_threshold
        
        # Performance tracking
        self.total_tasks_assigned = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        
        self.logger.info(
            "agent_manager_initialized",
            base_agent_count=config.base_agent_count,
            max_agent_count=config.max_agent_count,
            scale_threshold=config.scale_threshold
        )
    
    async def initialize(self) -> bool:
        """Initialize agent manager and create base agent pool."""
        try:
            self.logger.info("agent_manager_initializing")
            
            # Create base agent pool
            for i in range(self.config.base_agent_count):
                agent_id = f"claude_agent_{i+1}"
                agent = ClaudeAgent(
                    agent_id=agent_id,
                    claude_cli_path=self.config.claude_cli_path,
                    timeout=self.config.default_task_timeout
                )
                self.agents[agent_id] = agent
                self.agent_counter += 1
            
            self.logger.info(
                "agent_manager_initialized",
                agent_count=len(self.agents)
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "agent_manager_initialization_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def get_available_agent(self) -> Optional[ClaudeAgent]:
        """Get an available agent from the pool."""
        try:
            # Find available agent
            for agent in self.agents.values():
                if agent.is_available():
                    return agent
            
            # No available agents, try auto-scaling
            if await self._try_scale_up():
                # Try again after scaling
                for agent in self.agents.values():
                    if agent.is_available():
                        return agent
            
            self.logger.debug(
                "agent_manager_no_available_agents",
                total_agents=len(self.agents),
                busy_agents=len([a for a in self.agents.values() if a.is_busy])
            )
            
            return None
            
        except Exception as e:
            self.logger.error(
                "agent_manager_get_available_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return None
    
    async def _try_scale_up(self) -> bool:
        """Try to scale up the agent pool."""
        try:
            current_time = time.time()
            
            # Check cooldown
            if current_time - self.last_scale_time < self.scale_cooldown:
                return False
            
            # Check if we're at max capacity
            if len(self.agents) >= self.config.max_agent_count:
                return False
            
            # Check utilization
            utilization = self._calculate_agent_utilization()
            if utilization < self.scale_threshold:
                return False
            
            # Scale up by adding 1-2 agents
            agents_to_add = min(2, self.config.max_agent_count - len(self.agents))
            
            for i in range(agents_to_add):
                self.agent_counter += 1
                agent_id = f"claude_agent_{self.agent_counter}"
                agent = ClaudeAgent(
                    agent_id=agent_id,
                    claude_cli_path=self.config.claude_cli_path,
                    timeout=self.config.default_task_timeout
                )
                self.agents[agent_id] = agent
            
            self.last_scale_time = current_time
            
            self.logger.info(
                "agent_manager_scaled_up",
                agents_added=agents_to_add,
                total_agents=len(self.agents),
                utilization=utilization
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "agent_manager_scale_up_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def _try_scale_down(self) -> bool:
        """Try to scale down the agent pool."""
        try:
            current_time = time.time()
            
            # Check cooldown
            if current_time - self.last_scale_time < self.scale_cooldown:
                return False
            
            # Don't scale below base count
            if len(self.agents) <= self.config.base_agent_count:
                return False
            
            # Check utilization (scale down if very low)
            utilization = self._calculate_agent_utilization()
            if utilization > 0.3:  # Don't scale down if utilization > 30%
                return False
            
            # Find idle agents to remove
            idle_agents = [
                agent for agent in self.agents.values()
                if agent.is_available() and 
                (datetime.utcnow() - agent.last_activity).total_seconds() > 300  # Idle for 5+ minutes
            ]
            
            if not idle_agents:
                return False
            
            # Remove 1-2 idle agents
            agents_to_remove = min(2, len(idle_agents), len(self.agents) - self.config.base_agent_count)
            
            for i in range(agents_to_remove):
                agent = idle_agents[i]
                await agent.shutdown()
                del self.agents[agent.agent_id]
            
            self.last_scale_time = current_time
            
            self.logger.info(
                "agent_manager_scaled_down",
                agents_removed=agents_to_remove,
                total_agents=len(self.agents),
                utilization=utilization
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "agent_manager_scale_down_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    def _calculate_agent_utilization(self) -> float:
        """Calculate current agent utilization percentage."""
        if not self.agents:
            return 0.0
        
        busy_agents = sum(1 for agent in self.agents.values() if agent.is_busy)
        return busy_agents / len(self.agents)
    
    async def auto_scale_agents(self) -> bool:
        """Automatically scale agent pool based on demand."""
        try:
            utilization = self._calculate_agent_utilization()
            
            if utilization > self.scale_threshold:
                return await self._try_scale_up()
            elif utilization < 0.3:
                return await self._try_scale_down()
            
            return False
            
        except Exception as e:
            self.logger.error(
                "agent_manager_auto_scale_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def get_agent_status(self) -> Dict[str, str]:
        """Get current status of all managed agents."""
        try:
            status = {}
            for agent_id, agent in self.agents.items():
                if agent.is_available():
                    status[agent_id] = "available"
                elif agent.is_busy:
                    status[agent_id] = "busy"
                else:
                    status[agent_id] = "unknown"
            
            return status
            
        except Exception as e:
            self.logger.error(
                "agent_manager_get_status_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    def get_available_agent_count(self) -> int:
        """Get number of available agents."""
        return len([agent for agent in self.agents.values() if agent.is_available()])
    
    def get_total_agent_count(self) -> int:
        """Get total number of agents."""
        return len(self.agents)
    
    def get_active_agent_count(self) -> int:
        """Get number of busy agents."""
        return len([agent for agent in self.agents.values() if agent.is_busy])
    
    async def health_check_agents(self) -> Dict[str, bool]:
        """Perform health check on all agents."""
        try:
            health_results = {}
            
            # Check each agent
            for agent_id, agent in self.agents.items():
                try:
                    # Skip health check for busy agents
                    if agent.is_busy:
                        health_results[agent_id] = True
                        continue
                    
                    # Perform health check
                    is_healthy = await agent.health_check()
                    health_results[agent_id] = is_healthy
                    
                    if not is_healthy:
                        self.logger.warning(
                            "agent_manager_unhealthy_agent",
                            agent_id=agent_id
                        )
                    
                except Exception as e:
                    self.logger.error(
                        "agent_manager_health_check_error",
                        agent_id=agent_id,
                        error=str(e),
                        error_type=type(e).__name__
                    )
                    health_results[agent_id] = False
            
            healthy_count = sum(1 for is_healthy in health_results.values() if is_healthy)
            
            self.logger.debug(
                "agent_manager_health_check_completed",
                total_agents=len(health_results),
                healthy_agents=healthy_count,
                unhealthy_agents=len(health_results) - healthy_count
            )
            
            return health_results
            
        except Exception as e:
            self.logger.error(
                "agent_manager_health_check_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    def get_agent_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all agents."""
        try:
            metrics = {}
            
            for agent_id, agent in self.agents.items():
                metrics[agent_id] = agent.get_performance_metrics()
            
            return metrics
            
        except Exception as e:
            self.logger.error(
                "agent_manager_get_metrics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive agent pool statistics."""
        try:
            agent_statuses = [agent.get_status() for agent in self.agents.values()]
            
            total_tasks_completed = sum(status['tasks_completed'] for status in agent_statuses)
            total_tasks_failed = sum(status['tasks_failed'] for status in agent_statuses)
            total_execution_time = sum(status['total_execution_time'] for status in agent_statuses)
            
            return {
                'total_agents': len(self.agents),
                'available_agents': self.get_available_agent_count(),
                'busy_agents': self.get_active_agent_count(),
                'utilization': self._calculate_agent_utilization(),
                'total_tasks_completed': total_tasks_completed,
                'total_tasks_failed': total_tasks_failed,
                'total_execution_time': total_execution_time,
                'average_success_rate': total_tasks_completed / (total_tasks_completed + total_tasks_failed) if (total_tasks_completed + total_tasks_failed) > 0 else 0.0,
                'average_execution_time': total_execution_time / total_tasks_completed if total_tasks_completed > 0 else 0.0,
                'last_scale_time': datetime.fromtimestamp(self.last_scale_time).isoformat() if self.last_scale_time > 0 else None
            }
            
        except Exception as e:
            self.logger.error(
                "agent_manager_get_statistics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    async def health_check(self) -> bool:
        """Health check for agent manager."""
        try:
            # Check if we have agents
            if not self.agents:
                return False
            
            # Check if at least some agents are healthy
            health_results = await self.health_check_agents()
            healthy_count = sum(1 for is_healthy in health_results.values() if is_healthy)
            
            # Consider healthy if at least 50% of agents are healthy
            return healthy_count >= (len(self.agents) * 0.5)
            
        except Exception as e:
            self.logger.error(
                "agent_manager_health_check_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def shutdown(self) -> None:
        """Shutdown all agents and clean up."""
        try:
            self.logger.info(
                "agent_manager_shutting_down",
                agent_count=len(self.agents)
            )
            
            # Shutdown all agents
            shutdown_tasks = []
            for agent in self.agents.values():
                shutdown_tasks.append(agent.shutdown())
            
            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)
            
            # Clear agent pool
            self.agents.clear()
            
            self.logger.info("agent_manager_shutdown_complete")
            
        except Exception as e:
            self.logger.error(
                "agent_manager_shutdown_error",
                error=str(e),
                error_type=type(e).__name__
            )