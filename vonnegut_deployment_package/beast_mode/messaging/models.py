#!/usr/bin/env python3
"""
Beast Mode Messaging Models

Core message models for Beast Mode agent communication.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    # Create a dummy BaseModel class for fallback
    class BaseModel:
        pass


class MessageType(str, Enum):
    """Message types for Beast Mode communication."""
    SIMPLE_MESSAGE = "simple_message"
    PROMPT_REQUEST = "prompt_request"
    PROMPT_RESPONSE = "prompt_response"
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_RESPONSE = "agent_response"
    HELP_WANTED = "help_wanted"
    HELP_RESPONSE = "help_response"
    SPORE_DELIVERY = "spore_delivery"
    SPORE_REQUEST = "spore_request"
    SPORE_SPAWN = "spore_spawn"
    TECHNICAL_EXCHANGE = "technical_exchange"
    SYSTEM_HEALTH = "system_health"


if PYDANTIC_AVAILABLE:
    class BeastModeMessage(BaseModel):
        """Beast Mode message model with Pydantic validation."""
        
        id: str = Field(default_factory=lambda: str(uuid.uuid4()))
        type: MessageType
        source: str
        target: Optional[str] = None
        payload: Dict[str, Any] = Field(default_factory=dict)
        timestamp: datetime = Field(default_factory=datetime.now)
        priority: int = Field(default=5, ge=1, le=10)
        correlation_id: Optional[str] = None

        def model_dump(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "id": self.id,
                "type": self.type.value,
                "source": self.source,
                "target": self.target,
                "payload": self.payload,
                "timestamp": self.timestamp.isoformat(),
                "priority": self.priority,
                "correlation_id": self.correlation_id,
            }

    class AgentCapabilities(BaseModel):
        """Agent capabilities model with Pydantic validation."""
        
        agent_id: str
        capabilities: List[str] = Field(default_factory=list)
        availability: str = Field(default="ready_for_business")
        specializations: List[str] = Field(default_factory=list)
        collaboration_history: List[str] = Field(default_factory=list)
        last_seen: datetime = Field(default_factory=datetime.now)

        def model_dump(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "agent_id": self.agent_id,
                "capabilities": self.capabilities,
                "availability": self.availability,
                "specializations": self.specializations,
                "collaboration_history": self.collaboration_history,
                "last_seen": self.last_seen.isoformat(),
            }

else:
    # Fallback implementations without Pydantic
    @dataclass
    class BeastModeMessage:
        """Beast Mode message model without Pydantic."""
        
        id: str = field(default_factory=lambda: str(uuid.uuid4()))
        type: MessageType = MessageType.SIMPLE_MESSAGE
        source: str = ""
        target: Optional[str] = None
        payload: Dict[str, Any] = field(default_factory=dict)
        timestamp: datetime = field(default_factory=datetime.now)
        priority: int = 5
        correlation_id: Optional[str] = None

        def model_dump(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "id": self.id,
                "type": self.type.value,
                "source": self.source,
                "target": self.target,
                "payload": self.payload,
                "timestamp": self.timestamp.isoformat(),
                "priority": self.priority,
                "correlation_id": self.correlation_id,
            }

    @dataclass
    class AgentCapabilities:
        """Agent capabilities model without Pydantic."""
        
        agent_id: str
        capabilities: List[str] = field(default_factory=list)
        availability: str = "ready_for_business"
        specializations: List[str] = field(default_factory=list)
        collaboration_history: List[str] = field(default_factory=list)
        last_seen: datetime = field(default_factory=datetime.now)

        def model_dump(self) -> Dict[str, Any]:
            """Convert to dictionary."""
            return {
                "agent_id": self.agent_id,
                "capabilities": self.capabilities,
                "availability": self.availability,
                "specializations": self.specializations,
                "collaboration_history": self.collaboration_history,
                "last_seen": self.last_seen.isoformat(),
            }


# Export all classes
__all__ = [
    "MessageType",
    "BeastModeMessage", 
    "AgentCapabilities",
]
