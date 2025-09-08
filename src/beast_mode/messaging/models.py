"""
Beast Mode Message Data Models

Defines the core data structures for agent communication.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class MessageType(str, Enum):
    """Standardized message types for agent communication"""
    SIMPLE_MESSAGE = "simple_message"           # Basic text communication
    PROMPT_REQUEST = "prompt_request"           # Request for processing
    PROMPT_RESPONSE = "prompt_response"         # Response to request
    AGENT_DISCOVERY = "agent_discovery"         # Presence announcement
    AGENT_RESPONSE = "agent_response"           # Discovery response
    HELP_WANTED = "help_wanted"                 # Request for assistance
    HELP_RESPONSE = "help_response"             # Offer to help
    SPORE_DELIVERY = "spore_delivery"           # Spore sharing
    SPORE_REQUEST = "spore_request"             # Request for specific spore
    SPORE_SPAWN = "spore_spawn"                 # Spore spawn request
    TECHNICAL_EXCHANGE = "technical_exchange"   # Setup/debugging info
    SYSTEM_HEALTH = "system_health"             # Health monitoring
    OFFICE_HOURS_ANNOUNCEMENT = "office_hours_announcement"  # Office hours scheduling
    COLLABORATION_REQUEST = "collaboration_request"          # Request for collaboration
    COLLABORATION_RESPONSE = "collaboration_response"        # Response to collaboration request
    COLLABORATION_START = "collaboration_start"              # Start collaboration session
    COLLABORATION_END = "collaboration_end"                  # End collaboration session
    COLLABORATION_UPDATE = "collaboration_update"            # Update collaboration session


class BeastModeMessage(BaseModel):
    """Core message structure for Beast Mode agent communication"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    source: str
    target: Optional[str] = None  # None for broadcast messages
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = Field(default=5, ge=1, le=10)  # 1=highest, 10=lowest
    correlation_id: Optional[str] = None  # For request/response tracking
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class AgentCapabilities(BaseModel):
    """Agent capability and metadata information"""
    
    agent_id: str
    capabilities: List[str] = Field(default_factory=list)
    availability: str = "ready_for_business"  # ready_for_business, busy, offline
    specializations: List[str] = Field(default_factory=list)
    collaboration_history: List[str] = Field(default_factory=list)
    last_seen: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )