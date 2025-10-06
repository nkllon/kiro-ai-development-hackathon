"""WebSocket connection management with state tracking and heartbeat integration."""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Callable

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode, WebSocketException

from .exceptions import (
    AuthenticationError,
    ConnectionFailedError,
    ConnectionTimeoutError,
    ProtocolError,
    RateLimitError,
)
from .heartbeat import WebSocketHeartbeat, HeartbeatConfig, HeartbeatEvent

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """WebSocket connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"
    RECONNECTING = "reconnecting"


@dataclass
class ConnectionState:
    """WebSocket connection state information."""
    endpoint: str
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    connection_time: Optional[datetime] = None
    last_message_time: Optional[datetime] = None
    failure_count: int = 0
    last_error: Optional[str] = None
    message_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    heartbeat_enabled: bool = True
    heartbeat_metrics: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection state to dictionary."""
        return {
            'endpoint': self.endpoint,
            'status': self.status.value,
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'failure_count': self.failure_count,
            'last_error': self.last_error,
            'message_count': self.message_count,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'heartbeat_enabled': self.heartbeat_enabled,
            'heartbeat_metrics': self.heartbeat_metrics,
            'metadata': self.metadata,
        }


class WebSocketConnection:
    """Manages a single WebSocket connection with state tracking and heartbeat."""

    def __init__(self, endpoint: str, connection_timeout: float = 10.0, 
                 heartbeat_config: Optional[HeartbeatConfig] = None):
        self.endpoint = endpoint
        self.connection_timeout = connection_timeout
        self.state = ConnectionState(endpoint=endpoint)
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connection_lock = asyncio.Lock()
        self._message_queue = asyncio.Queue()
        self._background_tasks = set()
        
        # Heartbeat integration
        self.heartbeat_config = heartbeat_config or HeartbeatConfig()
        self.heartbeat: Optional[WebSocketHeartbeat] = None
        self._heartbeat_callbacks = set()

    async def connect(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Establish WebSocket connection."""
        async with self._connection_lock:
            if self.state.status == ConnectionStatus.CONNECTED:
                return

            self.state.status = ConnectionStatus.CONNECTING
            self._log_action("connecting", {"endpoint": self.endpoint})

            try:
                # Add default headers if not provided
                connection_headers = headers or {}
                if 'User-Agent' not in connection_headers:
                    connection_headers['User-Agent'] = 'BeastMode-Observatory/1.0'

                self.websocket = await asyncio.wait_for(
                    websockets.connect(
                        self.endpoint,
                        extra_headers=connection_headers,
                        ping_interval=20,
                        ping_timeout=10,
                    ),
                    timeout=self.connection_timeout
                )

                self.state.status = ConnectionStatus.CONNECTED
                self.state.connection_time = datetime.utcnow()
                self.state.failure_count = 0
                self.state.last_error = None

                self._log_action("connected", {
                    "endpoint": self.endpoint,
                    "connection_time": self.state.connection_time.isoformat()
                })

                # Start heartbeat if enabled
                if self.state.heartbeat_enabled:
                    await self._start_heartbeat()

                # Start background message processing
                task = asyncio.create_task(self._process_messages())
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)

            except asyncio.TimeoutError:
                self.state.status = ConnectionStatus.FAILED
                self.state.failure_count += 1
                error_msg = f"Connection timeout to {self.endpoint}"
                self.state.last_error = error_msg
                self._log_action("connection_failed", {"error": error_msg, "type": "timeout"})
                raise ConnectionTimeoutError(error_msg, self.endpoint)

            except InvalidStatusCode as e:
                self.state.status = ConnectionStatus.FAILED
                self.state.failure_count += 1
                error_msg = f"Connection failed with status {e.status_code}: {e.reason}"
                self.state.last_error = error_msg

                # Handle specific status codes
                if e.status_code == 401:
                    self._log_action("connection_failed", {"error": error_msg, "type": "authentication"})
                    raise AuthenticationError(error_msg, self.endpoint)
                elif e.status_code == 429:
                    self._log_action("connection_failed", {"error": error_msg, "type": "rate_limit"})
                    raise RateLimitError(error_msg, self.endpoint)
                else:
                    self._log_action("connection_failed", {"error": error_msg, "type": "status_code"})
                    raise ConnectionFailedError(error_msg, self.endpoint)

            except (ConnectionClosed, WebSocketException) as e:
                self.state.status = ConnectionStatus.FAILED
                self.state.failure_count += 1
                error_msg = f"WebSocket error: {str(e)}"
                self.state.last_error = error_msg
                self._log_action("connection_failed", {"error": error_msg, "type": "websocket"})
                raise ProtocolError(error_msg, self.endpoint)

            except Exception as e:
                self.state.status = ConnectionStatus.FAILED
                self.state.failure_count += 1
                error_msg = f"Unexpected connection error: {str(e)}"
                self.state.last_error = error_msg
                self._log_action("connection_failed", {"error": error_msg, "type": "unexpected"})
                raise ConnectionFailedError(error_msg, self.endpoint)

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        async with self._connection_lock:
            # Stop heartbeat if running
            if self.heartbeat:
                await self.heartbeat.stop()
                self.heartbeat = None
            
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
                self._log_action("disconnected", {"endpoint": self.endpoint})

            self.state.status = ConnectionStatus.DISCONNECTED
            self.websocket = None

            # Cancel background tasks
            for task in self._background_tasks.copy():
                task.cancel()

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message through WebSocket connection."""
        if self.state.status != ConnectionStatus.CONNECTED or not self.websocket:
            raise ConnectionFailedError("WebSocket not connected", self.endpoint)

        try:
            message_str = json.dumps(message)
            await self.websocket.send(message_str)

            self.state.message_count += 1
            self.state.bytes_sent += len(message_str.encode('utf-8'))
            self.state.last_message_time = datetime.utcnow()

            self._log_action("message_sent", {
                "endpoint": self.endpoint,
                "message_size": len(message_str),
                "message_count": self.state.message_count
            })

        except ConnectionClosed:
            self.state.status = ConnectionStatus.FAILED
            error_msg = "Connection closed while sending message"
            self.state.last_error = error_msg
            self._log_action("send_failed", {"error": error_msg, "type": "connection_closed"})
            raise ConnectionFailedError(error_msg, self.endpoint)

        except Exception as e:
            error_msg = f"Failed to send message: {str(e)}"
            self.state.last_error = error_msg
            self._log_action("send_failed", {"error": error_msg, "type": "unexpected"})
            raise

    async def _process_messages(self) -> None:
        """Process incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                self.state.bytes_received += len(message.encode('utf-8') if isinstance(message, str) else message)
                self.state.last_message_time = datetime.utcnow()

                # Handle pong responses for heartbeat
                if isinstance(message, str):
                    try:
                        message_data = json.loads(message)
                        if message_data.get("type") == "pong" and self.heartbeat:
                            # Forward pong to heartbeat mechanism
                            await self.websocket.send(json.dumps(message_data))
                    except json.JSONDecodeError:
                        pass  # Not a JSON message, continue normal processing

                self._log_action("message_received", {
                    "endpoint": self.endpoint,
                    "message_size": len(message.encode('utf-8') if isinstance(message, str) else message)
                })

        except ConnectionClosed:
            self.state.status = ConnectionStatus.DISCONNECTED
            self._log_action("connection_lost", {"endpoint": self.endpoint})
        except Exception as e:
            self.state.status = ConnectionStatus.FAILED
            self.state.last_error = f"Message processing error: {str(e)}"
            self._log_action("message_processing_error", {
                "endpoint": self.endpoint,
                "error": str(e)
            })

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return (
            self.state.status == ConnectionStatus.CONNECTED and
            self.websocket is not None and
            not self.websocket.closed
        )

    def get_connection_metrics(self) -> Dict[str, Any]:
        """Get connection performance metrics."""
        uptime = None
        if self.state.connection_time:
            uptime = (datetime.utcnow() - self.state.connection_time).total_seconds()

        return {
            'endpoint': self.endpoint,
            'status': self.state.status.value,
            'uptime_seconds': uptime,
            'message_count': self.state.message_count,
            'bytes_sent': self.state.bytes_sent,
            'bytes_received': self.state.bytes_received,
            'failure_count': self.state.failure_count,
            'last_error': self.state.last_error,
        }

    async def _start_heartbeat(self) -> None:
        """Start heartbeat mechanism."""
        if self.heartbeat:
            return
        
        self.heartbeat = WebSocketHeartbeat(self.endpoint, self.heartbeat_config)
        
        # Add heartbeat event callbacks
        self.heartbeat.add_event_callback(self._on_heartbeat_event)
        
        # Start heartbeat
        await self.heartbeat.start()
        
        self._log_action("heartbeat_started", {
            "endpoint": self.endpoint,
            "config": self.heartbeat_config.to_dict()
        })
    
    async def _on_heartbeat_event(self, event: HeartbeatEvent) -> None:
        """Handle heartbeat events."""
        # Update connection state with heartbeat metrics
        self.state.heartbeat_metrics = self.heartbeat.get_metrics() if self.heartbeat else None
        
        # Notify registered callbacks
        for callback in self._heartbeat_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Heartbeat callback error: {e}")
        
        # Handle critical heartbeat events
        if event.status.value in ["timeout", "unhealthy"]:
            self.state.status = ConnectionStatus.FAILED
            self.state.last_error = f"Heartbeat failure: {event.error_message}"
            
            self._log_action("heartbeat_failure", {
                "endpoint": self.endpoint,
                "status": event.status.value,
                "error": event.error_message
            })
    
    def enable_heartbeat(self, config: Optional[HeartbeatConfig] = None) -> None:
        """Enable heartbeat mechanism."""
        self.state.heartbeat_enabled = True
        if config:
            self.heartbeat_config = config
        
        self._log_action("heartbeat_enabled", {
            "endpoint": self.endpoint,
            "config": self.heartbeat_config.to_dict()
        })
    
    def disable_heartbeat(self) -> None:
        """Disable heartbeat mechanism."""
        self.state.heartbeat_enabled = False
        
        if self.heartbeat:
            asyncio.create_task(self.heartbeat.stop())
            self.heartbeat = None
        
        self._log_action("heartbeat_disabled", {"endpoint": self.endpoint})
    
    def add_heartbeat_callback(self, callback: Callable[[HeartbeatEvent], None]) -> None:
        """Add callback for heartbeat events."""
        self._heartbeat_callbacks.add(callback)
    
    def remove_heartbeat_callback(self, callback: Callable[[HeartbeatEvent], None]) -> None:
        """Remove heartbeat callback."""
        self._heartbeat_callbacks.discard(callback)
    
    def get_heartbeat_metrics(self) -> Optional[Dict[str, Any]]:
        """Get heartbeat metrics."""
        return self.heartbeat.get_metrics() if self.heartbeat else None
    
    def get_heartbeat_status(self) -> Optional[Dict[str, Any]]:
        """Get heartbeat status."""
        return self.heartbeat.get_status() if self.heartbeat else None

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log WebSocket action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '8.0',
            'action': f'websocket_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))