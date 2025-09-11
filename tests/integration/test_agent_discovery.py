"""
Integration tests for Beast Mode Agent Discovery Protocol

Tests multi-agent discovery scenarios, capability matching, and collaboration workflows.
"""

import asyncio
import pytest
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import List

from src.beast_mode.messaging import BeastModeBusClient, BeastModeMessage, MessageType, DiscoveredAgent


@pytest.fixture
async def redis_client():
    """Provide a Redis client for test setup/teardown"""
    client = redis.from_url("redis://localhost:6379", decode_responses=True)
    try:
        await client.ping()
        yield client
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")
    finally:
        await client.aclose()


@pytest.fixture
async def agent_network():
    """Provide a network of connected agents with different capabilities"""
    agents = [
        BeastModeBusClient(
            agent_id="python_expert",
            capabilities=["python", "testing", "debugging", "code_review"]
        ),
        BeastModeBusClient(
            agent_id="devops_specialist", 
            capabilities=["devops", "kubernetes", "docker", "monitoring"]
        ),
        BeastModeBusClient(
            agent_id="fullstack_dev",
            capabilities=["python", "javascript", "react", "nodejs", "testing"]
        ),
        BeastModeBusClient(
            agent_id="data_scientist",
            capabilities=["python", "machine_learning", "data_analysis", "pandas"]
        ),
        BeastModeBusClient(
            agent_id="security_expert",
            capabilities=["security", "penetration_testing", "compliance", "audit"]
        )
    ]
    
    # Connect all agents
    connected_agents = []
    for agent in agents:
        if await agent.connect():
            connected_agents.append(agent)
        else:
            pytest.skip(f"Could not connect agent {agent.agent_id}")
    
    yield connected_agents
    
    # Cleanup
    for agent in connected_agents:
        await agent.disconnect()


