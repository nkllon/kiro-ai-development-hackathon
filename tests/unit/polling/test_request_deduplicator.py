"""
Unit tests for RequestDeduplicator.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from src.beast_mode.observatory.polling.request_deduplicator import RequestDeduplicator, CachedRequest


class TestRequestDeduplicator:
    """Test cases for RequestDeduplicator."""
    
    @pytest.fixture
    def deduplicator(self):
        """Create a RequestDeduplicator instance for testing."""
        return RequestDeduplicator(cache_ttl=10, max_cache_size=100)
    
    @pytest.fixture
    def mock_request_func(self):
        """Create a mock request function."""
        async def mock_func(endpoint, params=None):
            return {"data": "test"}, 200
        return mock_func
    
    @pytest.mark.asyncio
    async def test_cache_miss_new_request(self, deduplicator, mock_request_func):
        """Test cache miss triggers new request."""
        endpoint = "test-endpoint"
        params = {"key": "value"}
        
        response_data, status_code = await deduplicator.get_or_request(
            endpoint, params, mock_request_func
        )
        
        assert response_data == {"data": "test"}
        assert status_code == 200
        assert len(deduplicator.cache) == 1
    
    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached(self, deduplicator, mock_request_func):
        """Test cache hit returns cached response."""
        endpoint = "test-endpoint"
        params = {"key": "value"}
        
        # First request
        response_data1, status_code1 = await deduplicator.get_or_request(
            endpoint, params, mock_request_func
        )
        
        # Second request with same parameters
        response_data2, status_code2 = await deduplicator.get_or_request(
            endpoint, params, mock_request_func
        )
        
        assert response_data1 == response_data2
        assert status_code1 == status_code2
        assert len(deduplicator.cache) == 1
    
    @pytest.mark.asyncio
    async def test_different_params_create_different_cache_entries(self, deduplicator, mock_request_func):
        """Test different parameters create different cache entries."""
        endpoint = "test-endpoint"
        
        # First request
        await deduplicator.get_or_request(
            endpoint, {"key1": "value1"}, mock_request_func
        )
        
        # Second request with different parameters
        await deduplicator.get_or_request(
            endpoint, {"key2": "value2"}, mock_request_func
        )
        
        assert len(deduplicator.cache) == 2
    
    @pytest.mark.asyncio
    async def test_request_batching(self, deduplicator):
        """Test that multiple simultaneous requests are batched."""
        endpoint = "test-endpoint"
        params = {"key": "value"}
        
        call_count = 0
        
        async def counting_request_func(endpoint, params=None):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate network delay
            return {"data": f"response-{call_count}"}, 200
        
        # Make multiple simultaneous requests
        tasks = [
            deduplicator.get_or_request(endpoint, params, counting_request_func)
            for _ in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All requests should get the same response
        for response_data, status_code in results:
            assert response_data == {"data": "response-1"}
            assert status_code == 200
        
        # Only one actual HTTP request should have been made
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, deduplicator, mock_request_func):
        """Test cache expiration."""
        endpoint = "test-endpoint"
        params = {"key": "value"}
        
        # First request
        await deduplicator.get_or_request(endpoint, params, mock_request_func)
        assert len(deduplicator.cache) == 1
        
        # Simulate time passing beyond TTL
        with patch('src.beast_mode.observatory.polling.request_deduplicator.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(seconds=15)
            
            # Second request should trigger new HTTP request
            await deduplicator.get_or_request(endpoint, params, mock_request_func)
            
            # Cache should be cleaned up
            assert len(deduplicator.cache) == 1
    
    @pytest.mark.asyncio
    async def test_request_error_propagation(self, deduplicator):
        """Test that request errors are properly propagated."""
        endpoint = "test-endpoint"
        
        async def error_request_func(endpoint, params=None):
            raise Exception("Network error")
        
        with pytest.raises(Exception, match="Network error"):
            await deduplicator.get_or_request(endpoint, {}, error_request_func)
    
    @pytest.mark.asyncio
    async def test_cache_size_limit(self, deduplicator):
        """Test cache size limit enforcement."""
        # Create deduplicator with small cache size
        small_deduplicator = RequestDeduplicator(cache_ttl=3600, max_cache_size=2)
        
        async def mock_request_func(endpoint, params=None):
            return {"data": "test"}, 200
        
        # Fill cache to limit
        await small_deduplicator.get_or_request("endpoint1", {}, mock_request_func)
        await small_deduplicator.get_or_request("endpoint2", {}, mock_request_func)
        
        # Add one more request
        await small_deduplicator.get_or_request("endpoint3", {}, mock_request_func)
        
        # Cache should not exceed limit
        assert len(small_deduplicator.cache) <= 2
    
    def test_get_cache_stats(self, deduplicator):
        """Test cache statistics."""
        stats = deduplicator.get_cache_stats()
        
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "expired_entries" in stats
        assert "pending_requests" in stats
        assert "request_counts" in stats
    
    def test_clear_cache(self, deduplicator):
        """Test cache clearing."""
        # Add some cache entries
        cached_request = CachedRequest(
            endpoint="test",
            params_hash="hash",
            timestamp=datetime.utcnow(),
            response_data={"data": "test"},
            response_status=200
        )
        deduplicator.cache["test:hash"] = cached_request
        
        assert len(deduplicator.cache) == 1
        
        deduplicator.clear_cache()
        
        assert len(deduplicator.cache) == 0
    
    def test_params_hash_generation(self, deduplicator):
        """Test parameter hash generation."""
        endpoint = "test-endpoint"
        params1 = {"key1": "value1", "key2": "value2"}
        params2 = {"key2": "value2", "key1": "value1"}  # Different order
        
        hash1 = deduplicator._generate_params_hash(endpoint, params1)
        hash2 = deduplicator._generate_params_hash(endpoint, params2)
        
        # Hashes should be the same regardless of parameter order
        assert hash1 == hash2