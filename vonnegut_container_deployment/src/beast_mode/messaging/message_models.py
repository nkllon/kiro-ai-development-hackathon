#!/usr/bin/env python3
"""
Beast Mode Message Data Models
=============================

Comprehensive message models for agent collaboration with validation,
serialization, and Beast Mode compliance.

Requirements: 6.1, 6.2
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4

try:
    from pydantic import BaseModel, Field, validator

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object


class MessageType(str, Enum):
    """Standard Beast Mode message types for agent collaboration."""

    # Discovery and presence
    AGENT_ANNOUNCEMENT = "agent_announcement"
    CAPABILITY_BROADCAST = "capability_broadcast"
    DISCOVERY_REQUEST = "discovery_request"
    DISCOVERY_RESPONSE = "discovery_response"

    # Help and collaboration
    HELP_REQUEST = "help_request"
    HELP_RESPONSE = "help_response"
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_ACCEPT = "collaboration_accept"
    COLLABORATION_DECLINE = "collaboration_decline"

    # Task execution
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"

    # Spore management
    SPORE_SHARE = "spore_share"
    SPORE_REQUEST = "spore_request"
    SPORE_VALIDATION = "spore_validation"
    SPORE_APPLICATION = "spore_application"

    # System messages
    HEARTBEAT = "heartbeat"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    SHUTDOWN_NOTICE = "shutdown_notice"

    # Office hours and scheduling
    OFFICE_HOURS_ANNOUNCEMENT = "office_hours_announcement"
    SCHEDULE_REQUEST = "schedule_request"
    SCHEDULE_CONFIRMATION = "schedule_confirmation"

    # Generic communication
    DIRECT_MESSAGE = "direct_message"
    BROADCAST_MESSAGE = "broadcast_message"
    SIMPLE_MESSAGE = "simple_message"


class AgentCapability(str, Enum):
    """Standard agent capabilities for Beast Mode collaboration."""

    # Analysis capabilities
    CODE_ANALYSIS = "code_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"

    # Development capabilities
    CODE_GENERATION = "code_generation"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION_GENERATION = "documentation_generation"
    REFACTORING = "refactoring"

    # DevOps capabilities
    DEPLOYMENT_MANAGEMENT = "deployment_management"
    MONITORING_SETUP = "monitoring_setup"
    CI_CD_CONFIGURATION = "ci_cd_configuration"
    INFRASTRUCTURE_MANAGEMENT = "infrastructure_management"

    # Quality assurance
    AUTOMATED_TESTING = "automated_testing"
    CODE_REVIEW = "code_review"
    COMPLIANCE_CHECKING = "compliance_checking"
    VULNERABILITY_SCANNING = "vulnerability_scanning"

    # Collaboration
    PROJECT_COORDINATION = "project_coordination"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    MENTORING = "mentoring"
    PROBLEM_SOLVING = "problem_solving"

    # Specialized
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_TUNING = "performance_tuning"
    DISASTER_RECOVERY = "disaster_recovery"
    DATA_ANALYSIS = "data_analysis"


if PYDANTIC_AVAILABLE:

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
        max_concurrent_tasks: int = Field(
            default=3, description="Maximum concurrent tasks"
        )
        current_load: int = Field(default=0, description="Current task load")
        trust_score: float = Field(
            default=0.5,
            ge=0.0,
            le=1.0,
            description="Trust score based on past performance",
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

        # Message identification
        message_id: str = Field(
            default_factory=lambda: str(uuid4()),
            description="Unique message identifier",
        )
        message_type: MessageType = Field(..., description="Type of message")
        timestamp: datetime = Field(
            default_factory=datetime.now, description="Message creation timestamp"
        )

        # Routing information
        sender_id: str = Field(..., description="Sender agent identifier")
        recipient_id: Optional[str] = Field(
            None, description="Target recipient (None for broadcast)"
        )
        channel: str = Field(
            default="beast_mode_general", description="Communication channel"
        )

        # Message content
        subject: Optional[str] = Field(None, description="Message subject/title")
        content: Dict[str, Any] = Field(
            default_factory=dict, description="Message payload"
        )
        attachments: List[Dict[str, Any]] = Field(
            default_factory=list, description="File attachments or references"
        )

        # Collaboration metadata
        correlation_id: Optional[str] = Field(
            None, description="Correlation ID for message chains"
        )
        reply_to: Optional[str] = Field(
            None, description="Reply to message ID"
        )
        thread_id: Optional[str] = Field(
            None, description="Thread identifier for conversation grouping"
        )

        # System metadata
        priority: str = Field(default="normal", description="Message priority")
        ttl: int = Field(default=3600, description="Time to live in seconds")
        requires_ack: bool = Field(default=False, description="Requires acknowledgment")

        # Beast Mode specific
        systematic_score: float = Field(
            default=0.5,
            ge=0.0,
            le=1.0,
            description="Systematic compliance score"
        )
        rca_metadata: Dict[str, Any] = Field(
            default_factory=dict, description="Root Cause Analysis metadata"
        )

        @validator("sender_id")
        def validate_sender_id(cls, v):
            """Validate sender ID format."""
            if not v or len(v) < 3:
                raise ValueError("Sender ID must be at least 3 characters")
            return v

        @validator("priority")
        def validate_priority(cls, v):
            """Validate priority levels."""
            valid_priorities = ["low", "normal", "high", "urgent"]
            if v not in valid_priorities:
                raise ValueError(f"Priority must be one of: {valid_priorities}")
            return v

        def to_dict(self) -> Dict[str, Any]:
            """Convert message to dictionary for serialization."""
            return {
                "message_id": self.message_id,
                "message_type": self.message_type.value,
                "timestamp": self.timestamp.isoformat(),
                "sender_id": self.sender_id,
                "recipient_id": self.recipient_id,
                "channel": self.channel,
                "subject": self.subject,
                "content": self.content,
                "attachments": self.attachments,
                "correlation_id": self.correlation_id,
                "reply_to": self.reply_to,
                "thread_id": self.thread_id,
                "priority": self.priority,
                "ttl": self.ttl,
                "requires_ack": self.requires_ack,
                "systematic_score": self.systematic_score,
                "rca_metadata": self.rca_metadata,
            }

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "BeastModeMessage":
            """Create message from dictionary."""
            # Convert string enums back to enum values
            if isinstance(data.get("message_type"), str):
                data["message_type"] = MessageType(data["message_type"])

            return cls(**data)

        def get_conversation_context(self) -> Dict[str, Any]:
            """Get conversation context for threading."""
            return {
                "thread_id": self.thread_id,
                "correlation_id": self.correlation_id,
                "sender_id": self.sender_id,
                "channel": self.channel,
                "subject": self.subject,
            }

        def is_expired(self) -> bool:
            """Check if message has expired based on TTL."""
            if self.ttl <= 0:
                return False  # No expiration

            age = (datetime.now() - self.timestamp).total_seconds()
            return age > self.ttl


else:
    # Fallback implementation without Pydantic

    @dataclass
    class AgentCapabilities:
        """Agent capabilities model without validation."""

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
        """
        Core Beast Mode message model without validation.

        Provides systematic message structure for agent collaboration.
        """

        # Message identification
        message_id: str = field(default_factory=lambda: str(uuid4()))
        message_type: MessageType = None
        timestamp: datetime = field(default_factory=datetime.now)

        # Routing information
        sender_id: str = ""
        recipient_id: Optional[str] = None
        channel: str = "beast_mode_general"

        # Message content
        subject: Optional[str] = None
        content: Dict[str, Any] = field(default_factory=dict)
        attachments: List[Dict[str, Any]] = field(default_factory=list)

        # Collaboration metadata
        correlation_id: Optional[str] = None
        reply_to: Optional[str] = None
        thread_id: Optional[str] = None

        # System metadata
        priority: str = "normal"
        ttl: int = 3600
        requires_ack: bool = False

        # Beast Mode specific
        systematic_score: float = 0.5
        rca_metadata: Dict[str, Any] = field(default_factory=dict)

        def to_dict(self) -> Dict[str, Any]:
            """Convert message to dictionary for serialization."""
            return {
                "message_id": self.message_id,
                "message_type": self.message_type.value if self.message_type else None,
                "timestamp": self.timestamp.isoformat(),
                "sender_id": self.sender_id,
                "recipient_id": self.recipient_id,
                "channel": self.channel,
                "subject": self.subject,
                "content": self.content,
                "attachments": self.attachments,
                "correlation_id": self.correlation_id,
                "reply_to": self.reply_to,
                "thread_id": self.thread_id,
                "priority": self.priority,
                "ttl": self.ttl,
                "requires_ack": self.requires_ack,
                "systematic_score": self.systematic_score,
                "rca_metadata": self.rca_metadata,
            }

        @classmethod
        def from_dict(cls, data: Dict[str, Any]) -> "BeastModeMessage":
            """Create message from dictionary."""
            # Convert string enums back to enum values
            if isinstance(data.get("message_type"), str):
                data["message_type"] = MessageType(data["message_type"])

            return cls(**data)


# Export all classes
__all__ = [
    "MessageType",
    "AgentCapability",
    "AgentCapabilities",
    "BeastModeMessage",
]
