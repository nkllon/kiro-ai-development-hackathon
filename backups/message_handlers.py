"""
Beast Mode Message Type Handlers

Implements standardized handlers for each MessageType enum value with routing,
validation, and compatibility layers.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum

from .models import BeastModeMessage, MessageType, AgentCapabilities


logger = logging.getLogger(__name__)


class MessageHandlerResult(Enum):
    """Result of message handling"""
    SUCCESS = "success"
    HANDLED = "handled"
    IGNORED = "ignored"
    ERROR = "error"
    RETRY = "retry"


class MessageValidationError(Exception):
    """Raised when message validation fails"""
    pass


class MessageCompatibilityError(Exception):
    """Raised when message format is incompatible"""
    pass


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
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
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
    
    async def _handle_with_stats(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
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
            "last_handled": self.last_handled.isoformat() if self.last_handled else None
        }


class SimpleMessageHandler(BaseMessageHandler):
    """Handler for simple text messages"""
    
    def __init__(self, agent_id: str, message_callback: Optional[Callable[[str, str], None]] = None):
        super().__init__(agent_id)
        self.message_callback = message_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SIMPLE_MESSAGE]
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle simple text message"""
        content = message.payload.get("content", "")
        
        if self.message_callback:
            try:
                self.message_callback(message.source, content)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")
                raise  # Re-raise to be caught by error handling
        
        logger.info(f"Received simple message from {message.source}: {content}")
        return None


class PromptRequestHandler(BaseMessageHandler):
    """Handler for prompt requests"""
    
    def __init__(self, agent_id: str, prompt_processor: Optional[Callable[[str], str]] = None):
        super().__init__(agent_id)
        self.prompt_processor = prompt_processor
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.PROMPT_REQUEST]
    
    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate prompt request message"""
        super().validate_message(message)
        
        if "prompt" not in message.payload:
            raise MessageValidationError("Prompt request must contain 'prompt' in payload")
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle prompt request and generate response"""
        prompt = message.payload["prompt"]
        
        # Process prompt if processor is available
        response_text = "Prompt received"
        if self.prompt_processor:
            try:
                response_text = self.prompt_processor(prompt)
            except Exception as e:
                logger.error(f"Error processing prompt: {e}")
                response_text = f"Error processing prompt: {str(e)}"
        
        # Create response message
        response = BeastModeMessage(
            type=MessageType.PROMPT_RESPONSE,
            source=self.agent_id,
            target=message.source,
            payload={
                "response": response_text,
                "original_prompt": prompt,
                "processed_at": datetime.now().isoformat()
            },
            correlation_id=message.id,
            priority=message.priority
        )
        
        logger.info(f"Processed prompt request from {message.source}")
        return response


