"""
Help System Core Core

This module was extracted from help_system_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .agent_registry import AgentRegistry, DiscoveredAgent


class HelpUrgency(str, Enum):
    """Help request urgency levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CollaborationStatus(str, Enum):
    """Status of collaboration sessions"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class HelpRequest:
    """Information about a help request"""

    request_id: str
    requester_id: str
    required_capabilities: List[str]
    description: str
    urgency: HelpUrgency = HelpUrgency.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    max_helpers: int = 1
    context: Dict[str, Any] = field(default_factory=dict)
    responses: List["HelpResponse"] = field(default_factory=list)
    accepted_helpers: List[str] = field(default_factory=list)
    status: CollaborationStatus = CollaborationStatus.PENDING


@dataclass
class HelpResponse:
    """Information about a help response"""

    response_id: str
    responder_id: str
    request_id: str
    matching_capabilities: List[str]
    confidence_score: float
    availability: str
    estimated_time: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationSession:
    """Active collaboration session tracking"""

    session_id: str
    request_id: str
    requester_id: str
    helper_id: str
    capabilities_used: List[str]
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    status: CollaborationStatus = CollaborationStatus.IN_PROGRESS
    messages_exchanged: int = 0
    success_metrics: Dict[str, Any] = field(default_factory=dict)


class CapabilityMatcher:
    """Algorithm for matching help requests with agent capabilities"""

    def __init__(self):
        self.capability_weights = {
            "python": 1.0,
            "javascript": 1.0,
            "java": 1.0,
            "go": 1.0,
            "docker": 0.9,
            "kubernetes": 0.9,
            "terraform": 0.9,
            "gcp": 0.8,
            "aws": 0.8,
            "machine_learning": 1.2,
            "data_analysis": 1.1,
            "security": 1.2,
            "performance_optimization": 1.1,
            "testing": 0.8,
            "debugging": 0.8,
            "code_review": 0.7,
            "documentation": 0.6,
        }

    def calculate_match_score(
        self,
        required_capabilities: List[str],
        agent_capabilities: List[str],
        agent_collaboration_score: float = 0.0,
    ) -> float:
        """
        Calculate how well an agent matches a help request.

        Args:
            required_capabilities: Capabilities needed for the request
            agent_capabilities: Agent's available capabilities
            agent_collaboration_score: Agent's historical collaboration success

        Returns:
            float: Match score from 0.0 to 1.0
        """
        if not required_capabilities:
            return 0.0
        required_set = set(required_capabilities)
        agent_set = set(agent_capabilities)
        direct_matches = required_set.intersection(agent_set)
        if not direct_matches:
            return 0.0
        total_weight = 0.0
        matched_weight = 0.0
        for capability in required_capabilities:
            weight = self.capability_weights.get(capability, 0.5)
            total_weight += weight
            if capability in agent_capabilities:
                matched_weight += weight
        if total_weight > 0:
            avg_weight = total_weight / len(required_capabilities)
            base_score = matched_weight / total_weight * avg_weight
        else:
            base_score = 0.0
        extra_capabilities = agent_set - required_set
        extra_bonus = min(0.2, len(extra_capabilities) * 0.05)
        collaboration_bonus = min(0.3, agent_collaboration_score * 0.1)
        final_score = base_score + extra_bonus + collaboration_bonus
        return final_score

    def find_best_matches(
        self,
        help_request: HelpRequest,
        available_agents: List[DiscoveredAgent],
        min_score: float = 0.3,
    ) -> List[Tuple[DiscoveredAgent, float]]:
        """
        Find the best agent matches for a help request.

        Args:
            help_request: The help request to match
            available_agents: List of available agents
            min_score: Minimum match score to include

        Returns:
            List of (agent, score) tuples sorted by score descending
        """
        matches = []
        for agent in available_agents:
            if agent.capabilities.availability not in ["ready_for_business", "busy"]:
                continue
            score = self.calculate_match_score(
                help_request.required_capabilities,
                agent.capabilities.capabilities,
                agent.collaboration_score,
            )
            if score >= min_score:
                matches.append((agent, score))
        matches.sort(
            key=lambda x: (x[1], x[0].collaboration_score, -x[0].last_seen.timestamp()),
            reverse=True,
        )
        return matches


class HelpWantedSystem:
    """Complete help wanted system for agent collaboration"""

    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self.capability_matcher = CapabilityMatcher()
        self.active_requests: Dict[str, HelpRequest] = {}
        self.collaboration_sessions: Dict[str, CollaborationSession] = {}
        self.default_request_timeout = timedelta(hours=1)
        self.max_responses_per_request = 10
        self.auto_accept_threshold = 1.5
        self.stats = {
            "requests_created": 0,
            "responses_received": 0,
            "collaborations_started": 0,
            "collaborations_completed": 0,
            "collaborations_failed": 0,
            "average_response_time": 0.0,
            "average_collaboration_duration": 0.0,
            "capability_success_rates": {},
        }

    def create_help_request(
        self,
        requester_id: str,
        required_capabilities: List[str],
        description: str,
        urgency: HelpUrgency = HelpUrgency.NORMAL,
        max_helpers: int = 1,
        timeout_hours: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> HelpRequest:
        """
        Create a new help request.

        Args:
            requester_id: ID of the agent requesting help
            required_capabilities: List of required capabilities
            description: Description of what help is needed
            urgency: Urgency level of the request
            max_helpers: Maximum number of helpers needed
            timeout_hours: Hours until request expires (None for default)
            context: Additional context information

        Returns:
            HelpRequest: The created help request
        """
        request_id = str(uuid.uuid4())
        expires_at = None
        if timeout_hours is not None:
            expires_at = datetime.now() + timedelta(hours=timeout_hours)
        else:
            expires_at = datetime.now() + self.default_request_timeout
        help_request = HelpRequest(
            request_id=request_id,
            requester_id=requester_id,
            required_capabilities=required_capabilities,
            description=description,
            urgency=urgency,
            expires_at=expires_at,
            max_helpers=max_helpers,
            context=context or {},
        )
        self.active_requests[request_id] = help_request
        self.stats["requests_created"] += 1
        logger.info(
            f"Created help request {request_id} for capabilities: {required_capabilities}"
        )
        return help_request

    def create_help_request_message(
        self, help_request: HelpRequest
    ) -> BeastModeMessage:
        """
        Create a help wanted message for broadcasting.

        Args:
            help_request: The help request to broadcast

        Returns:
            BeastModeMessage: Message ready for broadcasting
        """
        priority_map = {
            HelpUrgency.LOW: 7,
            HelpUrgency.NORMAL: 5,
            HelpUrgency.HIGH: 3,
            HelpUrgency.CRITICAL: 1,
        }
        message = BeastModeMessage(
            type=MessageType.HELP_WANTED,
            source=help_request.requester_id,
            target=None,
            payload={
                "request_id": help_request.request_id,
                "required_capabilities": help_request.required_capabilities,
                "description": help_request.description,
                "urgency": help_request.urgency,
                "max_helpers": help_request.max_helpers,
                "expires_at": (
                    help_request.expires_at.isoformat()
                    if help_request.expires_at
                    else None
                ),
                "context": help_request.context,
            },
            priority=priority_map[help_request.urgency],
        )
        return message

    def process_help_request(
        self, message: BeastModeMessage, responder_id: str
    ) -> Optional[HelpResponse]:
        """
        Process an incoming help request and generate a response if capable.

        Args:
            message: The help wanted message
            responder_id: ID of the potential responder

        Returns:
            Optional[HelpResponse]: Response if agent can help, None otherwise
        """
        if message.type != MessageType.HELP_WANTED:
            return None
        request_id = message.payload.get("request_id")
        required_capabilities = message.payload.get("required_capabilities", [])
        if not request_id or not required_capabilities:
            logger.warning(f"Invalid help request message from {message.source}")
            return None
        responder_agent = self.agent_registry.get_agent(responder_id)
        if not responder_agent:
            logger.warning(f"Responder {responder_id} not found in registry")
            return None
        match_score = self.capability_matcher.calculate_match_score(
            required_capabilities,
            responder_agent.capabilities.capabilities,
            responder_agent.collaboration_score,
        )
        if match_score < 0.3:
            logger.debug(
                f"Match score {match_score} too low for {responder_id} to help with {request_id}"
            )
            return None
        matching_capabilities = [
            cap
            for cap in required_capabilities
            if cap in responder_agent.capabilities.capabilities
        ]
        response = HelpResponse(
            response_id=str(uuid.uuid4()),
            responder_id=responder_id,
            request_id=request_id,
            matching_capabilities=matching_capabilities,
            confidence_score=match_score,
            availability=responder_agent.capabilities.availability,
            message=f"I can help with {', '.join(matching_capabilities)} (confidence: {match_score:.2f})",
        )
        self.stats["responses_received"] += 1
        logger.info(
            f"Generated help response from {responder_id} for {request_id} (score: {match_score:.2f})"
        )
        return response

    def create_help_response_message(
        self, help_response: HelpResponse
    ) -> BeastModeMessage:
        """
        Create a help response message.

        Args:
            help_response: The help response to send

        Returns:
            BeastModeMessage: Message ready for sending
        """
        help_request = self.active_requests.get(help_response.request_id)
        target = help_request.requester_id if help_request else None
        message = BeastModeMessage(
            type=MessageType.HELP_RESPONSE,
            source=help_response.responder_id,
            target=target,
            payload={
                "response_id": help_response.response_id,
                "request_id": help_response.request_id,
                "matching_capabilities": help_response.matching_capabilities,
                "confidence_score": help_response.confidence_score,
                "availability": help_response.availability,
                "estimated_time": help_response.estimated_time,
                "message": help_response.message,
            },
            priority=4,
            correlation_id=help_response.request_id,
        )
        return message

    def process_help_response(self, message: BeastModeMessage) -> bool:
        """
        Process an incoming help response.

        Args:
            message: The help response message

        Returns:
            bool: True if response was processed successfully
        """
        if message.type != MessageType.HELP_RESPONSE:
            return False
        request_id = message.payload.get("request_id")
        if not request_id or request_id not in self.active_requests:
            logger.warning(f"Help response for unknown request {request_id}")
            return False
        help_request = self.active_requests[request_id]
        if help_request.status != CollaborationStatus.PENDING:
            logger.debug(f"Help request {request_id} no longer accepting responses")
            return False
        if len(help_request.responses) >= self.max_responses_per_request:
            logger.debug(f"Help request {request_id} has reached maximum responses")
            return False
        help_response = HelpResponse(
            response_id=message.payload.get("response_id", str(uuid.uuid4())),
            responder_id=message.source,
            request_id=request_id,
            matching_capabilities=message.payload.get("matching_capabilities", []),
            confidence_score=message.payload.get("confidence_score", 0.0),
            availability=message.payload.get("availability", "unknown"),
            estimated_time=message.payload.get("estimated_time"),
            message=message.payload.get("message"),
        )
        help_request.responses.append(help_response)
        if (
            help_response.confidence_score >= self.auto_accept_threshold
            and len(help_request.accepted_helpers) < help_request.max_helpers
        ):
            self.accept_help_response(request_id, help_response.response_id)
        logger.info(f"Processed help response from {message.source} for {request_id}")
        return True

    def accept_help_response(
        self, request_id: str, response_id: str
    ) -> Optional[CollaborationSession]:
        """
        Accept a help response and start a collaboration session.

        Args:
            request_id: ID of the help request
            response_id: ID of the response to accept

        Returns:
            Optional[CollaborationSession]: Started session if successful
        """
        if request_id not in self.active_requests:
            return None
        help_request = self.active_requests[request_id]
        help_response = None
        for response in help_request.responses:
            if response.response_id == response_id:
                help_response = response
                break
        if not help_response:
            logger.warning(
                f"Help response {response_id} not found for request {request_id}"
            )
            return None
        if len(help_request.accepted_helpers) >= help_request.max_helpers:
            logger.warning(f"Help request {request_id} already has maximum helpers")
            return None
        help_request.accepted_helpers.append(help_response.responder_id)
        session = CollaborationSession(
            session_id=str(uuid.uuid4()),
            request_id=request_id,
            requester_id=help_request.requester_id,
            helper_id=help_response.responder_id,
            capabilities_used=help_response.matching_capabilities,
        )
        self.collaboration_sessions[session.session_id] = session
        if len(help_request.accepted_helpers) >= help_request.max_helpers:
            help_request.status = CollaborationStatus.ACCEPTED
        self.agent_registry.update_collaboration_score(help_response.responder_id, 0.1)
        self.stats["collaborations_started"] += 1
        logger.info(
            f"Started collaboration session {session.session_id} between {help_request.requester_id} and {help_response.responder_id}"
        )
        return session

    def complete_collaboration(
        self, session_id: str, success: bool, metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark a collaboration session as completed.

        Args:
            session_id: ID of the collaboration session
            success: Whether the collaboration was successful
            metrics: Optional success metrics

        Returns:
            bool: True if session was updated successfully
        """
        if session_id not in self.collaboration_sessions:
            return False
        session = self.collaboration_sessions[session_id]
        session.status = (
            CollaborationStatus.COMPLETED if success else CollaborationStatus.FAILED
        )
        session.success_metrics = metrics or {}
        score_delta = 1.0 if success else -0.5
        self.agent_registry.update_collaboration_score(session.helper_id, score_delta)
        for capability in session.capabilities_used:
            if capability not in self.stats["capability_success_rates"]:
                self.stats["capability_success_rates"][capability] = {
                    "successes": 0,
                    "total": 0,
                }
            self.stats["capability_success_rates"][capability]["total"] += 1
            if success:
                self.stats["capability_success_rates"][capability]["successes"] += 1
        if success:
            self.stats["collaborations_completed"] += 1
        else:
            self.stats["collaborations_failed"] += 1
        duration = (datetime.now() - session.started_at).total_seconds()
        current_avg = self.stats["average_collaboration_duration"]
        total_collaborations = (
            self.stats["collaborations_completed"] + self.stats["collaborations_failed"]
        )
        if total_collaborations > 0:
            self.stats["average_collaboration_duration"] = (
                current_avg * (total_collaborations - 1) + duration
            ) / total_collaborations
        logger.info(
            f"Completed collaboration session {session_id} (success: {success})"
        )
        return True

    def cleanup_expired_requests(self) -> int:
        """
        Clean up expired help requests.

        Returns:
            int: Number of requests cleaned up
        """
        now = datetime.now()
        expired_requests = []
        for request_id, help_request in self.active_requests.items():
            if help_request.expires_at and now > help_request.expires_at:
                expired_requests.append(request_id)
        for request_id in expired_requests:
            del self.active_requests[request_id]
            logger.info(f"Cleaned up expired help request {request_id}")
        return len(expired_requests)

    def get_help_system_stats(self) -> Dict[str, Any]:
        """Get help system statistics"""
        return {
            **self.stats,
            "active_requests": len(self.active_requests),
            "active_collaborations": len(
                [
                    s
                    for s in self.collaboration_sessions.values()
                    if s.status == CollaborationStatus.IN_PROGRESS
                ]
            ),
            "total_collaborations": len(self.collaboration_sessions),
        }

    def get_active_requests(self) -> List[HelpRequest]:
        """Get all active help requests"""
        return list(self.active_requests.values())

    def get_collaboration_sessions(self) -> List[CollaborationSession]:
        """Get all collaboration sessions"""
        return list(self.collaboration_sessions.values())

    def find_matching_agents(
        self, required_capabilities: List[str]
    ) -> List[Tuple[DiscoveredAgent, float]]:
        """
        Find agents that match the required capabilities.

        Args:
            required_capabilities: List of required capabilities

        Returns:
            List of (agent, match_score) tuples
        """
        available_agents = self.agent_registry.get_active_agents()
        temp_request = HelpRequest(
            request_id="temp",
            requester_id="temp",
            required_capabilities=required_capabilities,
            description="Temporary request for matching",
        )
        return self.capability_matcher.find_best_matches(temp_request, available_agents)


