"""
Bus Client Core

This module was extracted from bus_client.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, time
from typing import Any, Callable, Dict, List, Optional, Set
import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .agent_registry import AgentRegistry, DiscoveredAgent
from .help_system import HelpWantedSystem, HelpUrgency
from .message_router import StandardMessageRouter
from .collaboration_scheduler import (
    CollaborationScheduler,
    CollaborationType,
    OfficeHoursPattern,
)


class BeastModeBusClient:
    """Redis-based pub/sub client for Beast Mode agent communication"""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        agent_id: str = "beast_mode_agent",
        capabilities: Optional[List[str]] = None,
        channel: str = "beast_mode_network",
    ):
        self.redis_url = redis_url
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        self.channel = channel
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.is_connected = False
        self.is_listening = False
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.received_messages: List[BeastModeMessage] = []
        self.message_router: Optional[StandardMessageRouter] = None
        self.agent_registry = AgentRegistry()
        self.discovery_enabled = True
        self.help_system = HelpWantedSystem(self.agent_registry)
        self.collaboration_scheduler = CollaborationScheduler(self.agent_id)
        self.max_retries = 5
        self.retry_delay = 1.0
        self.connection_timeout = 10.0
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "connection_errors": 0,
            "last_activity": None,
        }

    async def connect(self) -> bool:
        """
        Establish connection to Redis server with retry logic.

        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Attempting to connect to Redis (attempt {attempt + 1}/{self.max_retries})"
                )
                self.client = redis.from_url(
                    self.redis_url,
                    socket_connect_timeout=self.connection_timeout,
                    socket_timeout=self.connection_timeout,
                    retry_on_timeout=True,
                    decode_responses=True,
                )
                await self.client.ping()
                self.is_connected = True
                if self.discovery_enabled:
                    self.agent_registry.start_background_cleanup()
                self.collaboration_scheduler.start_background_tasks()
                if self.message_router is None:
                    self.message_router = StandardMessageRouter(
                        agent_id=self.agent_id, capabilities=self.capabilities
                    )
                logger.info(f"Successfully connected to Redis at {self.redis_url}")
                return True
            except (ConnectionError, TimeoutError) as e:
                self.stats["connection_errors"] += 1
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * 2**attempt)
                else:
                    logger.error(
                        f"Failed to connect to Redis after {self.max_retries} attempts"
                    )
                    return False
            except Exception as e:
                logger.error(f"Unexpected error connecting to Redis: {e}")
                return False
        return False

    async def disconnect(self) -> None:
        """Gracefully disconnect from Redis"""
        try:
            self.is_listening = False
            if self.discovery_enabled:
                self.agent_registry.stop_background_cleanup()
            self.collaboration_scheduler.stop_background_tasks()
            if self.pubsub:
                await self.pubsub.unsubscribe(self.channel)
                await self.pubsub.aclose()
                self.pubsub = None
            if self.client:
                await self.client.aclose()
                self.client = None
            self.is_connected = False
            logger.info("Disconnected from Redis")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    async def announce_presence(self) -> None:
        """Announce agent presence and capabilities to the network"""
        if not self.is_connected:
            raise RuntimeError("Not connected to Redis")
        capabilities_data = AgentCapabilities(
            agent_id=self.agent_id,
            capabilities=self.capabilities,
            availability="ready_for_business",
            last_seen=datetime.now(),
        )
        message = BeastModeMessage(
            type=MessageType.AGENT_DISCOVERY,
            source=self.agent_id,
            target=None,
            payload={
                "agent_capabilities": capabilities_data.model_dump(),
                "announcement": f"Agent {self.agent_id} is ready for collaboration",
            },
            priority=3,
        )
        await self.send_message(message)
        logger.info(f"Announced presence for agent {self.agent_id}")

    async def send_message(self, message: BeastModeMessage) -> None:
        """
        Send a message to the network.

        Args:
            message: The message to send
        """
        if not self.is_connected or not self.client:
            raise RuntimeError("Not connected to Redis")
        try:
            if not message.source:
                message.source = self.agent_id
            message_data = message.model_dump()
            message_json = json.dumps(message_data, default=str)
            await self.client.publish(self.channel, message_json)
            self.stats["messages_sent"] += 1
            self.stats["last_activity"] = datetime.now()
            logger.debug(
                f"Sent {message.type} message from {message.source} to {message.target or 'broadcast'}"
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def send_simple_message(
        self, content: str, target: Optional[str] = None
    ) -> None:
        """Send a simple text message"""
        message = BeastModeMessage(
            type=MessageType.SIMPLE_MESSAGE,
            source=self.agent_id,
            target=target,
            payload={"content": content},
        )
        await self.send_message(message)

    async def send_help_request(
        self,
        required_capabilities: List[str],
        description: str,
        urgency: HelpUrgency = HelpUrgency.NORMAL,
        max_helpers: int = 1,
        timeout_hours: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send a help request with required capabilities.

        Args:
            required_capabilities: List of required capabilities
            description: Description of what help is needed
            urgency: Urgency level of the request
            max_helpers: Maximum number of helpers needed
            timeout_hours: Hours until request expires
            context: Additional context information

        Returns:
            str: Request ID for tracking
        """
        help_request = self.help_system.create_help_request(
            requester_id=self.agent_id,
            required_capabilities=required_capabilities,
            description=description,
            urgency=urgency,
            max_helpers=max_helpers,
            timeout_hours=timeout_hours,
            context=context,
        )
        message = self.help_system.create_help_request_message(help_request)
        if self.client and self.client is not True:
            await self.send_message(message)
        return help_request.request_id

    async def listen_for_messages(
        self, message_callback: Optional[Callable[[BeastModeMessage], None]] = None
    ) -> None:
        """
        Listen for messages from the network.

        Args:
            message_callback: Optional callback function to handle received messages
        """
        if not self.is_connected or not self.client:
            raise RuntimeError("Not connected to Redis")
        try:
            self.pubsub = self.client.pubsub()
            await self.pubsub.subscribe(self.channel)
            self.is_listening = True
            logger.info(f"Started listening on channel {self.channel}")
            async for raw_message in self.pubsub.listen():
                if not self.is_listening:
                    break
                if raw_message["type"] == "message":
                    try:
                        message_data = json.loads(raw_message["data"])
                        message = BeastModeMessage(**message_data)
                        if message.source == self.agent_id:
                            continue
                        self.stats["messages_received"] += 1
                        self.stats["last_activity"] = datetime.now()
                        self.received_messages.append(message)
                        if self.message_router:
                            try:
                                router_responses = (
                                    await self.message_router.process_message(message)
                                )
                                for response in router_responses:
                                    await self.send_message(response)
                            except Exception as e:
                                logger.error(f"Error in message router: {e}")
                        await self._handle_message(message)
                        if message_callback:
                            try:
                                message_callback(message)
                            except Exception as e:
                                logger.error(f"Error in message callback: {e}")
                        logger.debug(f"Received {message.type} from {message.source}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse message JSON: {e}")
                        logger.debug(f"Raw message data: {raw_message['data']}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        logger.debug(f"Message data: {raw_message}")
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            raise
        finally:
            self.is_listening = False

    async def _handle_message(self, message: BeastModeMessage) -> None:
        """Internal message handler for standard message types"""
        try:
            if message.type == MessageType.AGENT_DISCOVERY:
                await self._handle_agent_discovery(message)
            elif message.type == MessageType.AGENT_RESPONSE:
                await self._handle_agent_response(message)
            elif message.type == MessageType.HELP_WANTED:
                await self._handle_help_request(message)
            elif message.type == MessageType.HELP_RESPONSE:
                await self._handle_help_response(message)
            elif message.type == MessageType.OFFICE_HOURS_ANNOUNCEMENT:
                await self._handle_office_hours_announcement(message)
            elif message.type == MessageType.COLLABORATION_REQUEST:
                await self._handle_collaboration_request(message)
            elif message.type == MessageType.COLLABORATION_RESPONSE:
                await self._handle_collaboration_response(message)
            elif message.type == MessageType.COLLABORATION_START:
                await self._handle_collaboration_start(message)
            elif message.type == MessageType.COLLABORATION_END:
                await self._handle_collaboration_end(message)
            elif message.type == MessageType.COLLABORATION_UPDATE:
                await self._handle_collaboration_update(message)
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
        except Exception as e:
            logger.error(f"Error in internal message handler: {e}")

    async def _handle_agent_discovery(self, message: BeastModeMessage) -> None:
        """Handle agent discovery messages"""
        if self.discovery_enabled:
            try:
                discovered_agent = self.agent_registry.register_agent_discovery(message)
                logger.info(
                    f"Registered agent {discovered_agent.agent_id} with capabilities: {discovered_agent.capabilities.capabilities}"
                )
            except Exception as e:
                logger.error(f"Error registering discovered agent: {e}")
        response = BeastModeMessage(
            type=MessageType.AGENT_RESPONSE,
            source=self.agent_id,
            target=message.source,
            payload={
                "agent_capabilities": AgentCapabilities(
                    agent_id=self.agent_id,
                    capabilities=self.capabilities,
                    availability="ready_for_business",
                ).model_dump(),
                "response_to": message.id,
            },
            correlation_id=message.id,
            priority=3,
        )
        await self.send_message(response)
        logger.info(f"Responded to discovery from {message.source}")

    async def _handle_agent_response(self, message: BeastModeMessage) -> None:
        """Handle agent response messages"""
        if self.discovery_enabled:
            try:
                updated_agent = self.agent_registry.register_agent_response(message)
                if updated_agent:
                    logger.debug(
                        f"Updated agent {updated_agent.agent_id} from response"
                    )
                else:
                    logger.debug(
                        f"Received response from unknown agent {message.source}, registering as discovery"
                    )
                    capabilities_data = message.payload.get("agent_capabilities", {})
                    if capabilities_data:
                        pseudo_discovery = BeastModeMessage(
                            type=MessageType.AGENT_DISCOVERY,
                            source=message.source,
                            payload={"agent_capabilities": capabilities_data},
                            timestamp=message.timestamp,
                        )
                        discovered_agent = self.agent_registry.register_agent_discovery(
                            pseudo_discovery
                        )
                        logger.info(
                            f"Registered responding agent {discovered_agent.agent_id} with capabilities: {discovered_agent.capabilities.capabilities}"
                        )
            except Exception as e:
                logger.error(f"Error processing agent response: {e}")

    async def _handle_help_request(self, message: BeastModeMessage) -> None:
        """Handle help request messages"""
        help_response = self.help_system.process_help_request(message, self.agent_id)
        if help_response:
            response_message = self.help_system.create_help_response_message(
                help_response
            )
            await self.send_message(response_message)
            logger.info(
                f"Offered help to {message.source} for request {help_response.request_id} (confidence: {help_response.confidence_score:.2f})"
            )

    async def _handle_help_response(self, message: BeastModeMessage) -> None:
        """Handle help response messages"""
        success = self.help_system.process_help_response(message)
        if success:
            logger.info(
                f"Received help response from {message.source} for request {message.payload.get('request_id')}"
            )
        else:
            logger.warning(f"Failed to process help response from {message.source}")

    async def _handle_office_hours_announcement(
        self, message: BeastModeMessage
    ) -> None:
        """Handle office hours announcement messages"""
        success = self.collaboration_scheduler.update_office_hours_from_message(message)
        if success:
            logger.info(f"Updated office hours for {message.source}")
        else:
            logger.warning(f"Failed to update office hours from {message.source}")

    async def _handle_collaboration_request(self, message: BeastModeMessage) -> None:
        """Handle collaboration request messages"""
        try:
            payload = message.payload
            requested_time = None
            if payload.get("scheduled_start"):
                requested_time = datetime.fromisoformat(payload["scheduled_start"])
            is_available = self.collaboration_scheduler.is_agent_available(
                self.agent_id, requested_time
            )
            response_payload = {
                "request_id": payload.get("request_id", message.id),
                "available": is_available,
                "agent_capabilities": AgentCapabilities(
                    agent_id=self.agent_id,
                    capabilities=self.capabilities,
                    availability="ready_for_business" if is_available else "busy",
                ).model_dump(),
            }
            if is_available and requested_time:
                next_slot = self.collaboration_scheduler.get_next_available_slot(
                    self.agent_id, payload.get("duration_minutes", 30), requested_time
                )
                if next_slot:
                    response_payload["suggested_time"] = next_slot.isoformat()
            response = BeastModeMessage(
                type=MessageType.COLLABORATION_RESPONSE,
                source=self.agent_id,
                target=message.source,
                payload=response_payload,
                correlation_id=message.id,
                priority=3,
            )
            await self.send_message(response)
            logger.info(f"Responded to collaboration request from {message.source}")
        except Exception as e:
            logger.error(f"Error handling collaboration request: {e}")

    async def _handle_collaboration_response(self, message: BeastModeMessage) -> None:
        """Handle collaboration response messages"""
        try:
            payload = message.payload
            request_id = payload.get("request_id")
            if payload.get("available", False):
                logger.info(
                    f"Agent {message.source} is available for collaboration (request {request_id})"
                )
                self.collaboration_scheduler.trigger_collaboration_callback(
                    "on_collaboration_response", message.source, payload
                )
            else:
                logger.info(
                    f"Agent {message.source} is not available for collaboration (request {request_id})"
                )
                if payload.get("suggested_time"):
                    logger.info(
                        f"Agent {message.source} suggested alternative time: {payload['suggested_time']}"
                    )
        except Exception as e:
            logger.error(f"Error handling collaboration response: {e}")

    async def _handle_collaboration_start(self, message: BeastModeMessage) -> None:
        """Handle collaboration start messages"""
        try:
            payload = message.payload
            session_id = payload.get("session_id")
            if session_id:
                success = self.collaboration_scheduler.start_collaboration_session(
                    session_id
                )
                if success:
                    logger.info(f"Started collaboration session {session_id}")
                    self.collaboration_scheduler.trigger_collaboration_callback(
                        "on_collaboration_start", session_id, payload
                    )
                else:
                    logger.warning(
                        f"Failed to start collaboration session {session_id}"
                    )
        except Exception as e:
            logger.error(f"Error handling collaboration start: {e}")

    async def _handle_collaboration_end(self, message: BeastModeMessage) -> None:
        """Handle collaboration end messages"""
        try:
            payload = message.payload
            session_id = payload.get("session_id")
            success = payload.get("success", True)
            success_metrics = payload.get("success_metrics", {})
            if session_id:
                ended = self.collaboration_scheduler.end_collaboration_session(
                    session_id, success, success_metrics
                )
                if ended:
                    logger.info(
                        f"Ended collaboration session {session_id} (success: {success})"
                    )
                    self.collaboration_scheduler.trigger_collaboration_callback(
                        "on_collaboration_end", session_id, success, success_metrics
                    )
                else:
                    logger.warning(f"Failed to end collaboration session {session_id}")
        except Exception as e:
            logger.error(f"Error handling collaboration end: {e}")

    async def _handle_collaboration_update(self, message: BeastModeMessage) -> None:
        """Handle collaboration update messages"""
        try:
            payload = message.payload
            session_id = payload.get("session_id")
            if session_id:
                session = self.collaboration_scheduler.get_session(session_id)
                if session:
                    update_data = payload.get("update_data", {})
                    session.collaboration_data.update(update_data)
                    session.updated_at = datetime.now()
                    logger.info(f"Updated collaboration session {session_id}")
                    self.collaboration_scheduler.trigger_collaboration_callback(
                        "on_collaboration_update", session_id, update_data
                    )
                else:
                    logger.warning(
                        f"Collaboration session {session_id} not found for update"
                    )
        except Exception as e:
            logger.error(f"Error handling collaboration update: {e}")

    def register_message_handler(
        self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]
    ) -> None:
        """Register a custom message handler"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        logger.info(f"Registered handler for {message_type}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get client health and statistics"""
        return {
            "agent_id": self.agent_id,
            "is_connected": self.is_connected,
            "is_listening": self.is_listening,
            "channel": self.channel,
            "capabilities": self.capabilities,
            "stats": self.stats.copy(),
            "message_handlers": list(self.message_handlers.keys()),
        }

    def get_recent_messages(self, limit: int = 10) -> List[BeastModeMessage]:
        """Get recent received messages"""
        return self.received_messages[-limit:] if self.received_messages else []

    async def discover_agents(self) -> List[DiscoveredAgent]:
        """
        Perform agent discovery and return currently known agents.

        Returns:
            List[DiscoveredAgent]: List of discovered agents
        """
        if not self.discovery_enabled:
            return []
        await self.announce_presence()
        await asyncio.sleep(1.0)
        return self.agent_registry.get_active_agents()

    def find_agents_with_capabilities(
        self, required_capabilities: List[str]
    ) -> List[DiscoveredAgent]:
        """
        Find agents that have any of the required capabilities.

        Args:
            required_capabilities: List of required capabilities

        Returns:
            List[DiscoveredAgent]: Agents with matching capabilities
        """
        if not self.discovery_enabled:
            return []
        return self.agent_registry.find_agents_with_capabilities(required_capabilities)

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
        if not self.discovery_enabled:
            return []
        return self.agent_registry.find_agents_with_all_capabilities(
            required_capabilities
        )

    def get_discovered_agents(self) -> List[DiscoveredAgent]:
        """Get all discovered agents"""
        if not self.discovery_enabled:
            return []
        return self.agent_registry.get_active_agents()

    def get_discovered_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
        """Get a specific discovered agent by ID"""
        if not self.discovery_enabled:
            return None
        return self.agent_registry.get_agent(agent_id)

    def get_all_capabilities(self) -> Set[str]:
        """Get all unique capabilities across all discovered agents"""
        if not self.discovery_enabled:
            return set()
        return self.agent_registry.get_all_capabilities()

    def update_agent_collaboration_score(
        self, agent_id: str, score_delta: float
    ) -> None:
        """
        Update an agent's collaboration score.

        Args:
            agent_id: Agent to update
            score_delta: Change in score (positive for successful collaboration)
        """
        if self.discovery_enabled:
            self.agent_registry.update_collaboration_score(agent_id, score_delta)

    def cleanup_inactive_agents(self) -> int:
        """
        Manually trigger cleanup of inactive agents.

        Returns:
            int: Number of agents cleaned up
        """
        if not self.discovery_enabled:
            return 0
        return self.agent_registry.cleanup_inactive_agents()

    def get_discovery_stats(self) -> Dict:
        """Get agent discovery statistics"""
        if not self.discovery_enabled:
            return {"discovery_enabled": False}
        return {"discovery_enabled": True, **self.agent_registry.get_registry_stats()}

    def accept_help_response(self, request_id: str, response_id: str) -> bool:
        """
        Accept a help response and start collaboration.

        Args:
            request_id: ID of the help request
            response_id: ID of the response to accept

        Returns:
            bool: True if response was accepted successfully
        """
        session = self.help_system.accept_help_response(request_id, response_id)
        return session is not None

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
        return self.help_system.complete_collaboration(session_id, success, metrics)

    def get_active_help_requests(self) -> List:
        """Get all active help requests"""
        return [req.__dict__ for req in self.help_system.get_active_requests()]

    def get_collaboration_sessions(self) -> List:
        """Get all collaboration sessions"""
        return [
            session.__dict__
            for session in self.help_system.get_collaboration_sessions()
        ]

    def find_agents_for_capabilities(
        self, required_capabilities: List[str]
    ) -> List[Dict]:
        """
        Find agents that match the required capabilities.

        Args:
            required_capabilities: List of required capabilities

        Returns:
            List of agent match information
        """
        matches = self.help_system.find_matching_agents(required_capabilities)
        return [
            {
                "agent_id": agent.agent_id,
                "capabilities": agent.capabilities.capabilities,
                "match_score": score,
                "collaboration_score": agent.collaboration_score,
                "availability": agent.capabilities.availability,
                "last_seen": agent.last_seen.isoformat(),
            }
            for agent, score in matches
        ]

    def get_help_system_stats(self) -> Dict[str, Any]:
        """Get help system statistics"""
        return self.help_system.get_help_system_stats()

    def cleanup_expired_help_requests(self) -> int:
        """
        Clean up expired help requests.

        Returns:
            int: Number of requests cleaned up
        """
        return self.help_system.cleanup_expired_requests()

    def set_message_callback(self, callback_name: str, callback: Callable) -> None:
        """
        Set a callback for the message router.

        Args:
            callback_name: Name of the callback (e.g., 'on_simple_message')
            callback: Callback function
        """
        if self.message_router:
            self.message_router.set_callback(callback_name, callback)
        else:
            logger.warning("Message router not initialized, callback not set")

    def get_message_router_stats(self) -> Dict[str, Any]:
        """Get message router statistics"""
        if self.message_router:
            return self.message_router.get_handler_stats()
        return {"error": "Message router not initialized"}

    def get_message_router_info(self) -> Dict[str, Any]:
        """Get message router information"""
        if self.message_router:
            return self.message_router.get_handler_info()
        return {"error": "Message router not initialized"}

    def validate_message_format(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate message format using the router.

        Args:
            message_data: Raw message data

        Returns:
            Validation result
        """
        if self.message_router:
            return self.message_router.validate_message_compatibility(message_data)
        try:
            BeastModeMessage(**message_data)
            return {"is_valid": True, "is_legacy": False, "errors": []}
        except Exception as e:
            return {"is_valid": False, "is_legacy": False, "errors": [str(e)]}

    def create_test_message(self, msg_type: MessageType, **kwargs) -> BeastModeMessage:
        """
        Create a test message for a specific type.

        Args:
            msg_type: Message type to create
            **kwargs: Additional message parameters

        Returns:
            Test message
        """
        if self.message_router:
            return self.message_router.create_test_message(msg_type, **kwargs)
        return BeastModeMessage(
            type=msg_type,
            source=kwargs.get("source", self.agent_id),
            target=kwargs.get("target"),
            payload=kwargs.get("payload", {}),
            priority=kwargs.get("priority", 5),
        )

    def get_message_history(
        self, limit: Optional[int] = None
    ) -> Dict[str, List[BeastModeMessage]]:
        """
        Get message history from the router.

        Args:
            limit: Maximum number of messages to return

        Returns:
            Message history
        """
        if self.message_router:
            return self.message_router.get_message_history(limit)
        recent_messages = (
            self.received_messages[-limit:] if limit else self.received_messages
        )
        return {"sent": [], "received": recent_messages}

    async def announce_office_hours(
        self,
        pattern: OfficeHoursPattern,
        start_time: time,
        end_time: time,
        timezone: str = "UTC",
        days_of_week: Optional[Set[int]] = None,
        description: str = "",
        capabilities_focus: Optional[List[str]] = None,
    ) -> None:
        """
        Announce office hours to the network.

        Args:
            pattern: Scheduling pattern
            start_time: Start time for office hours
            end_time: End time for office hours
            timezone: Timezone for the schedule
            days_of_week: Days of week for custom patterns
            description: Description of office hours focus
            capabilities_focus: Specific capabilities to focus on
        """
        office_hours = self.collaboration_scheduler.set_office_hours(
            pattern=pattern,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            days_of_week=days_of_week,
            description=description,
            capabilities_focus=capabilities_focus or [],
        )
        message = BeastModeMessage(
            type=MessageType.OFFICE_HOURS_ANNOUNCEMENT,
            source=self.agent_id,
            target=None,
            payload={
                "office_hours": {
                    "pattern": office_hours.pattern.value,
                    "start_time": office_hours.start_time.isoformat(),
                    "end_time": office_hours.end_time.isoformat(),
                    "timezone": office_hours.timezone,
                    "days_of_week": list(office_hours.days_of_week),
                    "description": office_hours.description,
                    "capabilities_focus": office_hours.capabilities_focus,
                    "max_concurrent_sessions": office_hours.max_concurrent_sessions,
                    "session_duration_minutes": office_hours.session_duration_minutes,
                },
                "announcement": f"Agent {self.agent_id} office hours: {pattern.value} {start_time}-{end_time}",
            },
            priority=4,
        )
        await self.send_message(message)
        logger.info(f"Announced office hours: {pattern.value} {start_time}-{end_time}")

    async def request_collaboration(
        self,
        target_agents: List[str],
        topic: str,
        collaboration_type: CollaborationType = CollaborationType.AD_HOC,
        scheduled_start: Optional[datetime] = None,
        duration_minutes: int = 30,
        description: str = "",
        required_capabilities: Optional[List[str]] = None,
    ) -> str:
        """
        Request collaboration with other agents.

        Args:
            target_agents: List of agents to collaborate with
            topic: Collaboration topic
            collaboration_type: Type of collaboration
            scheduled_start: When to start (None for immediate)
            duration_minutes: Session duration
            description: Session description
            required_capabilities: Required capabilities

        Returns:
            str: Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        session = self.collaboration_scheduler.schedule_collaboration(
            participants=[self.agent_id] + target_agents,
            topic=topic,
            session_type=collaboration_type,
            scheduled_start=scheduled_start,
            duration_minutes=duration_minutes,
            description=description,
            required_capabilities=required_capabilities,
        )
        if not session:
            raise RuntimeError("Failed to schedule collaboration session")
        for target_agent in target_agents:
            message = BeastModeMessage(
                type=MessageType.COLLABORATION_REQUEST,
                source=self.agent_id,
                target=target_agent,
                payload={
                    "request_id": request_id,
                    "session_id": session.session_id,
                    "topic": topic,
                    "collaboration_type": collaboration_type.value,
                    "scheduled_start": (
                        scheduled_start.isoformat() if scheduled_start else None
                    ),
                    "duration_minutes": duration_minutes,
                    "description": description,
                    "required_capabilities": required_capabilities or [],
                    "organizer_capabilities": self.capabilities,
                },
                correlation_id=request_id,
                priority=3,
            )
            await self.send_message(message)
        logger.info(
            f"Requested collaboration with {len(target_agents)} agents: {topic}"
        )
        return request_id

    async def start_collaboration_session(self, session_id: str) -> bool:
        """
        Start a collaboration session and notify participants.

        Args:
            session_id: Session to start

        Returns:
            bool: True if session was started successfully
        """
        session = self.collaboration_scheduler.get_session(session_id)
        if not session:
            return False
        success = self.collaboration_scheduler.start_collaboration_session(session_id)
        if not success:
            return False
        for participant in session.participants:
            if participant != self.agent_id:
                message = BeastModeMessage(
                    type=MessageType.COLLABORATION_START,
                    source=self.agent_id,
                    target=participant,
                    payload={
                        "session_id": session_id,
                        "topic": session.topic,
                        "organizer": self.agent_id,
                        "participants": session.participants,
                        "started_at": datetime.now().isoformat(),
                    },
                    priority=2,
                )
                await self.send_message(message)
        logger.info(f"Started collaboration session {session_id}")
        return True

    async def end_collaboration_session(
        self,
        session_id: str,
        success: bool = True,
        success_metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        End a collaboration session and notify participants.

        Args:
            session_id: Session to end
            success: Whether the session was successful
            success_metrics: Success metrics and outcomes

        Returns:
            bool: True if session was ended successfully
        """
        session = self.collaboration_scheduler.get_session(session_id)
        if not session:
            return False
        ended = self.collaboration_scheduler.end_collaboration_session(
            session_id, success, success_metrics
        )
        if not ended:
            return False
        for participant in session.participants:
            if participant != self.agent_id:
                message = BeastModeMessage(
                    type=MessageType.COLLABORATION_END,
                    source=self.agent_id,
                    target=participant,
                    payload={
                        "session_id": session_id,
                        "success": success,
                        "success_metrics": success_metrics or {},
                        "ended_at": datetime.now().isoformat(),
                        "organizer": self.agent_id,
                    },
                    priority=2,
                )
                await self.send_message(message)
        logger.info(f"Ended collaboration session {session_id} (success: {success})")
        return True

    def set_collaboration_callback(
        self, callback_name: str, callback: Callable
    ) -> None:
        """
        Set a callback for collaboration events.

        Args:
            callback_name: Name of the callback
            callback: Callback function
        """
        self.collaboration_scheduler.set_collaboration_callback(callback_name, callback)

    def get_collaboration_recommendations(self) -> List[Dict[str, Any]]:
        """Get collaboration recommendations based on patterns"""
        return self.collaboration_scheduler.get_collaboration_recommendations(
            self.agent_id
        )

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        return self.collaboration_scheduler.get_collaboration_stats()

    def get_active_collaboration_sessions(self) -> List:
        """Get active collaboration sessions"""
        sessions = self.collaboration_scheduler.get_active_sessions()
        return [
            {
                "session_id": s.session_id,
                "type": s.session_type.value,
                "organizer": s.organizer_id,
                "participants": s.participants,
                "topic": s.topic,
                "scheduled_start": (
                    s.scheduled_start.isoformat() if s.scheduled_start else None
                ),
                "actual_start": s.actual_start.isoformat() if s.actual_start else None,
                "status": s.status.value,
            }
            for s in sessions
        ]

    def is_agent_available_for_collaboration(
        self, agent_id: str, at_time: Optional[datetime] = None
    ) -> bool:
        """Check if an agent is available for collaboration"""
        return self.collaboration_scheduler.is_agent_available(agent_id, at_time)

    def get_next_available_collaboration_slot(
        self, agent_id: str, duration_minutes: int = 30
    ) -> Optional[datetime]:
        """Find the next available collaboration slot for an agent"""
        return self.collaboration_scheduler.get_next_available_slot(
            agent_id, duration_minutes
        )


def __init__(
    self,
    redis_url: str = "redis://localhost:6379",
    agent_id: str = "beast_mode_agent",
    capabilities: Optional[List[str]] = None,
    channel: str = "beast_mode_network",
):
    self.redis_url = redis_url
    self.agent_id = agent_id
    self.capabilities = capabilities or []
    self.channel = channel
    self.client: Optional[redis.Redis] = None
    self.pubsub: Optional[redis.client.PubSub] = None
    self.is_connected = False
    self.is_listening = False
    self.message_handlers: Dict[MessageType, List[Callable]] = {}
    self.received_messages: List[BeastModeMessage] = []
    self.message_router: Optional[StandardMessageRouter] = None
    self.agent_registry = AgentRegistry()
    self.discovery_enabled = True
    self.help_system = HelpWantedSystem(self.agent_registry)
    self.collaboration_scheduler = CollaborationScheduler(self.agent_id)
    self.max_retries = 5
    self.retry_delay = 1.0
    self.connection_timeout = 10.0
    self.stats = {
        "messages_sent": 0,
        "messages_received": 0,
        "connection_errors": 0,
        "last_activity": None,
    }


def register_message_handler(
    self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]
) -> None:
    """Register a custom message handler"""
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)
    logger.info(f"Registered handler for {message_type}")


