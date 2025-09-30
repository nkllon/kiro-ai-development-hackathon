#!/usr/bin/env python3
"""
Observatory WebSocket Client - Real-time Service Discovery
=========================================================

WebSocket client for real-time integration with Observatory server.
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class WebSocketEndpoint:
    """WebSocket endpoint information."""
    path: str
    purpose: str
    message_types: List[str]
    connection_limits: Optional[int] = None
    authentication_required: bool = False
    last_connected: Optional[datetime] = None
    connection_status: str = "disconnected"
    message_count: int = 0


@dataclass
class WebSocketMessage:
    """WebSocket message structure."""
    endpoint: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class ObservatoryWebSocketClient(ReflectiveModule):
    """
    WebSocket client for real-time Observatory integration.
    """
    
    def __init__(self, observatory_url: str = "ws://localhost:8888"):
        super().__init__()
        self.module_id = "ObservatoryWebSocketClient"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        self._observatory_url = observatory_url
        self._websocket_connections: Dict[str, Any] = {}
        self._endpoints: List[WebSocketEndpoint] = []
        self._message_handlers: Dict[str, Callable] = {}
        self._correlation_tracking: Dict[str, Dict[str, Any]] = {}
        self._connection_recovery_enabled = True
        
    def discover_websocket_endpoints(self) -> List[WebSocketEndpoint]:
        """Discover available WebSocket endpoints."""
        self._logger.info("Discovering WebSocket endpoints...")
        
        endpoints = [
            WebSocketEndpoint(
                path="/ws/observatory",
                purpose="Main observatory events",
                message_types=["service_status", "metrics_update", "system_event", "health_check"],
                connection_limits=100,
                authentication_required=False
            ),
            WebSocketEndpoint(
                path="/ws/emoji-rain", 
                purpose="Real-time emoji rain streaming",
                message_types=["emoji_event", "celebration", "achievement", "coordination_visual"],
                connection_limits=50,
                authentication_required=False
            ),
            WebSocketEndpoint(
                path="/ws/anomalies",
                purpose="Anomaly detection alerts", 
                message_types=["anomaly_detected", "threshold_exceeded", "alert", "performance_warning"],
                connection_limits=25,
                authentication_required=True
            ),
            WebSocketEndpoint(
                path="/ws/doctor-status",
                purpose="System health monitoring",
                message_types=["health_check", "status_update", "diagnostic", "system_recovery"],
                connection_limits=10,
                authentication_required=True
            )
        ]
        
        self._endpoints = endpoints
        self._logger.info(f"Discovered {len(endpoints)} WebSocket endpoints")
        return endpoints
    
    async def connect_to_observatory(self, endpoint_path: str = "/ws/observatory") -> bool:
        """Connect to Observatory WebSocket endpoint."""
        try:
            full_url = f"{self._observatory_url}{endpoint_path}"
            self._logger.info(f"Connecting to Observatory at {full_url}")
            
            # Attempt WebSocket connection
            websocket = await websockets.connect(full_url)
            self._websocket_connections[endpoint_path] = websocket
            
            # Update endpoint status
            for endpoint in self._endpoints:
                if endpoint.path == endpoint_path:
                    endpoint.connection_status = "connected"
                    endpoint.last_connected = datetime.now()
                    break
            
            self._logger.info(f"Connected to Observatory WebSocket: {endpoint_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to connect to Observatory {endpoint_path}: {e}")
            
            # Update endpoint status
            for endpoint in self._endpoints:
                if endpoint.path == endpoint_path:
                    endpoint.connection_status = "failed"
                    break
                    
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register handler for specific message types."""
        self._message_handlers[message_type] = handler
        self._logger.info(f"Registered handler for {message_type}")
    
    async def send_message(self, endpoint_path: str, message_type: str, payload: Dict[str, Any]) -> str:
        """Send message to Observatory WebSocket endpoint."""
        correlation_id = str(uuid.uuid4())
        
        try:
            if endpoint_path not in self._websocket_connections:
                raise ConnectionError(f"Not connected to {endpoint_path}")
            
            websocket = self._websocket_connections[endpoint_path]
            
            message = WebSocketMessage(
                endpoint=endpoint_path,
                message_type=message_type,
                payload=payload,
                correlation_id=correlation_id
            )
            
            # Send message
            message_json = json.dumps({
                "type": message_type,
                "payload": payload,
                "correlation_id": correlation_id,
                "timestamp": message.timestamp.isoformat()
            })
            
            await websocket.send(message_json)
            
            # Track correlation
            self._correlation_tracking[correlation_id] = {
                "endpoint": endpoint_path,
                "message_type": message_type,
                "sent_at": message.timestamp,
                "status": "sent"
            }
            
            self._logger.info(f"Sent message {message_type} to {endpoint_path} (correlation: {correlation_id})")
            return correlation_id
            
        except Exception as e:
            self._logger.error(f"Failed to send message to {endpoint_path}: {e}")
            
            # Track failed correlation
            self._correlation_tracking[correlation_id] = {
                "endpoint": endpoint_path,
                "message_type": message_type,
                "sent_at": datetime.now(),
                "status": "failed",
                "error": str(e)
            }
            
            raise e
    
    async def listen_for_messages(self, endpoint_path: str) -> None:
        """Listen for incoming messages from Observatory WebSocket."""
        try:
            if endpoint_path not in self._websocket_connections:
                raise ConnectionError(f"Not connected to {endpoint_path}")
            
            websocket = self._websocket_connections[endpoint_path]
            self._logger.info(f"Starting message listener for {endpoint_path}")
            
            async for message in websocket:
                try:
                    # Parse message
                    message_data = json.loads(message)
                    message_type = message_data.get("type", "unknown")
                    payload = message_data.get("payload", {})
                    correlation_id = message_data.get("correlation_id")
                    
                    # Update correlation tracking
                    if correlation_id and correlation_id in self._correlation_tracking:
                        self._correlation_tracking[correlation_id].update({
                            "status": "received",
                            "received_at": datetime.now()
                        })
                    
                    # Update endpoint message count
                    for endpoint in self._endpoints:
                        if endpoint.path == endpoint_path:
                            endpoint.message_count += 1
                            break
                    
                    # Handle message
                    if message_type in self._message_handlers:
                        await self._message_handlers[message_type](payload, correlation_id)
                    else:
                        self._logger.info(f"Received unhandled message type: {message_type}")
                    
                except json.JSONDecodeError as e:
                    self._logger.error(f"Failed to parse WebSocket message: {e}")
                except Exception as e:
                    self._logger.error(f"Error handling WebSocket message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self._logger.warning(f"WebSocket connection closed for {endpoint_path}")
            
            # Update endpoint status
            for endpoint in self._endpoints:
                if endpoint.path == endpoint_path:
                    endpoint.connection_status = "disconnected"
                    break
            
            # Attempt reconnection if enabled
            if self._connection_recovery_enabled:
                await self._attempt_reconnection(endpoint_path)
                
        except Exception as e:
            self._logger.error(f"Error in message listener for {endpoint_path}: {e}")
    
    async def _attempt_reconnection(self, endpoint_path: str, max_retries: int = 3) -> bool:
        """Attempt to reconnect to WebSocket endpoint."""
        for attempt in range(max_retries):
            self._logger.info(f"Attempting reconnection to {endpoint_path} (attempt {attempt + 1}/{max_retries})")
            
            # Wait before retry
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            if await self.connect_to_observatory(endpoint_path):
                self._logger.info(f"Successfully reconnected to {endpoint_path}")
                
                # Restart message listener
                asyncio.create_task(self.listen_for_messages(endpoint_path))
                return True
        
        self._logger.error(f"Failed to reconnect to {endpoint_path} after {max_retries} attempts")
        return False
    
    async def start_real_time_monitoring(self) -> Dict[str, Any]:
        """Start real-time monitoring of Observatory events."""
        self._logger.info("Starting real-time monitoring...")
        
        # Discover endpoints if not already done
        if not self._endpoints:
            self.discover_websocket_endpoints()
        
        # Connect to primary endpoints
        primary_endpoints = ["/ws/observatory", "/ws/anomalies", "/ws/doctor-status"]
        connected_endpoints = []
        
        for endpoint_path in primary_endpoints:
            if await self.connect_to_observatory(endpoint_path):
                connected_endpoints.append(endpoint_path)
                
                # Start message listener
                asyncio.create_task(self.listen_for_messages(endpoint_path))
        
        # Register default handlers
        self._register_default_handlers()
        
        monitoring_stats = {
            "endpoints_monitored": len(connected_endpoints),
            "handlers_registered": len(self._message_handlers),
            "connection_status": "active" if connected_endpoints else "failed",
            "monitoring_start_time": datetime.now().isoformat(),
            "connected_endpoints": connected_endpoints,
            "recovery_enabled": self._connection_recovery_enabled
        }
        
        self._logger.info(f"Real-time monitoring started: {len(connected_endpoints)} endpoints connected")
        return monitoring_stats
    
    def _register_default_handlers(self):
        """Register default message handlers."""
        
        async def handle_service_status(payload: Dict[str, Any], correlation_id: Optional[str] = None):
            self._logger.info(f"Service status update: {payload.get('service')} -> {payload.get('status')}")
        
        async def handle_anomaly_detected(payload: Dict[str, Any], correlation_id: Optional[str] = None):
            self._logger.warning(f"Anomaly detected: {payload.get('type')} - {payload.get('description')}")
        
        async def handle_health_check(payload: Dict[str, Any], correlation_id: Optional[str] = None):
            self._logger.info(f"Health check: {payload.get('component')} -> {payload.get('status')}")
        
        async def handle_system_event(payload: Dict[str, Any], correlation_id: Optional[str] = None):
            self._logger.info(f"System event: {payload.get('event_type')} - {payload.get('message')}")
        
        # Register handlers
        self.register_message_handler("service_status", handle_service_status)
        self.register_message_handler("anomaly_detected", handle_anomaly_detected)
        self.register_message_handler("health_check", handle_health_check)
        self.register_message_handler("system_event", handle_system_event)
    
    def get_connection_summary(self) -> Dict[str, Any]:
        """Get WebSocket connection summary."""
        connected_endpoints = [
            endpoint.path for endpoint in self._endpoints 
            if endpoint.connection_status == "connected"
        ]
        
        total_messages = sum(endpoint.message_count for endpoint in self._endpoints)
        
        return {
            "observatory_url": self._observatory_url,
            "endpoints_discovered": len(self._endpoints),
            "endpoints_connected": len(connected_endpoints),
            "connected_endpoints": connected_endpoints,
            "handlers_registered": len(self._message_handlers),
            "total_messages_received": total_messages,
            "correlation_tracking_active": len(self._correlation_tracking),
            "recovery_enabled": self._connection_recovery_enabled,
            "status": "operational" if connected_endpoints else "disconnected"
        }
    
    async def disconnect_all(self):
        """Disconnect from all WebSocket endpoints."""
        self._logger.info("Disconnecting from all WebSocket endpoints...")
        
        for endpoint_path, websocket in self._websocket_connections.items():
            try:
                await websocket.close()
                self._logger.info(f"Disconnected from {endpoint_path}")
            except Exception as e:
                self._logger.error(f"Error disconnecting from {endpoint_path}: {e}")
        
        # Update endpoint statuses
        for endpoint in self._endpoints:
            endpoint.connection_status = "disconnected"
        
        self._websocket_connections.clear()
        self._logger.info("All WebSocket connections closed")