"""
Beast Mode Agent Registry

Tracks discovered agents and their capabilities for collaboration matching.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

from .models import AgentCapabilities, BeastModeMessage, MessageType


logger = logging.getLogger(__name__)


@dataclass
class DiscoveredAgent:
    """Information about a discovered agent"""

    agent_id: str
    capabilities: AgentCapabilities
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    discovery_count: int = 1
    response_count: int = 0
    collaboration_score: float = 0.0
    is_active: bool = True


class AgentRegistry:
    """Registry for tracking discovered agents and their capabilities"""

    def __init__(self, agent_timeout_minutes: int = 30):
        self.agents: Dict[str, DiscoveredAgent] = {}
        self.agent_timeout = timedelta(minutes=agent_timeout_minutes)

        # Capability index for fast lookups
        self.capability_index: Dict[str, Set[str]] = (
            {}
        )  # capability -> set of agent_ids

        # Statistics
        self.stats = {
            "total_agents_discovered": 0,
            "active_agents": 0,
            "discovery_messages_processed": 0,
            "capability_matches_found": 0,
            "last_cleanup": datetime.now(),
        }

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = 300  # 5 minutes

    def start_background_cleanup(self) -> None:
        """Start background task to clean up inactive agents"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started agent registry background cleanup")

    def stop_background_cleanup(self) -> None:
        """Stop background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            logger.info("Stopped agent registry background cleanup")

    async def _cleanup_loop(self) -> None:
        """Background loop to clean up inactive agents"""
        try:
            while True:
                await asyncio.sleep(self._cleanup_interval)
                self.cleanup_inactive_agents()
        except asyncio.CancelledError:
            logger.info("Agent registry cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Error in agent registry cleanup loop: {e}")

    def register_agent_discovery(self, message: BeastModeMessage) -> DiscoveredAgent:
        """
        Register an agent discovery message.

        Args:
            message: Agent discovery message

        Returns:
            DiscoveredAgent: The registered/updated agent info
        """
        if message.type != MessageType.AGENT_DISCOVERY:
            raise ValueError(f"Expected AGENT_DISCOVERY message, got {message.type}")

        agent_id = message.source

        # Extract capabilities from payload
        capabilities_data = message.payload.get("agent_capabilities", {})
        if isinstance(capabilities_data, dict):
            capabilities = AgentCapabilities(**capabilities_data)
        else:
            # Fallback to basic capabilities
            capabilities = AgentCapabilities(
                agent_id=agent_id,
                capabilities=message.payload.get("capabilities", []),
                availability=message.payload.get("availability", "ready_for_business"),
            )

        now = datetime.now()

        if agent_id in self.agents:
            # Update existing agent
            agent = self.agents[agent_id]
            agent.capabilities = capabilities
            agent.last_seen = now
            agent.discovery_count += 1
            agent.is_active = True

            logger.debug(
                f"Updated agent {agent_id} (discovery #{agent.discovery_count})"
            )
        else:
            # Register new agent
            agent = DiscoveredAgent(
                agent_id=agent_id,
                capabilities=capabilities,
                first_seen=now,
                last_seen=now,
            )
            self.agents[agent_id] = agent
            self.stats["total_agents_discovered"] += 1

            logger.info(
                f"Registered new agent {agent_id} with capabilities: {capabilities.capabilities}"
            )

        # Update capability index
        self._update_capability_index(agent_id, capabilities.capabilities)

        # Update stats
        self.stats["discovery_messages_processed"] += 1
        self._update_active_count()

        return agent

    def register_agent_response(
        self, message: BeastModeMessage
    ) -> Optional[DiscoveredAgent]:
        """
        Register an agent response message.

        Args:
            message: Agent response message

        Returns:
            Optional[DiscoveredAgent]: The updated agent info if found
        """
        if message.type != MessageType.AGENT_RESPONSE:
            raise ValueError(f"Expected AGENT_RESPONSE message, got {message.type}")

        agent_id = message.source

        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.response_count += 1
            agent.last_seen = datetime.now()
            agent.is_active = True

            # Update capabilities if provided
            capabilities_data = message.payload.get("agent_capabilities", {})
            if isinstance(capabilities_data, dict):
                capabilities = AgentCapabilities(**capabilities_data)
                agent.capabilities = capabilities
                self._update_capability_index(agent_id, capabilities.capabilities)

            logger.debug(
                f"Updated agent {agent_id} from response (response #{agent.response_count})"
            )
            return agent

        return None

    def find_agents_with_capabilities(
        self, required_capabilities: List[str]
    ) -> List[DiscoveredAgent]:
        """
        Find agents that have any of the required capabilities.

        Args:
            required_capabilities: List of required capabilities

        Returns:
            List[DiscoveredAgent]: Agents with matching capabilities, sorted by match score
        """
        matching_agents = []

        for capability in required_capabilities:
            if capability in self.capability_index:
                for agent_id in self.capability_index[capability]:
                    if agent_id in self.agents and self.agents[agent_id].is_active:
                        matching_agents.append(self.agents[agent_id])

        # Remove duplicates and calculate match scores
        unique_agents = {}
        for agent in matching_agents:
            if agent.agent_id not in unique_agents:
                # Calculate match score
                agent_caps = set(agent.capabilities.capabilities)
                required_caps = set(required_capabilities)
                match_score = len(agent_caps.intersection(required_caps)) / len(
                    required_caps
                )

                unique_agents[agent.agent_id] = (agent, match_score)

        # Sort by match score (descending) and collaboration score
        sorted_agents = sorted(
            unique_agents.values(),
            key=lambda x: (x[1], x[0].collaboration_score, -x[0].last_seen.timestamp()),
            reverse=True,
        )

        self.stats["capability_matches_found"] += len(sorted_agents)

        return [agent for agent, _ in sorted_agents]

    def find_agents_with_all_capabilities(
        self, required_capabilities: List[str]
    ) -> List[DiscoveredAgent]:
        """
        Find agents that have ALL of the required capabilities.

        Args:
            required_capabilities: List of required capabilities

        Returns:
            List[DiscoveredAgent]: Agents with all matching capabilities
        """
        if not required_capabilities:
            return []

        matching_agents = []
        required_caps_set = set(required_capabilities)

        for agent in self.agents.values():
            if not agent.is_active:
                continue

            agent_caps_set = set(agent.capabilities.capabilities)
            if required_caps_set.issubset(agent_caps_set):
                matching_agents.append(agent)

        # Sort by collaboration score and recency
        matching_agents.sort(
            key=lambda x: (x.collaboration_score, -x.last_seen.timestamp()),
            reverse=True,
        )

        return matching_agents

    def get_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def get_active_agents(self) -> List[DiscoveredAgent]:
        """Get all active agents"""
        return [agent for agent in self.agents.values() if agent.is_active]

    def get_all_capabilities(self) -> Set[str]:
        """Get all unique capabilities across all agents"""
        return set(self.capability_index.keys())

    def update_collaboration_score(self, agent_id: str, score_delta: float) -> None:
        """
        Update an agent's collaboration score.

        Args:
            agent_id: Agent to update
            score_delta: Change in score (positive for successful collaboration)
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.collaboration_score = max(
                0.0, agent.collaboration_score + score_delta
            )
            logger.debug(
                f"Updated collaboration score for {agent_id}: {agent.collaboration_score}"
            )

    def cleanup_inactive_agents(self) -> int:
        """
        Remove agents that haven't been seen recently.

        Returns:
            int: Number of agents removed
        """
        now = datetime.now()
        inactive_agents = []

        for agent_id, agent in self.agents.items():
            if now - agent.last_seen > self.agent_timeout:
                inactive_agents.append(agent_id)

        # Remove inactive agents
        removed_count = 0
        for agent_id in inactive_agents:
            agent = self.agents[agent_id]
            agent.is_active = False

            # Remove from capability index
            for capability in agent.capabilities.capabilities:
                if capability in self.capability_index:
                    self.capability_index[capability].discard(agent_id)
                    if not self.capability_index[capability]:
                        del self.capability_index[capability]

            removed_count += 1
            logger.info(
                f"Marked agent {agent_id} as inactive (last seen: {agent.last_seen})"
            )

        if removed_count > 0:
            self._update_active_count()
            self.stats["last_cleanup"] = now
            logger.info(f"Cleaned up {removed_count} inactive agents")

        return removed_count

    def _update_capability_index(self, agent_id: str, capabilities: List[str]) -> None:
        """Update the capability index for an agent"""
        # Remove agent from old capabilities and clean up empty sets
        capabilities_to_remove = []
        for capability, agent_set in self.capability_index.items():
            agent_set.discard(agent_id)
            if not agent_set:  # If set is empty, mark for removal
                capabilities_to_remove.append(capability)

        # Remove empty capability entries
        for capability in capabilities_to_remove:
            del self.capability_index[capability]

        # Add agent to new capabilities
        for capability in capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = set()
            self.capability_index[capability].add(agent_id)

    def _update_active_count(self) -> None:
        """Update the active agents count"""
        self.stats["active_agents"] = len(
            [a for a in self.agents.values() if a.is_active]
        )

    def get_registry_stats(self) -> Dict:
        """Get registry statistics"""
        return {
            **self.stats,
            "total_agents_registered": len(self.agents),
            "unique_capabilities": len(self.capability_index),
            "capability_distribution": {
                cap: len(agents) for cap, agents in self.capability_index.items()
            },
        }

    def export_agents(self) -> List[Dict]:
        """Export all agents as dictionaries"""
        return [
            {
                "agent_id": agent.agent_id,
                "capabilities": agent.capabilities.model_dump(),
                "first_seen": agent.first_seen.isoformat(),
                "last_seen": agent.last_seen.isoformat(),
                "discovery_count": agent.discovery_count,
                "response_count": agent.response_count,
                "collaboration_score": agent.collaboration_score,
                "is_active": agent.is_active,
            }
            for agent in self.agents.values()
        ]
