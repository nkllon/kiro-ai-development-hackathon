"""
Message Handlers Handlers

This module was extracted from message_handlers.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from .models import BeastModeMessage, MessageType, AgentCapabilities


class MessageHandlerResult(Enum):
    """Result of message handling"""

    SUCCESS = "success"
    HANDLED = "handled"
    IGNORED = "ignored"
    ERROR = "error"
    RETRY = "retry"


class BaseMessageHandler(ABC):
    """Abstract base class for message handlers"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.handled_count = 0
        self.error_count = 0
        self.last_handled = None

    @abstractmethod
    def get_supported_types(self) -> List[MessageType]:
        """Return list of supported message types"""
        pass

    @abstractmethod
    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """
        Handle an incoming message.

        Args:
            message: The message to handle

        Returns:
            Optional response message
        """
        pass

    def can_handle(self, message: BeastModeMessage) -> bool:
        """Check if this handler can process the message"""
        return message.type in self.get_supported_types()

    def validate_message(self, message: BeastModeMessage) -> None:
        """
        Validate message structure and content.

        Raises:
            MessageValidationError: If message is invalid
        """
        if not message.type:
            raise MessageValidationError("Message type is required")
        if not message.source:
            raise MessageValidationError("Message source is required")
        if message.priority < 1 or message.priority > 10:
            raise MessageValidationError("Message priority must be between 1 and 10")

    async def _handle_with_stats(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle message with statistics tracking"""
        try:
            self.validate_message(message)
            result = await self.handle_message(message)
            self.handled_count += 1
            self.last_handled = datetime.now()
            return result
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics"""
        return {
            "handler_type": self.__class__.__name__,
            "supported_types": [t.value for t in self.get_supported_types()],
            "handled_count": self.handled_count,
            "error_count": self.error_count,
            "last_handled": (
                self.last_handled.isoformat() if self.last_handled else None
            ),
        }


class SimpleMessageHandler(BaseMessageHandler):
    """Handler for simple text messages"""

    def __init__(
        self,
        agent_id: str,
        message_callback: Optional[Callable[[str, str], None]] = None,
    ):
        super().__init__(agent_id)
        self.message_callback = message_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SIMPLE_MESSAGE]

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle simple text message"""
        content = message.payload.get("content", "")
        if self.message_callback:
            try:
                self.message_callback(message.source, content)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")
                raise
        logger.info(f"Received simple message from {message.source}: {content}")
        return None


class PromptRequestHandler(BaseMessageHandler):
    """Handler for prompt requests"""

    def __init__(
        self, agent_id: str, prompt_processor: Optional[Callable[[str], str]] = None
    ):
        super().__init__(agent_id)
        self.prompt_processor = prompt_processor

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.PROMPT_REQUEST]

    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate prompt request message"""
        super().validate_message(message)
        if "prompt" not in message.payload:
            raise MessageValidationError(
                "Prompt request must contain 'prompt' in payload"
            )

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle prompt request and generate response"""
        prompt = message.payload["prompt"]
        response_text = "Prompt received"
        if self.prompt_processor:
            try:
                response_text = self.prompt_processor(prompt)
            except Exception as e:
                logger.error(f"Error processing prompt: {e}")
                response_text = f"Error processing prompt: {str(e)}"
        response = BeastModeMessage(
            type=MessageType.PROMPT_RESPONSE,
            source=self.agent_id,
            target=message.source,
            payload={
                "response": response_text,
                "original_prompt": prompt,
                "processed_at": datetime.now().isoformat(),
            },
            correlation_id=message.id,
            priority=message.priority,
        )
        logger.info(f"Processed prompt request from {message.source}")
        return response


class PromptResponseHandler(BaseMessageHandler):
    """Handler for prompt responses"""

    def __init__(
        self,
        agent_id: str,
        response_callback: Optional[Callable[[str, str, str], None]] = None,
    ):
        super().__init__(agent_id)
        self.response_callback = response_callback
        self.pending_requests: Dict[str, BeastModeMessage] = {}

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.PROMPT_RESPONSE]

    def track_request(self, request: BeastModeMessage) -> None:
        """Track a sent prompt request for correlation"""
        if request.type == MessageType.PROMPT_REQUEST:
            self.pending_requests[request.id] = request

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle prompt response"""
        response_text = message.payload.get("response", "")
        correlation_id = message.correlation_id
        original_request = None
        if correlation_id and correlation_id in self.pending_requests:
            original_request = self.pending_requests.pop(correlation_id)
        if self.response_callback:
            try:
                original_prompt = (
                    original_request.payload.get("prompt", "")
                    if original_request
                    else ""
                )
                self.response_callback(message.source, response_text, original_prompt)
            except Exception as e:
                logger.error(f"Error in response callback: {e}")
        logger.info(f"Received prompt response from {message.source}")
        return None


