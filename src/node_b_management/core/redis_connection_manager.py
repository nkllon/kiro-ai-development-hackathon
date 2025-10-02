"""
Redis Connection Manager for Node B Management

Provides secure Redis connection management with proper credential handling,
connection pooling, and error recovery for Node B coordination.
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


@dataclass
class RedisConfig:
    """Redis configuration with secure credential handling"""
    host: str
    port: int
    password: str
    db: int = 0
    ssl: bool = False
    ssl_cert_reqs: str = "required"
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    retry_on_timeout: bool = True
    max_connections: int = 10


class RedisConnectionError(Exception):
    """Redis connection specific errors"""
    pass


class RedisConnectionManager:
    """
    Secure Redis connection manager for Node B coordination
    
    Handles Redis connections with proper credential management,
    connection pooling, and automatic retry logic.
    
    Requirements: 4.1, 4.2, 6.6
    """

    def __init__(self, config: Optional[RedisConfig] = None):
        """
        Initialize Redis connection manager
        
        Args:
            config: Optional RedisConfig, will load from environment if not provided
        """
        self._logger = logging.getLogger("node_b.redis_manager")
        
        # Load configuration
        self._config = config or self._load_config_from_env()
        
        # Connection pool and state
        self._connection_pool = None
        self._redis_client = None
        self._connected = False
        self._connection_attempts = 0
        self._max_connection_attempts = 5
        
        # Validate Redis availability
        if not REDIS_AVAILABLE:
            raise RedisConnectionError(
                "Redis client not available. Install with: pip install redis[hiredis]"
            )
        
        self._logger.info(f"Redis connection manager initialized for {self._config.host}:{self._config.port}")

    def _load_config_from_env(self) -> RedisConfig:
        """
        Load Redis configuration from environment variables
        
        Returns:
            RedisConfig: Configuration loaded from environment
            
        Requirements: 4.1, 4.2
        """
        # Load credentials from environment - NEVER hardcode passwords
        redis_password = os.getenv('REDIS_PASSWORD') or os.getenv('BEAST_MODE_REDIS_PASSWORD')
        
        if not redis_password:
            raise ValueError(
                "Redis password must be set in environment variables. "
                "Set REDIS_PASSWORD or BEAST_MODE_REDIS_PASSWORD"
            )
        
        # Load other configuration with defaults
        config = RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            password=redis_password,
            db=int(os.getenv('REDIS_DB', '0')),
            ssl=os.getenv('REDIS_SSL', 'false').lower() == 'true',
            ssl_cert_reqs=os.getenv('REDIS_SSL_CERT_REQS', 'required'),
            socket_timeout=float(os.getenv('REDIS_SOCKET_TIMEOUT', '5.0')),
            socket_connect_timeout=float(os.getenv('REDIS_CONNECT_TIMEOUT', '5.0')),
            retry_on_timeout=os.getenv('REDIS_RETRY_ON_TIMEOUT', 'true').lower() == 'true',
            max_connections=int(os.getenv('REDIS_MAX_CONNECTIONS', '10'))
        )
        
        self._logger.info(f"Redis configuration loaded from environment: {config.host}:{config.port}")
        return config

    async def get_connection(self) -> redis.Redis:
        """
        Get Redis connection with automatic connection management
        
        Returns:
            redis.Redis: Configured Redis connection
            
        Raises:
            RedisConnectionError: If connection cannot be established
            
        Requirements: 4.1, 4.2, 6.6
        """
        if not self._connected or self._redis_client is None:
            await self._establish_connection()
        
        return self._redis_client

    async def _establish_connection(self):
        """
        Establish Redis connection with retry logic
        
        Requirements: 4.1, 4.2
        """
        self._connection_attempts += 1
        
        if self._connection_attempts > self._max_connection_attempts:
            raise RedisConnectionError(
                f"Failed to connect to Redis after {self._max_connection_attempts} attempts"
            )
        
        try:
            # Create connection pool
            if self._connection_pool is None:
                self._connection_pool = redis.ConnectionPool(
                    host=self._config.host,
                    port=self._config.port,
                    password=self._config.password,
                    db=self._config.db,
                    ssl=self._config.ssl,
                    ssl_cert_reqs=self._config.ssl_cert_reqs,
                    socket_timeout=self._config.socket_timeout,
                    socket_connect_timeout=self._config.socket_connect_timeout,
                    retry_on_timeout=self._config.retry_on_timeout,
                    max_connections=self._config.max_connections,
                    decode_responses=True
                )
            
            # Create Redis client
            self._redis_client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._redis_client.ping()
            
            self._connected = True
            self._connection_attempts = 0
            self._logger.info("Redis connection established successfully")
            
        except Exception as e:
            self._connected = False
            self._logger.error(f"Redis connection attempt {self._connection_attempts} failed: {e}")
            
            if self._connection_attempts < self._max_connection_attempts:
                # Exponential backoff
                delay = min(2 ** self._connection_attempts, 30)
                self._logger.info(f"Retrying Redis connection in {delay} seconds...")
                await asyncio.sleep(delay)
                await self._establish_connection()
            else:
                raise RedisConnectionError(f"Failed to establish Redis connection: {e}")

    async def test_connection(self) -> bool:
        """
        Test Redis connection health
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            if self._redis_client is None:
                return False
            
            await self._redis_client.ping()
            return True
            
        except Exception as e:
            self._logger.warning(f"Redis connection test failed: {e}")
            self._connected = False
            return False

    async def close_connection(self):
        """Close Redis connection and cleanup resources"""
        try:
            if self._redis_client:
                await self._redis_client.close()
                self._redis_client = None
            
            if self._connection_pool:
                await self._connection_pool.disconnect()
                self._connection_pool = None
            
            self._connected = False
            self._logger.info("Redis connection closed")
            
        except Exception as e:
            self._logger.error(f"Error closing Redis connection: {e}")

    @asynccontextmanager
    async def get_connection_context(self):
        """
        Context manager for Redis connections with automatic cleanup
        
        Usage:
            async with redis_manager.get_connection_context() as redis_conn:
                await redis_conn.set("key", "value")
        """
        connection = None
        try:
            connection = await self.get_connection()
            yield connection
        except Exception as e:
            self._logger.error(f"Redis operation failed: {e}")
            raise
        finally:
            # Connection is returned to pool automatically
            pass

    async def publish_message(self, channel: str, message: str) -> bool:
        """
        Publish message to Redis channel
        
        Args:
            channel: Redis channel name
            message: Message to publish
            
        Returns:
            bool: True if message published successfully, False otherwise
        """
        try:
            async with self.get_connection_context() as redis_conn:
                result = await redis_conn.publish(channel, message)
                self._logger.debug(f"Published message to channel {channel}: {result} subscribers")
                return True
                
        except Exception as e:
            self._logger.error(f"Failed to publish message to channel {channel}: {e}")
            return False

    async def subscribe_to_channel(self, channel: str):
        """
        Subscribe to Redis channel
        
        Args:
            channel: Redis channel name
            
        Returns:
            Redis PubSub object for message handling
        """
        try:
            connection = await self.get_connection()
            pubsub = connection.pubsub()
            await pubsub.subscribe(channel)
            self._logger.info(f"Subscribed to Redis channel: {channel}")
            return pubsub
            
        except Exception as e:
            self._logger.error(f"Failed to subscribe to channel {channel}: {e}")
            raise RedisConnectionError(f"Subscription failed: {e}")

    async def set_with_expiry(self, key: str, value: str, expiry_seconds: int = 3600) -> bool:
        """
        Set key-value pair with expiry
        
        Args:
            key: Redis key
            value: Value to store
            expiry_seconds: Expiry time in seconds
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        try:
            async with self.get_connection_context() as redis_conn:
                await redis_conn.setex(key, expiry_seconds, value)
                return True
                
        except Exception as e:
            self._logger.error(f"Failed to set key {key} with expiry: {e}")
            return False

    async def get_value(self, key: str) -> Optional[str]:
        """
        Get value by key
        
        Args:
            key: Redis key
            
        Returns:
            Optional[str]: Value if found, None otherwise
        """
        try:
            async with self.get_connection_context() as redis_conn:
                value = await redis_conn.get(key)
                return value
                
        except Exception as e:
            self._logger.error(f"Failed to get key {key}: {e}")
            return None

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get connection information for diagnostics
        
        Returns:
            Dict[str, Any]: Connection status and configuration info
        """
        return {
            "host": self._config.host,
            "port": self._config.port,
            "db": self._config.db,
            "ssl": self._config.ssl,
            "connected": self._connected,
            "connection_attempts": self._connection_attempts,
            "max_connections": self._config.max_connections,
            "socket_timeout": self._config.socket_timeout
        }

    def __repr__(self) -> str:
        """String representation of RedisConnectionManager"""
        return f"RedisConnectionManager(host='{self._config.host}', port={self._config.port}, connected={self._connected})"