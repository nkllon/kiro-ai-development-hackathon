#!/usr/bin/env python3
"""
Redis Transport for Beast Mode Messaging

Provides Redis-based message transport with pub/sub capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime

from .transport import Transport
from .daemon_client import BeastModeDaemon, MockBeastModeDaemon
from .models import BeastModeMessage


class RedisTransport(Transport):
    """Redis-based message transport implementation."""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.logger = logging.getLogger(__name__)
        self.daemon: Optional[BeastModeDaemon] = None
        self._processing_task: Optional[asyncio.Task] = None
        self._processing = False

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Redis transport."""
        self.config = config
        
        # For now, use mock daemon - can be replaced with real Redis daemon
        self.daemon = MockBeastModeDaemon()
        
        self.logger.info(f"Redis transport initialized for agent: {self.agent_id}")
        return True

    async def send_message(self, message: BeastModeMessage) -> bool:
        """Send a message via Redis transport."""
        try:
            if not self.daemon:
                self.logger.error("Transport not initialized")
                return False
            
            await self.daemon.send_message(message)
            self.logger.debug(f"Message sent: {message.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False

    async def subscribe(self, handler: Callable) -> bool:
        """Subscribe to message handlers."""
        try:
            self.message_handlers.append(handler)
            self.logger.info(f"Handler subscribed. Total handlers: {len(self.message_handlers)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe handler: {e}")
            return False

    async def start_daemon(self) -> bool:
        """Start the Redis daemon."""
        try:
            if not self.daemon:
                self.logger.error("Transport not initialized")
                return False
            
            result = await self.daemon.start_daemon()
            if result:
                await self.daemon.announce_presence()
                self.logger.info("Redis daemon started")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            return False

    async def stop_daemon(self) -> None:
        """Stop the Redis daemon."""
        try:
            if self.daemon:
                await self.daemon.stop_daemon()
            
            # Stop message processing
            await self._stop_message_processing()
            
            self.logger.info("Redis daemon stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping daemon: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get transport status."""
        daemon_status = {}
        if self.daemon:
            # In a real implementation, this would be async
            daemon_status = {
                'daemon_running': True,  # Mock status
                'daemon_connected': True,
                'stats': {}
            }
        
        return {
            'transport_type': 'redis',
            'agent_id': self.agent_id,
            **daemon_status
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get transport capabilities."""
        return {
            'reliable_delivery': False,  # Redis pub/sub limitation
            'message_persistence': True,
            'shared_state': True,
            'scalability': 'moderate',
            'background_processing': True
        }

    async def _start_message_processing(self) -> None:
        """Start message processing loop."""
        if self._processing:
            return
        
        self._processing = True
        self._processing_task = asyncio.create_task(self._message_processing_loop())

    async def _stop_message_processing(self) -> None:
        """Stop message processing loop."""
        self._processing = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

    async def _message_processing_loop(self) -> None:
        """Main message processing loop."""
        while self._processing and self.daemon:
            try:
                # Check for incoming messages
                messages = await self.daemon.check_mail()
                
                for queued_msg in messages:
                    # Process message with all handlers
                    for handler in self.message_handlers:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(queued_msg.message)
                            else:
                                handler(queued_msg.message)
                        except Exception as e:
                            self.logger.error(f"Handler error: {e}")
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Message processing error: {e}")
                await asyncio.sleep(1)  # Longer delay on error

    # Backward compatibility methods
    def send_spore(self, spore_data: Dict[str, Any]) -> None:
        """Send spore data (synchronous wrapper)."""
        if self.daemon:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.daemon.send_spore(spore_data))
                else:
                    loop.run_until_complete(self.daemon.send_spore(spore_data))
            except RuntimeError:
                # No event loop running, create a new one
                asyncio.run(self.daemon.send_spore(spore_data))

    def announce_presence(self) -> None:
        """Announce presence (synchronous wrapper)."""
        if self.daemon:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.daemon.announce_presence())
                else:
                    loop.run_until_complete(self.daemon.announce_presence())
            except RuntimeError:
                # No event loop running, create a new one
                asyncio.run(self.daemon.announce_presence())

    def get_unread_count(self) -> int:
        """Get unread message count (synchronous wrapper)."""
        if self.daemon:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, we can't use run_until_complete
                    # Return a default value for now
                    return 0
                else:
                    return loop.run_until_complete(self.daemon.get_unread_count())
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self.daemon.get_unread_count())
        return 0

    def check_mail(self) -> List[Any]:
        """Check mail (synchronous wrapper)."""
        if self.daemon:
            # In a real implementation, this would be async
            return []  # Mock implementation
        return []


# Register this transport with the factory
from .transport import TransportFactory
TransportFactory.register_transport('redis', RedisTransport)