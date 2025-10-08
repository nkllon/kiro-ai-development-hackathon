#!/usr/bin/env python3
"""
Daemon Client for Beast Mode Messaging

Provides client interface for communicating with messaging daemons.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class QueuedMessage:
    """A message queued for processing."""
    message: Any
    received_at: datetime


class BeastModeDaemon(ABC):
    """Abstract base class for Beast Mode daemons."""
    
    @abstractmethod
    async def start_daemon(self) -> bool:
        """Start the daemon."""
        pass
    
    @abstractmethod
    async def stop_daemon(self) -> None:
        """Stop the daemon."""
        pass
    
    @abstractmethod
    async def send_message(self, message: Any) -> None:
        """Send a message."""
        pass
    
    @abstractmethod
    async def check_mail(self) -> List[QueuedMessage]:
        """Check for incoming messages."""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        pass
    
    @abstractmethod
    async def announce_presence(self) -> None:
        """Announce agent presence."""
        pass
    
    @abstractmethod
    async def send_spore(self, spore_data: Dict[str, Any]) -> None:
        """Send spore data."""
        pass
    
    @abstractmethod
    async def get_unread_count(self) -> int:
        """Get unread message count."""
        pass


class MockBeastModeDaemon(BeastModeDaemon):
    """Mock implementation of Beast Mode daemon for testing."""
    
    def __init__(self):
        self.is_running = False
        self.is_connected = False
        self.inbox: List[QueuedMessage] = []
        self.outbox: List[Any] = []
        self.stats = {}
    
    async def start_daemon(self) -> bool:
        """Start the mock daemon."""
        self.is_running = True
        self.is_connected = True
        return True
    
    async def stop_daemon(self) -> None:
        """Stop the mock daemon."""
        self.is_running = False
        self.is_connected = False
    
    async def send_message(self, message: Any) -> None:
        """Send a message via mock daemon."""
        self.outbox.append(message)
    
    async def check_mail(self) -> List[QueuedMessage]:
        """Check for incoming messages."""
        messages = self.inbox.copy()
        self.inbox.clear()
        return messages
    
    async def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        return {
            'is_running': self.is_running,
            'is_connected': self.is_connected,
            'inbox_count': len(self.inbox),
            'outbox_count': len(self.outbox),
            'stats': self.stats
        }
    
    async def announce_presence(self) -> None:
        """Announce presence."""
        pass
    
    async def send_spore(self, spore_data: Dict[str, Any]) -> None:
        """Send spore data."""
        self.outbox.append({'type': 'spore', 'data': spore_data})
    
    async def get_unread_count(self) -> int:
        """Get unread message count."""
        return len(self.inbox)
