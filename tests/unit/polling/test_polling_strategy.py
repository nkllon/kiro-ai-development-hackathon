"""
Unit tests for PollingStrategy
"""

import pytest
import time
from unittest.mock import patch

from src.beast_mode.observatory.polling.polling_strategy import (
    PollingStrategy, 
    PollingConfig, 
    PollingState
)


class TestPollingStrategy:
    """Test cases for PollingStrategy"""
    
    @pytest.fixture
    def polling_strategy(self):
        """Create a PollingStrategy instance for testing"""
        config = PollingConfig(
            base_interval=5.0,
            max_interval=60.0,
            min_interval=1.0,
            backoff_multiplier=1.5,
            jitter_factor=0.1,
            max_failures=3,
            recovery_threshold=2
        )
        return PollingStrategy(config)
    
    def test_initial_state(self, polling_strategy):
        """Test initial endpoint state"""
        endpoint = "test-endpoint"
        state = polling_strategy.get_endpoint_state(endpoint)
        
        assert state.endpoint == endpoint
        assert state.state == PollingState.INITIAL
        assert state.current_interval == 5.0
        assert state.failure_count == 0
        assert state.success_count == 0
    
    def test_successful_request_interval(self, polling_strategy):
        """Test interval calculation for successful requests"""
        endpoint = "test-endpoint"
        
        # First successful request
        interval = polling_strategy.calculate_next_interval(endpoint, True)
        assert interval >= 1.0  # Min interval
        assert interval <= 60.0  # Max interval
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.success_count == 1
        assert state.consecutive_successes == 1
        assert state.consecutive_failures == 0
    
    def test_failed_request_backoff(self, polling_strategy):
        """Test exponential backoff for failed requests"""
        endpoint = "test-endpoint"
        
        # First failure
        interval1 = polling_strategy.calculate_next_interval(endpoint, False)
        state1 = polling_strategy.get_endpoint_state(endpoint)
        assert state1.state == PollingState.NORMAL
        assert state1.consecutive_failures == 1
        
        # Second failure - should trigger backoff
        interval2 = polling_strategy.calculate_next_interval(endpoint, False)
        state2 = polling_strategy.get_endpoint_state(endpoint)
        assert state2.state == PollingState.BACKOFF
        assert state2.consecutive_failures == 2
        assert interval2 > interval1  # Should be longer
        
        # Third failure - more backoff
        interval3 = polling_strategy.calculate_next_interval(endpoint, False)
        state3 = polling_strategy.get_endpoint_state(endpoint)
        assert state3.state == PollingState.BACKOFF
        assert state3.consecutive_failures == 3
        assert interval3 > interval2  # Should be even longer
    
    def test_suspension_on_max_failures(self, polling_strategy):
        """Test suspension when max failures reached"""
        endpoint = "test-endpoint"
        
        # Trigger max failures
        for i in range(3):
            polling_strategy.calculate_next_interval(endpoint, False)
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.state == PollingState.SUSPENDED
        assert state.consecutive_failures == 3
    
    def test_recovery_after_suspension(self, polling_strategy):
        """Test recovery after suspension period"""
        endpoint = "test-endpoint"
        
        # Trigger suspension
        for i in range(3):
            polling_strategy.calculate_next_interval(endpoint, False)
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.state == PollingState.SUSPENDED
        
        # Mock time to simulate suspension end
        with patch('time.time', return_value=time.time() + 400.0):
            # Try to calculate interval - should trigger recovery
            interval = polling_strategy.calculate_next_interval(endpoint, True)
            state = polling_strategy.get_endpoint_state(endpoint)
            assert state.state == PollingState.RECOVERY
    
    def test_recovery_to_normal(self, polling_strategy):
        """Test recovery from backoff to normal state"""
        endpoint = "test-endpoint"
        
        # Trigger backoff
        polling_strategy.calculate_next_interval(endpoint, False)
        polling_strategy.calculate_next_interval(endpoint, False)
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.state == PollingState.BACKOFF
        
        # Successful requests should trigger recovery
        polling_strategy.calculate_next_interval(endpoint, True)
        polling_strategy.calculate_next_interval(endpoint, True)
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.state == PollingState.NORMAL
        assert state.consecutive_successes == 2
        assert state.consecutive_failures == 0
    
    def test_jitter_application(self, polling_strategy):
        """Test that jitter is applied to intervals"""
        endpoint = "test-endpoint"
        
        # Calculate multiple intervals and check for variation
        intervals = []
        for i in range(10):
            interval = polling_strategy.calculate_next_interval(endpoint, True)
            intervals.append(interval)
        
        # Should have some variation due to jitter
        assert len(set(intervals)) > 1  # Not all identical
        
        # All intervals should be within bounds
        for interval in intervals:
            assert interval >= 1.0
            assert interval <= 60.0
    
    def test_should_poll_endpoint(self, polling_strategy):
        """Test endpoint polling eligibility"""
        endpoint = "test-endpoint"
        
        # Initially should be able to poll
        assert polling_strategy.should_poll_endpoint(endpoint) is True
        
        # After suspension, should not be able to poll
        for i in range(3):
            polling_strategy.calculate_next_interval(endpoint, False)
        
        assert polling_strategy.should_poll_endpoint(endpoint) is False
    
    def test_reset_endpoint(self, polling_strategy):
        """Test endpoint reset"""
        endpoint = "test-endpoint"
        
        # Trigger some failures
        polling_strategy.calculate_next_interval(endpoint, False)
        polling_strategy.calculate_next_interval(endpoint, False)
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.failure_count > 0
        
        # Reset endpoint
        polling_strategy.reset_endpoint(endpoint)
        
        state = polling_strategy.get_endpoint_state(endpoint)
        assert state.failure_count == 0
        assert state.success_count == 0
        assert state.state == PollingState.INITIAL
    
    def test_endpoint_stats(self, polling_strategy):
        """Test endpoint statistics"""
        endpoint = "test-endpoint"
        
        # Make some requests
        polling_strategy.calculate_next_interval(endpoint, True)
        polling_strategy.calculate_next_interval(endpoint, False)
        
        stats = polling_strategy.get_endpoint_stats(endpoint)
        
        assert stats["endpoint"] == endpoint
        assert stats["success_count"] == 1
        assert stats["failure_count"] == 1
        assert "current_interval" in stats
        assert "state" in stats
    
    def test_global_stats(self, polling_strategy):
        """Test global statistics"""
        endpoint1 = "endpoint-1"
        endpoint2 = "endpoint-2"
        
        # Make requests on different endpoints
        polling_strategy.calculate_next_interval(endpoint1, True)
        polling_strategy.calculate_next_interval(endpoint1, False)
        polling_strategy.calculate_next_interval(endpoint2, True)
        
        stats = polling_strategy.get_global_stats()
        
        assert stats["global_stats"]["total_requests"] == 3
        assert stats["global_stats"]["successful_requests"] == 2
        assert stats["global_stats"]["failed_requests"] == 1
        assert stats["endpoint_count"] == 2
        assert stats["active_endpoints"] == 2