class PromptResponseHandler(BaseMessageHandler):
    """Handler for prompt responses"""
    
    def __init__(self, agent_id: str, response_callback: Optional[Callable[[str, str, str], None]] = None):
        super().__init__(agent_id)
        self.response_callback = response_callback
        self.pending_requests: Dict[str, BeastModeMessage] = {}
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.PROMPT_RESPONSE]
    
    def track_request(self, request: BeastModeMessage) -> None:
        """Track a sent prompt request for correlation"""
        if request.type == MessageType.PROMPT_REQUEST:
            self.pending_requests[request.id] = request
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle prompt response"""
        response_text = message.payload.get("response", "")
        correlation_id = message.correlation_id
        
        # Find original request if available
        original_request = None
        if correlation_id and correlation_id in self.pending_requests:
            original_request = self.pending_requests.pop(correlation_id)
        
        if self.response_callback:
            try:
                original_prompt = original_request.payload.get("prompt", "") if original_request else ""
                self.response_callback(message.source, response_text, original_prompt)
            except Exception as e:
                logger.error(f"Error in response callback: {e}")
        
        logger.info(f"Received prompt response from {message.source}")
        return None


class AgentDiscoveryHandler(BaseMessageHandler):
    """Handler for agent discovery messages"""
    
    def __init__(self, agent_id: str, capabilities: List[str], discovery_callback: Optional[Callable[[str, AgentCapabilities], None]] = None):
        super().__init__(agent_id)
        self.capabilities = capabilities
        self.discovery_callback = discovery_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.AGENT_DISCOVERY]
    
    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate agent discovery message"""
        super().validate_message(message)
        
        if "agent_capabilities" not in message.payload:
            raise MessageValidationError("Agent discovery must contain 'agent_capabilities' in payload")
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle agent discovery and respond with capabilities"""
        try:
            # Parse discovered agent capabilities
            caps_data = message.payload["agent_capabilities"]
            discovered_caps = AgentCapabilities(**caps_data)
            
            if self.discovery_callback:
                try:
                    self.discovery_callback(message.source, discovered_caps)
                except Exception as e:
                    logger.error(f"Error in discovery callback: {e}")
            
            # Create response with our capabilities
            our_capabilities = AgentCapabilities(
                agent_id=self.agent_id,
                capabilities=self.capabilities,
                availability="ready_for_business"
            )
            
            response = BeastModeMessage(
                type=MessageType.AGENT_RESPONSE,
                source=self.agent_id,
                target=message.source,
                payload={
                    "agent_capabilities": our_capabilities.model_dump(),
                    "response_to": message.id
                },
                correlation_id=message.id,
                priority=3
            )
            
            logger.info(f"Responded to discovery from {message.source}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing agent discovery: {e}")
            return None


class AgentResponseHandler(BaseMessageHandler):
    """Handler for agent response messages"""
    
    def __init__(self, agent_id: str, response_callback: Optional[Callable[[str, AgentCapabilities], None]] = None):
        super().__init__(agent_id)
        self.response_callback = response_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.AGENT_RESPONSE]
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle agent response message"""
        try:
            # Parse agent capabilities from response
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
    
    def __init__(self, agent_id: str, capabilities: List[str], help_callback: Optional[Callable[[str, List[str], str], bool]] = None):
        super().__init__(agent_id)
        self.capabilities = capabilities
        self.help_callback = help_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.HELP_WANTED]
    
    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate help wanted message"""
        super().validate_message(message)
        
        if "required_capabilities" not in message.payload:
            raise MessageValidationError("Help wanted must contain 'required_capabilities' in payload")
        
        if "description" not in message.payload:
            raise MessageValidationError("Help wanted must contain 'description' in payload")
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle help wanted request"""
        required_caps = message.payload["required_capabilities"]
        description = message.payload["description"]
        
        # Check if we can help (have any of the required capabilities)
        can_help = any(cap in self.capabilities for cap in required_caps)
        
        if self.help_callback:
            try:
                can_help = self.help_callback(message.source, required_caps, description)
            except Exception as e:
                logger.error(f"Error in help callback: {e}")
        
        if can_help:
            # Calculate confidence score based on capability match
            matching_caps = [cap for cap in required_caps if cap in self.capabilities]
            confidence = len(matching_caps) / len(required_caps) if required_caps else 0.0
            
            # Create help response
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
                    "response_message": f"I can help with: {', '.join(matching_caps)}"
                },
                correlation_id=message.id,
                priority=message.priority
            )
            
            logger.info(f"Offering help to {message.source} (confidence: {confidence:.2f})")
            return response
        
        logger.debug(f"Cannot help with request from {message.source}")
        return None