def get_health_status(self) -> Dict[str, Any]:
    """Get client health and statistics"""
    return {
        "agent_id": self.agent_id,
        "is_connected": self.is_connected,
        "is_listening": self.is_listening,
        "channel": self.channel,
        "capabilities": self.capabilities,
        "stats": self.stats.copy(),
        "message_handlers": list(self.message_handlers.keys()),
    }


def get_recent_messages(self, limit: int = 10) -> List[BeastModeMessage]:
    """Get recent received messages"""
    return self.received_messages[-limit:] if self.received_messages else []


def find_agents_with_capabilities(
    self, required_capabilities: List[str]
) -> List[DiscoveredAgent]:
    """
    Find agents that have any of the required capabilities.

    Args:
        required_capabilities: List of required capabilities

    Returns:
        List[DiscoveredAgent]: Agents with matching capabilities
    """
    if not self.discovery_enabled:
        return []
    return self.agent_registry.find_agents_with_capabilities(required_capabilities)


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
    if not self.discovery_enabled:
        return []
    return self.agent_registry.find_agents_with_all_capabilities(required_capabilities)


def get_discovered_agents(self) -> List[DiscoveredAgent]:
    """Get all discovered agents"""
    if not self.discovery_enabled:
        return []
    return self.agent_registry.get_active_agents()


