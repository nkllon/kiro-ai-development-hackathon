"""
Unit tests for RequestDeduplicator
"""

import pytest
import asyncio
import time
from unittest.mock import patch

from src.beast_mode.observatory.polling.request_deduplicator import RequestDeduplicator


class TestRequestDeduplicator:
    """Test cases for RequestDeduplicator"""
    
    @pytest.fixture
    def deduplicator(self):
        """Create a RequestDeduplicator instance for testing"""
        return RequestDeduplicator(cache_ttl=10.0, batch_window=1.0)
    
    def test_generate_request_key(self, deduplicator):
        """Test request key generation"""
        endpoint1 = "https://api.example.com/data"
        params1 = {"param1": "value1", "param2": "value2"}
        headers1 = {"User-Agent": "test-agent"}
        
        endpoint2 = "https://api.example.com/data"
        params2 = {"param2": "value2", "param1": "value1"}  # Different order
        headers2 = {"User-Agent": "test-agent"}
        
        # Same request should generate same key
        key1 = deduplicator._generate_request_key(endpoint1, params1, headers1)
        key2 = deduplicator._generate_request_key(endpoint2, params2, headers2)
        assert key1 == key2
        
        # Different endpoint should generate different key
        endpoint3 = "https://api.example.com/other"
        key3 = deduplicator._generate_request_key(endpoint3, params1, headers1)
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_get_or_create_request_new(self, deduplicator):
        """Test creating a new request"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        client_id = "client-1"
        
        request, is_new = await deduplicator.get_or_create_request(
            endpoint, params, headers, client_id
        )
        
        assert is_new is True
        assert request.endpoint == endpoint
        assert request.params == params
        assert request.headers == headers
        assert client_id in request.clients_waiting
    
    @pytest.mark.asyncio
    async def test_get_or_create_request_cached(self, deduplicator):
        """Test getting a cached request"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        
        # Create first request
        request1, is_new1 = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-1"
        )
        assert is_new1 is True
        
        # Complete the request
        await deduplicator.complete_request(
            deduplicator._generate_request_key(endpoint, params, headers),
            response_data={"result": "success"},
            status_code=200
        )
        
        # Get same request again
        request2, is_new2 = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-2"
        )
        assert is_new2 is False
        assert request2.response_data == {"result": "success"}
        assert request2.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_or_create_request_deduplication(self, deduplicator):
        """Test request deduplication for active requests"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        
        # Create first request
        request1, is_new1 = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-1"
        )
        assert is_new1 is True
        
        # Try to create same request while first is still active
        request2, is_new2 = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-2"
        )
        assert is_new2 is False
        assert request1 == request2
        assert "client-2" in request1.clients_waiting
    
    @pytest.mark.asyncio
    async def test_complete_request(self, deduplicator):
        """Test request completion"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        
        # Create request
        request, is_new = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-1"
        )
        assert is_new is True
        
        # Complete request
        request_key = deduplicator._generate_request_key(endpoint, params, headers)
        await deduplicator.complete_request(
            request_key,
            response_data={"result": "success"},
            response_headers={"Content-Type": "application/json"},
            status_code=200
        )
        
        # Check that request is now cached
        stats = deduplicator.get_stats()
        assert stats["cache_size"] == 1
        assert stats["active_requests"] == 0
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, deduplicator):
        """Test cache expiration"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        
        # Create and complete request
        request, is_new = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-1"
        )
        request_key = deduplicator._generate_request_key(endpoint, params, headers)
        await deduplicator.complete_request(request_key, response_data={"result": "success"})
        
        # Mock time to simulate cache expiration
        with patch('time.time', return_value=time.time() + 15.0):  # Past TTL
            # Try to get same request - should create new one
            request2, is_new2 = await deduplicator.get_or_create_request(
                endpoint, params, headers, "client-2"
            )
            assert is_new2 is True
    
    @pytest.mark.asyncio
    async def test_batching_logic(self, deduplicator):
        """Test request batching"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        
        # Create first request
        request1, is_new1 = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-1"
        )
        assert is_new1 is True
        
        # Create second request quickly - should be batched
        request2, is_new2 = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-2"
        )
        assert is_new2 is False  # Should be deduplicated
        
        # Check batching stats
        stats = deduplicator.get_stats()
        assert stats["stats"]["batched_requests"] > 0
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, deduplicator):
        """Test cache clearing"""
        endpoint = "https://api.example.com/data"
        params = {"param1": "value1"}
        headers = {"User-Agent": "test-agent"}
        
        # Create and complete request
        request, is_new = await deduplicator.get_or_create_request(
            endpoint, params, headers, "client-1"
        )
        request_key = deduplicator._generate_request_key(endpoint, params, headers)
        await deduplicator.complete_request(request_key, response_data={"result": "success"})
        
        # Check cache has data
        stats = deduplicator.get_stats()
        assert stats["cache_size"] == 1
        
        # Clear cache
        await deduplicator.clear_cache()
        
        # Check cache is empty
        stats = deduplicator.get_stats()
        assert stats["cache_size"] == 0
        assert stats["active_requests"] == 0
    
    def test_stats_tracking(self, deduplicator):
        """Test statistics tracking"""
        stats = deduplicator.get_stats()
        
        assert "stats" in stats
        assert "cache_size" in stats
        assert "active_requests" in stats
        assert "pending_batches" in stats
        assert "batch_timers" in stats
        
        # Check initial stats
        assert stats["stats"]["total_requests"] == 0
        assert stats["cache_size"] == 0
        assert stats["active_requests"] == 0