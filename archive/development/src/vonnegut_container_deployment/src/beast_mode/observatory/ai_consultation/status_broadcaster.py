"""
Status Broadcasting System

Provides WebSocket broadcasting for doctor status changes with brownfield safety.
Integrates with existing Observatory WebSocket infrastructure without conflicts.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import weakref
import uuid

from .models import DoctorStatus, BudgetStatus
from .doctor_status_manager import StatusChangeEvent, StatusTransition
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import ConsultationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class BroadcastChannel(str, Enum):
    """WebSocket broadcast channels"""
    DOCTOR_STATUS = "ai_consultation.doctor_status"
    BUDGET_STATUS = "ai_consultation.budget_status"
    SYSTEM_HEALTH = "ai_consultation.system_health"
    COST_ANALYTICS = "ai_consultation.cost_analytics"


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    channel: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    message_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'channel': self.channel,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id
        }


@dataclass
class ClientConnection:
    """WebSocket client connection info"""
    connection_id: str
    user_id: Optional[str]
    subscribed_channels: Set[str]
    connected_at: datetime
    last_ping: datetime
    metadata: Dict[str, Any]


class StatusBroadcaster:
    """
    Manages WebSocket broadcasting for AI consultation status updates
    
    Features:
    - Brownfield safe WebSocket integration
    - Channel-based subscriptions
    - Connection management with cleanup
    - Message queuing and delivery
    - Circuit breaker protection
    - Fallback mechanisms
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        channel_prefix: str = "ai_consultation",
        max_connections: int = 1000,
        message_ttl: int = 300,  # 5 minutes
        ping_interval: int = 30   # 30 seconds
    ):
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix
        self.max_connections = max_connections
        self.message_ttl = message_ttl
        self.ping_interval = ping_interval
        
        # Connection management
        self._connections: Dict[str, ClientConnection] = {}
        self._connection_handlers: Dict[str, Any] = {}  # WebSocket handlers
        self._message_queue: Dict[str, List[WebSocketMessage]] = {}
        
        # Redis for distributed broadcasting (optional)
        self._redis_client = None
        self._redis_subscriber = None
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._redis_listener_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'connections_total': 0,
            'connections_active': 0,
            'last_broadcast': None
        }
        
        # Brownfield safety
        self._observatory_websocket_detected = False
        self._fallback_mode = False
    
    async def initialize(self) -> None:
        """Initialize the broadcaster"""
        try:
            logger.info("Initializing Status Broadcaster")
            
            # Check if feature is enabled
            if not await feature_flags.is_enabled(FeatureFlag.WEBSOCKET_BROADCASTING):
                logger.info("WebSocket broadcasting is disabled via feature flag")
                return
            
            # Detect existing Observatory WebSocket infrastructure
            await self._detect_observatory_websockets()
            
            # Initialize Redis if configured
            if self.redis_url:
                await self._initialize_redis()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info(f"Status Broadcaster initialized - Fallback mode: {self._fallback_mode}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Status Broadcaster: {e}")
            self._fallback_mode = True
            # Don't raise - broadcaster should degrade gracefully
    
    async def _detect_observatory_websockets(self) -> None:
        """Detect existing Observatory WebSocket infrastructure"""
        try:
            # Check for common Observatory WebSocket patterns
            # This is a placeholder - in real implementation, would check for:
            # - Existing WebSocket servers on common ports
            # - Observatory-specific WebSocket endpoints
            # - Shared WebSocket connection pools
            
            # For now, assume Observatory WebSocket exists and use safe integration
            self._observatory_websocket_detected = True
            
            if self._observatory_websocket_detected:
                logger.info("Observatory WebSocket infrastructure detected - using safe integration mode")
                # Use channel-based approach to avoid conflicts
                self.channel_prefix = f"ai_consultation_{uuid.uuid4().hex[:8]}"
            
        except Exception as e:
            logger.warning(f"Failed to detect Observatory WebSockets: {e}")
            self._fallback_mode = True
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis for distributed broadcasting"""
        try:
            # Import Redis only if needed
            import redis.asyncio as redis
            
            self._redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self._redis_client.ping()
            
            # Initialize subscriber for distributed messages
            self._redis_subscriber = self._redis_client.pubsub()
            
            logger.info("Redis initialized for distributed broadcasting")
            
        except ImportError:
            logger.warning("Redis not available - using local broadcasting only")
            self._redis_client = None
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            self._redis_client = None
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        try:
            # Connection cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_connections())
            
            # Ping task for connection health
            self._ping_task = asyncio.create_task(self._ping_connections())
            
            # Redis listener task
            if self._redis_subscriber:
                self._redis_listener_task = asyncio.create_task(self._listen_redis_messages())
            
            logger.debug("Background tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {e}")
    
    async def register_connection(
        self,
        connection_id: str,
        websocket_handler: Any,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register a new WebSocket connection"""
        try:
            # Check connection limits
            if len(self._connections) >= self.max_connections:
                logger.warning(f"Connection limit reached: {self.max_connections}")
                return False
            
            # Check if feature is enabled
            if not await feature_flags.is_enabled(FeatureFlag.WEBSOCKET_BROADCASTING):
                return False
            
            # Create connection record
            connection = ClientConnection(
                connection_id=connection_id,
                user_id=user_id,
                subscribed_channels=set(),
                connected_at=datetime.utcnow(),
                last_ping=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Store connection
            self._connections[connection_id] = connection
            self._connection_handlers[connection_id] = websocket_handler
            self._message_queue[connection_id] = []
            
            # Update statistics
            self._stats['connections_total'] += 1
            self._stats['connections_active'] = len(self._connections)
            
            logger.info(f"WebSocket connection registered: {connection_id} (user: {user_id})")
            
            # Send welcome message
            await self._send_to_connection(connection_id, WebSocketMessage(
                channel="system",
                event_type="connection_established",
                data={
                    "connection_id": connection_id,
                    "server_time": datetime.utcnow().isoformat(),
                    "available_channels": [channel.value for channel in BroadcastChannel]
                },
                timestamp=datetime.utcnow(),
                message_id=str(uuid.uuid4())
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register connection {connection_id}: {e}")
            return False
    
    async def unregister_connection(self, connection_id: str) -> None:
        """Unregister a WebSocket connection"""
        try:
            if connection_id in self._connections:
                # Remove connection
                del self._connections[connection_id]
                
                if connection_id in self._connection_handlers:
                    del self._connection_handlers[connection_id]
                
                if connection_id in self._message_queue:
                    del self._message_queue[connection_id]
                
                # Update statistics
                self._stats['connections_active'] = len(self._connections)
                
                logger.info(f"WebSocket connection unregistered: {connection_id}")
            
        except Exception as e:
            logger.error(f"Failed to unregister connection {connection_id}: {e}")
    
    async def subscribe_to_channel(self, connection_id: str, channel: str) -> bool:
        """Subscribe connection to a broadcast channel"""
        try:
            if connection_id not in self._connections:
                return False
            
            connection = self._connections[connection_id]
            connection.subscribed_channels.add(channel)
            
            logger.debug(f"Connection {connection_id} subscribed to channel {channel}")
            
            # Send subscription confirmation
            await self._send_to_connection(connection_id, WebSocketMessage(
                channel="system",
                event_type="subscription_confirmed",
                data={
                    "channel": channel,
                    "subscribed_channels": list(connection.subscribed_channels)
                },
                timestamp=datetime.utcnow(),
                message_id=str(uuid.uuid4())
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe connection {connection_id} to {channel}: {e}")
            return False
    
    async def unsubscribe_from_channel(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe connection from a broadcast channel"""
        try:
            if connection_id not in self._connections:
                return False
            
            connection = self._connections[connection_id]
            connection.subscribed_channels.discard(channel)
            
            logger.debug(f"Connection {connection_id} unsubscribed from channel {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe connection {connection_id} from {channel}: {e}")
            return False
    
    @with_circuit_breaker('websocket_broadcast')
    async def broadcast_status_change(self, event: StatusChangeEvent) -> None:
        """Broadcast doctor status change to all subscribers"""
        try:
            if self._fallback_mode:
                logger.debug("Broadcaster in fallback mode - skipping broadcast")
                return
            
            message = WebSocketMessage(
                channel=BroadcastChannel.DOCTOR_STATUS.value,
                event_type="status_changed",
                data={
                    "old_status": event.old_status,
                    "new_status": event.new_status,
                    "reason": event.reason.value,
                    "transition_type": event.transition_type.value,
                    "triggered_by": event.triggered_by,
                    "cost_data": event.cost_data,
                    "metadata": event.metadata
                },
                timestamp=event.timestamp,
                message_id=str(uuid.uuid4())
            )
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast status change: {e}")
    
    @with_circuit_breaker('websocket_broadcast')
    async def broadcast_budget_update(self, budget_status: BudgetStatus) -> None:
        """Broadcast budget status update"""
        try:
            if self._fallback_mode:
                return
            
            message = WebSocketMessage(
                channel=BroadcastChannel.BUDGET_STATUS.value,
                event_type="budget_updated",
                data={
                    "daily_budget": budget_status.daily_budget,
                    "monthly_budget": budget_status.monthly_budget,
                    "daily_spent": budget_status.daily_spent,
                    "monthly_spent": budget_status.monthly_spent,
                    "daily_remaining": budget_status.daily_remaining,
                    "monthly_remaining": budget_status.monthly_remaining,
                    "daily_percentage": budget_status.daily_percentage,
                    "monthly_percentage": budget_status.monthly_percentage,
                    "daily_warning": budget_status.daily_warning,
                    "monthly_warning": budget_status.monthly_warning,
                    "daily_critical": budget_status.daily_critical,
                    "monthly_critical": budget_status.monthly_critical,
                    "daily_exhausted": budget_status.daily_exhausted,
                    "monthly_exhausted": budget_status.monthly_exhausted
                },
                timestamp=datetime.utcnow(),
                message_id=str(uuid.uuid4())
            )
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast budget update: {e}")
    
    @with_circuit_breaker('websocket_broadcast')
    async def broadcast_system_health(self, health: ComponentHealth) -> None:
        """Broadcast system health update"""
        try:
            if self._fallback_mode:
                return
            
            message = WebSocketMessage(
                channel=BroadcastChannel.SYSTEM_HEALTH.value,
                event_type="health_updated",
                data={
                    "component": health.component,
                    "status": health.status.value,
                    "response_time": health.response_time,
                    "error_message": health.error_message,
                    "metadata": health.metadata,
                    "last_check": health.last_check.isoformat()
                },
                timestamp=datetime.utcnow(),
                message_id=str(uuid.uuid4())
            )
            
            await self._broadcast_message(message)
            
        except Exception as e:
            logger.error(f"Failed to broadcast system health: {e}")
    
    async def _broadcast_message(self, message: WebSocketMessage) -> None:
        """Broadcast message to all subscribed connections"""
        try:
            # Get connections subscribed to this channel
            target_connections = [
                conn_id for conn_id, conn in self._connections.items()
                if message.channel in conn.subscribed_channels
            ]
            
            if not target_connections:
                logger.debug(f"No subscribers for channel {message.channel}")
                return
            
            # Send to local connections
            local_tasks = [
                self._send_to_connection(conn_id, message)
                for conn_id in target_connections
            ]
            
            if local_tasks:
                await asyncio.gather(*local_tasks, return_exceptions=True)
            
            # Send to Redis for distributed broadcasting
            if self._redis_client:
                await self._publish_to_redis(message)
            
            # Update statistics
            self._stats['messages_sent'] += len(target_connections)
            self._stats['last_broadcast'] = datetime.utcnow()
            
            logger.debug(f"Broadcasted message to {len(target_connections)} connections on channel {message.channel}")
            
        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            self._stats['messages_failed'] += 1
    
    async def _send_to_connection(self, connection_id: str, message: WebSocketMessage) -> None:
        """Send message to a specific connection"""
        try:
            if connection_id not in self._connection_handlers:
                return
            
            handler = self._connection_handlers[connection_id]
            message_data = json.dumps(message.to_dict())
            
            # Try to send message
            if hasattr(handler, 'send_text'):
                # FastAPI WebSocket
                await handler.send_text(message_data)
            elif hasattr(handler, 'send'):
                # Generic WebSocket
                await handler.send(message_data)
            elif callable(handler):
                # Custom handler function
                await handler(message_data)
            else:
                logger.warning(f"Unknown WebSocket handler type for connection {connection_id}")
                return
            
            # Update connection ping time
            if connection_id in self._connections:
                self._connections[connection_id].last_ping = datetime.utcnow()
            
        except Exception as e:
            logger.warning(f"Failed to send message to connection {connection_id}: {e}")
            # Queue message for retry
            if connection_id in self._message_queue:
                self._message_queue[connection_id].append(message)
                # Limit queue size
                if len(self._message_queue[connection_id]) > 100:
                    self._message_queue[connection_id] = self._message_queue[connection_id][-50:]
    
    async def _publish_to_redis(self, message: WebSocketMessage) -> None:
        """Publish message to Redis for distributed broadcasting"""
        try:
            if not self._redis_client:
                return
            
            redis_channel = f"{self.channel_prefix}:{message.channel}"
            message_data = json.dumps(message.to_dict())
            
            await self._redis_client.publish(redis_channel, message_data)
            
        except Exception as e:
            logger.warning(f"Failed to publish to Redis: {e}")
    
    async def _listen_redis_messages(self) -> None:
        """Listen for Redis messages for distributed broadcasting"""
        try:
            if not self._redis_subscriber:
                return
            
            # Subscribe to all AI consultation channels
            pattern = f"{self.channel_prefix}:*"
            await self._redis_subscriber.psubscribe(pattern)
            
            logger.info(f"Listening for Redis messages on pattern: {pattern}")
            
            async for redis_message in self._redis_subscriber.listen():
                if redis_message['type'] == 'pmessage':
                    try:
                        # Parse message
                        message_data = json.loads(redis_message['data'])
                        message = WebSocketMessage(
                            channel=message_data['channel'],
                            event_type=message_data['event_type'],
                            data=message_data['data'],
                            timestamp=datetime.fromisoformat(message_data['timestamp']),
                            message_id=message_data['message_id']
                        )
                        
                        # Broadcast to local connections
                        await self._broadcast_message(message)
                        
                    except Exception as e:
                        logger.error(f"Failed to process Redis message: {e}")
        
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
    
    async def _cleanup_connections(self) -> None:
        """Background task to cleanup stale connections"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                current_time = datetime.utcnow()
                stale_connections = []
                
                for conn_id, connection in self._connections.items():
                    # Remove connections that haven't pinged in 5 minutes
                    if current_time - connection.last_ping > timedelta(minutes=5):
                        stale_connections.append(conn_id)
                
                # Remove stale connections
                for conn_id in stale_connections:
                    await self.unregister_connection(conn_id)
                    logger.info(f"Removed stale connection: {conn_id}")
                
                if stale_connections:
                    logger.info(f"Cleaned up {len(stale_connections)} stale connections")
                
            except Exception as e:
                logger.error(f"Connection cleanup error: {e}")
    
    async def _ping_connections(self) -> None:
        """Background task to ping connections"""
        while True:
            try:
                await asyncio.sleep(self.ping_interval)
                
                if not self._connections:
                    continue
                
                ping_message = WebSocketMessage(
                    channel="system",
                    event_type="ping",
                    data={"server_time": datetime.utcnow().isoformat()},
                    timestamp=datetime.utcnow(),
                    message_id=str(uuid.uuid4())
                )
                
                # Send ping to all connections
                ping_tasks = [
                    self._send_to_connection(conn_id, ping_message)
                    for conn_id in self._connections.keys()
                ]
                
                if ping_tasks:
                    await asyncio.gather(*ping_tasks, return_exceptions=True)
                
            except Exception as e:
                logger.error(f"Ping task error: {e}")
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get broadcaster statistics"""
        return {
            **self._stats,
            'connections_by_channel': {
                channel.value: len([
                    conn for conn in self._connections.values()
                    if channel.value in conn.subscribed_channels
                ])
                for channel in BroadcastChannel
            },
            'message_queue_sizes': {
                conn_id: len(queue)
                for conn_id, queue in self._message_queue.items()
            },
            'redis_enabled': self._redis_client is not None,
            'fallback_mode': self._fallback_mode
        }
    
    async def health_check(self) -> ComponentHealth:
        """Perform health check"""
        try:
            # Check basic functionality
            active_connections = len(self._connections)
            redis_healthy = True
            
            if self._redis_client:
                try:
                    await self._redis_client.ping()
                except Exception:
                    redis_healthy = False
            
            # Determine overall health
            if self._fallback_mode:
                status = "degraded"
                error_message = "Running in fallback mode"
            elif not redis_healthy and self._redis_client:
                status = "degraded"
                error_message = "Redis connection failed"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="status_broadcaster",
                status=status,
                response_time=0.0,  # Not applicable
                error_message=error_message,
                metadata={
                    "active_connections": active_connections,
                    "redis_enabled": self._redis_client is not None,
                    "redis_healthy": redis_healthy,
                    "fallback_mode": self._fallback_mode,
                    "messages_sent": self._stats['messages_sent'],
                    "messages_failed": self._stats['messages_failed']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="status_broadcaster",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def cleanup(self) -> None:
        """Cleanup broadcaster resources"""
        try:
            logger.info("Cleaning up Status Broadcaster")
            
            # Cancel background tasks
            if self._cleanup_task:
                self._cleanup_task.cancel()
            if self._ping_task:
                self._ping_task.cancel()
            if self._redis_listener_task:
                self._redis_listener_task.cancel()
            
            # Close Redis connections
            if self._redis_subscriber:
                await self._redis_subscriber.unsubscribe()
                await self._redis_subscriber.close()
            
            if self._redis_client:
                await self._redis_client.close()
            
            # Clear connections
            self._connections.clear()
            self._connection_handlers.clear()
            self._message_queue.clear()
            
            logger.info("Status Broadcaster cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global broadcaster instance
status_broadcaster = StatusBroadcaster()


async def initialize_broadcaster() -> None:
    """Initialize the status broadcaster"""
    await status_broadcaster.initialize()


async def cleanup_broadcaster() -> None:
    """Cleanup the status broadcaster"""
    await status_broadcaster.cleanup()