def get_discovered_agent(self, agent_id: str) -> Optional[DiscoveredAgent]:
    """Get a specific discovered agent by ID"""
    if not self.discovery_enabled:
        return None
    return self.agent_registry.get_agent(agent_id)


def get_all_capabilities(self) -> Set[str]:
    """Get all unique capabilities across all discovered agents"""
    if not self.discovery_enabled:
        return set()
    return self.agent_registry.get_all_capabilities()


def update_agent_collaboration_score(self, agent_id: str, score_delta: float) -> None:
    """
    Update an agent's collaboration score.

    Args:
        agent_id: Agent to update
        score_delta: Change in score (positive for successful collaboration)
    """
    if self.discovery_enabled:
        self.agent_registry.update_collaboration_score(agent_id, score_delta)


def cleanup_inactive_agents(self) -> int:
    """
    Manually trigger cleanup of inactive agents.

    Returns:
        int: Number of agents cleaned up
    """
    if not self.discovery_enabled:
        return 0
    return self.agent_registry.cleanup_inactive_agents()


def get_discovery_stats(self) -> Dict:
    """Get agent discovery statistics"""
    if not self.discovery_enabled:
        return {"discovery_enabled": False}
    return {"discovery_enabled": True, **self.agent_registry.get_registry_stats()}


