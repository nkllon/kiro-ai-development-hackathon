"""
Message Router Core Validation

This module was extracted from message_router_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from .models import BeastModeMessage, MessageType, AgentCapabilities
from .message_handlers import MessageRouter, BaseMessageHandler, SimpleMessageHandler, PromptRequestHandler, PromptResponseHandler, AgentDiscoveryHandler, AgentResponseHandler, HelpWantedHandler, HelpResponseHandler, SporeDeliveryHandler, SporeRequestHandler, SporeSpawnHandler, TechnicalExchangeHandler, SystemHealthHandler, MessageValidationError, MessageCompatibilityError
from src.rm_ddd.core.health import ModuleHealth


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

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

