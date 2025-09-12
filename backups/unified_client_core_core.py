"""
Unified Client Core Core

This module was extracted from unified_client_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from .transport import TransportFactory, BeastModeTransport
from .shared_state import BeastModeSharedState, SharedStateConfig
from .models import BeastModeMessage, MessageType, AgentCapabilities

class BeastModeClient:
    """
    Unified client interface with pluggable transport.
    
    Combines transport abstraction with shared state management
    to provide a complete Beast Mode networking solution.
    """

    def __init__(self, agent_id: str, transport_type: str='redis', transport_config: Optional[Dict[str, Any]]=None, shared_state_config: Optional[SharedStateConfig]=None, capabilities: Optional[List[str]]=None, specializations: Optional[List[str]]=None):
        """
        Initialize unified Beast Mode client.
        
        Args:
            agent_id: Unique agent identifier
            transport_type: Type of transport ('redis', 'nats', etc.)
            transport_config: Transport-specific configuration
            shared_state_config: Shared state configuration
            capabilities: Agent capabilities list
            specializations: Agent specializations list
        """
        self.agent_id = agent_id
        self.transport_type = transport_type
        self.capabilities = capabilities or []
        self.specializations = specializations or []
        self.transport = TransportFactory.create_transport(transport_type, agent_id=agent_id, **transport_config or {})
        self.shared_state = BeastModeSharedState(shared_state_config)
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.is_started = False
        self.stats = {'messages_sent': 0, 'messages_received': 0, 'start_time': None, 'last_activity': None}
        self.logger = logging.getLogger(__name__)

    async def start(self) -> bool:
        """
        Start the Beast Mode client.
        
        Returns:
            True if started successfully
        """
        if self.is_started:
            self.logger.warning('Client already started')
            return True
        try:
            if not await self.shared_state.initialize():
                self.logger.error('Failed to initialize shared state')
                return False
            if not await self.transport.initialize({}):
                self.logger.error('Failed to initialize transport')
                return False
            await self.transport.subscribe(self._handle_message)
            if not await self.transport.start_daemon():
                self.logger.error('Failed to start transport daemon')
                return False
            await self._announce_presence()
            self.is_started = True
            self.stats['start_time'] = datetime.now()
            self.logger.info(f'Beast Mode client started: {self.agent_id} using {self.transport_type}')
            return True
        except Exception as e:
            self.logger.error(f'Failed to start client: {e}')
            return False

    async def stop(self):
        """Stop the Beast Mode client gracefully."""
        if not self.is_started:
            return
        try:
            await self.shared_state.remove_agent_state(self.agent_id)
            await self.transport.stop_daemon()
            await self.shared_state.shutdown()
            self.is_started = False
            self.logger.info(f'Beast Mode client stopped: {self.agent_id}')
        except Exception as e:
            self.logger.error(f'Error stopping client: {e}')

    async def send_message(self, message: BeastModeMessage) -> bool:
        """
        Send a message via transport and update shared state.
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        if not self.is_started:
            self.logger.error('Client not started')
            return False
        try:
            if not message.source:
                message.source = self.agent_id
            success = await self.transport.send_message(message)
            if success:
                self.stats['messages_sent'] += 1
                self.stats['last_activity'] = datetime.now()
                await self.shared_state.increment_counter('messages_sent', self.agent_id)
                await self.shared_state.update_agent_state(self.agent_id, {'last_activity': datetime.now().isoformat(), 'status': 'active'})
            return success
        except Exception as e:
            self.logger.error(f'Failed to send message: {e}')
            return False

    def register_handler(self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]):
        """
        Register a message handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call when message received
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        self.logger.info(f'Registered handler for {message_type}')

    async def _handle_message(self, message: BeastModeMessage):
        """
        Internal message handler called by transport.
        
        Args:
            message: Received message
        """
        try:
            self.stats['messages_received'] += 1
            self.stats['last_activity'] = datetime.now()
            await self.shared_state.increment_counter('messages_received', self.agent_id)
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(message)
                        else:
                            handler(message)
                    except Exception as e:
                        self.logger.error(f'Handler error for {message.type}: {e}')
            await self._handle_builtin_messages(message)
        except Exception as e:
            self.logger.error(f'Error handling message: {e}')

    async def _handle_builtin_messages(self, message: BeastModeMessage):
        """Handle built-in message types."""
        if message.type == MessageType.AGENT_DISCOVERY:
            response = BeastModeMessage(type=MessageType.AGENT_RESPONSE, source=self.agent_id, target=message.source, payload={'agent_id': self.agent_id, 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type, 'status': 'online'})
            await self.send_message(response)

    async def _announce_presence(self):
        """Announce agent presence in shared state."""
        agent_state = {'status': 'online', 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type, 'last_seen': datetime.now().isoformat(), 'stats': self.stats.copy()}
        await self.shared_state.update_agent_state(self.agent_id, agent_state)

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive client status.
        
        Returns:
            Dictionary containing status information
        """
        transport_status = self.transport.get_status()
        return {'agent_id': self.agent_id, 'transport_type': self.transport_type, 'is_started': self.is_started, 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_status': transport_status, 'stats': self.stats.copy(), 'message_handlers': {str(msg_type): len(handlers) for msg_type, handlers in self.message_handlers.items()}}

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get combined client and transport capabilities.
        
        Returns:
            Dictionary describing all capabilities
        """
        transport_capabilities = self.transport.get_capabilities()
        return {'agent_capabilities': self.capabilities, 'agent_specializations': self.specializations, 'transport_capabilities': transport_capabilities, 'client_features': ['unified_interface', 'pluggable_transport', 'shared_state_integration', 'async_message_handling', 'automatic_presence_management', 'built_in_discovery_response']}

    async def discover_agents(self) -> List[str]:
        """
        Discover active agents in the network.
        
        Returns:
            List of active agent IDs
        """
        return await self.shared_state.get_active_agents()

    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about another agent.
        
        Args:
            agent_id: Agent to get info for
            
        Returns:
            Agent information or None if not found
        """
        return await self.shared_state.get_agent_state(agent_id)

    async def send_simple_message(self, target: str, text: str) -> bool:
        """
        Send a simple text message.
        
        Args:
            target: Target agent ID
            text: Message text
            
        Returns:
            True if sent successfully
        """
        message = BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source=self.agent_id, target=target, payload={'text': text})
        return await self.send_message(message)

    async def broadcast_message(self, text: str) -> bool:
        """
        Broadcast a message to all agents.
        
        Args:
            text: Message text
            
        Returns:
            True if sent successfully
        """
        message = BeastModeMessage(type=MessageType.SIMPLE_MESSAGE, source=self.agent_id, target=None, payload={'text': text})
        return await self.send_message(message)

    async def request_help(self, topic: str, details: str='') -> bool:
        """
        Request help from other agents.
        
        Args:
            topic: Help topic
            details: Additional details
            
        Returns:
            True if request sent successfully
        """
        message = BeastModeMessage(type=MessageType.HELP_WANTED, source=self.agent_id, payload={'topic': topic, 'details': details, 'capabilities_needed': [], 'urgency': 'normal'})
        return await self.send_message(message)

    def send_spore(self, spore_data: Dict[str, Any]):
        """Send a spore (backward compatibility)."""
        message = BeastModeMessage(type=MessageType.SPORE_DELIVERY, source=self.agent_id, payload={'spore_type': 'systematic_pattern', 'spore_data': spore_data, 'shared_at': datetime.now().isoformat()})
        asyncio.create_task(self.send_message(message))

    def announce_presence(self):
        """Announce presence (backward compatibility)."""
        message = BeastModeMessage(type=MessageType.AGENT_DISCOVERY, source=self.agent_id, payload={'agent_type': 'UnifiedClient', 'status': 'online', 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type})
        asyncio.create_task(self.send_message(message))