def __init__(self):
    self.capability_weights = {
        "python": 1.0,
        "javascript": 1.0,
        "java": 1.0,
        "go": 1.0,
        "docker": 0.9,
        "kubernetes": 0.9,
        "terraform": 0.9,
        "gcp": 0.8,
        "aws": 0.8,
        "machine_learning": 1.2,
        "data_analysis": 1.1,
        "security": 1.2,
        "performance_optimization": 1.1,
        "testing": 0.8,
        "debugging": 0.8,
        "code_review": 0.7,
        "documentation": 0.6,
    }


def calculate_match_score(
    self,
    required_capabilities: List[str],
    agent_capabilities: List[str],
    agent_collaboration_score: float = 0.0,
) -> float:
    """
    Calculate how well an agent matches a help request.

    Args:
        required_capabilities: Capabilities needed for the request
        agent_capabilities: Agent's available capabilities
        agent_collaboration_score: Agent's historical collaboration success

    Returns:
        float: Match score from 0.0 to 1.0
    """
    if not required_capabilities:
        return 0.0
    required_set = set(required_capabilities)
    agent_set = set(agent_capabilities)
    direct_matches = required_set.intersection(agent_set)
    if not direct_matches:
        return 0.0
    total_weight = 0.0
    matched_weight = 0.0
    for capability in required_capabilities:
        weight = self.capability_weights.get(capability, 0.5)
        total_weight += weight
        if capability in agent_capabilities:
            matched_weight += weight
    if total_weight > 0:
        avg_weight = total_weight / len(required_capabilities)
        base_score = matched_weight / total_weight * avg_weight
    else:
        base_score = 0.0
    extra_capabilities = agent_set - required_set
    extra_bonus = min(0.2, len(extra_capabilities) * 0.05)
    collaboration_bonus = min(0.3, agent_collaboration_score * 0.1)
    final_score = base_score + extra_bonus + collaboration_bonus
    return final_score