def accept_help_response(self, request_id: str, response_id: str) -> bool:
    """
    Accept a help response and start collaboration.

    Args:
        request_id: ID of the help request
        response_id: ID of the response to accept

    Returns:
        bool: True if response was accepted successfully
    """
    session = self.help_system.accept_help_response(request_id, response_id)
    return session is not None


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
    return self.help_system.complete_collaboration(session_id, success, metrics)


def get_active_help_requests(self) -> List:
    """Get all active help requests"""
    return [req.__dict__ for req in self.help_system.get_active_requests()]


def get_collaboration_sessions(self) -> List:
    """Get all collaboration sessions"""
    return [
        session.__dict__ for session in self.help_system.get_collaboration_sessions()
    ]


def find_agents_for_capabilities(self, required_capabilities: List[str]) -> List[Dict]:
    """
    Find agents that match the required capabilities.

    Args:
        required_capabilities: List of required capabilities

    Returns:
        List of agent match information
    """
    matches = self.help_system.find_matching_agents(required_capabilities)
    return [
        {
            "agent_id": agent.agent_id,
            "capabilities": agent.capabilities.capabilities,
            "match_score": score,
            "collaboration_score": agent.collaboration_score,
            "availability": agent.capabilities.availability,
            "last_seen": agent.last_seen.isoformat(),
        }
        for agent, score in matches
    ]


