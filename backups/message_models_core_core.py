"""
Message Models Core Core

This module was extracted from message_models_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4
from pydantic import BaseModel, Field, validator


class MessageType(str, Enum):
    """Standard Beast Mode message types for agent collaboration."""

    AGENT_ANNOUNCEMENT = "agent_announcement"
    CAPABILITY_BROADCAST = "capability_broadcast"
    DISCOVERY_REQUEST = "discovery_request"
    DISCOVERY_RESPONSE = "discovery_response"
    HELP_REQUEST = "help_request"
    HELP_RESPONSE = "help_response"
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_ACCEPT = "collaboration_accept"
    COLLABORATION_DECLINE = "collaboration_decline"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"
    SPORE_SHARE = "spore_share"
    SPORE_REQUEST = "spore_request"
    SPORE_VALIDATION = "spore_validation"
    SPORE_APPLICATION = "spore_application"
    HEARTBEAT = "heartbeat"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    SHUTDOWN_NOTICE = "shutdown_notice"
    OFFICE_HOURS_ANNOUNCEMENT = "office_hours_announcement"
    SCHEDULE_REQUEST = "schedule_request"
    SCHEDULE_CONFIRMATION = "schedule_confirmation"
    DIRECT_MESSAGE = "direct_message"
    BROADCAST_MESSAGE = "broadcast_message"


class AgentCapability(str, Enum):
    """Standard agent capabilities for Beast Mode collaboration."""

    CODE_ANALYSIS = "code_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    CODE_GENERATION = "code_generation"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION_GENERATION = "documentation_generation"
    REFACTORING = "refactoring"
    DEPLOYMENT_MANAGEMENT = "deployment_management"
    MONITORING_SETUP = "monitoring_setup"
    CI_CD_CONFIGURATION = "ci_cd_configuration"
    INFRASTRUCTURE_MANAGEMENT = "infrastructure_management"
    AUTOMATED_TESTING = "automated_testing"
    CODE_REVIEW = "code_review"
    COMPLIANCE_CHECKING = "compliance_checking"
    VULNERABILITY_SCANNING = "vulnerability_scanning"
    PROJECT_COORDINATION = "project_coordination"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    MENTORING = "mentoring"
    PROBLEM_SOLVING = "problem_solving"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_TUNING = "performance_tuning"
    DISASTER_RECOVERY = "disaster_recovery"
    DATA_ANALYSIS = "data_analysis"


class AgentCapabilities(BaseModel):
    """Agent capabilities model with validation."""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_name: str = Field(..., description="Human-readable agent name")
    capabilities: List[AgentCapability] = Field(
        default_factory=list, description="List of agent capabilities"
    )
    specializations: List[str] = Field(
        default_factory=list, description="Specialized skills or domains"
    )
    availability: str = Field(
        default="available", description="Current availability status"
    )
    office_hours: Optional[Dict[str, str]] = Field(
        None, description="Office hours schedule"
    )
    max_concurrent_tasks: int = Field(default=3, description="Maximum concurrent tasks")
    current_load: int = Field(default=0, description="Current task load")
    trust_score: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Trust score based on past performance"
    )
    last_seen: datetime = Field(
        default_factory=datetime.now, description="Last activity timestamp"
    )

    @validator("capabilities")
    def validate_capabilities(cls, v):
        """Validate capabilities list."""
        if not v:
            raise ValueError("Agent must have at least one capability")
        return v

    @validator("agent_id")
    def validate_agent_id(cls, v):
        """Validate agent ID format."""
        if not v or len(v) < 3:
            raise ValueError("Agent ID must be at least 3 characters")
        return v


class BeastModeMessage(BaseModel):
    """
    Core Beast Mode message model with comprehensive validation.

    Provides systematic message structure for agent collaboration
    with proper serialization and validation.
    """

    message_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique message identifier"
    )
    message_type: MessageType = Field(..., description="Type of message")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Message creation timestamp"
    )
    sender_id: str = Field(..., description="Sender agent identifier")
    recipient_id: Optional[str] = Field(
        None, description="Target recipient (None for broadcast)"
    )
    channel: str = Field(
        default="beast_mode_general", description="Communication channel"
    )
    subject: Optional[str] = Field(None, description="Message subject/title")
    content: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    attachments: List[Dict[str, Any]] = Field(
        default_factory=list, description="File attachments or references"
    )
    correlation_id: Optional[str] = Field(
        None, description="Correlation ID for message chains"
    )
    reply_to: Optional[str] = Field(None, description="Message ID this is replying to")
    priority: str = Field(default="normal", description="Message priority level")
    expires_at: Optional[datetime] = Field(None, description="Message expiration time")
    requires_response: bool = Field(
        default=False, description="Whether response is required"
    )
    capabilities_required: List[AgentCapability] = Field(
        default_factory=list, description="Required capabilities for handling"
    )
    spore_references: List[str] = Field(
        default_factory=list, description="Referenced spore IDs"
    )

    @validator("priority")
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return v

    @validator("content")
    def validate_content(cls, v):
        """Validate message content is serializable."""
        try:
            json.dumps(v)
            return v
        except (TypeError, ValueError) as e:
            raise ValueError(f"Message content must be JSON serializable: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        data = self.dict()
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Enum):
                data[key] = value.value
            elif isinstance(value, list) and value and hasattr(value[0], "value"):
                data[key] = [
                    item.value if hasattr(item, "value") else item for item in value
                ]
        return data

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return self.json()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BeastModeMessage":
        """Create message from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "BeastModeMessage":
        """Create message from JSON string."""
        return cls.parse_raw(json_str)

    def create_reply(
        self,
        sender_id: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.DIRECT_MESSAGE,
    ) -> "BeastModeMessage":
        """Create a reply message to this message."""
        return BeastModeMessage(
            message_type=message_type,
            sender_id=sender_id,
            recipient_id=self.sender_id,
            channel=self.channel,
            content=content,
            correlation_id=self.correlation_id or self.message_id,
            reply_to=self.message_id,
        )

    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def get_age_seconds(self) -> float:
        """Get message age in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()


@dataclass
class AgentCapabilities:
    """Fallback agent capabilities without Pydantic validation."""

    agent_id: str
    agent_name: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    availability: str = "available"
    office_hours: Optional[Dict[str, str]] = None
    max_concurrent_tasks: int = 3
    current_load: int = 0
    trust_score: float = 0.5
    last_seen: datetime = field(default_factory=datetime.now)


@dataclass
class BeastModeMessage:
    """Fallback message model without Pydantic validation."""

    message_type: MessageType
    sender_id: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    recipient_id: Optional[str] = None
    channel: str = "beast_mode_general"
    subject: Optional[str] = None
    content: Dict[str, Any] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    priority: str = "normal"
    expires_at: Optional[datetime] = None
    requires_response: bool = False
    capabilities_required: List[AgentCapability] = field(default_factory=list)
    spore_references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list) and value and isinstance(value[0], Enum):
                result[key] = [item.value for item in value]
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


def create_agent_announcement(
    agent_id: str, capabilities: AgentCapabilities
) -> BeastModeMessage:
    """Create an agent announcement message."""
    if hasattr(capabilities, "model_dump"):
        caps_dict = capabilities.model_dump()
    elif hasattr(capabilities, "to_dict"):
        caps_dict = capabilities.to_dict()
    else:
        caps_dict = capabilities.__dict__.copy()

    def make_serializable(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return obj

    caps_dict = make_serializable(caps_dict)
    return BeastModeMessage(
        message_type=MessageType.AGENT_ANNOUNCEMENT,
        sender_id=agent_id,
        subject=f"Agent {capabilities.agent_name} is online",
        content={
            "capabilities": caps_dict,
            "announcement_time": datetime.now().isoformat(),
        },
    )


def create_help_request(
    sender_id: str,
    required_capabilities: List[AgentCapability],
    description: str,
    priority: str = "normal",
) -> BeastModeMessage:
    """Create a help request message."""
    return BeastModeMessage(
        message_type=MessageType.HELP_REQUEST,
        sender_id=sender_id,
        subject="Help Request",
        content={
            "description": description,
            "required_capabilities": [cap.value for cap in required_capabilities],
            "deadline": None,
        },
        capabilities_required=required_capabilities,
        priority=priority,
        requires_response=True,
    )


def create_spore_share(
    sender_id: str, spore_id: str, spore_data: Dict[str, Any]
) -> BeastModeMessage:
    """Create a spore sharing message."""
    return BeastModeMessage(
        message_type=MessageType.SPORE_SHARE,
        sender_id=sender_id,
        subject=f"Sharing spore: {spore_id}",
        content={
            "spore_id": spore_id,
            "spore_data": spore_data,
            "share_time": datetime.now().isoformat(),
        },
        spore_references=[spore_id],
    )


def create_heartbeat(agent_id: str, status_info: Dict[str, Any]) -> BeastModeMessage:
    """Create a heartbeat message."""
    return BeastModeMessage(
        message_type=MessageType.HEARTBEAT,
        sender_id=agent_id,
        content={"status": status_info, "heartbeat_time": datetime.now().isoformat()},
        expires_at=datetime.fromtimestamp(time.time() + 300),
    )


def filter_messages_by_capability(
    messages: List[BeastModeMessage], agent_capabilities: List[AgentCapability]
) -> List[BeastModeMessage]:
    """Filter messages that match agent capabilities."""
    filtered = []
    for msg in messages:
        if not msg.capabilities_required:
            filtered.append(msg)
        elif any((cap in agent_capabilities for cap in msg.capabilities_required)):
            filtered.append(msg)
    return filtered


def make_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return obj


def to_dict(self) -> Dict[str, Any]:
    """Convert message to dictionary for serialization."""
    data = self.dict()
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, Enum):
            data[key] = value.value
        elif isinstance(value, list) and value and hasattr(value[0], "value"):
            data[key] = [
                item.value if hasattr(item, "value") else item for item in value
            ]
    return data


def to_json(self) -> str:
    """Convert message to JSON string."""
    return self.json()


@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "BeastModeMessage":
    """Create message from dictionary."""
    return cls(**data)


@classmethod
def from_json(cls, json_str: str) -> "BeastModeMessage":
    """Create message from JSON string."""
    return cls.parse_raw(json_str)


def create_reply(
    self,
    sender_id: str,
    content: Dict[str, Any],
    message_type: MessageType = MessageType.DIRECT_MESSAGE,
) -> "BeastModeMessage":
    """Create a reply message to this message."""
    return BeastModeMessage(
        message_type=message_type,
        sender_id=sender_id,
        recipient_id=self.sender_id,
        channel=self.channel,
        content=content,
        correlation_id=self.correlation_id or self.message_id,
        reply_to=self.message_id,
    )


def is_expired(self) -> bool:
    """Check if message has expired."""
    if not self.expires_at:
        return False
    return datetime.now() > self.expires_at


def get_age_seconds(self) -> float:
    """Get message age in seconds."""
    return (datetime.now() - self.timestamp).total_seconds()


def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
    result = {}
    for key, value in self.__dict__.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Enum):
            result[key] = value.value
        elif isinstance(value, list) and value and isinstance(value[0], Enum):
            result[key] = [item.value for item in value]
        else:
            result[key] = value
    return result


def to_json(self) -> str:
    """Convert to JSON string."""
    return json.dumps(self.to_dict())


def to_dict(self) -> Dict[str, Any]:
    """Convert message to dictionary for serialization."""
    data = self.dict()
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, Enum):
            data[key] = value.value
        elif isinstance(value, list) and value and hasattr(value[0], "value"):
            data[key] = [
                item.value if hasattr(item, "value") else item for item in value
            ]
    return data


def to_json(self) -> str:
    """Convert message to JSON string."""
    return self.json()


@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "BeastModeMessage":
    """Create message from dictionary."""
    return cls(**data)


@classmethod
def from_json(cls, json_str: str) -> "BeastModeMessage":
    """Create message from JSON string."""
    return cls.parse_raw(json_str)


def create_reply(
    self,
    sender_id: str,
    content: Dict[str, Any],
    message_type: MessageType = MessageType.DIRECT_MESSAGE,
) -> "BeastModeMessage":
    """Create a reply message to this message."""
    return BeastModeMessage(
        message_type=message_type,
        sender_id=sender_id,
        recipient_id=self.sender_id,
        channel=self.channel,
        content=content,
        correlation_id=self.correlation_id or self.message_id,
        reply_to=self.message_id,
    )


def is_expired(self) -> bool:
    """Check if message has expired."""
    if not self.expires_at:
        return False
    return datetime.now() > self.expires_at


def get_age_seconds(self) -> float:
    """Get message age in seconds."""
    return (datetime.now() - self.timestamp).total_seconds()


def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary."""
    result = {}
    for key, value in self.__dict__.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Enum):
            result[key] = value.value
        elif isinstance(value, list) and value and isinstance(value[0], Enum):
            result[key] = [item.value for item in value]
        else:
            result[key] = value
    return result


def to_json(self) -> str:
    """Convert to JSON string."""
    return json.dumps(self.to_dict())


def make_serializable(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return obj