def find_best_matches(
    self,
    help_request: HelpRequest,
    available_agents: List[DiscoveredAgent],
    min_score: float = 0.3,
) -> List[Tuple[DiscoveredAgent, float]]:
    """
    Find the best agent matches for a help request.

    Args:
        help_request: The help request to match
        available_agents: List of available agents
        min_score: Minimum match score to include

    Returns:
        List of (agent, score) tuples sorted by score descending
    """
    matches = []
    for agent in available_agents:
        if agent.capabilities.availability not in ["ready_for_business", "busy"]:
            continue
        score = self.calculate_match_score(
            help_request.required_capabilities,
            agent.capabilities.capabilities,
            agent.collaboration_score,
        )
        if score >= min_score:
            matches.append((agent, score))
    matches.sort(
        key=lambda x: (x[1], x[0].collaboration_score, -x[0].last_seen.timestamp()),
        reverse=True,
    )
    return matches


def __init__(self, agent_registry: AgentRegistry):
    self.agent_registry = agent_registry
    self.capability_matcher = CapabilityMatcher()
    self.active_requests: Dict[str, HelpRequest] = {}
    self.collaboration_sessions: Dict[str, CollaborationSession] = {}
    self.default_request_timeout = timedelta(hours=1)
    self.max_responses_per_request = 10
    self.auto_accept_threshold = 1.5
    self.stats = {
        "requests_created": 0,
        "responses_received": 0,
        "collaborations_started": 0,
        "collaborations_completed": 0,
        "collaborations_failed": 0,
        "average_response_time": 0.0,
        "average_collaboration_duration": 0.0,
        "capability_success_rates": {},
    }