class AgentDiscoveryHandler(BaseMessageHandler):
    """Handler for agent discovery messages"""

    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        discovery_callback: Optional[Callable[[str, AgentCapabilities], None]] = None,
    ):
        super().__init__(agent_id)
        self.capabilities = capabilities
        self.discovery_callback = discovery_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.AGENT_DISCOVERY]

    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate agent discovery message"""
        super().validate_message(message)
        if "agent_capabilities" not in message.payload:
            raise MessageValidationError(
                "Agent discovery must contain 'agent_capabilities' in payload"
            )

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle agent discovery and respond with capabilities"""
        try:
            caps_data = message.payload["agent_capabilities"]
            discovered_caps = AgentCapabilities(**caps_data)
            if self.discovery_callback:
                try:
                    self.discovery_callback(message.source, discovered_caps)
                except Exception as e:
                    logger.error(f"Error in discovery callback: {e}")
            our_capabilities = AgentCapabilities(
                agent_id=self.agent_id,
                capabilities=self.capabilities,
                availability="ready_for_business",
            )
            response = BeastModeMessage(
                type=MessageType.AGENT_RESPONSE,
                source=self.agent_id,
                target=message.source,
                payload={
                    "agent_capabilities": our_capabilities.model_dump(),
                    "response_to": message.id,
                },
                correlation_id=message.id,
                priority=3,
            )
            logger.info(f"Responded to discovery from {message.source}")
            return response
        except Exception as e:
            logger.error(f"Error processing agent discovery: {e}")
            return None


class AgentResponseHandler(BaseMessageHandler):
    """Handler for agent response messages"""

    def __init__(
        self,
        agent_id: str,
        response_callback: Optional[Callable[[str, AgentCapabilities], None]] = None,
    ):
        super().__init__(agent_id)
        self.response_callback = response_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.AGENT_RESPONSE]

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle agent response message"""
        try:
            caps_data = message.payload.get("agent_capabilities", {})
            if caps_data:
                agent_caps = AgentCapabilities(**caps_data)
                if self.response_callback:
                    try:
                        self.response_callback(message.source, agent_caps)
                    except Exception as e:
                        logger.error(f"Error in response callback: {e}")
                logger.info(f"Processed agent response from {message.source}")
        except Exception as e:
            logger.error(f"Error processing agent response: {e}")
        return None


class HelpWantedHandler(BaseMessageHandler):
    """Handler for help wanted messages"""

    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        help_callback: Optional[Callable[[str, List[str], str], bool]] = None,
    ):
        super().__init__(agent_id)
        self.capabilities = capabilities
        self.help_callback = help_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.HELP_WANTED]

    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate help wanted message"""
        super().validate_message(message)
        if "required_capabilities" not in message.payload:
            raise MessageValidationError(
                "Help wanted must contain 'required_capabilities' in payload"
            )
        if "description" not in message.payload:
            raise MessageValidationError(
                "Help wanted must contain 'description' in payload"
            )

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle help wanted request"""
        required_caps = message.payload["required_capabilities"]
        description = message.payload["description"]
        can_help = any((cap in self.capabilities for cap in required_caps))
        if self.help_callback:
            try:
                can_help = self.help_callback(
                    message.source, required_caps, description
                )
            except Exception as e:
                logger.error(f"Error in help callback: {e}")
        if can_help:
            matching_caps = [cap for cap in required_caps if cap in self.capabilities]
            confidence = (
                len(matching_caps) / len(required_caps) if required_caps else 0.0
            )
            response = BeastModeMessage(
                type=MessageType.HELP_RESPONSE,
                source=self.agent_id,
                target=message.source,
                payload={
                    "request_id": message.payload.get("request_id", message.id),
                    "can_help": True,
                    "matching_capabilities": matching_caps,
                    "confidence_score": confidence,
                    "agent_capabilities": self.capabilities,
                    "response_message": f"I can help with: {', '.join(matching_caps)}",
                },
                correlation_id=message.id,
                priority=message.priority,
            )
            logger.info(
                f"Offering help to {message.source} (confidence: {confidence:.2f})"
            )
            return response
        logger.debug(f"Cannot help with request from {message.source}")
        return None


class HelpResponseHandler(BaseMessageHandler):
    """Handler for help response messages"""

    def __init__(
        self,
        agent_id: str,
        response_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        super().__init__(agent_id)
        self.response_callback = response_callback
        self.pending_requests: Dict[str, BeastModeMessage] = {}

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.HELP_RESPONSE]

    def track_help_request(self, request: BeastModeMessage) -> None:
        """Track a sent help request for correlation"""
        if request.type == MessageType.HELP_WANTED:
            request_id = request.payload.get("request_id", request.id)
            self.pending_requests[request_id] = request

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle help response"""
        request_id = message.payload.get("request_id")
        can_help = message.payload.get("can_help", False)
        if self.response_callback and can_help:
            try:
                self.response_callback(message.source, message.payload)
            except Exception as e:
                logger.error(f"Error in help response callback: {e}")
        logger.info(
            f"Received help response from {message.source} (can_help: {can_help})"
        )
        return None


