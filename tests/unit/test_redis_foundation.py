"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.528730
"""




import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime

from src.beast_mode.messaging.redis_foundation import (
    RedisFoundation, RedisConfig, ConnectionStatus, REDIS_AVAILABLE
)


class TestRedisFoundation:
    """Test suite for Redis Foundation."""
    
    @pytest.fixture
    def config(self):
        """Test Redis configuration."""
        return RedisConfig(
            host="localhost",
            port=6379,
            health_check_interval=1.0,
            reconnect_delay=0.1,
            max_reconnect_attempts=3
        )
    
    @pytest.fixture
    def redis_foundation(self, config):
        """Redis foundation instance for testing."""
        return RedisFoundation(config)
    
    def test_redis_config_defaults(self):
        """Test Redis configuration defaults."""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.max_connections == 10
    
    def test_redis_foundation_initialization(self, redis_foundation):
        """Test Redis foundation initialization."""
        assert redis_foundation.status == ConnectionStatus.DISCONNECTED
        assert redis_foundation.reconnect_attempts == 0
        assert redis_foundation.subscribers == {}
        
        if not REDIS_AVAILABLE:
            assert redis_foundation.status == ConnectionStatus.FAILED
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_successful_initialization(self, mock_redis, redis_foundation):
        """Test successful Redis initialization."""
        # Mock Redis components
        mock_pool = AsyncMock()
        mock_client = AsyncMock()
        mock_redis.ConnectionPool.return_value = mock_pool
        mock_redis.Redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        # Test initialization
        result = await redis_foundation.initialize()
        
        assert result is True
        assert redis_foundation.status == ConnectionStatus.CONNECTED
        assert redis_foundation.reconnect_attempts == 0
        mock_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_failed_initialization(self, mock_redis, redis_foundation):
        """Test failed Redis initialization."""
        # Mock Redis failure
        mock_redis.ConnectionPool.side_effect = Exception("Connection failed")
        
        # Test initialization
        result = await redis_foundation.initialize()
        
        assert result is False
        assert redis_foundation.status == ConnectionStatus.FAILED
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_health_check_success(self, mock_redis, redis_foundation):
        """Test successful health check."""
        # Setup mocks
        mock_client = AsyncMock()
        redis_foundation.client = mock_client
        redis_foundation.status = ConnectionStatus.CONNECTED
        mock_client.ping.return_value = True
        
        # Test health check
        result = await redis_foundation.health_check()
        
        assert result is True
        assert redis_foundation.status == ConnectionStatus.CONNECTED
        mock_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_health_check_failure(self, mock_redis, redis_foundation):
        """Test failed health check triggers reconnection."""
        # Setup mocks
        mock_client = AsyncMock()
        redis_foundation.client = mock_client
        redis_foundation.status = ConnectionStatus.CONNECTED
        mock_client.ping.side_effect = Exception("Ping failed")
        
        # Test health check
        result = await redis_foundation.health_check()
        
        assert result is False
        assert redis_foundation.status == ConnectionStatus.RECONNECTING
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_publish_message(self, mock_redis, redis_foundation):
        """Test message publishing."""
        # Setup mocks
        mock_client = AsyncMock()
        redis_foundation.client = mock_client
        redis_foundation.status = ConnectionStatus.CONNECTED
        
        # Test message
        message = {"type": "test", "data": "hello"}
        
        # Test publish
        result = await redis_foundation.publish("test_channel", message)
        
        assert result is True
        mock_client.publish.assert_called_once_with("test_channel", json.dumps(message))
    
    @pytest.mark.asyncio
    async def test_publish_without_connection(self, redis_foundation):
        """Test publish fails without connection."""
        redis_foundation.client = None
        redis_foundation.status = ConnectionStatus.DISCONNECTED
        
        result = await redis_foundation.publish("test_channel", {"test": "data"})
        
        assert result is False
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_subscribe_to_channel(self, mock_redis, redis_foundation):
        """Test channel subscription."""
        # Setup mocks
        mock_client = AsyncMock()
        redis_foundation.client = mock_client
        redis_foundation.status = ConnectionStatus.CONNECTED
        
        # Test callback
        callback = Mock()
        
        # Test subscribe
        result = await redis_foundation.subscribe("test_channel", callback)
        
        assert result is True
        assert "test_channel" in redis_foundation.subscribers
        assert callback in redis_foundation.subscribers["test_channel"]
    
    @pytest.mark.asyncio
    async def test_subscribe_without_connection(self, redis_foundation):
        """Test subscribe fails without connection."""
        redis_foundation.client = None
        redis_foundation.status = ConnectionStatus.DISCONNECTED
        
        callback = Mock()
        result = await redis_foundation.subscribe("test_channel", callback)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_channel(self, redis_foundation):
        """Test channel unsubscription."""
        # Setup subscription
        callback = Mock()
        redis_foundation.subscribers["test_channel"] = [callback]
        
        # Test unsubscribe
        result = await redis_foundation.unsubscribe("test_channel", callback)
        
        assert result is True
        assert "test_channel" not in redis_foundation.subscribers
    
    @pytest.mark.asyncio
    async def test_unsubscribe_all_callbacks(self, redis_foundation):
        """Test unsubscribing all callbacks from channel."""
        # Setup subscriptions
        callback1 = Mock()
        callback2 = Mock()
        redis_foundation.subscribers["test_channel"] = [callback1, callback2]
        
        # Test unsubscribe all
        result = await redis_foundation.unsubscribe("test_channel")
        
        assert result is True
        assert "test_channel" not in redis_foundation.subscribers
    
    @pytest.mark.asyncio
    async def test_get_connection_info(self, redis_foundation):
        """Test connection info retrieval."""
        redis_foundation.status = ConnectionStatus.CONNECTED
        redis_foundation.subscribers = {"test_channel": [Mock()]}
        
        info = await redis_foundation.get_connection_info()
        
        assert info["status"] == "connected"
        assert info["host"] == "localhost"
        assert info["port"] == 6379
        assert info["connected"] is True
        assert info["active_subscriptions"] == ["test_channel"]
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_graceful_shutdown(self, mock_redis, redis_foundation):
        """Test graceful shutdown."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_pool = AsyncMock()
        redis_foundation.client = mock_client
        redis_foundation.connection_pool = mock_pool
        redis_foundation.subscribers = {"test": [Mock()]}
        
        # Test shutdown
        await redis_foundation.shutdown()
        
        assert redis_foundation.subscribers == {}
        assert redis_foundation.status == ConnectionStatus.DISCONNECTED
        mock_client.close.assert_called_once()
        mock_pool.disconnect.assert_called_once()
    
    def test_get_health_status(self, redis_foundation):
        """Test health status for Beast Mode monitoring."""
        redis_foundation.status = ConnectionStatus.CONNECTED
        redis_foundation.subscribers = {"test": [Mock()]}
        
        health = redis_foundation.get_health_status()
        
        assert health["module"] == "RedisFoundation"
        assert health["status"] == "connected"
        assert health["healthy"] is True
        assert health["active_subscriptions"] == 1
        assert "redis_available" in health
    
    def test_get_capabilities(self, redis_foundation):
        """Test capabilities reporting."""
        capabilities = redis_foundation.get_capabilities()
        
        expected_caps = [
            "redis_pubsub",
            "connection_management",
            "health_monitoring", 
            "automatic_reconnection"
        ]
        
        for cap in expected_caps:
            assert cap in capabilities
        
        if REDIS_AVAILABLE:
            assert "redis_client" in capabilities
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.messaging.redis_foundation.redis')
    async def test_reconnection_with_backoff(self, mock_redis, redis_foundation):
        """Test reconnection with exponential backoff."""
        # Mock failed then successful connection
        mock_redis.ConnectionPool.side_effect = [
            Exception("First attempt fails"),
            Mock()  # Second attempt succeeds
        ]
        
        mock_client = AsyncMock()
        mock_redis.Redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        # First attempt should fail
        result1 = await redis_foundation.initialize()
        assert result1 is False
        assert redis_foundation.reconnect_attempts == 0
        
        # Trigger reconnection
        redis_foundation.status = ConnectionStatus.RECONNECTING
        result2 = await redis_foundation._reconnect()
        
        assert redis_foundation.reconnect_attempts == 1
    
    @pytest.mark.asyncio
    async def test_max_reconnection_attempts(self, redis_foundation):
        """Test max reconnection attempts limit."""
        redis_foundation.reconnect_attempts = redis_foundation.config.max_reconnect_attempts
        
        result = await redis_foundation._reconnect()
        
        assert result is False
        assert redis_foundation.status == ConnectionStatus.FAILED