def __init__(self, agent_id: str, transport_type: str='redis', transport_config: Optional[Dict[str, Any]]=None, shared_state_config: Optional[SharedStateConfig]=None, capabilities: Optional[List[str]]=None, specializations: Optional[List[str]]=None):
    """
        Initialize unified Beast Mode client.
        
        Args:
            agent_id: Unique agent identifier
            transport_type: Type of transport ('redis', 'nats', etc.)
            transport_config: Transport-specific configuration
            shared_state_config: Shared state configuration
            capabilities: Agent capabilities list
            specializations: Agent specializations list
        """
    self.agent_id = agent_id
    self.transport_type = transport_type
    self.capabilities = capabilities or []
    self.specializations = specializations or []
    self.transport = TransportFactory.create_transport(transport_type, agent_id=agent_id, **transport_config or {})
    self.shared_state = BeastModeSharedState(shared_state_config)
    self.message_handlers: Dict[MessageType, List[Callable]] = {}
    self.is_started = False
    self.stats = {'messages_sent': 0, 'messages_received': 0, 'start_time': None, 'last_activity': None}
    self.logger = logging.getLogger(__name__)

def register_handler(self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]):
    """
        Register a message handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call when message received
        """
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)
    self.logger.info(f'Registered handler for {message_type}')