class SporeDeliveryHandler(BaseMessageHandler):
    """Handler for spore delivery messages"""

    def __init__(
        self,
        agent_id: str,
        spore_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
    ):
        super().__init__(agent_id)
        self.spore_callback = spore_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SPORE_DELIVERY]

    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate spore delivery message"""
        super().validate_message(message)
        if "spore_name" not in message.payload:
            raise MessageValidationError(
                "Spore delivery must contain 'spore_name' in payload"
            )
        if "spore_content" not in message.payload:
            raise MessageValidationError(
                "Spore delivery must contain 'spore_content' in payload"
            )

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle spore delivery"""
        spore_name = message.payload["spore_name"]
        spore_content = message.payload["spore_content"]
        metadata = message.payload.get("metadata", {})
        if self.spore_callback:
            try:
                self.spore_callback(
                    message.source,
                    spore_name,
                    {
                        "content": spore_content,
                        "metadata": metadata,
                        "delivered_at": datetime.now().isoformat(),
                    },
                )
            except Exception as e:
                logger.error(f"Error in spore callback: {e}")
        logger.info(f"Received spore '{spore_name}' from {message.source}")
        return None


class SporeRequestHandler(BaseMessageHandler):
    """Handler for spore request messages"""

    def __init__(
        self,
        agent_id: str,
        spore_provider: Optional[Callable[[str], Optional[Dict[str, Any]]]] = None,
    ):
        super().__init__(agent_id)
        self.spore_provider = spore_provider

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SPORE_REQUEST]

    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate spore request message"""
        super().validate_message(message)
        if "spore_name" not in message.payload:
            raise MessageValidationError(
                "Spore request must contain 'spore_name' in payload"
            )

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle spore request"""
        spore_name = message.payload["spore_name"]
        if self.spore_provider:
            try:
                spore_data = self.spore_provider(spore_name)
                if spore_data:
                    response = BeastModeMessage(
                        type=MessageType.SPORE_DELIVERY,
                        source=self.agent_id,
                        target=message.source,
                        payload={
                            "spore_name": spore_name,
                            "spore_content": spore_data.get("content", ""),
                            "metadata": spore_data.get("metadata", {}),
                            "requested_by": message.source,
                        },
                        correlation_id=message.id,
                        priority=message.priority,
                    )
                    logger.info(f"Delivering spore '{spore_name}' to {message.source}")
                    return response
                else:
                    logger.info(f"Spore '{spore_name}' not found for {message.source}")
            except Exception as e:
                logger.error(f"Error providing spore: {e}")
        return None


class TechnicalExchangeHandler(BaseMessageHandler):
    """Handler for technical exchange messages"""

    def __init__(
        self,
        agent_id: str,
        tech_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        super().__init__(agent_id)
        self.tech_callback = tech_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.TECHNICAL_EXCHANGE]

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle technical exchange message"""
        if self.tech_callback:
            try:
                self.tech_callback(message.source, message.payload)
            except Exception as e:
                logger.error(f"Error in technical exchange callback: {e}")
        logger.info(f"Received technical exchange from {message.source}")
        return None


class SporeSpawnHandler(BaseMessageHandler):
    """Handler for spore spawn messages"""

    def __init__(
        self,
        agent_id: str,
        spawn_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None,
    ):
        super().__init__(agent_id)
        self.spawn_callback = spawn_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SPORE_SPAWN]

    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate spore spawn message"""
        super().validate_message(message)
        if "spore_type" not in message.payload:
            raise MessageValidationError(
                "Spore spawn must contain 'spore_type' in payload"
            )

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle spore spawn message"""
        spore_type = message.payload["spore_type"]
        metadata = message.payload.get("metadata", {})
        if self.spawn_callback:
            try:
                self.spawn_callback(message.source, spore_type, metadata)
            except Exception as e:
                logger.error(f"Error in spawn callback: {e}")
        logger.info(
            f"Received spore spawn request for '{spore_type}' from {message.source}"
        )
        return None


class SystemHealthHandler(BaseMessageHandler):
    """Handler for system health messages"""

    def __init__(
        self,
        agent_id: str,
        health_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        super().__init__(agent_id)
        self.health_callback = health_callback

    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SYSTEM_HEALTH]

    async def handle_message(
        self, message: BeastModeMessage
    ) -> Optional[BeastModeMessage]:
        """Handle system health message"""
        if self.health_callback:
            try:
                self.health_callback(message.source, message.payload)
            except Exception as e:
                logger.error(f"Error in health callback: {e}")
        logger.debug(f"Received health update from {message.source}")
        return None
