"""
Unit tests for PollingStrategy.
"""

import pytest
import random
from unittest.mock import patch

from src.beast_mode.observatory.polling.polling_strategy import PollingStrategy, PollingConfig


class TestPollingStrategy:
    """Test cases for PollingStrategy."""
    
    @pytest.fixture
    def polling_strategy(self):
        """Create a PollingStrategy instance for testing."""
        config = PollingConfig(
            base_interval=2.0,
            max_interval=10.0,
            backoff_multiplier=2.0,
            jitter_factor=0.1,
            max_failures=3,
            success_reset_threshold=2
        )
        return PollingStrategy(config)
    
    def test_calculate_next_interval_success(self, polling_strategy):
        """Test interval calculation for successful requests."""
        endpoint = "test-endpoint"
        
        # First success should return base interval
        interval = polling_strategy.calculate_next_interval(endpoint, success=True)
        assert interval == polling_strategy.config.base_interval
    
    def test_calculate_next_interval_failure_backoff(self, polling_strategy):
        """Test exponential backoff on failures."""
        endpoint = "test-endpoint"
        
        # First failure
        interval1 = polling_strategy.calculate_next_interval(endpoint, success=False)
        expected1 = polling_strategy.config.base_interval * polling_strategy.config.backoff_multiplier
        assert interval1 == expected1
        
        # Second failure
        interval2 = polling_strategy.calculate_next_interval(endpoint, success=False)
        expected2 = polling_strategy.config.base_interval * (polling_strategy.config.backoff_multiplier ** 2)
        assert interval2 == expected2
    
    def test_calculate_next_interval_max_limit(self, polling_strategy):
        """Test that interval doesn't exceed maximum."""
        endpoint = "test-endpoint"
        
        # Multiple failures to trigger max interval
        for _ in range(5):
            polling_strategy.calculate_next_interval(endpoint, success=False)
        
        interval = polling_strategy.calculate_next_interval(endpoint, success=False)
        assert interval <= polling_strategy.config.max_interval
    
    def test_success_reset_threshold(self, polling_strategy):
        """Test that successes reset failure count."""
        endpoint = "test-endpoint"
        
        # Cause some failures
        polling_strategy.calculate_next_interval(endpoint, success=False)
        polling_strategy.calculate_next_interval(endpoint, success=False)
        
        # Check that we're backed off
        assert polling_strategy.endpoint_failures[endpoint] == 2
        
        # Successes should reset after threshold
        polling_strategy.calculate_next_interval(endpoint, success=True)
        polling_strategy.calculate_next_interval(endpoint, success=True)
        
        # Failures should be reset
        assert polling_strategy.endpoint_failures[endpoint] == 0
    
    def test_jitter_factor(self, polling_strategy):
        """Test that jitter is applied to intervals."""
        endpoint = "test-endpoint"
        
        # Mock random to get predictable jitter
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = 0.1  # Fixed jitter
            
            interval = polling_strategy.calculate_next_interval(endpoint, success=True)
            
            # Should be base interval + jitter
            expected = polling_strategy.config.base_interval + 0.1
            assert interval == expected
    
    def test_minimum_interval(self, polling_strategy):
        """Test that interval never goes below minimum."""
        endpoint = "test-endpoint"
        
        # Mock random to return large negative jitter
        with patch('random.uniform') as mock_uniform:
            mock_uniform.return_value = -100.0  # Large negative jitter
            
            interval = polling_strategy.calculate_next_interval(endpoint, success=True)
            
            # Should be clamped to minimum of 1.0
            assert interval == 1.0
    
    def test_get_current_interval(self, polling_strategy):
        """Test getting current interval for endpoint."""
        endpoint = "test-endpoint"
        
        # Initially should return base interval
        assert polling_strategy.get_current_interval(endpoint) == polling_strategy.config.base_interval
        
        # After calculating interval, should return that value
        calculated_interval = polling_strategy.calculate_next_interval(endpoint, success=True)
        assert polling_strategy.get_current_interval(endpoint) == calculated_interval
    
    def test_reset_endpoint(self, polling_strategy):
        """Test resetting endpoint state."""
        endpoint = "test-endpoint"
        
        # Set some state
        polling_strategy.calculate_next_interval(endpoint, success=False)
        polling_strategy.calculate_next_interval(endpoint, success=False)
        
        # Reset endpoint
        polling_strategy.reset_endpoint(endpoint)
        
        # State should be cleared
        assert polling_strategy.endpoint_failures[endpoint] == 0
        assert polling_strategy.endpoint_successes[endpoint] == 0
        assert endpoint not in polling_strategy.endpoint_last_interval
    
    def test_get_endpoint_stats(self, polling_strategy):
        """Test getting endpoint statistics."""
        endpoint = "test-endpoint"
        
        # Set some state
        polling_strategy.calculate_next_interval(endpoint, success=False)
        
        stats = polling_strategy.get_endpoint_stats(endpoint)
        
        assert "failures" in stats
        assert "successes" in stats
        assert "current_interval" in stats
        assert "is_backed_off" in stats
        assert stats["failures"] == 1
        assert stats["is_backed_off"] is True
    
    def test_get_all_stats(self, polling_strategy):
        """Test getting statistics for all endpoints."""
        endpoint1 = "endpoint1"
        endpoint2 = "endpoint2"
        
        # Set state for both endpoints
        polling_strategy.calculate_next_interval(endpoint1, success=False)
        polling_strategy.calculate_next_interval(endpoint2, success=True)
        
        all_stats = polling_strategy.get_all_stats()
        
        assert endpoint1 in all_stats
        assert endpoint2 in all_stats
        assert all_stats[endpoint1]["failures"] == 1
        assert all_stats[endpoint2]["successes"] == 1
    
    def test_should_poll_time_based(self, polling_strategy):
        """Test should_poll based on time elapsed."""
        endpoint = "test-endpoint"
        
        # Set a specific interval
        polling_strategy.calculate_next_interval(endpoint, success=True)
        
        # Should poll if enough time has passed
        assert polling_strategy.should_poll(endpoint, 5.0) is True
        
        # Should not poll if not enough time has passed
        assert polling_strategy.should_poll(endpoint, 1.0) is False
    
    def test_adapt_to_response_time(self, polling_strategy):
        """Test adaptation to response time."""
        endpoint = "test-endpoint"
        
        # Set initial interval
        initial_interval = polling_strategy.calculate_next_interval(endpoint, success=True)
        
        # Adapt to slow response time
        polling_strategy.adapt_to_response_time(endpoint, 15.0)
        
        # Interval should be increased
        new_interval = polling_strategy.get_current_interval(endpoint)
        assert new_interval > initial_interval
    
    def test_adapt_to_fast_response_time(self, polling_strategy):
        """Test that fast response times don't decrease interval."""
        endpoint = "test-endpoint"
        
        # Set initial interval
        initial_interval = polling_strategy.calculate_next_interval(endpoint, success=True)
        
        # Adapt to fast response time
        polling_strategy.adapt_to_response_time(endpoint, 1.0)
        
        # Interval should not change
        new_interval = polling_strategy.get_current_interval(endpoint)
        assert new_interval == initial_interval
    
    def test_polling_config_defaults(self):
        """Test default configuration values."""
        config = PollingConfig()
        assert config.base_interval == 5.0
        assert config.max_interval == 60.0
        assert config.backoff_multiplier == 1.5
        assert config.jitter_factor == 0.1
        assert config.max_failures == 10
        assert config.success_reset_threshold == 3