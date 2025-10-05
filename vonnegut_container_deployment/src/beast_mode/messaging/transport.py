#!/usr/bin/env python3
"""
Transport Factory for Beast Mode Messaging

Provides factory pattern for creating different transport implementations.
"""

from typing import Dict, Any, Type, Callable
from abc import ABC, abstractmethod


class Transport(ABC):
    """Abstract base class for message transports."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config: Dict[str, Any] = {}
        self.message_handlers: list = []
        self.daemon = None

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the transport."""
        pass

    @abstractmethod
    async def send_message(self, message) -> bool:
        """Send a message."""
        pass

    @abstractmethod
    async def subscribe(self, handler: Callable) -> bool:
        """Subscribe to messages."""
        pass

    @abstractmethod
    async def start_daemon(self) -> bool:
        """Start the transport daemon."""
        pass

    @abstractmethod
    async def stop_daemon(self) -> None:
        """Stop the transport daemon."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get transport status."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get transport capabilities."""
        pass


class TransportFactory:
    """Factory for creating transport instances."""
    
    _transports: Dict[str, Type[Transport]] = {}
    
    @classmethod
    def register_transport(cls, name: str, transport_class: Type[Transport]) -> None:
        """Register a transport type."""
        cls._transports[name] = transport_class
    
    @classmethod
    def create_transport(cls, transport_type: str, agent_id: str) -> Transport:
        """Create a transport instance."""
        if transport_type not in cls._transports:
            raise ValueError(f"Unknown transport type: {transport_type}")
        
        return cls._transports[transport_type](agent_id)
    
    @classmethod
    def get_available_transports(cls) -> list:
        """Get list of available transport types."""
        return list(cls._transports.keys())


# Register transports immediately
try:
    from .redis_transport import RedisTransport
    TransportFactory.register_transport('redis', RedisTransport)
except ImportError:
    pass