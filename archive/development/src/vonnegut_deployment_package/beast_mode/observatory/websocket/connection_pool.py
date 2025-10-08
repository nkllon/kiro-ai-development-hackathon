"""WebSocket connection pooling and reuse mechanisms for performance optimization."""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from weakref import WeakValueDictionary

import psutil
from websockets.exceptions import ConnectionClosed

from .connection import WebSocketConnection, ConnectionStatus
from .exceptions import ConnectionFailedError, ProtocolError

logger = logging.getLogger(__name__)


class PoolStrategy(Enum):
    """Connection pool strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_LATENCY = "least_latency"
    STICKY_SESSION = "sticky_session"


@dataclass
class PoolMetrics:
    """Connection pool performance metrics."""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_connections': self.total_connections,
            'active_connections': self.active_connections,
            'idle_connections': self.idle_connections,
            'failed_connections': self.failed_connections,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'avg_response_time': self.avg_response_time,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
        }


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pooling."""
    max_connections: int = 50
    min_connections: int = 5
    max_idle_time: int = 300  # seconds
    connection_timeout: float = 10.0
    health_check_interval: int = 30  # seconds
    pool_strategy: PoolStrategy = PoolStrategy.LEAST_CONNECTIONS
    enable_compression: bool = True
    enable_keepalive: bool = True
    keepalive_interval: int = 20  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0


