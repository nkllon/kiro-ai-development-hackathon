"""WebSocket heartbeat mechanism with ping-pong frames and connection health monitoring."""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
import uuid

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from .exceptions import (
    ConnectionFailedError,
    ConnectionTimeoutError,
    ProtocolError,
)

logger = logging.getLogger(__name__)


class HeartbeatStatus(Enum):
    """Heartbeat status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    TIMEOUT = "timeout"
    DISCONNECTED = "disconnected"


@dataclass
class HeartbeatConfig:
    """Configuration for WebSocket heartbeat mechanism."""
    ping_interval: float = 30.0  # Default 30 seconds
    pong_timeout: float = 90.0  # Default 90 seconds timeout
    max_retries: int = 3  # Maximum retry attempts
    backoff_base: float = 2.0  # Exponential backoff base
    max_backoff: float = 300.0  # Maximum backoff delay (5 minutes)
    jitter_range: float = 0.1  # Random jitter range (10%)
    health_check_interval: float = 60.0  # Health check interval
    connection_timeout: float = 10.0  # Connection establishment timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'ping_interval': self.ping_interval,
            'pong_timeout': self.pong_timeout,
            'max_retries': self.max_retries,
            'backoff_base': self.backoff_base,
            'max_backoff': self.max_backoff,
            'jitter_range': self.jitter_range,
            'health_check_interval': self.health_check_interval,
            'connection_timeout': self.connection_timeout,
        }


@dataclass
class HeartbeatMetrics:
    """Heartbeat performance metrics."""
    endpoint: str
    last_ping_time: Optional[datetime] = None
    last_pong_time: Optional[datetime] = None
    ping_count: int = 0
    pong_count: int = 0
    missed_heartbeats: int = 0
    connection_latency_ms: float = 0.0
    average_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    consecutive_timeouts: int = 0
    total_reconnections: int = 0
    last_reconnection_time: Optional[datetime] = None
    uptime_percentage: float = 100.0
    health_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'endpoint': self.endpoint,
            'last_ping_time': self.last_ping_time.isoformat() if self.last_ping_time else None,
            'last_pong_time': self.last_pong_time.isoformat() if self.last_pong_time else None,
            'ping_count': self.ping_count,
            'pong_count': self.pong_count,
            'missed_heartbeats': self.missed_heartbeats,
            'connection_latency_ms': self.connection_latency_ms,
            'average_latency_ms': self.average_latency_ms,
            'max_latency_ms': self.max_latency_ms,
            'min_latency_ms': self.min_latency_ms if self.min_latency_ms != float('inf') else 0.0,
            'consecutive_timeouts': self.consecutive_timeouts,
            'total_reconnections': self.total_reconnections,
            'last_reconnection_time': self.last_reconnection_time.isoformat() if self.last_reconnection_time else None,
            'uptime_percentage': self.uptime_percentage,
            'health_score': self.health_score,
        }


@dataclass
class HeartbeatEvent:
    """Heartbeat event for monitoring and callbacks."""
    event_type: str
    endpoint: str
    timestamp: datetime
    status: HeartbeatStatus
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_type': self.event_type,
            'endpoint': self.endpoint,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status.value,
            'latency_ms': self.latency_ms,
            'error_message': self.error_message,
            'metadata': self.metadata,
        }


class WebSocketHeartbeat:
    """Comprehensive WebSocket heartbeat mechanism with ping-pong frames."""
    
    def __init__(self, endpoint: str, config: Optional[HeartbeatConfig] = None):
        self.endpoint = endpoint
        self.config = config or HeartbeatConfig()
        self.metrics = HeartbeatMetrics(endpoint=endpoint)
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.is_running = False
        
        # Background tasks
        self._ping_task: Optional[asyncio.Task] = None
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._background_tasks: Set[asyncio.Task] = set()
        
        # Synchronization
        self._connection_lock = asyncio.Lock()
        self._ping_lock = asyncio.Lock()
        
        # Event callbacks
        self._event_callbacks: Set[Callable[[HeartbeatEvent], None]] = set()
        
        # Retry state
        self._retry_count = 0
        self._last_retry_time: Optional[datetime] = None
        
        self._log_action("heartbeat_initialized", {
            "endpoint": self.endpoint,
            "config": self.config.to_dict()
        })
    
    async def start(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Start the heartbeat mechanism."""
        async with self._connection_lock:
            if self.is_running:
                return
            
            self._log_action("heartbeat_starting", {"endpoint": self.endpoint})
            
            try:
                # Establish initial connection
                await self._connect(headers)
                
                # Start background tasks
                self._ping_task = asyncio.create_task(self._ping_loop())
                self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
                
                self._background_tasks.add(self._ping_task)
                self._background_tasks.add(self._health_monitor_task)
                
                # Add done callbacks
                self._ping_task.add_done_callback(self._background_tasks.discard)
                self._health_monitor_task.add_done_callback(self._background_tasks.discard)
                
                self.is_running = True
                
                self._log_action("heartbeat_started", {
                    "endpoint": self.endpoint,
                    "ping_interval": self.config.ping_interval,
                    "pong_timeout": self.config.pong_timeout
                })
                
                # Emit start event
                await self._emit_event("heartbeat_started", HeartbeatStatus.HEALTHY)
                
            except Exception as e:
                self._log_action("heartbeat_start_failed", {
                    "endpoint": self.endpoint,
                    "error": str(e)
                })
                await self._emit_event("heartbeat_start_failed", HeartbeatStatus.UNHEALTHY, error_message=str(e))
                raise
    
    async def stop(self) -> None:
        """Stop the heartbeat mechanism."""
        async with self._connection_lock:
            if not self.is_running:
                return
            
            self._log_action("heartbeat_stopping", {"endpoint": self.endpoint})
            
            self.is_running = False
            
            # Cancel background tasks
            for task in self._background_tasks.copy():
                task.cancel()
            
            # Close connection
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            
            self.is_connected = False
            self.websocket = None
            
            self._log_action("heartbeat_stopped", {"endpoint": self.endpoint})
            await self._emit_event("heartbeat_stopped", HeartbeatStatus.DISCONNECTED)
    
    async def send_ping(self) -> bool:
        """Send a ping frame and wait for pong response."""
        if not self.is_connected or not self.websocket:
            return False
        
        async with self._ping_lock:
            ping_id = str(uuid.uuid4())
            ping_time = time.time()
            
            try:
                # Send ping frame
                ping_message = {
                    "type": "ping",
                    "id": ping_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.websocket.send(json.dumps(ping_message))
                self.metrics.ping_count += 1
                self.metrics.last_ping_time = datetime.utcnow()
                
                self._log_action("ping_sent", {
                    "endpoint": self.endpoint,
                    "ping_id": ping_id,
                    "ping_count": self.metrics.ping_count
                })
                
                # Wait for pong response
                try:
                    response = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=self.config.pong_timeout
                    )
                    
                    pong_time = time.time()
                    latency_ms = (pong_time - ping_time) * 1000
                    
                    # Parse response
                    response_data = json.loads(response) if isinstance(response, str) else response
                    
                    if response_data.get("type") == "pong" and response_data.get("id") == ping_id:
                        # Successful pong received
                        self.metrics.pong_count += 1
                        self.metrics.last_pong_time = datetime.utcnow()
                        self.metrics.connection_latency_ms = latency_ms
                        self.metrics.consecutive_timeouts = 0
                        
                        # Update latency statistics
                        self._update_latency_stats(latency_ms)
                        
                        # Update health score
                        self._update_health_score()
                        
                        self._log_action("pong_received", {
                            "endpoint": self.endpoint,
                            "ping_id": ping_id,
                            "latency_ms": latency_ms,
                            "pong_count": self.metrics.pong_count
                        })
                        
                        await self._emit_event("pong_received", HeartbeatStatus.HEALTHY, latency_ms=latency_ms)
                        return True
                    
                    else:
                        # Invalid pong response
                        self.metrics.missed_heartbeats += 1
                        self._log_action("invalid_pong", {
                            "endpoint": self.endpoint,
                            "ping_id": ping_id,
                            "response": response_data
                        })
                        
                        await self._emit_event("invalid_pong", HeartbeatStatus.DEGRADED, 
                                             error_message="Invalid pong response")
                        return False
                
                except asyncio.TimeoutError:
                    # Pong timeout
                    self.metrics.missed_heartbeats += 1
                    self.metrics.consecutive_timeouts += 1
                    
                    self._log_action("pong_timeout", {
                        "endpoint": self.endpoint,
                        "ping_id": ping_id,
                        "consecutive_timeouts": self.metrics.consecutive_timeouts
                    })
                    
                    await self._emit_event("pong_timeout", HeartbeatStatus.TIMEOUT,
                                         error_message=f"Pong timeout after {self.config.pong_timeout}s")
                    return False
                
            except ConnectionClosed:
                self.is_connected = False
                self._log_action("connection_closed_during_ping", {"endpoint": self.endpoint})
                await self._emit_event("connection_closed", HeartbeatStatus.DISCONNECTED,
                                     error_message="Connection closed during ping")
                return False
            
            except Exception as e:
                self._log_action("ping_error", {
                    "endpoint": self.endpoint,
                    "ping_id": ping_id,
                    "error": str(e)
                })
                await self._emit_event("ping_error", HeartbeatStatus.UNHEALTHY, error_message=str(e))
                return False
    
    async def _connect(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Establish WebSocket connection."""
        try:
            connection_headers = headers or {}
            if 'User-Agent' not in connection_headers:
                connection_headers['User-Agent'] = 'BeastMode-Observatory-Heartbeat/1.0'
            
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    self.endpoint,
                    extra_headers=connection_headers,
                    ping_interval=None,  # We handle ping/pong manually
                    ping_timeout=None,
                ),
                timeout=self.config.connection_timeout
            )
            
            self.is_connected = True
            self.metrics.total_reconnections += 1
            self.metrics.last_reconnection_time = datetime.utcnow()
            self._retry_count = 0
            
            self._log_action("connection_established", {
                "endpoint": self.endpoint,
                "reconnection_count": self.metrics.total_reconnections
            })
            
            await self._emit_event("connection_established", HeartbeatStatus.HEALTHY)
            
        except asyncio.TimeoutError:
            error_msg = f"Connection timeout to {self.endpoint}"
            self._log_action("connection_timeout", {"endpoint": self.endpoint})
            raise ConnectionTimeoutError(error_msg, self.endpoint)
        
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            self._log_action("connection_failed", {
                "endpoint": self.endpoint,
                "error": str(e)
            })
            raise ConnectionFailedError(error_msg, self.endpoint)
    
    async def _ping_loop(self) -> None:
        """Main ping loop for sending periodic heartbeats."""
        while self.is_running:
            try:
                # Calculate next ping interval with jitter
                base_interval = self.config.ping_interval
                jitter = random.uniform(-self.config.jitter_range, self.config.jitter_range)
                interval = base_interval * (1 + jitter)
                
                await asyncio.sleep(interval)
                
                if not self.is_running:
                    break
                
                # Send ping
                ping_success = await self.send_ping()
                
                if not ping_success and self.is_running:
                    # Handle ping failure
                    await self._handle_ping_failure()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log_action("ping_loop_error", {
                    "endpoint": self.endpoint,
                    "error": str(e)
                })
                await self._emit_event("ping_loop_error", HeartbeatStatus.UNHEALTHY, error_message=str(e))
    
    async def _health_monitor_loop(self) -> None:
        """Monitor overall connection health."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                if not self.is_running:
                    break
                
                # Perform health assessment
                health_status = self._assess_health()
                
                # Update uptime percentage
                self._update_uptime_percentage()
                
                self._log_action("health_check", {
                    "endpoint": self.endpoint,
                    "status": health_status.value,
                    "health_score": self.metrics.health_score,
                    "uptime_percentage": self.metrics.uptime_percentage
                })
                
                await self._emit_event("health_check", health_status)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log_action("health_monitor_error", {
                    "endpoint": self.endpoint,
                    "error": str(e)
                })
    
    async def _handle_ping_failure(self) -> None:
        """Handle ping failure with retry logic."""
        if self._retry_count >= self.config.max_retries:
            self._log_action("max_retries_exceeded", {
                "endpoint": self.endpoint,
                "retry_count": self._retry_count
            })
            await self._emit_event("max_retries_exceeded", HeartbeatStatus.UNHEALTHY,
                                 error_message="Maximum retry attempts exceeded")
            return
        
        # Calculate backoff delay
        backoff_delay = min(
            self.config.backoff_base ** self._retry_count,
            self.config.max_backoff
        )
        
        # Add jitter
        jitter = random.uniform(-self.config.jitter_range, self.config.jitter_range)
        delay = backoff_delay * (1 + jitter)
        
        self._retry_count += 1
        self._last_retry_time = datetime.utcnow()
        
        self._log_action("ping_failure_retry", {
            "endpoint": self.endpoint,
            "retry_count": self._retry_count,
            "backoff_delay": delay
        })
        
        await self._emit_event("ping_failure_retry", HeartbeatStatus.DEGRADED,
                             metadata={"retry_count": self._retry_count, "backoff_delay": delay})
        
        # Wait before retry
        await asyncio.sleep(delay)
        
        # Attempt reconnection
        try:
            await self._reconnect()
        except Exception as e:
            self._log_action("reconnection_failed", {
                "endpoint": self.endpoint,
                "retry_count": self._retry_count,
                "error": str(e)
            })
            await self._emit_event("reconnection_failed", HeartbeatStatus.UNHEALTHY, error_message=str(e))
    
    async def _reconnect(self) -> None:
        """Attempt to reconnect the WebSocket."""
        async with self._connection_lock:
            if self.is_connected:
                return
            
            self._log_action("reconnecting", {"endpoint": self.endpoint})
            
            try:
                # Close existing connection
                if self.websocket and not self.websocket.closed:
                    await self.websocket.close()
                
                # Establish new connection
                await self._connect()
                
                self._log_action("reconnection_successful", {"endpoint": self.endpoint})
                await self._emit_event("reconnection_successful", HeartbeatStatus.HEALTHY)
                
            except Exception as e:
                self._log_action("reconnection_failed", {
                    "endpoint": self.endpoint,
                    "error": str(e)
                })
                await self._emit_event("reconnection_failed", HeartbeatStatus.UNHEALTHY, error_message=str(e))
                raise
    
    def _update_latency_stats(self, latency_ms: float) -> None:
        """Update latency statistics."""
        if self.metrics.min_latency_ms == float('inf'):
            self.metrics.min_latency_ms = latency_ms
        
        self.metrics.min_latency_ms = min(self.metrics.min_latency_ms, latency_ms)
        self.metrics.max_latency_ms = max(self.metrics.max_latency_ms, latency_ms)
        
        # Calculate running average
        total_pings = self.metrics.ping_count
        if total_pings > 0:
            self.metrics.average_latency_ms = (
                (self.metrics.average_latency_ms * (total_pings - 1) + latency_ms) / total_pings
            )
        else:
            self.metrics.average_latency_ms = latency_ms
    
    def _update_health_score(self) -> None:
        """Update connection health score."""
        # Base health score
        health_score = 1.0
        
        # Penalize missed heartbeats
        if self.metrics.missed_heartbeats > 0:
            missed_ratio = self.metrics.missed_heartbeats / max(self.metrics.ping_count, 1)
            health_score -= missed_ratio * 0.3
        
        # Penalize consecutive timeouts
        if self.metrics.consecutive_timeouts > 0:
            health_score -= min(self.metrics.consecutive_timeouts * 0.1, 0.5)
        
        # Penalize high latency
        if self.metrics.average_latency_ms > 1000:  # > 1 second
            latency_penalty = min((self.metrics.average_latency_ms - 1000) / 10000, 0.3)
            health_score -= latency_penalty
        
        # Ensure health score is between 0 and 1
        self.metrics.health_score = max(0.0, min(1.0, health_score))
    
    def _update_uptime_percentage(self) -> None:
        """Update uptime percentage based on recent activity."""
        # This is a simplified calculation
        # In a real implementation, you'd track uptime more precisely
        if self.metrics.consecutive_timeouts == 0 and self.metrics.missed_heartbeats == 0:
            self.metrics.uptime_percentage = 100.0
        else:
            # Calculate based on recent ping/pong success rate
            recent_success_rate = self.metrics.pong_count / max(self.metrics.ping_count, 1)
            self.metrics.uptime_percentage = recent_success_rate * 100.0
    
    def _assess_health(self) -> HeartbeatStatus:
        """Assess overall connection health."""
        if not self.is_connected:
            return HeartbeatStatus.DISCONNECTED
        
        if self.metrics.consecutive_timeouts >= 3:
            return HeartbeatStatus.TIMEOUT
        
        if self.metrics.health_score < 0.5:
            return HeartbeatStatus.UNHEALTHY
        
        if self.metrics.health_score < 0.8:
            return HeartbeatStatus.DEGRADED
        
        return HeartbeatStatus.HEALTHY
    
    def add_event_callback(self, callback: Callable[[HeartbeatEvent], None]) -> None:
        """Add event callback for heartbeat events."""
        self._event_callbacks.add(callback)
    
    def remove_event_callback(self, callback: Callable[[HeartbeatEvent], None]) -> None:
        """Remove event callback."""
        self._event_callbacks.discard(callback)
    
    async def _emit_event(self, event_type: str, status: HeartbeatStatus, 
                         latency_ms: Optional[float] = None, error_message: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """Emit heartbeat event to callbacks."""
        event = HeartbeatEvent(
            event_type=event_type,
            endpoint=self.endpoint,
            timestamp=datetime.utcnow(),
            status=status,
            latency_ms=latency_ms,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current heartbeat metrics."""
        return self.metrics.to_dict()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current heartbeat status."""
        return {
            'endpoint': self.endpoint,
            'is_connected': self.is_connected,
            'is_running': self.is_running,
            'status': self._assess_health().value,
            'retry_count': self._retry_count,
            'last_retry_time': self._last_retry_time.isoformat() if self._last_retry_time else None,
            'config': self.config.to_dict(),
            'metrics': self.metrics.to_dict()
        }
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log heartbeat action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '8.0',
            'action': f'heartbeat_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))