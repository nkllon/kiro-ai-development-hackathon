"""WebSocket Connection Manager with retry logic and connection pooling."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

import websockets
from websockets.exceptions import ConnectionClosed, InvalidStatusCode, WebSocketException

from .connection import WebSocketConnection, ConnectionState, ConnectionStatus
from .retry_strategy import ExponentialBackoffRetry, retry_with_strategy
from .health_validator import WebSocketHealthValidator, HealthCheckResult, HealthStatus
from .connection_pool import ConnectionPool, ConnectionPoolConfig, PoolStrategy
from .message_optimizer import MessageOptimizer, MessageOptimizerConfig, MessagePriority
from .compression_handler import CompressionHandler, CompressionConfig, CompressionAlgorithm, SerializationFormat
from .exceptions import (
    WebSocketConnectionError,
    WebSocketTimeoutError,
    WebSocketAuthenticationError,
    WebSocketRateLimitError,
    ConnectionFailedError,
    ConnectionTimeoutError,
    AuthenticationError,
    RateLimitError,
    ProtocolError,
    RetryExhaustedError,
    MaxConnectionsError,
)

logger = logging.getLogger(__name__)


@dataclass
class WebSocketManagerConfig:
    """Configuration for WebSocket Manager."""
    base_url: str = "ws://localhost:8000"
    max_connections_per_endpoint: int = 5
    connection_timeout: float = 10.0
    retry_base_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_multiplier: float = 2.0
    retry_max_attempts: int = 10
    health_check_interval: float = 30.0
    enable_heartbeat: bool = True
    heartbeat_interval: float = 20.0
    heartbeat_timeout: float = 10.0
    enable_compression: bool = True
    enable_message_optimization: bool = True
    enable_connection_pooling: bool = True
    pool_strategy: PoolStrategy = PoolStrategy.LEAST_CONNECTIONS
    max_pool_connections: int = 50
    min_pool_connections: int = 5
    batch_timeout: float = 0.1
    max_batch_size: int = 8192
    compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.LZ4
    serialization_format: SerializationFormat = SerializationFormat.MSGPACK
    default_headers: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'base_url': self.base_url,
            'max_connections_per_endpoint': self.max_connections_per_endpoint,
            'connection_timeout': self.connection_timeout,
            'retry_base_delay': self.retry_base_delay,
            'retry_max_delay': self.retry_max_delay,
            'retry_multiplier': self.retry_multiplier,
            'retry_max_attempts': self.retry_max_attempts,
            'health_check_interval': self.health_check_interval,
            'enable_heartbeat': self.enable_heartbeat,
            'heartbeat_interval': self.heartbeat_interval,
            'heartbeat_timeout': self.heartbeat_timeout,
            'enable_compression': self.enable_compression,
            'enable_message_optimization': self.enable_message_optimization,
            'enable_connection_pooling': self.enable_connection_pooling,
            'pool_strategy': self.pool_strategy.value,
            'max_pool_connections': self.max_pool_connections,
            'min_pool_connections': self.min_pool_connections,
            'batch_timeout': self.batch_timeout,
            'max_batch_size': self.max_batch_size,
            'compression_algorithm': self.compression_algorithm.value,
            'serialization_format': self.serialization_format.value,
            'default_headers': self.default_headers,
        }


class WebSocketManager:
    """Manages WebSocket connections with retry logic, connection pooling, and health monitoring."""
    
    def __init__(self, config: Optional[WebSocketManagerConfig] = None):
        self.config = config or WebSocketManagerConfig()
        
        # Core endpoints to manage
        self.endpoints = [
            '/ws/emoji-rain',
            '/ws/observatory', 
            '/ws/anomalies',
            '/ws/doctor-status'
        ]
        
        # Connection management
        self.connections: Dict[str, List[WebSocketConnection]] = {}
        self.retry_strategies: Dict[str, ExponentialBackoffRetry] = {}
        self.connection_locks: Dict[str, asyncio.Lock] = {}
        
        # Health monitoring
        self.health_validator = WebSocketHealthValidator(
            timeout=self.config.connection_timeout,
            max_retries=self.config.retry_max_attempts
        )
        
        # Optimization components
        self.connection_pool: Optional[ConnectionPool] = None
        self.message_optimizer: Optional[MessageOptimizer] = None
        self.compression_handler: Optional[CompressionHandler] = None
        
        # Background tasks
        self._background_tasks = set()
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Event callbacks
        self._connection_callbacks: Dict[str, List[Callable]] = {
            'connected': [],
            'disconnected': [],
            'failed': [],
            'retry': [],
            'health_check': []
        }
        
        # Initialize retry strategies for each endpoint
        for endpoint in self.endpoints:
            self.retry_strategies[endpoint] = ExponentialBackoffRetry(
                base_delay=self.config.retry_base_delay,
                max_delay=self.config.retry_max_delay,
                multiplier=self.config.retry_multiplier,
                max_attempts=self.config.retry_max_attempts
            )
            self.connection_locks[endpoint] = asyncio.Lock()
            self.connections[endpoint] = []
        
        self._log_action("manager_initialized", {
            "endpoints": self.endpoints,
            "config": self.config.to_dict()
        })
    
    async def start(self) -> None:
        """Start the WebSocket manager and background monitoring."""
        if self._is_running:
            return
        
        self._is_running = True
        
        # Initialize optimization components
        await self._initialize_optimization_components()
        
        # Start health monitoring task
        if self.config.health_check_interval > 0:
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            self._background_tasks.add(self._health_monitor_task)
            self._health_monitor_task.add_done_callback(self._background_tasks.discard)
        
        self._log_action("manager_started", {
            "health_check_interval": self.config.health_check_interval,
            "endpoint_count": len(self.endpoints),
            "optimization_enabled": {
                "connection_pooling": self.config.enable_connection_pooling,
                "message_optimization": self.config.enable_message_optimization,
                "compression": self.config.enable_compression
            }
        })
    
    async def stop(self) -> None:
        """Stop the WebSocket manager and close all connections."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # Cancel health monitoring
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
        
        # Close optimization components
        await self._cleanup_optimization_components()
        
        # Close all connections
        for endpoint in self.endpoints:
            await self.disconnect_all_websockets(endpoint)
        
        # Cancel all background tasks
        for task in self._background_tasks.copy():
            task.cancel()
        
        self._log_action("manager_stopped", {
            "total_connections_closed": sum(len(conns) for conns in self.connections.values())
        })
    
    async def connect_websocket(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> WebSocketConnection:
        """Connect to a WebSocket endpoint with retry logic."""
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        async with self.connection_locks[endpoint]:
            # Check if we've reached max connections
            if len(self.connections[endpoint]) >= self.config.max_connections_per_endpoint:
                raise MaxConnectionsError(
                    f"Maximum connections ({self.config.max_connections_per_endpoint}) reached for {endpoint}",
                    endpoint
                )
            
            # Prepare connection headers
            connection_headers = self.config.default_headers.copy() if self.config.default_headers else {}
            if headers:
                connection_headers.update(headers)
            
            # Build full URL
            full_url = self.config.base_url.rstrip('/') + endpoint
            
            self._log_action("connection_attempt_started", {
                "endpoint": endpoint,
                "full_url": full_url,
                "current_connections": len(self.connections[endpoint])
            })
            
            # Create connection with retry logic
            retry_strategy = self.retry_strategies[endpoint]
            
            try:
                connection = await retry_with_strategy(
                    retry_strategy,
                    self._create_connection,
                    endpoint,
                    full_url,
                    connection_headers
                )
                
                # Add to connection pool
                self.connections[endpoint].append(connection)
                
                # Notify callbacks
                await self._notify_callbacks('connected', endpoint, connection)
                
                self._log_action("connection_established", {
                    "endpoint": endpoint,
                    "connection_id": id(connection),
                    "total_connections": len(self.connections[endpoint])
                })
                
                return connection
                
            except RetryExhaustedError as e:
                self._log_action("connection_failed_exhausted", {
                    "endpoint": endpoint,
                    "attempts": e.attempts,
                    "error": str(e)
                })
                await self._notify_callbacks('failed', endpoint, None, str(e))
                raise WebSocketConnectionError(f"Failed to connect to {endpoint} after {e.attempts} attempts", endpoint)
            
            except Exception as e:
                self._log_action("connection_failed_unexpected", {
                    "endpoint": endpoint,
                    "error": str(e)
                })
                await self._notify_callbacks('failed', endpoint, None, str(e))
                raise
    
    async def disconnect_websocket(self, endpoint: str, connection: Optional[WebSocketConnection] = None) -> None:
        """Disconnect a specific WebSocket connection or all connections for an endpoint."""
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        async with self.connection_locks[endpoint]:
            if connection:
                # Disconnect specific connection
                if connection in self.connections[endpoint]:
                    await connection.disconnect()
                    self.connections[endpoint].remove(connection)
                    
                    self._log_action("connection_disconnected", {
                        "endpoint": endpoint,
                        "connection_id": id(connection),
                        "remaining_connections": len(self.connections[endpoint])
                    })
                    
                    await self._notify_callbacks('disconnected', endpoint, connection)
            else:
                # Disconnect all connections for endpoint
                await self.disconnect_all_websockets(endpoint)
    
    async def disconnect_all_websockets(self, endpoint: str) -> None:
        """Disconnect all WebSocket connections for an endpoint."""
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        async with self.connection_locks[endpoint]:
            connections_to_close = self.connections[endpoint].copy()
            
            for connection in connections_to_close:
                await connection.disconnect()
                await self._notify_callbacks('disconnected', endpoint, connection)
            
            self.connections[endpoint].clear()
            
            self._log_action("all_connections_disconnected", {
                "endpoint": endpoint,
                "closed_connections": len(connections_to_close)
            })
    
    async def send_message(self, endpoint: str, message: Dict[str, Any], 
                          connection: Optional[WebSocketConnection] = None,
                          priority: MessagePriority = MessagePriority.NORMAL,
                          use_optimization: bool = True) -> None:
        """Send a message through a WebSocket connection with optimization."""
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        # Use message optimization if enabled
        if use_optimization and self.message_optimizer and self.config.enable_message_optimization:
            await self.message_optimizer.add_message(message, priority, f"{endpoint}_batch")
            return
        
        # Direct message sending (fallback or when optimization disabled)
        async with self.connection_locks[endpoint]:
            if connection:
                # Send through specific connection
                if connection not in self.connections[endpoint]:
                    raise ValueError("Connection not found in pool")
                
                # Apply compression if enabled
                if self.config.enable_compression and self.compression_handler:
                    compressed_result = await self.compression_handler.compress_message(
                        message, 
                        self.config.compression_algorithm,
                        self.config.serialization_format
                    )
                    await connection.send_message(compressed_result.data)
                else:
                    await connection.send_message(message)
            else:
                # Send through first available connection
                if not self.connections[endpoint]:
                    raise WebSocketConnectionError(f"No connections available for {endpoint}", endpoint)
                
                # Try to send through first healthy connection
                sent = False
                for conn in self.connections[endpoint]:
                    if conn.is_connected():
                        try:
                            # Apply compression if enabled
                            if self.config.enable_compression and self.compression_handler:
                                compressed_result = await self.compression_handler.compress_message(
                                    message, 
                                    self.config.compression_algorithm,
                                    self.config.serialization_format
                                )
                                await conn.send_message(compressed_result.data)
                            else:
                                await conn.send_message(message)
                            sent = True
                            break
                        except Exception as e:
                            self._log_action("message_send_failed", {
                                "endpoint": endpoint,
                                "connection_id": id(conn),
                                "error": str(e)
                            })
                            continue
                
                if not sent:
                    raise WebSocketConnectionError(f"Failed to send message to {endpoint}", endpoint)
    
    async def handle_connection_failure(self, endpoint: str, connection: WebSocketConnection, 
                                       error: Exception) -> None:
        """Handle connection failure with retry logic."""
        if endpoint not in self.endpoints:
            return
        
        self._log_action("connection_failure_handled", {
            "endpoint": endpoint,
            "connection_id": id(connection),
            "error_type": type(error).__name__,
            "error_message": str(error)
        })
        
        # Remove failed connection from pool
        async with self.connection_locks[endpoint]:
            if connection in self.connections[endpoint]:
                self.connections[endpoint].remove(connection)
        
        # Notify callbacks
        await self._notify_callbacks('failed', endpoint, connection, str(error))
        
        # Attempt reconnection if retry strategy allows
        retry_strategy = self.retry_strategies[endpoint]
        if retry_strategy.should_retry(error):
            retry_strategy.increment_attempt()
            delay = retry_strategy.calculate_delay()
            
            self._log_action("retry_scheduled", {
                "endpoint": endpoint,
                "attempt": retry_strategy.get_attempt_count(),
                "delay_seconds": delay
            })
            
            await self._notify_callbacks('retry', endpoint, connection, str(error))
            
            # Schedule reconnection
            if delay > 0:
                await asyncio.sleep(delay)
            
            try:
                await self.connect_websocket(endpoint)
            except Exception as retry_error:
                self._log_action("retry_failed", {
                    "endpoint": endpoint,
                    "retry_error": str(retry_error)
                })
        else:
            retry_strategy.reset()
    
    def get_connection_status(self, endpoint: str) -> Dict[str, Any]:
        """Get connection status for an endpoint."""
        if endpoint not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        connections = self.connections[endpoint]
        connected_count = sum(1 for conn in connections if conn.is_connected())
        
        return {
            'endpoint': endpoint,
            'total_connections': len(connections),
            'connected_connections': connected_count,
            'disconnected_connections': len(connections) - connected_count,
            'max_connections': self.config.max_connections_per_endpoint,
            'retry_attempts': self.retry_strategies[endpoint].get_attempt_count(),
            'connections': [
                {
                    'id': id(conn),
                    'status': conn.state.status.value,
                    'connected': conn.is_connected(),
                    'failure_count': conn.state.failure_count,
                    'last_error': conn.state.last_error,
                    'message_count': conn.state.message_count,
                    'uptime_seconds': (
                        (datetime.utcnow() - conn.state.connection_time).total_seconds()
                        if conn.state.connection_time else None
                    )
                }
                for conn in connections
            ]
        }
    
    def get_all_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get connection status for all endpoints."""
        return {
            endpoint: self.get_connection_status(endpoint)
            for endpoint in self.endpoints
        }
    
    async def get_health_status(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get health status for endpoint(s)."""
        if endpoint:
            if endpoint not in self.endpoints:
                raise ValueError(f"Unknown endpoint: {endpoint}")
            
            result = await self.health_validator.validate_endpoint_health(endpoint)
            return result.to_dict()
        else:
            results = await self.health_validator.validate_all_endpoints()
            return {
                ep: result.to_dict() 
                for ep, result in results.items()
            }
    
    def add_connection_callback(self, event_type: str, callback: Callable) -> None:
        """Add callback for connection events."""
        if event_type in self._connection_callbacks:
            self._connection_callbacks[event_type].append(callback)
    
    def remove_connection_callback(self, event_type: str, callback: Callable) -> None:
        """Remove connection callback."""
        if event_type in self._connection_callbacks:
            self._connection_callbacks[event_type].remove(callback)
    
    async def _create_connection(self, full_url: str, headers: Dict[str, str]) -> WebSocketConnection:
        """Create a new WebSocket connection."""
        from .heartbeat import HeartbeatConfig
        
        heartbeat_config = None
        if self.config.enable_heartbeat:
            heartbeat_config = HeartbeatConfig(
                interval=self.config.heartbeat_interval,
                timeout=self.config.heartbeat_timeout
            )
        
        connection = WebSocketConnection(
            endpoint=full_url,
            connection_timeout=self.config.connection_timeout,
            heartbeat_config=heartbeat_config
        )
        
        await connection.connect(headers)
        return connection
    
    async def _health_monitor_loop(self) -> None:
        """Background health monitoring loop."""
        while self._is_running:
            try:
                self._log_action("health_monitor_cycle_started", {
                    "endpoint_count": len(self.endpoints)
                })
                
                # Check health of all endpoints
                health_results = await self.health_validator.validate_all_endpoints()
                
                # Handle unhealthy endpoints
                for endpoint, result in health_results.items():
                    if result.status == HealthStatus.UNHEALTHY:
                        self._log_action("unhealthy_endpoint_detected", {
                            "endpoint": endpoint,
                            "status": result.status.value,
                            "error": result.error_message
                        })
                        
                        # Attempt to reconnect unhealthy endpoints
                        await self._handle_unhealthy_endpoint(endpoint, result)
                    
                    await self._notify_callbacks('health_check', endpoint, None, result.to_dict())
                
                self._log_action("health_monitor_cycle_completed", {
                    "healthy_endpoints": sum(1 for r in health_results.values() if r.status == HealthStatus.HEALTHY),
                    "unhealthy_endpoints": sum(1 for r in health_results.values() if r.status == HealthStatus.UNHEALTHY)
                })
                
            except Exception as e:
                self._log_action("health_monitor_error", {
                    "error": str(e)
                })
            
            # Wait for next health check
            await asyncio.sleep(self.config.health_check_interval)
    
    async def _handle_unhealthy_endpoint(self, endpoint: str, health_result: HealthCheckResult) -> None:
        """Handle unhealthy endpoint by attempting reconnection."""
        async with self.connection_locks[endpoint]:
            # Close existing connections
            for connection in self.connections[endpoint].copy():
                await connection.disconnect()
            
            self.connections[endpoint].clear()
            
            # Reset retry strategy
            self.retry_strategies[endpoint].reset()
            
            # Attempt to reconnect
            try:
                await self.connect_websocket(endpoint)
                self._log_action("unhealthy_endpoint_reconnected", {
                    "endpoint": endpoint
                })
            except Exception as e:
                self._log_action("unhealthy_endpoint_reconnection_failed", {
                    "endpoint": endpoint,
                    "error": str(e)
                })
    
    async def _notify_callbacks(self, event_type: str, endpoint: str, 
                               connection: Optional[WebSocketConnection], 
                               data: Optional[Any] = None) -> None:
        """Notify registered callbacks of events."""
        callbacks = self._connection_callbacks.get(event_type, [])
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(endpoint, connection, data)
                else:
                    callback(endpoint, connection, data)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")
    
    async def _initialize_optimization_components(self) -> None:
        """Initialize optimization components based on configuration."""
        try:
            # Initialize connection pool
            if self.config.enable_connection_pooling:
                pool_config = ConnectionPoolConfig(
                    max_connections=self.config.max_pool_connections,
                    min_connections=self.config.min_pool_connections,
                    connection_timeout=self.config.connection_timeout,
                    pool_strategy=self.config.pool_strategy,
                    enable_compression=self.config.enable_compression,
                    health_check_interval=self.config.health_check_interval
                )
                self.connection_pool = ConnectionPool(pool_config)
                await self.connection_pool.initialize()
                
                self._log_action("connection_pool_initialized", {
                    "max_connections": self.config.max_pool_connections,
                    "min_connections": self.config.min_pool_connections,
                    "strategy": self.config.pool_strategy.value
                })
            
            # Initialize message optimizer
            if self.config.enable_message_optimization:
                optimizer_config = MessageOptimizerConfig(
                    batch_timeout=self.config.batch_timeout,
                    max_batch_size=self.config.max_batch_size,
                    enable_compression=self.config.enable_compression,
                    enable_deduplication=True,
                    enable_prioritization=True,
                    batch_strategy=BatchStrategy.HYBRID
                )
                self.message_optimizer = MessageOptimizer(optimizer_config)
                await self.message_optimizer.initialize()
                
                self._log_action("message_optimizer_initialized", {
                    "batch_timeout": self.config.batch_timeout,
                    "max_batch_size": self.config.max_batch_size,
                    "compression_enabled": self.config.enable_compression
                })
            
            # Initialize compression handler
            if self.config.enable_compression:
                compression_config = CompressionConfig(
                    default_algorithm=self.config.compression_algorithm,
                    default_format=self.config.serialization_format,
                    compression_threshold=1024,
                    enable_adaptive_compression=True,
                    enable_parallel_compression=True,
                    cache_compressed_data=True
                )
                self.compression_handler = CompressionHandler(compression_config)
                
                self._log_action("compression_handler_initialized", {
                    "algorithm": self.config.compression_algorithm.value,
                    "format": self.config.serialization_format.value
                })
                
        except Exception as e:
            self._log_action("optimization_initialization_failed", {
                "error": str(e)
            })
            logger.error(f"Failed to initialize optimization components: {e}")

    async def _cleanup_optimization_components(self) -> None:
        """Clean up optimization components."""
        try:
            if self.connection_pool:
                await self.connection_pool.close()
                self.connection_pool = None
                
            if self.message_optimizer:
                await self.message_optimizer.close()
                self.message_optimizer = None
                
            if self.compression_handler:
                await self.compression_handler.cleanup_cache()
                self.compression_handler = None
                
            self._log_action("optimization_components_cleaned_up", {})
            
        except Exception as e:
            self._log_action("optimization_cleanup_failed", {
                "error": str(e)
            })
            logger.error(f"Failed to cleanup optimization components: {e}")

    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get metrics from all optimization components."""
        metrics = {
            'connection_pool': None,
            'message_optimizer': None,
            'compression_handler': None
        }
        
        try:
            if self.connection_pool:
                metrics['connection_pool'] = self.connection_pool.get_pool_metrics()
                
            if self.message_optimizer:
                metrics['message_optimizer'] = self.message_optimizer.get_metrics()
                
            if self.compression_handler:
                metrics['compression_handler'] = self.compression_handler.get_metrics()
                
        except Exception as e:
            logger.error(f"Failed to get optimization metrics: {e}")
            
        return metrics

    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log WebSocket manager action in JSON format."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task': '8.1',
            'action': f'websocket_manager_{action}',
            'status': 'in_progress',
            'details': details
        }
        print(json.dumps(log_data))


# Convenience functions for common operations
async def create_websocket_manager(base_url: str = "ws://localhost:8000", 
                                 **config_kwargs) -> WebSocketManager:
    """Create and start a WebSocket manager with default configuration."""
    config = WebSocketManagerConfig(base_url=base_url, **config_kwargs)
    manager = WebSocketManager(config)
    await manager.start()
    return manager


async def connect_to_endpoints(manager: WebSocketManager, 
                              endpoints: Optional[List[str]] = None) -> Dict[str, List[WebSocketConnection]]:
    """Connect to multiple endpoints and return connections."""
    if endpoints is None:
        endpoints = manager.endpoints
    
    connections = {}
    for endpoint in endpoints:
        try:
            connection = await manager.connect_websocket(endpoint)
            connections[endpoint] = [connection]
        except Exception as e:
            logger.error(f"Failed to connect to {endpoint}: {e}")
            connections[endpoint] = []
    
    return connections