class HelpResponseHandler(BaseMessageHandler):
    """Handler for help response messages"""
    
    def __init__(self, agent_id: str, response_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
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
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle help response"""
        request_id = message.payload.get("request_id")
        can_help = message.payload.get("can_help", False)
        
        if self.response_callback and can_help:
            try:
                self.response_callback(message.source, message.payload)
            except Exception as e:
                logger.error(f"Error in help response callback: {e}")
        
        logger.info(f"Received help response from {message.source} (can_help: {can_help})")
        return None


class SporeDeliveryHandler(BaseMessageHandler):
    """Handler for spore delivery messages"""
    
    def __init__(self, agent_id: str, spore_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None):
        super().__init__(agent_id)
        self.spore_callback = spore_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SPORE_DELIVERY]
    
    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate spore delivery message"""
        super().validate_message(message)
        
        if "spore_name" not in message.payload:
            raise MessageValidationError("Spore delivery must contain 'spore_name' in payload")
        
        if "spore_content" not in message.payload:
            raise MessageValidationError("Spore delivery must contain 'spore_content' in payload")
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle spore delivery"""
        spore_name = message.payload["spore_name"]
        spore_content = message.payload["spore_content"]
        metadata = message.payload.get("metadata", {})
        
        if self.spore_callback:
            try:
                self.spore_callback(message.source, spore_name, {
                    "content": spore_content,
                    "metadata": metadata,
                    "delivered_at": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error in spore callback: {e}")
        
        logger.info(f"Received spore '{spore_name}' from {message.source}")
        return None


class SporeRequestHandler(BaseMessageHandler):
    """Handler for spore request messages"""
    
    def __init__(self, agent_id: str, spore_provider: Optional[Callable[[str], Optional[Dict[str, Any]]]] = None):
        super().__init__(agent_id)
        self.spore_provider = spore_provider
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SPORE_REQUEST]
    
    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate spore request message"""
        super().validate_message(message)
        
        if "spore_name" not in message.payload:
            raise MessageValidationError("Spore request must contain 'spore_name' in payload")
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle spore request"""
        spore_name = message.payload["spore_name"]
        
        if self.spore_provider:
            try:
                spore_data = self.spore_provider(spore_name)
                
                if spore_data:
                    # Create spore delivery response
                    response = BeastModeMessage(
                        type=MessageType.SPORE_DELIVERY,
                        source=self.agent_id,
                        target=message.source,
                        payload={
                            "spore_name": spore_name,
                            "spore_content": spore_data.get("content", ""),
                            "metadata": spore_data.get("metadata", {}),
                            "requested_by": message.source
                        },
                        correlation_id=message.id,
                        priority=message.priority
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
    
    def __init__(self, agent_id: str, tech_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        super().__init__(agent_id)
        self.tech_callback = tech_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.TECHNICAL_EXCHANGE]
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
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
    
    def __init__(self, agent_id: str, spawn_callback: Optional[Callable[[str, str, Dict[str, Any]], None]] = None):
        super().__init__(agent_id)
        self.spawn_callback = spawn_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SPORE_SPAWN]
    
    def validate_message(self, message: BeastModeMessage) -> None:
        """Validate spore spawn message"""
        super().validate_message(message)
        
        if "spore_type" not in message.payload:
            raise MessageValidationError("Spore spawn must contain 'spore_type' in payload")
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle spore spawn message"""
        spore_type = message.payload["spore_type"]
        metadata = message.payload.get("metadata", {})
        
        if self.spawn_callback:
            try:
                self.spawn_callback(message.source, spore_type, metadata)
            except Exception as e:
                logger.error(f"Error in spawn callback: {e}")
        
        logger.info(f"Received spore spawn request for '{spore_type}' from {message.source}")
        return None


class SystemHealthHandler(BaseMessageHandler):
    """Handler for system health messages"""
    
    def __init__(self, agent_id: str, health_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        super().__init__(agent_id)
        self.health_callback = health_callback
    
    def get_supported_types(self) -> List[MessageType]:
        return [MessageType.SYSTEM_HEALTH]
    
    async def handle_message(self, message: BeastModeMessage) -> Optional[BeastModeMessage]:
        """Handle system health message"""
        if self.health_callback:
            try:
                self.health_callback(message.source, message.payload)
            except Exception as e:
                logger.error(f"Error in health callback: {e}")
        
        logger.debug(f"Received health update from {message.source}")
        return None


class MessageRouter:
    """Routes messages to appropriate handlers with validation and compatibility"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.handlers: Dict[MessageType, List[BaseMessageHandler]] = {}
        self.fallback_handlers: List[BaseMessageHandler] = []
        
        # Statistics
        self.stats = {
            'messages_routed': 0,
            'messages_handled': 0,
            'validation_errors': 0,
            'compatibility_errors': 0,
            'handler_errors': 0,
            'last_activity': None
        }
        
        # Compatibility settings
        self.strict_validation = False
        self.auto_convert_legacy = True
    
    def register_handler(self, handler: BaseMessageHandler) -> None:
        """Register a message handler"""
        for msg_type in handler.get_supported_types():
            if msg_type not in self.handlers:
                self.handlers[msg_type] = []
            self.handlers[msg_type].append(handler)
        
        logger.info(f"Registered {handler.__class__.__name__} for types: {[t.value for t in handler.get_supported_types()]}")
    
    def register_fallback_handler(self, handler: BaseMessageHandler) -> None:
        """Register a fallback handler for unhandled message types"""
        self.fallback_handlers.append(handler)
        logger.info(f"Registered fallback handler: {handler.__class__.__name__}")
    
    def _convert_legacy_message(self, message_data: Dict[str, Any]) -> BeastModeMessage:
        """
        Convert legacy message formats to current format.
        
        Args:
            message_data: Raw message data
            
        Returns:
            BeastModeMessage: Converted message
            
        Raises:
            MessageCompatibilityError: If conversion fails
        """
        try:
            # Handle missing required fields with defaults
            if "type" not in message_data:
                message_data["type"] = MessageType.SIMPLE_MESSAGE.value
            
            if "source" not in message_data:
                message_data["source"] = "unknown_agent"
            
            # Convert old message type formats
            msg_type = message_data["type"]
            if isinstance(msg_type, str):
                # Handle legacy type names
                type_mapping = {
                    "message": MessageType.SIMPLE_MESSAGE.value,
                    "request": MessageType.PROMPT_REQUEST.value,
                    "response": MessageType.PROMPT_RESPONSE.value,
                    "discovery": MessageType.AGENT_DISCOVERY.value,
                    "help": MessageType.HELP_WANTED.value,
                    "spore": MessageType.SPORE_DELIVERY.value
                }
                
                if msg_type in type_mapping:
                    message_data["type"] = type_mapping[msg_type]
            
            # Ensure payload exists
            if "payload" not in message_data:
                message_data["payload"] = {}
            
            # Convert timestamp if needed
            if "timestamp" in message_data and isinstance(message_data["timestamp"], str):
                try:
                    message_data["timestamp"] = datetime.fromisoformat(message_data["timestamp"].replace('Z', '+00:00'))
                except ValueError:
                    message_data["timestamp"] = datetime.now()
            
            return BeastModeMessage(**message_data)
            
        except Exception as e:
            raise MessageCompatibilityError(f"Failed to convert legacy message: {e}")
    
    async def route_message(self, message: Union[BeastModeMessage, Dict[str, Any]]) -> List[BeastModeMessage]:
        """
        Route a message to appropriate handlers.
        
        Args:
            message: Message to route (BeastModeMessage or dict)
            
        Returns:
            List of response messages from handlers
        """
        responses = []
        self.stats['messages_routed'] += 1
        self.stats['last_activity'] = datetime.now()
        
        try:
            # Convert to BeastModeMessage if needed
            if isinstance(message, dict):
                try:
                    beast_message = BeastModeMessage(**message)
                except Exception as e:
                    if self.auto_convert_legacy:
                        try:
                            beast_message = self._convert_legacy_message(message)
                            logger.info(f"Converted legacy message format: {message.get('type', 'unknown')}")
                        except MessageCompatibilityError as ce:
                            self.stats['compatibility_errors'] += 1
                            logger.error(f"Message compatibility error: {ce}")
                            return responses
                    else:
                        self.stats['validation_errors'] += 1
                        logger.error(f"Message validation error: {e}")
                        return responses
            else:
                beast_message = message
            
            # Skip messages from self
            if beast_message.source == self.agent_id:
                return responses
            
            # Check if message is targeted to us or is broadcast
            if beast_message.target and beast_message.target != self.agent_id:
                logger.debug(f"Message not targeted to us (target: {beast_message.target})")
                return responses
            
            # Find handlers for this message type
            handlers = self.handlers.get(beast_message.type, [])
            
            if not handlers and self.fallback_handlers:
                # Use fallback handlers if no specific handler found
                handlers = [h for h in self.fallback_handlers if h.can_handle(beast_message)]
            
            if not handlers:
                logger.debug(f"No handlers found for message type: {beast_message.type}")
                return responses
            
            # Process with each handler
            for handler in handlers:
                try:
                    response = await handler._handle_with_stats(beast_message)
                    if response:
                        responses.append(response)
                    self.stats['messages_handled'] += 1
                    
                except MessageValidationError as e:
                    self.stats['validation_errors'] += 1
                    if self.strict_validation:
                        logger.error(f"Validation error in {handler.__class__.__name__}: {e}")
                    else:
                        logger.warning(f"Validation warning in {handler.__class__.__name__}: {e}")
                
                except Exception as e:
                    self.stats['handler_errors'] += 1
                    logger.error(f"Handler error in {handler.__class__.__name__}: {e}")
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
        
        return responses
    
    def get_supported_types(self) -> List[MessageType]:
        """Get all supported message types"""
        return list(self.handlers.keys())
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get detailed handler statistics"""
        handler_stats = {}
        
        for msg_type, handlers in self.handlers.items():
            handler_stats[msg_type.value] = [h.get_stats() for h in handlers]
        
        return {
            "router_stats": self.stats.copy(),
            "handler_stats": handler_stats,
            "fallback_handlers": len(self.fallback_handlers),
            "supported_types": [t.value for t in self.get_supported_types()]
        }
    
    def validate_message_format(self, message_data: Dict[str, Any]) -> bool:
        """
        Validate message format without processing.
        
        Args:
            message_data: Raw message data
            
        Returns:
            bool: True if valid format
        """
        try:
            BeastModeMessage(**message_data)
            return True
        except Exception:
            return False