def get_status(self) -> Dict[str, Any]:
    """
        Get comprehensive client status.
        
        Returns:
            Dictionary containing status information
        """
    transport_status = self.transport.get_status()
    return {'agent_id': self.agent_id, 'transport_type': self.transport_type, 'is_started': self.is_started, 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_status': transport_status, 'stats': self.stats.copy(), 'message_handlers': {str(msg_type): len(handlers) for msg_type, handlers in self.message_handlers.items()}}

def get_capabilities(self) -> Dict[str, Any]:
    """
        Get combined client and transport capabilities.
        
        Returns:
            Dictionary describing all capabilities
        """
    transport_capabilities = self.transport.get_capabilities()
    return {'agent_capabilities': self.capabilities, 'agent_specializations': self.specializations, 'transport_capabilities': transport_capabilities, 'client_features': ['unified_interface', 'pluggable_transport', 'shared_state_integration', 'async_message_handling', 'automatic_presence_management', 'built_in_discovery_response']}

def send_spore(self, spore_data: Dict[str, Any]):
    """Send a spore (backward compatibility)."""
    message = BeastModeMessage(type=MessageType.SPORE_DELIVERY, source=self.agent_id, payload={'spore_type': 'systematic_pattern', 'spore_data': spore_data, 'shared_at': datetime.now().isoformat()})
    asyncio.create_task(self.send_message(message))

def announce_presence(self):
    """Announce presence (backward compatibility)."""
    message = BeastModeMessage(type=MessageType.AGENT_DISCOVERY, source=self.agent_id, payload={'agent_type': 'UnifiedClient', 'status': 'online', 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type})
    asyncio.create_task(self.send_message(message))

def __init__(self, agent_id: str, transport_type: str='redis', transport_config: Optional[Dict[str, Any]]=None, shared_state_config: Optional[SharedStateConfig]=None, capabilities: Optional[List[str]]=None, specializations: Optional[List[str]]=None):
    """
        Initialize unified Beast Mode client.
        
        Args:
            agent_id: Unique agent identifier
            transport_type: Type of transport ('redis', 'nats', etc.)
            transport_config: Transport-specific configuration
            shared_state_config: Shared state configuration
            capabilities: Agent capabilities list
            specializations: Agent specializations list
        """
    self.agent_id = agent_id
    self.transport_type = transport_type
    self.capabilities = capabilities or []
    self.specializations = specializations or []
    self.transport = TransportFactory.create_transport(transport_type, agent_id=agent_id, **transport_config or {})
    self.shared_state = BeastModeSharedState(shared_state_config)
    self.message_handlers: Dict[MessageType, List[Callable]] = {}
    self.is_started = False
    self.stats = {'messages_sent': 0, 'messages_received': 0, 'start_time': None, 'last_activity': None}
    self.logger = logging.getLogger(__name__)

def register_handler(self, message_type: MessageType, handler: Callable[[BeastModeMessage], None]):
    """
        Register a message handler for specific message type.
        
        Args:
            message_type: Type of message to handle
            handler: Function to call when message received
        """
    if message_type not in self.message_handlers:
        self.message_handlers[message_type] = []
    self.message_handlers[message_type].append(handler)
    self.logger.info(f'Registered handler for {message_type}')

def get_status(self) -> Dict[str, Any]:
    """
        Get comprehensive client status.
        
        Returns:
            Dictionary containing status information
        """
    transport_status = self.transport.get_status()
    return {'agent_id': self.agent_id, 'transport_type': self.transport_type, 'is_started': self.is_started, 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_status': transport_status, 'stats': self.stats.copy(), 'message_handlers': {str(msg_type): len(handlers) for msg_type, handlers in self.message_handlers.items()}}

def get_capabilities(self) -> Dict[str, Any]:
    """
        Get combined client and transport capabilities.
        
        Returns:
            Dictionary describing all capabilities
        """
    transport_capabilities = self.transport.get_capabilities()
    return {'agent_capabilities': self.capabilities, 'agent_specializations': self.specializations, 'transport_capabilities': transport_capabilities, 'client_features': ['unified_interface', 'pluggable_transport', 'shared_state_integration', 'async_message_handling', 'automatic_presence_management', 'built_in_discovery_response']}

def send_spore(self, spore_data: Dict[str, Any]):
    """Send a spore (backward compatibility)."""
    message = BeastModeMessage(type=MessageType.SPORE_DELIVERY, source=self.agent_id, payload={'spore_type': 'systematic_pattern', 'spore_data': spore_data, 'shared_at': datetime.now().isoformat()})
    asyncio.create_task(self.send_message(message))

def announce_presence(self):
    """Announce presence (backward compatibility)."""
    message = BeastModeMessage(type=MessageType.AGENT_DISCOVERY, source=self.agent_id, payload={'agent_type': 'UnifiedClient', 'status': 'online', 'capabilities': self.capabilities, 'specializations': self.specializations, 'transport_type': self.transport_type})
    asyncio.create_task(self.send_message(message))