class ConnectionPool:
    """High-performance WebSocket connection pool with reuse mechanisms."""

    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self._connections: Dict[str, List[WebSocketConnection]] = defaultdict(list)
        self._active_connections: Set[WebSocketConnection] = set()
        self._idle_connections: deque = deque()
        self._connection_metrics: Dict[WebSocketConnection, Dict[str, Any]] = {}
        self._pool_metrics = PoolMetrics()
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._session_sticky_map: Dict[str, WebSocketConnection] = {}
        self._connection_creation_times: Dict[WebSocketConnection, datetime] = {}
        self._last_used_times: Dict[WebSocketConnection, datetime] = {}
        self._request_times: List[float] = []
        self._start_time = time.time()

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        async with self._lock:
            # Start background tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            # Create initial connections
            await self._create_initial_connections()
            
            logger.info(f"Connection pool initialized with {self.config.min_connections} connections")

    async def get_connection(self, endpoint: str, session_id: Optional[str] = None) -> WebSocketConnection:
        """Get a connection from the pool with optimization strategies."""
        start_time = time.time()
        
        async with self._lock:
            self._pool_metrics.total_requests += 1
            
            # Try to reuse existing connection for sticky sessions
            if session_id and session_id in self._session_sticky_map:
                connection = self._session_sticky_map[session_id]
                if connection.is_connected():
                    self._update_connection_usage(connection)
                    self._pool_metrics.successful_requests += 1
                    self._record_response_time(time.time() - start_time)
                    return connection
                else:
                    # Remove stale sticky connection
                    del self._session_sticky_map[session_id]

            # Get connection based on strategy
            connection = await self._get_connection_by_strategy(endpoint)
            
            if connection:
                self._active_connections.add(connection)
                self._update_connection_usage(connection)
                
                # Set up sticky session if requested
                if session_id:
                    self._session_sticky_map[session_id] = connection
                
                self._pool_metrics.successful_requests += 1
                self._record_response_time(time.time() - start_time)
                return connection
            
            # Create new connection if pool is not full
            if len(self._active_connections) < self.config.max_connections:
                connection = await self._create_new_connection(endpoint)
                if connection:
                    self._active_connections.add(connection)
                    self._update_connection_usage(connection)
                    
                    if session_id:
                        self._session_sticky_map[session_id] = connection
                    
                    self._pool_metrics.successful_requests += 1
                    self._record_response_time(time.time() - start_time)
                    return connection
            
            # Pool is full, wait for available connection
            self._pool_metrics.failed_requests += 1
            raise ConnectionFailedError("Connection pool exhausted", endpoint)

    async def return_connection(self, connection: WebSocketConnection) -> None:
        """Return a connection to the pool for reuse."""
        async with self._lock:
            if connection in self._active_connections:
                self._active_connections.remove(connection)
                
                # Add to idle pool if connection is healthy
                if connection.is_connected():
                    self._idle_connections.append(connection)
                    self._last_used_times[connection] = datetime.utcnow()
                else:
                    # Remove failed connection
                    await self._remove_connection(connection)

    async def _get_connection_by_strategy(self, endpoint: str) -> Optional[WebSocketConnection]:
        """Get connection based on configured strategy."""
        available_connections = [
            conn for conn in self._connections[endpoint]
            if conn.is_connected() and conn not in self._active_connections
        ]
        
        if not available_connections:
            return None
        
        if self.config.pool_strategy == PoolStrategy.ROUND_ROBIN:
            return available_connections[0]  # Simple round-robin
        
        elif self.config.pool_strategy == PoolStrategy.LEAST_CONNECTIONS:
            return min(available_connections, key=lambda c: self._get_connection_load(c))
        
        elif self.config.pool_strategy == PoolStrategy.LEAST_LATENCY:
            return min(available_connections, key=lambda c: self._get_connection_latency(c))
        
        elif self.config.pool_strategy == PoolStrategy.STICKY_SESSION:
            # For sticky sessions, prefer connections with fewer active sessions
            return min(available_connections, key=lambda c: len([
                sid for sid, conn in self._session_sticky_map.items() 
                if conn == c
            ]))
        
        return available_connections[0]

    def _get_connection_load(self, connection: WebSocketConnection) -> int:
        """Get the current load of a connection."""
        return len([
            conn for conn in self._active_connections 
            if conn.endpoint == connection.endpoint
        ])

    def _get_connection_latency(self, connection: WebSocketConnection) -> float:
        """Get the average latency of a connection."""
        metrics = self._connection_metrics.get(connection, {})
        return metrics.get('avg_latency', 0.0)

    async def _create_new_connection(self, endpoint: str) -> Optional[WebSocketConnection]:
        """Create a new WebSocket connection."""
        try:
            connection = WebSocketConnection(endpoint, self.config.connection_timeout)
            await connection.connect()
            
            self._connections[endpoint].append(connection)
            self._connection_creation_times[connection] = datetime.utcnow()
            self._connection_metrics[connection] = {
                'requests': 0,
                'avg_latency': 0.0,
                'last_error': None,
                'created_at': datetime.utcnow()
            }
            
            self._pool_metrics.total_connections += 1
            logger.info(f"Created new connection to {endpoint}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create connection to {endpoint}: {e}")
            self._pool_metrics.failed_connections += 1
            return None

    async def _create_initial_connections(self) -> None:
        """Create initial connections for the pool."""
        # This would typically create connections to known endpoints
        # For now, we'll create them on-demand
        pass

    def _update_connection_usage(self, connection: WebSocketConnection) -> None:
        """Update connection usage metrics."""
        if connection in self._connection_metrics:
            self._connection_metrics[connection]['requests'] += 1
            self._last_used_times[connection] = datetime.utcnow()

    def _record_response_time(self, response_time: float) -> None:
        """Record response time for metrics."""
        self._request_times.append(response_time)
        # Keep only last 1000 response times
        if len(self._request_times) > 1000:
            self._request_times = self._request_times[-1000:]
        
        # Update average response time
        self._pool_metrics.avg_response_time = sum(self._request_times) / len(self._request_times)

    async def _remove_connection(self, connection: WebSocketConnection) -> None:
        """Remove a connection from the pool."""
        try:
            await connection.disconnect()
        except Exception:
            pass
        
        # Remove from all tracking structures
        if connection in self._connections[connection.endpoint]:
            self._connections[connection.endpoint].remove(connection)
        
        self._active_connections.discard(connection)
        
        # Remove from idle pool
        try:
            self._idle_connections.remove(connection)
        except ValueError:
            pass
        
        # Clean up tracking data
        self._connection_metrics.pop(connection, None)
        self._connection_creation_times.pop(connection, None)
        self._last_used_times.pop(connection, None)
        
        # Remove from sticky session map
        stale_sessions = [
            sid for sid, conn in self._session_sticky_map.items()
            if conn == connection
        ]
        for sid in stale_sessions:
            del self._session_sticky_map[sid]
        
        self._pool_metrics.total_connections -= 1

    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except Exception as e:
                logger.error(f"Health check loop error: {e}")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for idle connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                await self._cleanup_idle_connections()
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all connections."""
        async with self._lock:
            unhealthy_connections = []
            
            for endpoint, connections in self._connections.items():
                for connection in connections:
                    if not connection.is_connected():
                        unhealthy_connections.append(connection)
            
            # Remove unhealthy connections
            for connection in unhealthy_connections:
                await self._remove_connection(connection)
            
            # Update pool metrics
            self._update_pool_metrics()

    async def _cleanup_idle_connections(self) -> None:
        """Clean up idle connections that exceed max idle time."""
        async with self._lock:
            current_time = datetime.utcnow()
            idle_threshold = timedelta(seconds=self.config.max_idle_time)
            
            connections_to_remove = []
            for connection in list(self._idle_connections):
                last_used = self._last_used_times.get(connection)
                if last_used and (current_time - last_used) > idle_threshold:
                    connections_to_remove.append(connection)
            
            # Ensure we maintain minimum connections
            total_connections = sum(len(conns) for conns in self._connections.values())
            if total_connections - len(connections_to_remove) < self.config.min_connections:
                connections_to_remove = connections_to_remove[:max(0, total_connections - self.config.min_connections)]
            
            for connection in connections_to_remove:
                await self._remove_connection(connection)
                try:
                    self._idle_connections.remove(connection)
                except ValueError:
                    pass

    def _update_pool_metrics(self) -> None:
        """Update pool performance metrics."""
        # Count connections by status
        total_connections = sum(len(conns) for conns in self._connections.values())
        active_connections = len(self._active_connections)
        idle_connections = len(self._idle_connections)
        
        self._pool_metrics.total_connections = total_connections
        self._pool_metrics.active_connections = active_connections
        self._pool_metrics.idle_connections = idle_connections
        self._pool_metrics.last_updated = datetime.utcnow()
        
        # Update system metrics
        try:
            process = psutil.Process()
            self._pool_metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self._pool_metrics.cpu_usage_percent = process.cpu_percent()
        except Exception:
            pass

    async def close(self) -> None:
        """Close the connection pool and all connections."""
        async with self._lock:
            # Cancel background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            # Close all connections
            all_connections = []
            for connections in self._connections.values():
                all_connections.extend(connections)
            
            for connection in all_connections:
                try:
                    await connection.disconnect()
                except Exception:
                    pass
            
            # Clear all data structures
            self._connections.clear()
            self._active_connections.clear()
            self._idle_connections.clear()
            self._connection_metrics.clear()
            self._session_sticky_map.clear()
            self._connection_creation_times.clear()
            self._last_used_times.clear()
            
            logger.info("Connection pool closed")

    def get_pool_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pool metrics."""
        self._update_pool_metrics()
        return self._pool_metrics.to_dict()

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection statistics."""
        stats = {
            'endpoints': {},
            'total_connections': 0,
            'active_connections': len(self._active_connections),
            'idle_connections': len(self._idle_connections),
        }
        
        for endpoint, connections in self._connections.items():
            endpoint_stats = {
                'total': len(connections),
                'active': len([c for c in connections if c in self._active_connections]),
                'idle': len([c for c in connections if c in self._idle_connections]),
                'failed': len([c for c in connections if not c.is_connected()]),
            }
            stats['endpoints'][endpoint] = endpoint_stats
            stats['total_connections'] += len(connections)
        
        return stats