"""
Message Router Core Core Core

This module was extracted from message_router_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .message_handlers import MessageRouter, BaseMessageHandler, SimpleMessageHandler, PromptRequestHandler, PromptResponseHandler, AgentDiscoveryHandler, AgentResponseHandler, HelpWantedHandler, HelpResponseHandler, SporeDeliveryHandler, SporeRequestHandler, SporeSpawnHandler, TechnicalExchangeHandler, SystemHealthHandler, MessageValidationError, MessageCompatibilityError

class StandardMessageRouter(MessageRouter):
    """
    Standard message router with built-in handlers for all MessageType enum values.
    Provides a complete message handling system with callbacks and customization.
    """

    def __init__(self, agent_id: str, capabilities: Optional[List[str]]=None, callbacks: Optional[Dict[str, Callable]]=None):
        super().__init__(agent_id)
        self.capabilities = capabilities or []
        self.callbacks = callbacks or {}
        self._setup_standard_handlers()
        self.sent_messages: Dict[str, BeastModeMessage] = {}
        self.received_messages: List[BeastModeMessage] = []
        self.max_history = 1000
        self.enable_auto_responses = True
        self.auto_convert_legacy = False

    def _setup_standard_handlers(self) -> None:
        """Setup standard handlers for all message types"""
        simple_handler = SimpleMessageHandler(self.agent_id, message_callback=self.callbacks.get('on_simple_message'))
        self.register_handler(simple_handler)
        prompt_handler = PromptRequestHandler(self.agent_id, prompt_processor=self.callbacks.get('on_prompt_request'))
        self.register_handler(prompt_handler)
        response_handler = PromptResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_prompt_response'))
        self.register_handler(response_handler)
        discovery_handler = AgentDiscoveryHandler(self.agent_id, self.capabilities, discovery_callback=self.callbacks.get('on_agent_discovery'))
        self.register_handler(discovery_handler)
        agent_response_handler = AgentResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_agent_response'))
        self.register_handler(agent_response_handler)
        help_handler = HelpWantedHandler(self.agent_id, self.capabilities, help_callback=self.callbacks.get('on_help_wanted'))
        self.register_handler(help_handler)
        help_response_handler = HelpResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_help_response'))
        self.register_handler(help_response_handler)
        spore_handler = SporeDeliveryHandler(self.agent_id, spore_callback=self.callbacks.get('on_spore_delivery'))
        self.register_handler(spore_handler)
        spore_request_handler = SporeRequestHandler(self.agent_id, spore_provider=self.callbacks.get('on_spore_request'))
        self.register_handler(spore_request_handler)
        spore_spawn_handler = SporeSpawnHandler(self.agent_id, spawn_callback=self.callbacks.get('on_spore_spawn'))
        self.register_handler(spore_spawn_handler)
        tech_handler = TechnicalExchangeHandler(self.agent_id, tech_callback=self.callbacks.get('on_technical_exchange'))
        self.register_handler(tech_handler)
        health_handler = SystemHealthHandler(self.agent_id, health_callback=self.callbacks.get('on_system_health'))
        self.register_handler(health_handler)
        logger.info(f'Initialized standard message router for agent {self.agent_id}')

    async def process_message(self, message: Union[BeastModeMessage, Dict[str, Any]]) -> List[BeastModeMessage]:
        """
        Process an incoming message and return any responses.
        
        Args:
            message: Message to process
            
        Returns:
            List of response messages
        """
        if isinstance(message, BeastModeMessage):
            self.received_messages.append(message)
            self._trim_history()
        responses = await self.route_message(message)
        for response in responses:
            self.sent_messages[response.id] = response
        return responses

    def track_sent_message(self, message: BeastModeMessage) -> None:
        """Track a message that was sent for correlation"""
        self.sent_messages[message.id] = message
        for handlers in self.handlers.values():
            for handler in handlers:
                if hasattr(handler, 'track_request') and message.type == MessageType.PROMPT_REQUEST:
                    handler.track_request(message)
                elif hasattr(handler, 'track_help_request') and message.type == MessageType.HELP_WANTED:
                    handler.track_help_request(message)
        self._trim_history()

    def _trim_history(self) -> None:
        """Trim message history to prevent memory growth"""
        if len(self.received_messages) > self.max_history:
            self.received_messages = self.received_messages[-self.max_history:]
        if len(self.sent_messages) > self.max_history:
            sorted_messages = sorted(self.sent_messages.items(), key=lambda x: x[1].timestamp)
            to_remove = len(sorted_messages) - self.max_history
            for i in range(to_remove):
                del self.sent_messages[sorted_messages[i][0]]

    def update_capabilities(self, capabilities: List[str]) -> None:
        """Update agent capabilities and notify handlers"""
        self.capabilities = capabilities
        for handlers in self.handlers.values():
            for handler in handlers:
                if hasattr(handler, 'capabilities'):
                    handler.capabilities = capabilities
        logger.info(f'Updated capabilities for agent {self.agent_id}: {capabilities}')

    def set_callback(self, callback_name: str, callback: Callable) -> None:
        """Set or update a callback function"""
        self.callbacks[callback_name] = callback
        logger.info(f'Updated callback: {callback_name}')

    def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
        """
        Get message history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Dict with 'sent' and 'received' message lists
        """
        sent_list = list(self.sent_messages.values())
        received_list = self.received_messages
        if limit is not None:
            sent_list = sent_list[-limit:] if limit > 0 else []
            received_list = received_list[-limit:] if limit > 0 else []
        return {'sent': sent_list, 'received': received_list}

    def get_correlation_info(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get correlation information for a message.
        
        Args:
            message_id: Message ID to look up
            
        Returns:
            Correlation information if found
        """
        if message_id in self.sent_messages:
            sent_msg = self.sent_messages[message_id]
            related = []
            for msg in self.received_messages:
                if msg.correlation_id == message_id:
                    related.append(msg)
            return {'original_message': sent_msg, 'related_messages': related, 'type': 'sent'}
        for msg in self.received_messages:
            if msg.id == message_id:
                original = None
                if msg.correlation_id and msg.correlation_id in self.sent_messages:
                    original = self.sent_messages[msg.correlation_id]
                return {'original_message': original, 'received_message': msg, 'type': 'received'}
        return None

    def validate_message_compatibility(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate message compatibility and return validation info.
        
        Args:
            message_data: Raw message data
            
        Returns:
            Validation result with details
        """
        result = {'is_valid': False, 'is_legacy': False, 'errors': [], 'warnings': [], 'converted_message': None}
        try:
            message = BeastModeMessage(**message_data)
            result['is_valid'] = True
            result['converted_message'] = message
        except Exception as e:
            result['errors'].append(str(e))
            if self.auto_convert_legacy:
                try:
                    message_copy = message_data.copy()
                    converted = self._convert_legacy_message(message_copy)
                    result['is_valid'] = True
                    result['is_legacy'] = True
                    result['converted_message'] = converted
                    result['warnings'].append('Message was converted from legacy format')
                except MessageCompatibilityError as ce:
                    result['errors'].append(f'Legacy conversion failed: {ce}')
        return result

    def get_handler_info(self) -> Dict[str, Any]:
        """Get detailed information about registered handlers"""
        info = {'agent_id': self.agent_id, 'capabilities': self.capabilities, 'handlers_by_type': {}, 'total_handlers': 0, 'callback_status': {}}
        for msg_type, handlers in self.handlers.items():
            info['handlers_by_type'][msg_type.value] = [h.get_stats() for h in handlers]
            info['total_handlers'] += len(handlers)
        expected_callbacks = ['on_simple_message', 'on_prompt_request', 'on_prompt_response', 'on_agent_discovery', 'on_agent_response', 'on_help_wanted', 'on_help_response', 'on_spore_delivery', 'on_spore_request', 'on_spore_spawn', 'on_technical_exchange', 'on_system_health']
        for callback_name in expected_callbacks:
            info['callback_status'][callback_name] = callback_name in self.callbacks
        return info

    def create_test_message(self, msg_type: MessageType, **kwargs) -> BeastModeMessage:
        """
        Create a test message for a specific type.
        
        Args:
            msg_type: Message type to create
            **kwargs: Additional message parameters
            
        Returns:
            Test message
        """
        base_payload = {}
        if msg_type == MessageType.PROMPT_REQUEST:
            base_payload['prompt'] = kwargs.get('prompt', 'Test prompt')
        elif msg_type == MessageType.PROMPT_RESPONSE:
            base_payload['response'] = kwargs.get('response', 'Test response')
        elif msg_type == MessageType.AGENT_DISCOVERY:
            base_payload['agent_capabilities'] = AgentCapabilities(agent_id=kwargs.get('test_agent_id', 'test_agent'), capabilities=kwargs.get('test_capabilities', ['testing'])).model_dump()
        elif msg_type == MessageType.AGENT_RESPONSE:
            base_payload['agent_capabilities'] = AgentCapabilities(agent_id=kwargs.get('test_agent_id', 'test_agent'), capabilities=kwargs.get('test_capabilities', ['testing'])).model_dump()
        elif msg_type == MessageType.HELP_WANTED:
            base_payload['required_capabilities'] = kwargs.get('required_capabilities', ['testing'])
            base_payload['description'] = kwargs.get('description', 'Test help request')
        elif msg_type == MessageType.HELP_RESPONSE:
            base_payload['request_id'] = kwargs.get('request_id', 'test_request_id')
            base_payload['can_help'] = kwargs.get('can_help', True)
        elif msg_type == MessageType.SPORE_DELIVERY:
            base_payload['spore_name'] = kwargs.get('spore_name', 'test_spore')
            base_payload['spore_content'] = kwargs.get('spore_content', 'Test spore content')
        elif msg_type == MessageType.SPORE_REQUEST:
            base_payload['spore_name'] = kwargs.get('spore_name', 'test_spore')
        elif msg_type == MessageType.SPORE_SPAWN:
            base_payload['spore_type'] = kwargs.get('spore_type', 'test_spore_type')
        elif msg_type == MessageType.SIMPLE_MESSAGE:
            base_payload['content'] = kwargs.get('content', 'Test message')
        payload = {**base_payload, **kwargs.get('payload', {})}
        return BeastModeMessage(type=msg_type, source=kwargs.get('source', 'test_source'), target=kwargs.get('target'), payload=payload, priority=kwargs.get('priority', 5))

class MessageTypeRegistry:
    """Registry for message type information and validation"""

    def __init__(self):
        self.type_info = self._build_type_info()

    def _build_type_info(self) -> Dict[MessageType, Dict[str, Any]]:
        """Build comprehensive type information"""
        return {MessageType.SIMPLE_MESSAGE: {'description': 'Basic text communication between agents', 'required_fields': ['content'], 'optional_fields': ['context', 'metadata'], 'response_type': None, 'handler_class': 'SimpleMessageHandler'}, MessageType.PROMPT_REQUEST: {'description': 'Request for processing a prompt', 'required_fields': ['prompt'], 'optional_fields': ['context', 'parameters', 'timeout'], 'response_type': MessageType.PROMPT_RESPONSE, 'handler_class': 'PromptRequestHandler'}, MessageType.PROMPT_RESPONSE: {'description': 'Response to a prompt request', 'required_fields': ['response'], 'optional_fields': ['original_prompt', 'processed_at', 'metadata'], 'response_type': None, 'handler_class': 'PromptResponseHandler'}, MessageType.AGENT_DISCOVERY: {'description': 'Agent presence announcement', 'required_fields': ['agent_capabilities'], 'optional_fields': ['announcement', 'metadata'], 'response_type': MessageType.AGENT_RESPONSE, 'handler_class': 'AgentDiscoveryHandler'}, MessageType.AGENT_RESPONSE: {'description': 'Response to agent discovery', 'required_fields': ['agent_capabilities'], 'optional_fields': ['response_to', 'metadata'], 'response_type': None, 'handler_class': 'AgentResponseHandler'}, MessageType.HELP_WANTED: {'description': 'Request for assistance with specific capabilities', 'required_fields': ['required_capabilities', 'description'], 'optional_fields': ['urgency', 'max_helpers', 'timeout_hours', 'context'], 'response_type': MessageType.HELP_RESPONSE, 'handler_class': 'HelpWantedHandler'}, MessageType.HELP_RESPONSE: {'description': 'Offer to help with a request', 'required_fields': ['request_id', 'can_help'], 'optional_fields': ['matching_capabilities', 'confidence_score', 'response_message'], 'response_type': None, 'handler_class': 'HelpResponseHandler'}, MessageType.SPORE_DELIVERY: {'description': 'Delivery of a spore with methodology', 'required_fields': ['spore_name', 'spore_content'], 'optional_fields': ['metadata', 'version', 'dependencies'], 'response_type': None, 'handler_class': 'SporeDeliveryHandler'}, MessageType.SPORE_REQUEST: {'description': 'Request for a specific spore', 'required_fields': ['spore_name'], 'optional_fields': ['version', 'metadata'], 'response_type': MessageType.SPORE_DELIVERY, 'handler_class': 'SporeRequestHandler'}, MessageType.TECHNICAL_EXCHANGE: {'description': 'Technical information exchange', 'required_fields': [], 'optional_fields': ['topic', 'data', 'metadata'], 'response_type': None, 'handler_class': 'TechnicalExchangeHandler'}, MessageType.SPORE_SPAWN: {'description': 'Spore spawn request for creating new spores', 'required_fields': ['spore_type'], 'optional_fields': ['metadata', 'parameters'], 'response_type': None, 'handler_class': 'SporeSpawnHandler'}, MessageType.SYSTEM_HEALTH: {'description': 'System health and monitoring information', 'required_fields': [], 'optional_fields': ['status', 'metrics', 'alerts'], 'response_type': None, 'handler_class': 'SystemHealthHandler'}}

    def get_type_info(self, msg_type: MessageType) -> Dict[str, Any]:
        """Get information about a message type"""
        return self.type_info.get(msg_type, {})

    def validate_payload(self, msg_type: MessageType, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate message payload for a specific type.
        
        Args:
            msg_type: Message type
            payload: Message payload
            
        Returns:
            Validation result
        """
        type_info = self.get_type_info(msg_type)
        result = {'is_valid': True, 'missing_fields': [], 'extra_fields': [], 'warnings': []}
        if not type_info:
            result['warnings'].append(f'Unknown message type: {msg_type}')
            return result
        required = type_info.get('required_fields', [])
        for field in required:
            if field not in payload:
                result['missing_fields'].append(field)
                result['is_valid'] = False
        expected = required + type_info.get('optional_fields', [])
        for field in payload:
            if field not in expected:
                result['extra_fields'].append(field)
        return result

    def get_all_types(self) -> List[MessageType]:
        """Get all registered message types"""
        return list(self.type_info.keys())

    def get_types_with_responses(self) -> Dict[MessageType, MessageType]:
        """Get message types that expect responses"""
        return {msg_type: info['response_type'] for msg_type, info in self.type_info.items() if info.get('response_type')}

def __init__(self, agent_id: str, capabilities: Optional[List[str]]=None, callbacks: Optional[Dict[str, Callable]]=None):
    super().__init__(agent_id)
    self.capabilities = capabilities or []
    self.callbacks = callbacks or {}
    self._setup_standard_handlers()
    self.sent_messages: Dict[str, BeastModeMessage] = {}
    self.received_messages: List[BeastModeMessage] = []
    self.max_history = 1000
    self.enable_auto_responses = True
    self.auto_convert_legacy = False

def _setup_standard_handlers(self) -> None:
    """Setup standard handlers for all message types"""
    simple_handler = SimpleMessageHandler(self.agent_id, message_callback=self.callbacks.get('on_simple_message'))
    self.register_handler(simple_handler)
    prompt_handler = PromptRequestHandler(self.agent_id, prompt_processor=self.callbacks.get('on_prompt_request'))
    self.register_handler(prompt_handler)
    response_handler = PromptResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_prompt_response'))
    self.register_handler(response_handler)
    discovery_handler = AgentDiscoveryHandler(self.agent_id, self.capabilities, discovery_callback=self.callbacks.get('on_agent_discovery'))
    self.register_handler(discovery_handler)
    agent_response_handler = AgentResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_agent_response'))
    self.register_handler(agent_response_handler)
    help_handler = HelpWantedHandler(self.agent_id, self.capabilities, help_callback=self.callbacks.get('on_help_wanted'))
    self.register_handler(help_handler)
    help_response_handler = HelpResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_help_response'))
    self.register_handler(help_response_handler)
    spore_handler = SporeDeliveryHandler(self.agent_id, spore_callback=self.callbacks.get('on_spore_delivery'))
    self.register_handler(spore_handler)
    spore_request_handler = SporeRequestHandler(self.agent_id, spore_provider=self.callbacks.get('on_spore_request'))
    self.register_handler(spore_request_handler)
    spore_spawn_handler = SporeSpawnHandler(self.agent_id, spawn_callback=self.callbacks.get('on_spore_spawn'))
    self.register_handler(spore_spawn_handler)
    tech_handler = TechnicalExchangeHandler(self.agent_id, tech_callback=self.callbacks.get('on_technical_exchange'))
    self.register_handler(tech_handler)
    health_handler = SystemHealthHandler(self.agent_id, health_callback=self.callbacks.get('on_system_health'))
    self.register_handler(health_handler)
    logger.info(f'Initialized standard message router for agent {self.agent_id}')

def track_sent_message(self, message: BeastModeMessage) -> None:
    """Track a message that was sent for correlation"""
    self.sent_messages[message.id] = message
    for handlers in self.handlers.values():
        for handler in handlers:
            if hasattr(handler, 'track_request') and message.type == MessageType.PROMPT_REQUEST:
                handler.track_request(message)
            elif hasattr(handler, 'track_help_request') and message.type == MessageType.HELP_WANTED:
                handler.track_help_request(message)
    self._trim_history()

def _trim_history(self) -> None:
    """Trim message history to prevent memory growth"""
    if len(self.received_messages) > self.max_history:
        self.received_messages = self.received_messages[-self.max_history:]
    if len(self.sent_messages) > self.max_history:
        sorted_messages = sorted(self.sent_messages.items(), key=lambda x: x[1].timestamp)
        to_remove = len(sorted_messages) - self.max_history
        for i in range(to_remove):
            del self.sent_messages[sorted_messages[i][0]]

def update_capabilities(self, capabilities: List[str]) -> None:
    """Update agent capabilities and notify handlers"""
    self.capabilities = capabilities
    for handlers in self.handlers.values():
        for handler in handlers:
            if hasattr(handler, 'capabilities'):
                handler.capabilities = capabilities
    logger.info(f'Updated capabilities for agent {self.agent_id}: {capabilities}')

def set_callback(self, callback_name: str, callback: Callable) -> None:
    """Set or update a callback function"""
    self.callbacks[callback_name] = callback
    logger.info(f'Updated callback: {callback_name}')

def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
    """
        Get message history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Dict with 'sent' and 'received' message lists
        """
    sent_list = list(self.sent_messages.values())
    received_list = self.received_messages
    if limit is not None:
        sent_list = sent_list[-limit:] if limit > 0 else []
        received_list = received_list[-limit:] if limit > 0 else []
    return {'sent': sent_list, 'received': received_list}

def get_correlation_info(self, message_id: str) -> Optional[Dict[str, Any]]:
    """
        Get correlation information for a message.
        
        Args:
            message_id: Message ID to look up
            
        Returns:
            Correlation information if found
        """
    if message_id in self.sent_messages:
        sent_msg = self.sent_messages[message_id]
        related = []
        for msg in self.received_messages:
            if msg.correlation_id == message_id:
                related.append(msg)
        return {'original_message': sent_msg, 'related_messages': related, 'type': 'sent'}
    for msg in self.received_messages:
        if msg.id == message_id:
            original = None
            if msg.correlation_id and msg.correlation_id in self.sent_messages:
                original = self.sent_messages[msg.correlation_id]
            return {'original_message': original, 'received_message': msg, 'type': 'received'}
    return None

def get_handler_info(self) -> Dict[str, Any]:
    """Get detailed information about registered handlers"""
    info = {'agent_id': self.agent_id, 'capabilities': self.capabilities, 'handlers_by_type': {}, 'total_handlers': 0, 'callback_status': {}}
    for msg_type, handlers in self.handlers.items():
        info['handlers_by_type'][msg_type.value] = [h.get_stats() for h in handlers]
        info['total_handlers'] += len(handlers)
    expected_callbacks = ['on_simple_message', 'on_prompt_request', 'on_prompt_response', 'on_agent_discovery', 'on_agent_response', 'on_help_wanted', 'on_help_response', 'on_spore_delivery', 'on_spore_request', 'on_spore_spawn', 'on_technical_exchange', 'on_system_health']
    for callback_name in expected_callbacks:
        info['callback_status'][callback_name] = callback_name in self.callbacks
    return info

def __init__(self):
    self.type_info = self._build_type_info()

def _build_type_info(self) -> Dict[MessageType, Dict[str, Any]]:
    """Build comprehensive type information"""
    return {MessageType.SIMPLE_MESSAGE: {'description': 'Basic text communication between agents', 'required_fields': ['content'], 'optional_fields': ['context', 'metadata'], 'response_type': None, 'handler_class': 'SimpleMessageHandler'}, MessageType.PROMPT_REQUEST: {'description': 'Request for processing a prompt', 'required_fields': ['prompt'], 'optional_fields': ['context', 'parameters', 'timeout'], 'response_type': MessageType.PROMPT_RESPONSE, 'handler_class': 'PromptRequestHandler'}, MessageType.PROMPT_RESPONSE: {'description': 'Response to a prompt request', 'required_fields': ['response'], 'optional_fields': ['original_prompt', 'processed_at', 'metadata'], 'response_type': None, 'handler_class': 'PromptResponseHandler'}, MessageType.AGENT_DISCOVERY: {'description': 'Agent presence announcement', 'required_fields': ['agent_capabilities'], 'optional_fields': ['announcement', 'metadata'], 'response_type': MessageType.AGENT_RESPONSE, 'handler_class': 'AgentDiscoveryHandler'}, MessageType.AGENT_RESPONSE: {'description': 'Response to agent discovery', 'required_fields': ['agent_capabilities'], 'optional_fields': ['response_to', 'metadata'], 'response_type': None, 'handler_class': 'AgentResponseHandler'}, MessageType.HELP_WANTED: {'description': 'Request for assistance with specific capabilities', 'required_fields': ['required_capabilities', 'description'], 'optional_fields': ['urgency', 'max_helpers', 'timeout_hours', 'context'], 'response_type': MessageType.HELP_RESPONSE, 'handler_class': 'HelpWantedHandler'}, MessageType.HELP_RESPONSE: {'description': 'Offer to help with a request', 'required_fields': ['request_id', 'can_help'], 'optional_fields': ['matching_capabilities', 'confidence_score', 'response_message'], 'response_type': None, 'handler_class': 'HelpResponseHandler'}, MessageType.SPORE_DELIVERY: {'description': 'Delivery of a spore with methodology', 'required_fields': ['spore_name', 'spore_content'], 'optional_fields': ['metadata', 'version', 'dependencies'], 'response_type': None, 'handler_class': 'SporeDeliveryHandler'}, MessageType.SPORE_REQUEST: {'description': 'Request for a specific spore', 'required_fields': ['spore_name'], 'optional_fields': ['version', 'metadata'], 'response_type': MessageType.SPORE_DELIVERY, 'handler_class': 'SporeRequestHandler'}, MessageType.TECHNICAL_EXCHANGE: {'description': 'Technical information exchange', 'required_fields': [], 'optional_fields': ['topic', 'data', 'metadata'], 'response_type': None, 'handler_class': 'TechnicalExchangeHandler'}, MessageType.SPORE_SPAWN: {'description': 'Spore spawn request for creating new spores', 'required_fields': ['spore_type'], 'optional_fields': ['metadata', 'parameters'], 'response_type': None, 'handler_class': 'SporeSpawnHandler'}, MessageType.SYSTEM_HEALTH: {'description': 'System health and monitoring information', 'required_fields': [], 'optional_fields': ['status', 'metrics', 'alerts'], 'response_type': None, 'handler_class': 'SystemHealthHandler'}}

def get_type_info(self, msg_type: MessageType) -> Dict[str, Any]:
    """Get information about a message type"""
    return self.type_info.get(msg_type, {})

def get_all_types(self) -> List[MessageType]:
    """Get all registered message types"""
    return list(self.type_info.keys())

def get_types_with_responses(self) -> Dict[MessageType, MessageType]:
    """Get message types that expect responses"""
    return {msg_type: info['response_type'] for msg_type, info in self.type_info.items() if info.get('response_type')}

def __init__(self, agent_id: str, capabilities: Optional[List[str]]=None, callbacks: Optional[Dict[str, Callable]]=None):
    super().__init__(agent_id)
    self.capabilities = capabilities or []
    self.callbacks = callbacks or {}
    self._setup_standard_handlers()
    self.sent_messages: Dict[str, BeastModeMessage] = {}
    self.received_messages: List[BeastModeMessage] = []
    self.max_history = 1000
    self.enable_auto_responses = True
    self.auto_convert_legacy = False

def _setup_standard_handlers(self) -> None:
    """Setup standard handlers for all message types"""
    simple_handler = SimpleMessageHandler(self.agent_id, message_callback=self.callbacks.get('on_simple_message'))
    self.register_handler(simple_handler)
    prompt_handler = PromptRequestHandler(self.agent_id, prompt_processor=self.callbacks.get('on_prompt_request'))
    self.register_handler(prompt_handler)
    response_handler = PromptResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_prompt_response'))
    self.register_handler(response_handler)
    discovery_handler = AgentDiscoveryHandler(self.agent_id, self.capabilities, discovery_callback=self.callbacks.get('on_agent_discovery'))
    self.register_handler(discovery_handler)
    agent_response_handler = AgentResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_agent_response'))
    self.register_handler(agent_response_handler)
    help_handler = HelpWantedHandler(self.agent_id, self.capabilities, help_callback=self.callbacks.get('on_help_wanted'))
    self.register_handler(help_handler)
    help_response_handler = HelpResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_help_response'))
    self.register_handler(help_response_handler)
    spore_handler = SporeDeliveryHandler(self.agent_id, spore_callback=self.callbacks.get('on_spore_delivery'))
    self.register_handler(spore_handler)
    spore_request_handler = SporeRequestHandler(self.agent_id, spore_provider=self.callbacks.get('on_spore_request'))
    self.register_handler(spore_request_handler)
    spore_spawn_handler = SporeSpawnHandler(self.agent_id, spawn_callback=self.callbacks.get('on_spore_spawn'))
    self.register_handler(spore_spawn_handler)
    tech_handler = TechnicalExchangeHandler(self.agent_id, tech_callback=self.callbacks.get('on_technical_exchange'))
    self.register_handler(tech_handler)
    health_handler = SystemHealthHandler(self.agent_id, health_callback=self.callbacks.get('on_system_health'))
    self.register_handler(health_handler)
    logger.info(f'Initialized standard message router for agent {self.agent_id}')

def track_sent_message(self, message: BeastModeMessage) -> None:
    """Track a message that was sent for correlation"""
    self.sent_messages[message.id] = message
    for handlers in self.handlers.values():
        for handler in handlers:
            if hasattr(handler, 'track_request') and message.type == MessageType.PROMPT_REQUEST:
                handler.track_request(message)
            elif hasattr(handler, 'track_help_request') and message.type == MessageType.HELP_WANTED:
                handler.track_help_request(message)
    self._trim_history()

def _trim_history(self) -> None:
    """Trim message history to prevent memory growth"""
    if len(self.received_messages) > self.max_history:
        self.received_messages = self.received_messages[-self.max_history:]
    if len(self.sent_messages) > self.max_history:
        sorted_messages = sorted(self.sent_messages.items(), key=lambda x: x[1].timestamp)
        to_remove = len(sorted_messages) - self.max_history
        for i in range(to_remove):
            del self.sent_messages[sorted_messages[i][0]]

def update_capabilities(self, capabilities: List[str]) -> None:
    """Update agent capabilities and notify handlers"""
    self.capabilities = capabilities
    for handlers in self.handlers.values():
        for handler in handlers:
            if hasattr(handler, 'capabilities'):
                handler.capabilities = capabilities
    logger.info(f'Updated capabilities for agent {self.agent_id}: {capabilities}')

def set_callback(self, callback_name: str, callback: Callable) -> None:
    """Set or update a callback function"""
    self.callbacks[callback_name] = callback
    logger.info(f'Updated callback: {callback_name}')

def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
    """
        Get message history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Dict with 'sent' and 'received' message lists
        """
    sent_list = list(self.sent_messages.values())
    received_list = self.received_messages
    if limit is not None:
        sent_list = sent_list[-limit:] if limit > 0 else []
        received_list = received_list[-limit:] if limit > 0 else []
    return {'sent': sent_list, 'received': received_list}

def get_correlation_info(self, message_id: str) -> Optional[Dict[str, Any]]:
    """
        Get correlation information for a message.
        
        Args:
            message_id: Message ID to look up
            
        Returns:
            Correlation information if found
        """
    if message_id in self.sent_messages:
        sent_msg = self.sent_messages[message_id]
        related = []
        for msg in self.received_messages:
            if msg.correlation_id == message_id:
                related.append(msg)
        return {'original_message': sent_msg, 'related_messages': related, 'type': 'sent'}
    for msg in self.received_messages:
        if msg.id == message_id:
            original = None
            if msg.correlation_id and msg.correlation_id in self.sent_messages:
                original = self.sent_messages[msg.correlation_id]
            return {'original_message': original, 'received_message': msg, 'type': 'received'}
    return None

def get_handler_info(self) -> Dict[str, Any]:
    """Get detailed information about registered handlers"""
    info = {'agent_id': self.agent_id, 'capabilities': self.capabilities, 'handlers_by_type': {}, 'total_handlers': 0, 'callback_status': {}}
    for msg_type, handlers in self.handlers.items():
        info['handlers_by_type'][msg_type.value] = [h.get_stats() for h in handlers]
        info['total_handlers'] += len(handlers)
    expected_callbacks = ['on_simple_message', 'on_prompt_request', 'on_prompt_response', 'on_agent_discovery', 'on_agent_response', 'on_help_wanted', 'on_help_response', 'on_spore_delivery', 'on_spore_request', 'on_spore_spawn', 'on_technical_exchange', 'on_system_health']
    for callback_name in expected_callbacks:
        info['callback_status'][callback_name] = callback_name in self.callbacks
    return info

def __init__(self):
    self.type_info = self._build_type_info()

def _build_type_info(self) -> Dict[MessageType, Dict[str, Any]]:
    """Build comprehensive type information"""
    return {MessageType.SIMPLE_MESSAGE: {'description': 'Basic text communication between agents', 'required_fields': ['content'], 'optional_fields': ['context', 'metadata'], 'response_type': None, 'handler_class': 'SimpleMessageHandler'}, MessageType.PROMPT_REQUEST: {'description': 'Request for processing a prompt', 'required_fields': ['prompt'], 'optional_fields': ['context', 'parameters', 'timeout'], 'response_type': MessageType.PROMPT_RESPONSE, 'handler_class': 'PromptRequestHandler'}, MessageType.PROMPT_RESPONSE: {'description': 'Response to a prompt request', 'required_fields': ['response'], 'optional_fields': ['original_prompt', 'processed_at', 'metadata'], 'response_type': None, 'handler_class': 'PromptResponseHandler'}, MessageType.AGENT_DISCOVERY: {'description': 'Agent presence announcement', 'required_fields': ['agent_capabilities'], 'optional_fields': ['announcement', 'metadata'], 'response_type': MessageType.AGENT_RESPONSE, 'handler_class': 'AgentDiscoveryHandler'}, MessageType.AGENT_RESPONSE: {'description': 'Response to agent discovery', 'required_fields': ['agent_capabilities'], 'optional_fields': ['response_to', 'metadata'], 'response_type': None, 'handler_class': 'AgentResponseHandler'}, MessageType.HELP_WANTED: {'description': 'Request for assistance with specific capabilities', 'required_fields': ['required_capabilities', 'description'], 'optional_fields': ['urgency', 'max_helpers', 'timeout_hours', 'context'], 'response_type': MessageType.HELP_RESPONSE, 'handler_class': 'HelpWantedHandler'}, MessageType.HELP_RESPONSE: {'description': 'Offer to help with a request', 'required_fields': ['request_id', 'can_help'], 'optional_fields': ['matching_capabilities', 'confidence_score', 'response_message'], 'response_type': None, 'handler_class': 'HelpResponseHandler'}, MessageType.SPORE_DELIVERY: {'description': 'Delivery of a spore with methodology', 'required_fields': ['spore_name', 'spore_content'], 'optional_fields': ['metadata', 'version', 'dependencies'], 'response_type': None, 'handler_class': 'SporeDeliveryHandler'}, MessageType.SPORE_REQUEST: {'description': 'Request for a specific spore', 'required_fields': ['spore_name'], 'optional_fields': ['version', 'metadata'], 'response_type': MessageType.SPORE_DELIVERY, 'handler_class': 'SporeRequestHandler'}, MessageType.TECHNICAL_EXCHANGE: {'description': 'Technical information exchange', 'required_fields': [], 'optional_fields': ['topic', 'data', 'metadata'], 'response_type': None, 'handler_class': 'TechnicalExchangeHandler'}, MessageType.SPORE_SPAWN: {'description': 'Spore spawn request for creating new spores', 'required_fields': ['spore_type'], 'optional_fields': ['metadata', 'parameters'], 'response_type': None, 'handler_class': 'SporeSpawnHandler'}, MessageType.SYSTEM_HEALTH: {'description': 'System health and monitoring information', 'required_fields': [], 'optional_fields': ['status', 'metrics', 'alerts'], 'response_type': None, 'handler_class': 'SystemHealthHandler'}}

def get_type_info(self, msg_type: MessageType) -> Dict[str, Any]:
    """Get information about a message type"""
    return self.type_info.get(msg_type, {})

def get_all_types(self) -> List[MessageType]:
    """Get all registered message types"""
    return list(self.type_info.keys())

def get_types_with_responses(self) -> Dict[MessageType, MessageType]:
    """Get message types that expect responses"""
    return {msg_type: info['response_type'] for msg_type, info in self.type_info.items() if info.get('response_type')}

def __init__(self, agent_id: str, capabilities: Optional[List[str]]=None, callbacks: Optional[Dict[str, Callable]]=None):
    super().__init__(agent_id)
    self.capabilities = capabilities or []
    self.callbacks = callbacks or {}
    self._setup_standard_handlers()
    self.sent_messages: Dict[str, BeastModeMessage] = {}
    self.received_messages: List[BeastModeMessage] = []
    self.max_history = 1000
    self.enable_auto_responses = True
    self.auto_convert_legacy = False

def _setup_standard_handlers(self) -> None:
    """Setup standard handlers for all message types"""
    simple_handler = SimpleMessageHandler(self.agent_id, message_callback=self.callbacks.get('on_simple_message'))
    self.register_handler(simple_handler)
    prompt_handler = PromptRequestHandler(self.agent_id, prompt_processor=self.callbacks.get('on_prompt_request'))
    self.register_handler(prompt_handler)
    response_handler = PromptResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_prompt_response'))
    self.register_handler(response_handler)
    discovery_handler = AgentDiscoveryHandler(self.agent_id, self.capabilities, discovery_callback=self.callbacks.get('on_agent_discovery'))
    self.register_handler(discovery_handler)
    agent_response_handler = AgentResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_agent_response'))
    self.register_handler(agent_response_handler)
    help_handler = HelpWantedHandler(self.agent_id, self.capabilities, help_callback=self.callbacks.get('on_help_wanted'))
    self.register_handler(help_handler)
    help_response_handler = HelpResponseHandler(self.agent_id, response_callback=self.callbacks.get('on_help_response'))
    self.register_handler(help_response_handler)
    spore_handler = SporeDeliveryHandler(self.agent_id, spore_callback=self.callbacks.get('on_spore_delivery'))
    self.register_handler(spore_handler)
    spore_request_handler = SporeRequestHandler(self.agent_id, spore_provider=self.callbacks.get('on_spore_request'))
    self.register_handler(spore_request_handler)
    spore_spawn_handler = SporeSpawnHandler(self.agent_id, spawn_callback=self.callbacks.get('on_spore_spawn'))
    self.register_handler(spore_spawn_handler)
    tech_handler = TechnicalExchangeHandler(self.agent_id, tech_callback=self.callbacks.get('on_technical_exchange'))
    self.register_handler(tech_handler)
    health_handler = SystemHealthHandler(self.agent_id, health_callback=self.callbacks.get('on_system_health'))
    self.register_handler(health_handler)
    logger.info(f'Initialized standard message router for agent {self.agent_id}')

def track_sent_message(self, message: BeastModeMessage) -> None:
    """Track a message that was sent for correlation"""
    self.sent_messages[message.id] = message
    for handlers in self.handlers.values():
        for handler in handlers:
            if hasattr(handler, 'track_request') and message.type == MessageType.PROMPT_REQUEST:
                handler.track_request(message)
            elif hasattr(handler, 'track_help_request') and message.type == MessageType.HELP_WANTED:
                handler.track_help_request(message)
    self._trim_history()

def _trim_history(self) -> None:
    """Trim message history to prevent memory growth"""
    if len(self.received_messages) > self.max_history:
        self.received_messages = self.received_messages[-self.max_history:]
    if len(self.sent_messages) > self.max_history:
        sorted_messages = sorted(self.sent_messages.items(), key=lambda x: x[1].timestamp)
        to_remove = len(sorted_messages) - self.max_history
        for i in range(to_remove):
            del self.sent_messages[sorted_messages[i][0]]

def update_capabilities(self, capabilities: List[str]) -> None:
    """Update agent capabilities and notify handlers"""
    self.capabilities = capabilities
    for handlers in self.handlers.values():
        for handler in handlers:
            if hasattr(handler, 'capabilities'):
                handler.capabilities = capabilities
    logger.info(f'Updated capabilities for agent {self.agent_id}: {capabilities}')

def set_callback(self, callback_name: str, callback: Callable) -> None:
    """Set or update a callback function"""
    self.callbacks[callback_name] = callback
    logger.info(f'Updated callback: {callback_name}')

def get_message_history(self, limit: Optional[int]=None) -> Dict[str, List[BeastModeMessage]]:
    """
        Get message history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            Dict with 'sent' and 'received' message lists
        """
    sent_list = list(self.sent_messages.values())
    received_list = self.received_messages
    if limit is not None:
        sent_list = sent_list[-limit:] if limit > 0 else []
        received_list = received_list[-limit:] if limit > 0 else []
    return {'sent': sent_list, 'received': received_list}

def get_correlation_info(self, message_id: str) -> Optional[Dict[str, Any]]:
    """
        Get correlation information for a message.
        
        Args:
            message_id: Message ID to look up
            
        Returns:
            Correlation information if found
        """
    if message_id in self.sent_messages:
        sent_msg = self.sent_messages[message_id]
        related = []
        for msg in self.received_messages:
            if msg.correlation_id == message_id:
                related.append(msg)
        return {'original_message': sent_msg, 'related_messages': related, 'type': 'sent'}
    for msg in self.received_messages:
        if msg.id == message_id:
            original = None
            if msg.correlation_id and msg.correlation_id in self.sent_messages:
                original = self.sent_messages[msg.correlation_id]
            return {'original_message': original, 'received_message': msg, 'type': 'received'}
    return None

def get_handler_info(self) -> Dict[str, Any]:
    """Get detailed information about registered handlers"""
    info = {'agent_id': self.agent_id, 'capabilities': self.capabilities, 'handlers_by_type': {}, 'total_handlers': 0, 'callback_status': {}}
    for msg_type, handlers in self.handlers.items():
        info['handlers_by_type'][msg_type.value] = [h.get_stats() for h in handlers]
        info['total_handlers'] += len(handlers)
    expected_callbacks = ['on_simple_message', 'on_prompt_request', 'on_prompt_response', 'on_agent_discovery', 'on_agent_response', 'on_help_wanted', 'on_help_response', 'on_spore_delivery', 'on_spore_request', 'on_spore_spawn', 'on_technical_exchange', 'on_system_health']
    for callback_name in expected_callbacks:
        info['callback_status'][callback_name] = callback_name in self.callbacks
    return info

def __init__(self):
    self.type_info = self._build_type_info()

def _build_type_info(self) -> Dict[MessageType, Dict[str, Any]]:
    """Build comprehensive type information"""
    return {MessageType.SIMPLE_MESSAGE: {'description': 'Basic text communication between agents', 'required_fields': ['content'], 'optional_fields': ['context', 'metadata'], 'response_type': None, 'handler_class': 'SimpleMessageHandler'}, MessageType.PROMPT_REQUEST: {'description': 'Request for processing a prompt', 'required_fields': ['prompt'], 'optional_fields': ['context', 'parameters', 'timeout'], 'response_type': MessageType.PROMPT_RESPONSE, 'handler_class': 'PromptRequestHandler'}, MessageType.PROMPT_RESPONSE: {'description': 'Response to a prompt request', 'required_fields': ['response'], 'optional_fields': ['original_prompt', 'processed_at', 'metadata'], 'response_type': None, 'handler_class': 'PromptResponseHandler'}, MessageType.AGENT_DISCOVERY: {'description': 'Agent presence announcement', 'required_fields': ['agent_capabilities'], 'optional_fields': ['announcement', 'metadata'], 'response_type': MessageType.AGENT_RESPONSE, 'handler_class': 'AgentDiscoveryHandler'}, MessageType.AGENT_RESPONSE: {'description': 'Response to agent discovery', 'required_fields': ['agent_capabilities'], 'optional_fields': ['response_to', 'metadata'], 'response_type': None, 'handler_class': 'AgentResponseHandler'}, MessageType.HELP_WANTED: {'description': 'Request for assistance with specific capabilities', 'required_fields': ['required_capabilities', 'description'], 'optional_fields': ['urgency', 'max_helpers', 'timeout_hours', 'context'], 'response_type': MessageType.HELP_RESPONSE, 'handler_class': 'HelpWantedHandler'}, MessageType.HELP_RESPONSE: {'description': 'Offer to help with a request', 'required_fields': ['request_id', 'can_help'], 'optional_fields': ['matching_capabilities', 'confidence_score', 'response_message'], 'response_type': None, 'handler_class': 'HelpResponseHandler'}, MessageType.SPORE_DELIVERY: {'description': 'Delivery of a spore with methodology', 'required_fields': ['spore_name', 'spore_content'], 'optional_fields': ['metadata', 'version', 'dependencies'], 'response_type': None, 'handler_class': 'SporeDeliveryHandler'}, MessageType.SPORE_REQUEST: {'description': 'Request for a specific spore', 'required_fields': ['spore_name'], 'optional_fields': ['version', 'metadata'], 'response_type': MessageType.SPORE_DELIVERY, 'handler_class': 'SporeRequestHandler'}, MessageType.TECHNICAL_EXCHANGE: {'description': 'Technical information exchange', 'required_fields': [], 'optional_fields': ['topic', 'data', 'metadata'], 'response_type': None, 'handler_class': 'TechnicalExchangeHandler'}, MessageType.SPORE_SPAWN: {'description': 'Spore spawn request for creating new spores', 'required_fields': ['spore_type'], 'optional_fields': ['metadata', 'parameters'], 'response_type': None, 'handler_class': 'SporeSpawnHandler'}, MessageType.SYSTEM_HEALTH: {'description': 'System health and monitoring information', 'required_fields': [], 'optional_fields': ['status', 'metrics', 'alerts'], 'response_type': None, 'handler_class': 'SystemHealthHandler'}}

def get_type_info(self, msg_type: MessageType) -> Dict[str, Any]:
    """Get information about a message type"""
    return self.type_info.get(msg_type, {})

def get_all_types(self) -> List[MessageType]:
    """Get all registered message types"""
    return list(self.type_info.keys())

def get_types_with_responses(self) -> Dict[MessageType, MessageType]:
    """Get message types that expect responses"""
    return {msg_type: info['response_type'] for msg_type, info in self.type_info.items() if info.get('response_type')}