class TestAgentDiscoveryProtocol:
    """Test the agent discovery protocol functionality"""
    
    @pytest.mark.asyncio
    async def test_single_agent_discovery(self, agent_network):
        """Test discovery between two agents"""
        if len(agent_network) < 2:
            pytest.skip("Need at least 2 agents")
        
        agent1, agent2 = agent_network[0], agent_network[1]
        
        # Start listening on agent2
        received_messages = []
        def message_callback(message: BeastModeMessage):
            received_messages.append(message)
        
        listen_task = asyncio.create_task(
            agent2.listen_for_messages(message_callback)
        )
        await asyncio.sleep(0.1)
        
        # Agent1 announces presence
        await agent1.announce_presence()
        
        # Wait for discovery and response
        await asyncio.sleep(0.5)
        
        # Stop listening
        agent2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Verify discovery occurred
        discovery_messages = [m for m in received_messages if m.type == MessageType.AGENT_DISCOVERY]
        assert len(discovery_messages) == 1
        assert discovery_messages[0].source == agent1.agent_id
        
        # Verify agent2 responded
        assert agent2.stats['messages_sent'] >= 1
        
        # Verify agent1 is registered in agent2's registry
        discovered_agents = agent2.get_discovered_agents()
        agent1_discovered = next((a for a in discovered_agents if a.agent_id == agent1.agent_id), None)
        assert agent1_discovered is not None
        assert set(agent1.capabilities).issubset(set(agent1_discovered.capabilities.capabilities))
    
    @pytest.mark.asyncio
    async def test_multi_agent_discovery(self, agent_network):
        """Test discovery across multiple agents"""
        if len(agent_network) < 3:
            pytest.skip("Need at least 3 agents")
        
        # Use first agent as the discoverer
        discoverer = agent_network[0]
        other_agents = agent_network[1:]
        
        # Start listening on ALL agents (including discoverer to receive responses)
        listen_tasks = []
        for agent in agent_network:
            task = asyncio.create_task(agent.listen_for_messages())
            listen_tasks.append(task)
        
        await asyncio.sleep(0.1)
        
        # Discoverer announces presence
        await discoverer.announce_presence()
        
        # Wait for all responses
        await asyncio.sleep(1.0)
        
        # Stop all listeners
        for agent in agent_network:
            agent.is_listening = False
        await asyncio.sleep(0.1)
        for task in listen_tasks:
            task.cancel()
        
        # Verify discoveries
        final_discovered = discoverer.get_discovered_agents()
        discovered_ids = [a.agent_id for a in final_discovered]
        
        # Should have discovered all other agents
        for agent in other_agents:
            assert agent.agent_id in discovered_ids
        
        # Verify each agent has the discoverer in their registry
        for agent in other_agents:
            agent_discovered_agents = agent.get_discovered_agents()
            discoverer_found = any(a.agent_id == discoverer.agent_id for a in agent_discovered_agents)
            assert discoverer_found
    
    @pytest.mark.asyncio
    async def test_capability_matching(self, agent_network):
        """Test finding agents with specific capabilities"""
        if len(agent_network) < 4:
            pytest.skip("Need at least 4 agents")
        
        # Use first agent as the searcher
        searcher = agent_network[0]
        other_agents = agent_network[1:]
        
        # Perform discovery - all agents need to listen
        listen_tasks = []
        for agent in agent_network:
            task = asyncio.create_task(agent.listen_for_messages())
            listen_tasks.append(task)
        
        await asyncio.sleep(0.1)
        await searcher.announce_presence()
        await asyncio.sleep(1.0)
        
        # Stop listeners
        for agent in agent_network:
            agent.is_listening = False
        await asyncio.sleep(0.1)
        for task in listen_tasks:
            task.cancel()
        
        # Test capability matching
        python_agents = searcher.find_agents_with_capabilities(["python"])
        python_agent_ids = [a.agent_id for a in python_agents]
        
        # Should find agents with python capability
        expected_python_agents = [
            agent for agent in other_agents 
            if "python" in agent.capabilities
        ]
        
        for expected_agent in expected_python_agents:
            assert expected_agent.agent_id in python_agent_ids
        
        # Test finding agents with ALL capabilities
        python_testing_agents = searcher.find_agents_with_all_capabilities(["python", "testing"])
        python_testing_ids = [a.agent_id for a in python_testing_agents]
        
        expected_python_testing = [
            agent for agent in other_agents
            if "python" in agent.capabilities and "testing" in agent.capabilities
        ]
        
        for expected_agent in expected_python_testing:
            assert expected_agent.agent_id in python_testing_ids
    
    @pytest.mark.asyncio
    async def test_help_request_with_discovery(self, agent_network):
        """Test help request workflow with capability matching"""
        if len(agent_network) < 3:
            pytest.skip("Need at least 3 agents")
        
        requester = agent_network[0]  # python_expert
        helpers = agent_network[1:]   # other agents
        
        # Start discovery - all agents need to listen
        listen_tasks = []
        for agent in agent_network:
            task = asyncio.create_task(agent.listen_for_messages())
            listen_tasks.append(task)
        
        await asyncio.sleep(0.1)
        await requester.announce_presence()
        await asyncio.sleep(0.5)
        
        # Find agents that can help with devops
        devops_agents = requester.find_agents_with_capabilities(["devops"])
        assert len(devops_agents) > 0
        
        # Send help request
        await requester.send_help_request(
            required_capabilities=["devops", "kubernetes"],
            description="Need help with Kubernetes deployment"
        )
        
        # Wait for responses
        await asyncio.sleep(0.5)
        
        # Stop listeners
        for agent in agent_network:
            agent.is_listening = False
        await asyncio.sleep(0.1)
        for task in listen_tasks:
            task.cancel()
        
        # Verify help responses were sent
        devops_agent = next((a for a in helpers if "devops" in a.capabilities), None)
        if devops_agent:
            # The devops agent should have sent a help response
            assert devops_agent.stats['messages_sent'] >= 2  # discovery response + help response
    
    @pytest.mark.asyncio
    async def test_agent_registry_persistence(self, agent_network):
        """Test that agent registry persists information correctly"""
        if len(agent_network) < 2:
            pytest.skip("Need at least 2 agents")
        
        agent1, agent2 = agent_network[0], agent_network[1]
        
        # Perform initial discovery
        listen_task = asyncio.create_task(agent2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        await agent1.announce_presence()
        await asyncio.sleep(0.3)
        
        # Get initial discovery info
        discovered_agents = agent2.get_discovered_agents()
        assert len(discovered_agents) == 1
        initial_discovery_count = discovered_agents[0].discovery_count
        
        # Announce presence again
        await agent1.announce_presence()
        await asyncio.sleep(0.3)
        
        # Stop listening
        agent2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Verify discovery count increased
        updated_agents = agent2.get_discovered_agents()
        assert len(updated_agents) == 1
        assert updated_agents[0].discovery_count == initial_discovery_count + 1
        assert updated_agents[0].agent_id == agent1.agent_id
    
    @pytest.mark.asyncio
    async def test_collaboration_score_tracking(self, agent_network):
        """Test collaboration score tracking"""
        if len(agent_network) < 2:
            pytest.skip("Need at least 2 agents")
        
        agent1, agent2 = agent_network[0], agent_network[1]
        
        # Perform discovery
        listen_task = asyncio.create_task(agent2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        await agent1.announce_presence()
        await asyncio.sleep(0.3)
        
        agent2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Update collaboration score
        agent2.update_agent_collaboration_score(agent1.agent_id, 2.5)
        
        # Verify score was updated
        discovered_agent = agent2.get_discovered_agent(agent1.agent_id)
        assert discovered_agent is not None
        assert discovered_agent.collaboration_score == 2.5
        
        # Update score again
        agent2.update_agent_collaboration_score(agent1.agent_id, -1.0)
        assert discovered_agent.collaboration_score == 1.5
    
    @pytest.mark.asyncio
    async def test_agent_cleanup(self, agent_network):
        """Test cleanup of inactive agents"""
        if len(agent_network) < 2:
            pytest.skip("Need at least 2 agents")
        
        agent1, agent2 = agent_network[0], agent_network[1]
        
        # Perform discovery
        listen_task = asyncio.create_task(agent2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        await agent1.announce_presence()
        await asyncio.sleep(0.3)
        
        agent2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Verify agent is discovered
        discovered_agents = agent2.get_discovered_agents()
        assert len(discovered_agents) == 1
        
        # Manually mark agent as old
        discovered_agent = discovered_agents[0]
        old_time = datetime.now() - timedelta(minutes=35)  # Older than timeout
        discovered_agent.last_seen = old_time
        
        # Trigger cleanup
        cleaned_count = agent2.cleanup_inactive_agents()
        
        # Verify cleanup occurred
        assert cleaned_count == 1
        active_agents = agent2.get_discovered_agents()
        assert len(active_agents) == 0
    
    @pytest.mark.asyncio
    async def test_discovery_statistics(self, agent_network):
        """Test discovery statistics tracking"""
        if len(agent_network) < 3:
            pytest.skip("Need at least 3 agents")
        
        discoverer = agent_network[0]
        other_agents = agent_network[1:3]  # Use 2 other agents
        
        # Perform discovery - all agents need to listen
        listen_tasks = []
        for agent in [discoverer] + other_agents:
            task = asyncio.create_task(agent.listen_for_messages())
            listen_tasks.append(task)
        
        await asyncio.sleep(0.1)
        await discoverer.announce_presence()
        await asyncio.sleep(1.0)
        
        # Stop listeners
        for agent in [discoverer] + other_agents:
            agent.is_listening = False
        await asyncio.sleep(0.1)
        for task in listen_tasks:
            task.cancel()
        
        # Check statistics
        stats = discoverer.get_discovery_stats()
        
        assert stats['discovery_enabled'] is True
        assert stats['active_agents'] == len(other_agents)
        assert stats['total_agents_discovered'] == len(other_agents)
        assert stats['discovery_messages_processed'] == len(other_agents)
        assert 'unique_capabilities' in stats
        assert stats['unique_capabilities'] > 0
    
    @pytest.mark.asyncio
    async def test_capability_index_functionality(self, agent_network):
        """Test capability indexing and lookup functionality"""
        if len(agent_network) < 4:
            pytest.skip("Need at least 4 agents")
        
        searcher = agent_network[0]
        other_agents = agent_network[1:]
        
        # Perform discovery - all agents need to listen
        listen_tasks = []
        for agent in agent_network:
            task = asyncio.create_task(agent.listen_for_messages())
            listen_tasks.append(task)
        
        await asyncio.sleep(0.1)
        await searcher.announce_presence()
        await asyncio.sleep(1.0)
        
        # Stop listeners
        for agent in agent_network:
            agent.is_listening = False
        await asyncio.sleep(0.1)
        for task in listen_tasks:
            task.cancel()
        
        # Test getting all capabilities
        all_capabilities = searcher.get_all_capabilities()
        
        # Should include capabilities from all discovered agents
        expected_capabilities = set()
        for agent in other_agents:
            expected_capabilities.update(agent.capabilities)
        
        assert expected_capabilities.issubset(all_capabilities)
        
        # Test specific capability searches
        if "python" in all_capabilities:
            python_agents = searcher.find_agents_with_capabilities(["python"])
            assert len(python_agents) > 0
            
            # All returned agents should have python capability
            for agent in python_agents:
                assert "python" in agent.capabilities.capabilities
        
        if "devops" in all_capabilities:
            devops_agents = searcher.find_agents_with_capabilities(["devops"])
            assert len(devops_agents) > 0
            
            # All returned agents should have devops capability
            for agent in devops_agents:
                assert "devops" in agent.capabilities.capabilities


class TestAgentDiscoveryEdgeCases:
    """Test edge cases and error conditions in agent discovery"""
    
    @pytest.mark.asyncio
    async def test_discovery_with_disabled_registry(self):
        """Test agent behavior with discovery disabled"""
        agent = BeastModeBusClient(
            agent_id="test_agent",
            capabilities=["testing"]
        )
        
        # Disable discovery
        agent.discovery_enabled = False
        
        if not await agent.connect():
            pytest.skip("Could not connect to Redis")
        
        try:
            # Discovery methods should return empty results
            discovered = await agent.discover_agents()
            assert len(discovered) == 0
            
            agents_with_caps = agent.find_agents_with_capabilities(["testing"])
            assert len(agents_with_caps) == 0
            
            all_agents = agent.get_discovered_agents()
            assert len(all_agents) == 0
            
            all_caps = agent.get_all_capabilities()
            assert len(all_caps) == 0
            
            stats = agent.get_discovery_stats()
            assert stats['discovery_enabled'] is False
            
        finally:
            await agent.disconnect()
    
    @pytest.mark.asyncio
    async def test_malformed_discovery_messages(self, agent_network):
        """Test handling of malformed discovery messages"""
        if len(agent_network) < 2:
            pytest.skip("Need at least 2 agents")
        
        agent1, agent2 = agent_network[0], agent_network[1]
        
        # Start listening on agent2
        listen_task = asyncio.create_task(agent2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        # Send malformed discovery message
        malformed_msg = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="malformed_agent",
            payload={
                "invalid_field": "invalid_data",
                # Missing agent_capabilities
            }
        )
        
        await agent1.send_message(malformed_msg)
        await asyncio.sleep(0.3)
        
        # Stop listening
        agent2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Agent should handle gracefully - check that it didn't crash
        health = agent2.get_health_status()
        assert health['is_connected'] is True
        
        # Should still be able to perform normal operations
        await agent2.send_simple_message("Test message after malformed")
    
    @pytest.mark.asyncio
    async def test_rapid_discovery_messages(self, agent_network):
        """Test handling of rapid discovery messages"""
        if len(agent_network) < 2:
            pytest.skip("Need at least 2 agents")
        
        agent1, agent2 = agent_network[0], agent_network[1]
        
        # Start listening on agent2
        listen_task = asyncio.create_task(agent2.listen_for_messages())
        await asyncio.sleep(0.1)
        
        # Send multiple rapid discovery messages
        for i in range(10):
            await agent1.announce_presence()
            await asyncio.sleep(0.01)  # Very short delay
        
        await asyncio.sleep(0.5)
        
        # Stop listening
        agent2.is_listening = False
        await asyncio.sleep(0.1)
        listen_task.cancel()
        
        # Verify agent was registered only once but discovery count increased
        discovered_agents = agent2.get_discovered_agents()
        assert len(discovered_agents) == 1
        
        discovered_agent = discovered_agents[0]
        assert discovered_agent.agent_id == agent1.agent_id
        assert discovered_agent.discovery_count >= 10  # Should have counted all discoveries