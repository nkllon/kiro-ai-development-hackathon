"""
Help System Core Processing

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

def process_help_request(self, message: BeastModeMessage, responder_id: str) -> Optional[HelpResponse]:
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
    request_id = message.payload.get('request_id')
    required_capabilities = message.payload.get('required_capabilities', [])
    if not request_id or not required_capabilities:
        logger.warning(f'Invalid help request message from {message.source}')
        return None
    responder_agent = self.agent_registry.get_agent(responder_id)
    if not responder_agent:
        logger.warning(f'Responder {responder_id} not found in registry')
        return None
    match_score = self.capability_matcher.calculate_match_score(required_capabilities, responder_agent.capabilities.capabilities, responder_agent.collaboration_score)
    if match_score < 0.3:
        logger.debug(f'Match score {match_score} too low for {responder_id} to help with {request_id}')
        return None
    matching_capabilities = [cap for cap in required_capabilities if cap in responder_agent.capabilities.capabilities]
    response = HelpResponse(response_id=str(uuid.uuid4()), responder_id=responder_id, request_id=request_id, matching_capabilities=matching_capabilities, confidence_score=match_score, availability=responder_agent.capabilities.availability, message=f"I can help with {', '.join(matching_capabilities)} (confidence: {match_score:.2f})")
    self.stats['responses_received'] += 1
    logger.info(f'Generated help response from {responder_id} for {request_id} (score: {match_score:.2f})')
    return response

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
    request_id = message.payload.get('request_id')
    if not request_id or request_id not in self.active_requests:
        logger.warning(f'Help response for unknown request {request_id}')
        return False
    help_request = self.active_requests[request_id]
    if help_request.status != CollaborationStatus.PENDING:
        logger.debug(f'Help request {request_id} no longer accepting responses')
        return False
    if len(help_request.responses) >= self.max_responses_per_request:
        logger.debug(f'Help request {request_id} has reached maximum responses')
        return False
    help_response = HelpResponse(response_id=message.payload.get('response_id', str(uuid.uuid4())), responder_id=message.source, request_id=request_id, matching_capabilities=message.payload.get('matching_capabilities', []), confidence_score=message.payload.get('confidence_score', 0.0), availability=message.payload.get('availability', 'unknown'), estimated_time=message.payload.get('estimated_time'), message=message.payload.get('message'))
    help_request.responses.append(help_response)
    if help_response.confidence_score >= self.auto_accept_threshold and len(help_request.accepted_helpers) < help_request.max_helpers:
        self.accept_help_response(request_id, help_response.response_id)
    logger.info(f'Processed help response from {message.source} for {request_id}')
    return True