def create_help_request(
    self,
    requester_id: str,
    required_capabilities: List[str],
    description: str,
    urgency: HelpUrgency = HelpUrgency.NORMAL,
    max_helpers: int = 1,
    timeout_hours: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None,
) -> HelpRequest:
    """
    Create a new help request.

    Args:
        requester_id: ID of the agent requesting help
        required_capabilities: List of required capabilities
        description: Description of what help is needed
        urgency: Urgency level of the request
        max_helpers: Maximum number of helpers needed
        timeout_hours: Hours until request expires (None for default)
        context: Additional context information

    Returns:
        HelpRequest: The created help request
    """
    request_id = str(uuid.uuid4())
    expires_at = None
    if timeout_hours is not None:
        expires_at = datetime.now() + timedelta(hours=timeout_hours)
    else:
        expires_at = datetime.now() + self.default_request_timeout
    help_request = HelpRequest(
        request_id=request_id,
        requester_id=requester_id,
        required_capabilities=required_capabilities,
        description=description,
        urgency=urgency,
        expires_at=expires_at,
        max_helpers=max_helpers,
        context=context or {},
    )
    self.active_requests[request_id] = help_request
    self.stats["requests_created"] += 1
    logger.info(
        f"Created help request {request_id} for capabilities: {required_capabilities}"
    )
    return help_request