def get_help_system_stats(self) -> Dict[str, Any]:
    """Get help system statistics"""
    return self.help_system.get_help_system_stats()


def cleanup_expired_help_requests(self) -> int:
    """
    Clean up expired help requests.

    Returns:
        int: Number of requests cleaned up
    """
    return self.help_system.cleanup_expired_requests()


def set_message_callback(self, callback_name: str, callback: Callable) -> None:
    """
    Set a callback for the message router.

    Args:
        callback_name: Name of the callback (e.g., 'on_simple_message')
        callback: Callback function
    """
    if self.message_router:
        self.message_router.set_callback(callback_name, callback)
    else:
        logger.warning("Message router not initialized, callback not set")


def get_message_router_stats(self) -> Dict[str, Any]:
    """Get message router statistics"""
    if self.message_router:
        return self.message_router.get_handler_stats()
    return {"error": "Message router not initialized"}


def get_message_router_info(self) -> Dict[str, Any]:
    """Get message router information"""
    if self.message_router:
        return self.message_router.get_handler_info()
    return {"error": "Message router not initialized"}


def get_message_history(
    self, limit: Optional[int] = None
) -> Dict[str, List[BeastModeMessage]]:
    """
    Get message history from the router.

    Args:
        limit: Maximum number of messages to return

    Returns:
        Message history
    """
    if self.message_router:
        return self.message_router.get_message_history(limit)
    recent_messages = (
        self.received_messages[-limit:] if limit else self.received_messages
    )
    return {"sent": [], "received": recent_messages}


