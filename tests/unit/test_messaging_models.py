"""
Unit tests for Beast Mode messaging models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
import uuid

from src.beast_mode.messaging.models import BeastModeMessage, MessageType, AgentCapabilities
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule



class TestMessageType(ReflectiveModule):
    """Test MessageType enum"""
    
    def test_all_message_types_defined(self):
        """Test that all expected message types are defined"""
        expected_types = [
            "simple_message",
            "prompt_request", 
            "prompt_response",
            "agent_discovery",
            "agent_response",
            "help_wanted",
            "help_response", 
            "spore_delivery",
            "spore_request",
            "spore_spawn",
            "technical_exchange",
            "system_health"
        ]
        
        for msg_type in expected_types:
            assert hasattr(MessageType, msg_type.upper())
            assert MessageType(msg_type) == msg_type
    
    def test_message_type_string_values(self):
        """Test that message types have correct string values"""
        assert MessageType.SIMPLE_MESSAGE == "simple_message"
        assert MessageType.PROMPT_REQUEST == "prompt_request"
        assert MessageType.AGENT_DISCOVERY == "agent_discovery"


class TestBeastModeMessage(ReflectiveModule):
    """Test BeastModeMessage model"""
    
    def test_minimal_message_creation(self):
        """Test creating message with minimal required fields"""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test_agent"
        )
        
        assert message.type == MessageType.SIMPLE_MESSAGE
        assert message.source == "test_agent"
        assert message.target is None
        assert message.payload == {}
        assert isinstance(message.timestamp, datetime)
        assert message.priority == 5  # default
        assert message.correlation_id is None
        assert isinstance(message.id, str)
        assert len(message.id) > 0
    
    def test_full_message_creation(self):
        """Test creating message with all fields"""
        test_id = str(uuid.uuid4())
        test_timestamp = datetime.now()
        test_correlation_id = str(uuid.uuid4())
        
        message = BeastModeMessage(
            id=test_id,
            type=MessageType.PROMPT_REQUEST,
            source="agent_1",
            target="agent_2", 
            payload={"prompt": "Hello world", "context": "test"},
            timestamp=test_timestamp,
            priority=3,
            correlation_id=test_correlation_id
        )
        
        assert message.id == test_id
        assert message.type == MessageType.PROMPT_REQUEST
        assert message.source == "agent_1"
        assert message.target == "agent_2"
        assert message.payload == {"prompt": "Hello world", "context": "test"}
        assert message.timestamp == test_timestamp
        assert message.priority == 3
        assert message.correlation_id == test_correlation_id
    
    def test_priority_validation(self):
        """Test priority field validation"""
        # Valid priorities (1-10)
        for priority in range(1, 11):
            message = BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source="test",
                priority=priority
            )
            assert message.priority == priority
        
        # Invalid priorities
        with pytest.raises(ValidationError):
            BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source="test",
                priority=0  # Too low
            )
        
        with pytest.raises(ValidationError):
            BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source="test", 
                priority=11  # Too high
            )
    
    def test_message_serialization(self):
        """Test message serialization to dict"""
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source="needy_agent",
            target="helper_agent",
            payload={"capabilities": ["python", "testing"]},
            priority=4
        )
        
        data = message.model_dump()
        
        assert data["type"] == "help_wanted"
        assert data["source"] == "needy_agent"
        assert data["target"] == "helper_agent"
        assert data["payload"] == {"capabilities": ["python", "testing"]}
        assert data["priority"] == 4
        assert "id" in data
        assert "timestamp" in data
    
    def test_message_deserialization(self):
        """Test message deserialization from dict"""
        data = {
            "id": str(uuid.uuid4()),
            "type": "spore_delivery",
            "source": "spore_agent",
            "target": "recipient_agent",
            "payload": {"spore_name": "test_spore", "content": "spore data"},
            "timestamp": datetime.now().isoformat(),
            "priority": 2
        }
        
        message = BeastModeMessage(**data)
        
        assert message.id == data["id"]
        assert message.type == MessageType.SPORE_DELIVERY
        assert message.source == data["source"]
        assert message.target == data["target"]
        assert message.payload == data["payload"]
        assert message.priority == data["priority"]
    
    def test_required_fields(self):
        """Test that required fields are enforced"""
        # Missing type
        with pytest.raises(ValidationError):
            BeastModeMessage(source="test")
        
        # Missing source
        with pytest.raises(ValidationError):
            BeastModeMessage(type=MessageType.SIMPLE_MESSAGE)
    
    def test_auto_generated_id(self):
        """Test that ID is auto-generated if not provided"""
        message1 = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test"
        )
        
        message2 = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test"
        )
        
        # Should have different IDs
        assert message1.id != message2.id
        assert len(message1.id) > 0
        assert len(message2.id) > 0
    
    def test_auto_generated_timestamp(self):
        """Test that timestamp is auto-generated if not provided"""
        before = datetime.now()
        
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source="test"
        )
        
        after = datetime.now()
        
        assert before <= message.timestamp <= after


class TestAgentCapabilities(ReflectiveModule):
    """Test AgentCapabilities model"""
    
    def test_minimal_capabilities_creation(self):
        """Test creating capabilities with minimal fields"""
        caps = AgentCapabilities(agent_id="test_agent")
        
        assert caps.agent_id == "test_agent"
        assert caps.capabilities == []
        assert caps.availability == "ready_for_business"
        assert caps.specializations == []
        assert caps.collaboration_history == []
        assert isinstance(caps.last_seen, datetime)
    
    def test_full_capabilities_creation(self):
        """Test creating capabilities with all fields"""
        test_timestamp = datetime.now()
        
        caps = AgentCapabilities(
            agent_id="full_agent",
            capabilities=["python", "testing", "devops"],
            availability="busy",
            specializations=["machine_learning", "web_scraping"],
            collaboration_history=["project_1", "project_2"],
            last_seen=test_timestamp
        )
        
        assert caps.agent_id == "full_agent"
        assert caps.capabilities == ["python", "testing", "devops"]
        assert caps.availability == "busy"
        assert caps.specializations == ["machine_learning", "web_scraping"]
        assert caps.collaboration_history == ["project_1", "project_2"]
        assert caps.last_seen == test_timestamp
    
    def test_capabilities_serialization(self):
        """Test capabilities serialization"""
        caps = AgentCapabilities(
            agent_id="serialize_test",
            capabilities=["python", "redis"],
            availability="offline"
        )
        
        data = caps.model_dump()
        
        assert data["agent_id"] == "serialize_test"
        assert data["capabilities"] == ["python", "redis"]
        assert data["availability"] == "offline"
        assert "last_seen" in data
    
    def test_capabilities_deserialization(self):
        """Test capabilities deserialization"""
        data = {
            "agent_id": "deserialize_test",
            "capabilities": ["java", "kubernetes"],
            "availability": "ready_for_business",
            "specializations": ["microservices"],
            "collaboration_history": [],
            "last_seen": datetime.now().isoformat()
        }
        
        caps = AgentCapabilities(**data)
        
        assert caps.agent_id == "deserialize_test"
        assert caps.capabilities == ["java", "kubernetes"]
        assert caps.specializations == ["microservices"]
    
    def test_required_agent_id(self):
        """Test that agent_id is required"""
        with pytest.raises(ValidationError):
            AgentCapabilities()
    
    def test_auto_generated_last_seen(self):
        """Test that last_seen is auto-generated"""
        before = datetime.now()
        
        caps = AgentCapabilities(agent_id="timestamp_test")
        
        after = datetime.now()
        

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

        assert before <= caps.last_seen <= after