def create_help_request_message(self, help_request: HelpRequest) -> BeastModeMessage:
    """
    Create a help wanted message for broadcasting.

    Args:
        help_request: The help request to broadcast

    Returns:
        BeastModeMessage: Message ready for broadcasting
    """
    priority_map = {
        HelpUrgency.LOW: 7,
        HelpUrgency.NORMAL: 5,
        HelpUrgency.HIGH: 3,
        HelpUrgency.CRITICAL: 1,
    }
    message = BeastModeMessage(
        type=MessageType.HELP_WANTED,
        source=help_request.requester_id,
        target=None,
        payload={
            "request_id": help_request.request_id,
            "required_capabilities": help_request.required_capabilities,
            "description": help_request.description,
            "urgency": help_request.urgency,
            "max_helpers": help_request.max_helpers,
            "expires_at": (
                help_request.expires_at.isoformat() if help_request.expires_at else None
            ),
            "context": help_request.context,
        },
        priority=priority_map[help_request.urgency],
    )
    return message


def create_help_response_message(self, help_response: HelpResponse) -> BeastModeMessage:
    """
    Create a help response message.

    Args:
        help_response: The help response to send

    Returns:
        BeastModeMessage: Message ready for sending
    """
    help_request = self.active_requests.get(help_response.request_id)
    target = help_request.requester_id if help_request else None
    message = BeastModeMessage(
        type=MessageType.HELP_RESPONSE,
        source=help_response.responder_id,
        target=target,
        payload={
            "response_id": help_response.response_id,
            "request_id": help_response.request_id,
            "matching_capabilities": help_response.matching_capabilities,
            "confidence_score": help_response.confidence_score,
            "availability": help_response.availability,
            "estimated_time": help_response.estimated_time,
            "message": help_response.message,
        },
        priority=4,
        correlation_id=help_response.request_id,
    )
    return message


def accept_help_response(
    self, request_id: str, response_id: str
) -> Optional[CollaborationSession]:
    """
    Accept a help response and start a collaboration session.

    Args:
        request_id: ID of the help request
        response_id: ID of the response to accept

    Returns:
        Optional[CollaborationSession]: Started session if successful
    """
    if request_id not in self.active_requests:
        return None
    help_request = self.active_requests[request_id]
    help_response = None
    for response in help_request.responses:
        if response.response_id == response_id:
            help_response = response
            break
    if not help_response:
        logger.warning(
            f"Help response {response_id} not found for request {request_id}"
        )
        return None
    if len(help_request.accepted_helpers) >= help_request.max_helpers:
        logger.warning(f"Help request {request_id} already has maximum helpers")
        return None
    help_request.accepted_helpers.append(help_response.responder_id)
    session = CollaborationSession(
        session_id=str(uuid.uuid4()),
        request_id=request_id,
        requester_id=help_request.requester_id,
        helper_id=help_response.responder_id,
        capabilities_used=help_response.matching_capabilities,
    )
    self.collaboration_sessions[session.session_id] = session
    if len(help_request.accepted_helpers) >= help_request.max_helpers:
        help_request.status = CollaborationStatus.ACCEPTED
    self.agent_registry.update_collaboration_score(help_response.responder_id, 0.1)
    self.stats["collaborations_started"] += 1
    logger.info(
        f"Started collaboration session {session.session_id} between {help_request.requester_id} and {help_response.responder_id}"
    )
    return session