def set_collaboration_callback(self, callback_name: str, callback: Callable) -> None:
    """
    Set a callback for collaboration events.

    Args:
        callback_name: Name of the callback
        callback: Callback function
    """
    self.collaboration_scheduler.set_collaboration_callback(callback_name, callback)


def get_collaboration_recommendations(self) -> List[Dict[str, Any]]:
    """Get collaboration recommendations based on patterns"""
    return self.collaboration_scheduler.get_collaboration_recommendations(self.agent_id)


def get_collaboration_stats(self) -> Dict[str, Any]:
    """Get collaboration statistics"""
    return self.collaboration_scheduler.get_collaboration_stats()


def get_active_collaboration_sessions(self) -> List:
    """Get active collaboration sessions"""
    sessions = self.collaboration_scheduler.get_active_sessions()
    return [
        {
            "session_id": s.session_id,
            "type": s.session_type.value,
            "organizer": s.organizer_id,
            "participants": s.participants,
            "topic": s.topic,
            "scheduled_start": (
                s.scheduled_start.isoformat() if s.scheduled_start else None
            ),
            "actual_start": s.actual_start.isoformat() if s.actual_start else None,
            "status": s.status.value,
        }
        for s in sessions
    ]


def is_agent_available_for_collaboration(
    self, agent_id: str, at_time: Optional[datetime] = None
) -> bool:
    """Check if an agent is available for collaboration"""
    return self.collaboration_scheduler.is_agent_available(agent_id, at_time)


def get_next_available_collaboration_slot(
    self, agent_id: str, duration_minutes: int = 30
) -> Optional[datetime]:
    """Find the next available collaboration slot for an agent"""
    return self.collaboration_scheduler.get_next_available_slot(
        agent_id, duration_minutes
    )
