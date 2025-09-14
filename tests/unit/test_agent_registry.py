"""
Unit tests for Beast Mode Agent Registry
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch

from src.beast_mode.messaging.agent_registry import AgentRegistry, DiscoveredAgent
from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule



class TestDiscoveredAgent(ReflectiveModule):
    """Test DiscoveredAgent dataclass"""
    
    def test_discovered_agent_creation(self):
        """Test creating a DiscoveredAgent"""
        capabilities = AgentCapabilities(
            agent_id="test_agent",
            capabilities=["python", "testing"]
        )
        
        agent = DiscoveredAgent(
            agent_id="test_agent",
            capabilities=capabilities
        )
        
        assert agent.agent_id == "test_agent"
        assert agent.capabilities == capabilities
        assert isinstance(agent.first_seen, datetime)
        assert isinstance(agent.last_seen, datetime)
        assert agent.discovery_count == 1
        assert agent.response_count == 0
        assert agent.collaboration_score == 0.0
        assert agent.is_active is True


class TestAgentRegistry(ReflectiveModule):
    """Test AgentRegistry functionality"""
    
    @pytest.fixture
    def registry(self):
        """Provide a fresh agent registry"""
        return AgentRegistry(agent_timeout_minutes=5)
    
    @pytest.fixture
    def sample_discovery_message(self):
        """Provide a sample agent discovery message"""
        capabilities = AgentCapabilities(
            agent_id="test_agent_1",
            capabilities=["python", "testing", "devops"],
            availability="ready_for_business"
        )
        
        return BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="test_agent_1",
            payload={
                "agent_capabilities": capabilities.model_dump(),
                "announcement": "Test agent ready for collaboration"
            }
        )
    
    @pytest.fixture
    def sample_response_message(self):
        """Provide a sample agent response message"""
        capabilities = AgentCapabilities(
            agent_id="test_agent_2",
            capabilities=["java", "kubernetes"],
            availability="ready_for_business"
        )
        
        return BeastModeMessage(
            type=MessageType.AGENT_RESPONSE,
            source="test_agent_2",
            target="test_agent_1",
            payload={
                "agent_capabilities": capabilities.model_dump(),
                "response_to": "some_message_id"
            }
        )
    
    def test_registry_initialization(self, registry):
        """Test registry initialization"""
        assert len(registry.agents) == 0
        assert len(registry.capability_index) == 0
        assert registry.stats['total_agents_discovered'] == 0
        assert registry.stats['active_agents'] == 0
    
    def test_register_agent_discovery_new_agent(self, registry, sample_discovery_message):
        """Test registering a new agent discovery"""
        agent = registry.register_agent_discovery(sample_discovery_message)
        
        assert agent.agent_id == "test_agent_1"
        assert "python" in agent.capabilities.capabilities
        assert "testing" in agent.capabilities.capabilities
        assert "devops" in agent.capabilities.capabilities
        assert agent.discovery_count == 1
        assert agent.is_active is True
        
        # Check registry state
        assert len(registry.agents) == 1
        assert "test_agent_1" in registry.agents
        assert registry.stats['total_agents_discovered'] == 1
        assert registry.stats['active_agents'] == 1
        assert registry.stats['discovery_messages_processed'] == 1
        
        # Check capability index
        assert "python" in registry.capability_index
        assert "testing" in registry.capability_index
        assert "devops" in registry.capability_index
        assert "test_agent_1" in registry.capability_index["python"]
    
    def test_register_agent_discovery_existing_agent(self, registry, sample_discovery_message):
        """Test updating an existing agent discovery"""
        # Register first time
        agent1 = registry.register_agent_discovery(sample_discovery_message)
        first_seen = agent1.first_seen
        
        # Register again
        agent2 = registry.register_agent_discovery(sample_discovery_message)
        
        assert agent1 is agent2  # Same object
        assert agent2.discovery_count == 2
        assert agent2.first_seen == first_seen  # Should not change
        assert agent2.last_seen > first_seen  # Should be updated
        
        # Registry should still have only one agent
        assert len(registry.agents) == 1
        assert registry.stats['total_agents_discovered'] == 1  # Not incremented
        assert registry.stats['discovery_messages_processed'] == 2  # Incremented
    
    def test_register_agent_response(self, registry, sample_response_message):
        """Test registering an agent response"""
        # First register the agent via discovery
        discovery_msg = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="test_agent_2",
            payload={
                "agent_capabilities": AgentCapabilities(
                    agent_id="test_agent_2",
                    capabilities=["java"]
                ).model_dump()
            }
        )
        registry.register_agent_discovery(discovery_msg)
        
        # Now register response
        agent = registry.register_agent_response(sample_response_message)
        
        assert agent is not None
        assert agent.agent_id == "test_agent_2"
        assert agent.response_count == 1
        assert "kubernetes" in agent.capabilities.capabilities  # Updated from response
    
    def test_register_agent_response_unknown_agent(self, registry, sample_response_message):
        """Test registering response from unknown agent"""
        agent = registry.register_agent_response(sample_response_message)
        assert agent is None
    
    def test_find_agents_with_capabilities(self, registry):
        """Test finding agents with specific capabilities"""
        # Register multiple agents
        agents_data = [
            ("agent_1", ["python", "testing"]),
            ("agent_2", ["python", "devops"]),
            ("agent_3", ["java", "testing"]),
            ("agent_4", ["javascript", "frontend"])
        ]
        
        for agent_id, capabilities in agents_data:
            msg = BeastModeMessage(
                type=MessageType.AGENT_DISCOVERY,
                source=agent_id,
                payload={
                    "agent_capabilities": AgentCapabilities(
                        agent_id=agent_id,
                        capabilities=capabilities
                    ).model_dump()
                }
            )
            registry.register_agent_discovery(msg)
        
        # Test finding agents with python capability
        python_agents = registry.find_agents_with_capabilities(["python"])
        python_agent_ids = [a.agent_id for a in python_agents]
        assert "agent_1" in python_agent_ids
        assert "agent_2" in python_agent_ids
        assert "agent_3" not in python_agent_ids
        assert "agent_4" not in python_agent_ids
        
        # Test finding agents with testing capability
        testing_agents = registry.find_agents_with_capabilities(["testing"])
        testing_agent_ids = [a.agent_id for a in testing_agents]
        assert "agent_1" in testing_agent_ids
        assert "agent_3" in testing_agent_ids
        assert "agent_2" not in testing_agent_ids
        assert "agent_4" not in testing_agent_ids
        
        # Test finding agents with multiple capabilities (OR logic)
        multi_agents = registry.find_agents_with_capabilities(["python", "java"])
        multi_agent_ids = [a.agent_id for a in multi_agents]
        assert "agent_1" in multi_agent_ids  # has python
        assert "agent_2" in multi_agent_ids  # has python
        assert "agent_3" in multi_agent_ids  # has java
        assert "agent_4" not in multi_agent_ids  # has neither
    
    def test_find_agents_with_all_capabilities(self, registry):
        """Test finding agents with ALL required capabilities"""
        # Register agents
        agents_data = [
            ("agent_1", ["python", "testing", "devops"]),
            ("agent_2", ["python", "testing"]),
            ("agent_3", ["python", "devops"]),
            ("agent_4", ["testing", "devops"])
        ]
        
        for agent_id, capabilities in agents_data:
            msg = BeastModeMessage(
                type=MessageType.AGENT_DISCOVERY,
                source=agent_id,
                payload={
                    "agent_capabilities": AgentCapabilities(
                        agent_id=agent_id,
                        capabilities=capabilities
                    ).model_dump()
                }
            )
            registry.register_agent_discovery(msg)
        
        # Test finding agents with ALL capabilities
        all_caps_agents = registry.find_agents_with_all_capabilities(["python", "testing"])
        all_caps_agent_ids = [a.agent_id for a in all_caps_agents]
        assert "agent_1" in all_caps_agent_ids  # has both
        assert "agent_2" in all_caps_agent_ids  # has both
        assert "agent_3" not in all_caps_agent_ids  # missing testing
        assert "agent_4" not in all_caps_agent_ids  # missing python
        
        # Test with three capabilities
        three_caps_agents = registry.find_agents_with_all_capabilities(["python", "testing", "devops"])
        three_caps_agent_ids = [a.agent_id for a in three_caps_agents]
        assert "agent_1" in three_caps_agent_ids  # has all three
        assert len(three_caps_agent_ids) == 1
    
    def test_get_all_capabilities(self, registry):
        """Test getting all unique capabilities"""
        # Register agents with various capabilities
        agents_data = [
            ("agent_1", ["python", "testing"]),
            ("agent_2", ["java", "testing"]),
            ("agent_3", ["javascript", "frontend", "testing"])
        ]
        
        for agent_id, capabilities in agents_data:
            msg = BeastModeMessage(
                type=MessageType.AGENT_DISCOVERY,
                source=agent_id,
                payload={
                    "agent_capabilities": AgentCapabilities(
                        agent_id=agent_id,
                        capabilities=capabilities
                    ).model_dump()
                }
            )
            registry.register_agent_discovery(msg)
        
        all_caps = registry.get_all_capabilities()
        expected_caps = {"python", "java", "javascript", "testing", "frontend"}
        assert all_caps == expected_caps
    
    def test_update_collaboration_score(self, registry, sample_discovery_message):
        """Test updating collaboration scores"""
        agent = registry.register_agent_discovery(sample_discovery_message)
        
        # Initial score should be 0
        assert agent.collaboration_score == 0.0
        
        # Update score positively
        registry.update_collaboration_score("test_agent_1", 1.5)
        assert agent.collaboration_score == 1.5
        
        # Update score negatively
        registry.update_collaboration_score("test_agent_1", -0.5)
        assert agent.collaboration_score == 1.0
        
        # Score should not go below 0
        registry.update_collaboration_score("test_agent_1", -2.0)
        assert agent.collaboration_score == 0.0
    
    def test_cleanup_inactive_agents(self, registry):
        """Test cleanup of inactive agents"""
        # Register an agent
        msg = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="old_agent",
            payload={
                "agent_capabilities": AgentCapabilities(
                    agent_id="old_agent",
                    capabilities=["python"]
                ).model_dump()
            }
        )
        agent = registry.register_agent_discovery(msg)
        
        # Manually set last_seen to old time
        old_time = datetime.now() - timedelta(minutes=10)
        agent.last_seen = old_time
        
        # Cleanup should mark agent as inactive
        removed_count = registry.cleanup_inactive_agents()
        
        assert removed_count == 1
        assert not agent.is_active
        assert registry.stats['active_agents'] == 0
        
        # Capability index should be cleaned up
        assert "python" not in registry.capability_index
    
    def test_get_registry_stats(self, registry, sample_discovery_message):
        """Test getting registry statistics"""
        # Register an agent
        registry.register_agent_discovery(sample_discovery_message)
        
        stats = registry.get_registry_stats()
        
        assert stats['total_agents_registered'] == 1
        assert stats['active_agents'] == 1
        assert stats['total_agents_discovered'] == 1
        assert stats['discovery_messages_processed'] == 1
        assert stats['unique_capabilities'] == 3  # python, testing, devops
        assert 'capability_distribution' in stats
        assert stats['capability_distribution']['python'] == 1
    
    def test_export_agents(self, registry, sample_discovery_message):
        """Test exporting agents as dictionaries"""
        registry.register_agent_discovery(sample_discovery_message)
        
        exported = registry.export_agents()
        
        assert len(exported) == 1
        agent_data = exported[0]
        
        assert agent_data['agent_id'] == "test_agent_1"
        assert 'capabilities' in agent_data
        assert 'first_seen' in agent_data
        assert 'last_seen' in agent_data
        assert agent_data['discovery_count'] == 1
        assert agent_data['response_count'] == 0
        assert agent_data['collaboration_score'] == 0.0
        assert agent_data['is_active'] is True
    
    def test_invalid_message_types(self, registry):
        """Test handling invalid message types"""
        invalid_msg = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test_agent",
            payload={"content": "hello"}
        )
        
        with pytest.raises(ValueError, match="Expected AGENT_DISCOVERY"):
            registry.register_agent_discovery(invalid_msg)
        
        with pytest.raises(ValueError, match="Expected AGENT_RESPONSE"):
            registry.register_agent_response(invalid_msg)
    
    @pytest.mark.asyncio
    async def test_background_cleanup_task(self, registry):
        """Test background cleanup task"""
        # Start background cleanup
        registry.start_background_cleanup()
        
        # Verify task is running
        assert registry._cleanup_task is not None
        assert not registry._cleanup_task.done()
        
        # Stop cleanup
        registry.stop_background_cleanup()
        
        # Wait a bit for cancellation
        await asyncio.sleep(0.1)
        
        # Verify task is cancelled
        assert registry._cleanup_task.cancelled()
    
    def test_capability_index_updates(self, registry):
        """Test that capability index is properly updated"""
        # Register agent with initial capabilities
        msg1 = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="test_agent",
            payload={
                "agent_capabilities": AgentCapabilities(
                    agent_id="test_agent",
                    capabilities=["python", "testing"]
                ).model_dump()
            }
        )
        registry.register_agent_discovery(msg1)
        
        # Verify initial index
        assert "python" in registry.capability_index
        assert "testing" in registry.capability_index
        assert "test_agent" in registry.capability_index["python"]
        assert "test_agent" in registry.capability_index["testing"]
        
        # Update agent with different capabilities
        msg2 = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source="test_agent",
            payload={
                "agent_capabilities": AgentCapabilities(
                    agent_id="test_agent",
                    capabilities=["java", "devops"]
                ).model_dump()
            }
        )
        registry.register_agent_discovery(msg2)
        
        # Verify index is updated
        assert "java" in registry.capability_index
        assert "devops" in registry.capability_index
        assert "test_agent" in registry.capability_index["java"]
        assert "test_agent" in registry.capability_index["devops"]
        
        # Old capabilities should be removed if no other agents have them
        assert "python" not in registry.capability_index

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert "testing" not in registry.capability_index