def complete_collaboration(
    self, session_id: str, success: bool, metrics: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Mark a collaboration session as completed.

    Args:
        session_id: ID of the collaboration session
        success: Whether the collaboration was successful
        metrics: Optional success metrics

    Returns:
        bool: True if session was updated successfully
    """
    if session_id not in self.collaboration_sessions:
        return False
    session = self.collaboration_sessions[session_id]
    session.status = (
        CollaborationStatus.COMPLETED if success else CollaborationStatus.FAILED
    )
    session.success_metrics = metrics or {}
    score_delta = 1.0 if success else -0.5
    self.agent_registry.update_collaboration_score(session.helper_id, score_delta)
    for capability in session.capabilities_used:
        if capability not in self.stats["capability_success_rates"]:
            self.stats["capability_success_rates"][capability] = {
                "successes": 0,
                "total": 0,
            }
        self.stats["capability_success_rates"][capability]["total"] += 1
        if success:
            self.stats["capability_success_rates"][capability]["successes"] += 1
    if success:
        self.stats["collaborations_completed"] += 1
    else:
        self.stats["collaborations_failed"] += 1
    duration = (datetime.now() - session.started_at).total_seconds()
    current_avg = self.stats["average_collaboration_duration"]
    total_collaborations = (
        self.stats["collaborations_completed"] + self.stats["collaborations_failed"]
    )
    if total_collaborations > 0:
        self.stats["average_collaboration_duration"] = (
            current_avg * (total_collaborations - 1) + duration
        ) / total_collaborations
    logger.info(f"Completed collaboration session {session_id} (success: {success})")
    return True


def cleanup_expired_requests(self) -> int:
    """
    Clean up expired help requests.

    Returns:
        int: Number of requests cleaned up
    """
    now = datetime.now()
    expired_requests = []
    for request_id, help_request in self.active_requests.items():
        if help_request.expires_at and now > help_request.expires_at:
            expired_requests.append(request_id)
    for request_id in expired_requests:
        del self.active_requests[request_id]
        logger.info(f"Cleaned up expired help request {request_id}")
    return len(expired_requests)


def get_help_system_stats(self) -> Dict[str, Any]:
    """Get help system statistics"""
    return {
        **self.stats,
        "active_requests": len(self.active_requests),
        "active_collaborations": len(
            [
                s
                for s in self.collaboration_sessions.values()
                if s.status == CollaborationStatus.IN_PROGRESS
            ]
        ),
        "total_collaborations": len(self.collaboration_sessions),
    }


def get_active_requests(self) -> List[HelpRequest]:
    """Get all active help requests"""
    return list(self.active_requests.values())


def get_collaboration_sessions(self) -> List[CollaborationSession]:
    """Get all collaboration sessions"""
    return list(self.collaboration_sessions.values())


def find_matching_agents(
    self, required_capabilities: List[str]
) -> List[Tuple[DiscoveredAgent, float]]:
    """
    Find agents that match the required capabilities.

    Args:
        required_capabilities: List of required capabilities

    Returns:
        List of (agent, match_score) tuples
    """
    available_agents = self.agent_registry.get_active_agents()
    temp_request = HelpRequest(
        request_id="temp",
        requester_id="temp",
        required_capabilities=required_capabilities,
        description="Temporary request for matching",
    )
    return self.capability_matcher.find_best_matches(temp_request, available_agents)


def __init__(self):
    self.capability_weights = {
        "python": 1.0,
        "javascript": 1.0,
        "java": 1.0,
        "go": 1.0,
        "docker": 0.9,
        "kubernetes": 0.9,
        "terraform": 0.9,
        "gcp": 0.8,
        "aws": 0.8,
        "machine_learning": 1.2,
        "data_analysis": 1.1,
        "security": 1.2,
        "performance_optimization": 1.1,
        "testing": 0.8,
        "debugging": 0.8,
        "code_review": 0.7,
        "documentation": 0.6,
    }


def calculate_match_score(
    self,
    required_capabilities: List[str],
    agent_capabilities: List[str],
    agent_collaboration_score: float = 0.0,
) -> float:
    """
    Calculate how well an agent matches a help request.

    Args:
        required_capabilities: Capabilities needed for the request
        agent_capabilities: Agent's available capabilities
        agent_collaboration_score: Agent's historical collaboration success

    Returns:
        float: Match score from 0.0 to 1.0
    """
    if not required_capabilities:
        return 0.0
    required_set = set(required_capabilities)
    agent_set = set(agent_capabilities)
    direct_matches = required_set.intersection(agent_set)
    if not direct_matches:
        return 0.0
    total_weight = 0.0
    matched_weight = 0.0
    for capability in required_capabilities:
        weight = self.capability_weights.get(capability, 0.5)
        total_weight += weight
        if capability in agent_capabilities:
            matched_weight += weight
    if total_weight > 0:
        avg_weight = total_weight / len(required_capabilities)
        base_score = matched_weight / total_weight * avg_weight
    else:
        base_score = 0.0
    extra_capabilities = agent_set - required_set
    extra_bonus = min(0.2, len(extra_capabilities) * 0.05)
    collaboration_bonus = min(0.3, agent_collaboration_score * 0.1)
    final_score = base_score + extra_bonus + collaboration_bonus
    return final_score


def find_best_matches(
    self,
    help_request: HelpRequest,
    available_agents: List[DiscoveredAgent],
    min_score: float = 0.3,
) -> List[Tuple[DiscoveredAgent, float]]:
    """
    Find the best agent matches for a help request.

    Args:
        help_request: The help request to match
        available_agents: List of available agents
        min_score: Minimum match score to include

    Returns:
        List of (agent, score) tuples sorted by score descending
    """
    matches = []
    for agent in available_agents:
        if agent.capabilities.availability not in ["ready_for_business", "busy"]:
            continue
        score = self.calculate_match_score(
            help_request.required_capabilities,
            agent.capabilities.capabilities,
            agent.collaboration_score,
        )
        if score >= min_score:
            matches.append((agent, score))
    matches.sort(
        key=lambda x: (x[1], x[0].collaboration_score, -x[0].last_seen.timestamp()),
        reverse=True,
    )
    return matches


def __init__(self, agent_registry: AgentRegistry):
    self.agent_registry = agent_registry
    self.capability_matcher = CapabilityMatcher()
    self.active_requests: Dict[str, HelpRequest] = {}
    self.collaboration_sessions: Dict[str, CollaborationSession] = {}
    self.default_request_timeout = timedelta(hours=1)
    self.max_responses_per_request = 10
    self.auto_accept_threshold = 1.5
    self.stats = {
        "requests_created": 0,
        "responses_received": 0,
        "collaborations_started": 0,
        "collaborations_completed": 0,
        "collaborations_failed": 0,
        "average_response_time": 0.0,
        "average_collaboration_duration": 0.0,
        "capability_success_rates": {},
    }


def create_help_request(
    self,
    requester_id: str,
    required_capabilities: List[str],
    description: str,
    urgency: HelpUrgency = HelpUrgency.NORMAL,
    max_helpers: int = 1,
    timeout_hours: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None,
) -> HelpRequest:
    """
    Create a new help request.

    Args:
        requester_id: ID of the agent requesting help
        required_capabilities: List of required capabilities
        description: Description of what help is needed
        urgency: Urgency level of the request
        max_helpers: Maximum number of helpers needed
        timeout_hours: Hours until request expires (None for default)
        context: Additional context information

    Returns:
        HelpRequest: The created help request
    """
    request_id = str(uuid.uuid4())
    expires_at = None
    if timeout_hours is not None:
        expires_at = datetime.now() + timedelta(hours=timeout_hours)
    else:
        expires_at = datetime.now() + self.default_request_timeout
    help_request = HelpRequest(
        request_id=request_id,
        requester_id=requester_id,
        required_capabilities=required_capabilities,
        description=description,
        urgency=urgency,
        expires_at=expires_at,
        max_helpers=max_helpers,
        context=context or {},
    )
    self.active_requests[request_id] = help_request
    self.stats["requests_created"] += 1
    logger.info(
        f"Created help request {request_id} for capabilities: {required_capabilities}"
    )
    return help_request


def create_help_request_message(self, help_request: HelpRequest) -> BeastModeMessage:
    """
    Create a help wanted message for broadcasting.

    Args:
        help_request: The help request to broadcast

    Returns:
        BeastModeMessage: Message ready for broadcasting
    """
    priority_map = {
        HelpUrgency.LOW: 7,
        HelpUrgency.NORMAL: 5,
        HelpUrgency.HIGH: 3,
        HelpUrgency.CRITICAL: 1,
    }
    message = BeastModeMessage(
        type=MessageType.HELP_WANTED,
        source=help_request.requester_id,
        target=None,
        payload={
            "request_id": help_request.request_id,
            "required_capabilities": help_request.required_capabilities,
            "description": help_request.description,
            "urgency": help_request.urgency,
            "max_helpers": help_request.max_helpers,
            "expires_at": (
                help_request.expires_at.isoformat() if help_request.expires_at else None
            ),
            "context": help_request.context,
        },
        priority=priority_map[help_request.urgency],
    )
    return message


def create_help_response_message(self, help_response: HelpResponse) -> BeastModeMessage:
    """
    Create a help response message.

    Args:
        help_response: The help response to send

    Returns:
        BeastModeMessage: Message ready for sending
    """
    help_request = self.active_requests.get(help_response.request_id)
    target = help_request.requester_id if help_request else None
    message = BeastModeMessage(
        type=MessageType.HELP_RESPONSE,
        source=help_response.responder_id,
        target=target,
        payload={
            "response_id": help_response.response_id,
            "request_id": help_response.request_id,
            "matching_capabilities": help_response.matching_capabilities,
            "confidence_score": help_response.confidence_score,
            "availability": help_response.availability,
            "estimated_time": help_response.estimated_time,
            "message": help_response.message,
        },
        priority=4,
        correlation_id=help_response.request_id,
    )
    return message


def accept_help_response(
    self, request_id: str, response_id: str
) -> Optional[CollaborationSession]:
    """
    Accept a help response and start a collaboration session.

    Args:
        request_id: ID of the help request
        response_id: ID of the response to accept

    Returns:
        Optional[CollaborationSession]: Started session if successful
    """
    if request_id not in self.active_requests:
        return None
    help_request = self.active_requests[request_id]
    help_response = None
    for response in help_request.responses:
        if response.response_id == response_id:
            help_response = response
            break
    if not help_response:
        logger.warning(
            f"Help response {response_id} not found for request {request_id}"
        )
        return None
    if len(help_request.accepted_helpers) >= help_request.max_helpers:
        logger.warning(f"Help request {request_id} already has maximum helpers")
        return None
    help_request.accepted_helpers.append(help_response.responder_id)
    session = CollaborationSession(
        session_id=str(uuid.uuid4()),
        request_id=request_id,
        requester_id=help_request.requester_id,
        helper_id=help_response.responder_id,
        capabilities_used=help_response.matching_capabilities,
    )
    self.collaboration_sessions[session.session_id] = session
    if len(help_request.accepted_helpers) >= help_request.max_helpers:
        help_request.status = CollaborationStatus.ACCEPTED
    self.agent_registry.update_collaboration_score(help_response.responder_id, 0.1)
    self.stats["collaborations_started"] += 1
    logger.info(
        f"Started collaboration session {session.session_id} between {help_request.requester_id} and {help_response.responder_id}"
    )
    return session


def complete_collaboration(
    self, session_id: str, success: bool, metrics: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Mark a collaboration session as completed.

    Args:
        session_id: ID of the collaboration session
        success: Whether the collaboration was successful
        metrics: Optional success metrics

    Returns:
        bool: True if session was updated successfully
    """
    if session_id not in self.collaboration_sessions:
        return False
    session = self.collaboration_sessions[session_id]
    session.status = (
        CollaborationStatus.COMPLETED if success else CollaborationStatus.FAILED
    )
    session.success_metrics = metrics or {}
    score_delta = 1.0 if success else -0.5
    self.agent_registry.update_collaboration_score(session.helper_id, score_delta)
    for capability in session.capabilities_used:
        if capability not in self.stats["capability_success_rates"]:
            self.stats["capability_success_rates"][capability] = {
                "successes": 0,
                "total": 0,
            }
        self.stats["capability_success_rates"][capability]["total"] += 1
        if success:
            self.stats["capability_success_rates"][capability]["successes"] += 1
    if success:
        self.stats["collaborations_completed"] += 1
    else:
        self.stats["collaborations_failed"] += 1
    duration = (datetime.now() - session.started_at).total_seconds()
    current_avg = self.stats["average_collaboration_duration"]
    total_collaborations = (
        self.stats["collaborations_completed"] + self.stats["collaborations_failed"]
    )
    if total_collaborations > 0:
        self.stats["average_collaboration_duration"] = (
            current_avg * (total_collaborations - 1) + duration
        ) / total_collaborations
    logger.info(f"Completed collaboration session {session_id} (success: {success})")
    return True


def cleanup_expired_requests(self) -> int:
    """
    Clean up expired help requests.

    Returns:
        int: Number of requests cleaned up
    """
    now = datetime.now()
    expired_requests = []
    for request_id, help_request in self.active_requests.items():
        if help_request.expires_at and now > help_request.expires_at:
            expired_requests.append(request_id)
    for request_id in expired_requests:
        del self.active_requests[request_id]
        logger.info(f"Cleaned up expired help request {request_id}")
    return len(expired_requests)


def get_help_system_stats(self) -> Dict[str, Any]:
    """Get help system statistics"""
    return {
        **self.stats,
        "active_requests": len(self.active_requests),
        "active_collaborations": len(
            [
                s
                for s in self.collaboration_sessions.values()
                if s.status == CollaborationStatus.IN_PROGRESS
            ]
        ),
        "total_collaborations": len(self.collaboration_sessions),
    }


def get_active_requests(self) -> List[HelpRequest]:
    """Get all active help requests"""
    return list(self.active_requests.values())


def get_collaboration_sessions(self) -> List[CollaborationSession]:
    """Get all collaboration sessions"""
    return list(self.collaboration_sessions.values())


def find_matching_agents(
    self, required_capabilities: List[str]
) -> List[Tuple[DiscoveredAgent, float]]:
    """
    Find agents that match the required capabilities.

    Args:
        required_capabilities: List of required capabilities

    Returns:
        List of (agent, match_score) tuples
    """
    available_agents = self.agent_registry.get_active_agents()
    temp_request = HelpRequest(
        request_id="temp",
        requester_id="temp",
        required_capabilities=required_capabilities,
        description="Temporary request for matching",
    )
    return self.capability_matcher.find_best_matches(temp_request, available_agents)
