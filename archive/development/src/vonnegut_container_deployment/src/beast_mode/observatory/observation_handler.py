"""
Observatory Observation Handler
Manages real-time observation events from Beastly Modules
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ObservationHandler:
    """Handles real-time observation events from Beastly Modules"""
    
    def __init__(self):
        self.connected_clients: Set[WebSocket] = set()
        self.recent_observations: List[Dict[str, Any]] = []
        self.max_recent_observations = 100
        self._lock = asyncio.Lock()
        
        logger.info("🎬 ObservationHandler initialized")
    
    async def add_client(self, websocket: WebSocket):
        """Add a WebSocket client for observation updates"""
        self.connected_clients.add(websocket)
        logger.info(f"📡 Client connected to observations. Total: {len(self.connected_clients)}")
        
        # Send recent observations to new client
        try:
            for observation in self.recent_observations[-10:]:  # Send last 10 observations
                await websocket.send_text(json.dumps(observation))
        except Exception as e:
            logger.error(f"Failed to send recent observations to new client: {e}")
    
    async def remove_client(self, websocket: WebSocket):
        """Remove a WebSocket client"""
        self.connected_clients.discard(websocket)
        logger.info(f"📡 Client disconnected from observations. Total: {len(self.connected_clients)}")
    
    async def broadcast_observation(self, observation: Dict[str, Any]):
        """Broadcast an observation to all connected clients"""
        async with self._lock:
            # Add to recent observations
            self.recent_observations.append(observation)
            if len(self.recent_observations) > self.max_recent_observations:
                self.recent_observations.pop(0)
        
        # Broadcast to all connected clients
        if self.connected_clients:
            message = json.dumps(observation)
            disconnected_clients = set()
            
            for client in self.connected_clients:
                try:
                    await client.send_text(message)
                except Exception as e:
                    logger.warning(f"Failed to send observation to client: {e}")
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.connected_clients.discard(client)
            
            logger.debug(f"📰 Broadcasted observation to {len(self.connected_clients)} clients: {observation['message']}")
    
    def broadcast_observation_sync(self, observation: Dict[str, Any]):
        """Synchronous version for use from non-async contexts"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, schedule the coroutine
                asyncio.create_task(self.broadcast_observation(observation))
            else:
                # If no loop is running, run it
                asyncio.run(self.broadcast_observation(observation))
        except RuntimeError:
            # No event loop available, store for later
            asyncio.create_task(self.broadcast_observation(observation))
        except Exception as e:
            logger.error(f"Failed to broadcast observation: {e}")
    
    def get_recent_observations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent observations for HTTP API"""
        return self.recent_observations[-limit:] if self.recent_observations else []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get observation handler statistics"""
        return {
            "connected_clients": len(self.connected_clients),
            "recent_observations_count": len(self.recent_observations),
            "total_observations_stored": len(self.recent_observations)
        }

# Global observation handler instance
_global_observation_handler: Optional[ObservationHandler] = None

def get_global_observation_handler() -> Optional[ObservationHandler]:
    """Get the global observation handler instance"""
    return _global_observation_handler

def set_global_observation_handler(handler: ObservationHandler):
    """Set the global observation handler instance"""
    global _global_observation_handler
    _global_observation_handler = handler
    logger.info("🌐 Global observation handler set")

def create_observation_handler() -> ObservationHandler:
    """Create and set a new global observation handler"""
    handler = ObservationHandler()
    set_global_observation_handler(handler)
    return handler