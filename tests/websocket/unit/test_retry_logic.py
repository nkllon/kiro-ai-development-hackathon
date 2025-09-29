"""Unit tests for WebSocket Retry Logic."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.beast_mode.observatory.websocket.retry_strategy import (
    ExponentialBackoffRetry,
    retry_with_strategy
)
from src.beast_mode.observatory.websocket.exceptions import (
    RetryExhaustedError,
    WebSocketConnectionError
)
from tests.websocket.fixtures.websocket_test_data import (
    WebSocketTestConfig,
    WebSocketTestData,
    WebSocketTestMetrics
)


class TestExponentialBackoffRetry:
    """Test Exponential Backoff Retry functionality."""
    
    @pytest.fixture
    def retry_strategy(self):
        """Create retry strategy instance."""
        return ExponentialBackoffRetry(
            base_delay=1.0,
            max_delay=60.0,
            multiplier=2.0,
            max_attempts=5
        )
    
    def test_retry_strategy_initialization(self, retry_strategy):
        """Test retry strategy initialization."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_strategy_initialization",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        assert retry_strategy.base_delay == 1.0
        assert retry_strategy.max_delay == 60.0
        assert retry_strategy.multiplier == 2.0
        assert retry_strategy.max_attempts == 5
        assert retry_strategy.get_attempt_count() == 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_strategy_initialization",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_should_retry_first_attempt(self, retry_strategy):
        """Test retry decision on first attempt."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_should_retry_first_attempt",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        error = Exception("Test error")
        assert retry_strategy.should_retry(error) is True
        assert retry_strategy.get_attempt_count() == 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_should_retry_first_attempt",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_should_retry_max_attempts(self, retry_strategy):
        """Test retry decision at max attempts."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_should_retry_max_attempts",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Exhaust all attempts
        for _ in range(retry_strategy.max_attempts):
            retry_strategy.increment_attempt()
        
        error = Exception("Test error")
        assert retry_strategy.should_retry(error) is False
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_should_retry_max_attempts",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_calculate_delay_exponential(self, retry_strategy):
        """Test exponential delay calculation."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_calculate_delay_exponential",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Test first attempt
        retry_strategy.increment_attempt()
        delay1 = retry_strategy.calculate_delay()
        assert delay1 == 1.0  # base_delay
        
        # Test second attempt
        retry_strategy.increment_attempt()
        delay2 = retry_strategy.calculate_delay()
        assert delay2 == 2.0  # base_delay * multiplier
        
        # Test third attempt
        retry_strategy.increment_attempt()
        delay3 = retry_strategy.calculate_delay()
        assert delay3 == 4.0  # base_delay * multiplier^2
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_calculate_delay_exponential",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_calculate_delay_max_limit(self, retry_strategy):
        """Test delay calculation with max limit."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_calculate_delay_max_limit",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Set high attempt count to exceed max delay
        retry_strategy._attempt_count = 10
        delay = retry_strategy.calculate_delay()
        
        assert delay == retry_strategy.max_delay
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_calculate_delay_max_limit",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_increment_attempt(self, retry_strategy):
        """Test attempt increment."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_increment_attempt",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        assert retry_strategy.get_attempt_count() == 0
        
        retry_strategy.increment_attempt()
        assert retry_strategy.get_attempt_count() == 1
        
        retry_strategy.increment_attempt()
        assert retry_strategy.get_attempt_count() == 2
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_increment_attempt",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_reset(self, retry_strategy):
        """Test retry strategy reset."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_reset",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Increment attempts
        retry_strategy.increment_attempt()
        retry_strategy.increment_attempt()
        assert retry_strategy.get_attempt_count() == 2
        
        # Reset
        retry_strategy.reset()
        assert retry_strategy.get_attempt_count() == 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_reset",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_get_attempt_count(self, retry_strategy):
        """Test getting attempt count."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_get_attempt_count",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        assert retry_strategy.get_attempt_count() == 0
        
        retry_strategy.increment_attempt()
        assert retry_strategy.get_attempt_count() == 1
        
        retry_strategy.increment_attempt()
        retry_strategy.increment_attempt()
        assert retry_strategy.get_attempt_count() == 3
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_get_attempt_count",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_error_type_filtering(self, retry_strategy):
        """Test error type filtering for retry decisions."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_error_type_filtering",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Test retryable errors
        retryable_errors = [
            ConnectionError("Network error"),
            TimeoutError("Timeout"),
            Exception("Generic error")
        ]
        
        for error in retryable_errors:
            assert retry_strategy.should_retry(error) is True
        
        # Test non-retryable errors (if implemented)
        # This would depend on the specific implementation
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_error_type_filtering",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    def test_custom_retry_strategy(self):
        """Test custom retry strategy configuration."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_custom_retry_strategy",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Create custom strategy
        custom_strategy = ExponentialBackoffRetry(
            base_delay=0.5,
            max_delay=30.0,
            multiplier=1.5,
            max_attempts=10
        )
        
        assert custom_strategy.base_delay == 0.5
        assert custom_strategy.max_delay == 30.0
        assert custom_strategy.multiplier == 1.5
        assert custom_strategy.max_attempts == 10
        
        # Test delay calculation
        custom_strategy.increment_attempt()
        delay = custom_strategy.calculate_delay()
        assert delay == 0.5
        
        custom_strategy.increment_attempt()
        delay = custom_strategy.calculate_delay()
        assert delay == 0.75  # 0.5 * 1.5
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_custom_retry_strategy",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))


class TestRetryWithStrategy:
    """Test retry_with_strategy decorator functionality."""
    
    @pytest.fixture
    def retry_strategy(self):
        """Create retry strategy instance."""
        return ExponentialBackoffRetry(
            base_delay=0.1,  # Short delay for testing
            max_delay=1.0,
            multiplier=2.0,
            max_attempts=3
        )
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_success_first_attempt(self, retry_strategy):
        """Test successful retry on first attempt."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_success_first_attempt",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        async def test_function():
            return "success"
        
        result = await retry_with_strategy(retry_strategy, test_function)
        
        assert result == "success"
        assert retry_strategy.get_attempt_count() == 0  # No retries needed
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_success_first_attempt",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_success_after_retries(self, retry_strategy):
        """Test successful retry after multiple attempts."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_success_after_retries",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        attempt_count = 0
        
        async def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry_with_strategy(retry_strategy, test_function)
        
        assert result == "success"
        assert attempt_count == 3
        assert retry_strategy.get_attempt_count() == 2  # 2 retries
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_success_after_retries",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_exhausted(self, retry_strategy):
        """Test retry exhaustion."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_exhausted",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        async def test_function():
            raise Exception("Persistent failure")
        
        with pytest.raises(RetryExhaustedError):
            await retry_with_strategy(retry_strategy, test_function)
        
        assert retry_strategy.get_attempt_count() == retry_strategy.max_attempts
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_exhausted",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_with_args(self, retry_strategy):
        """Test retry with function arguments."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_with_args",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        async def test_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"
        
        result = await retry_with_strategy(
            retry_strategy, 
            test_function, 
            "arg1", 
            "arg2", 
            kwarg1="kwarg1"
        )
        
        assert result == "arg1-arg2-kwarg1"
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_with_args",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_delay_timing(self, retry_strategy):
        """Test retry delay timing."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_delay_timing",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        attempt_count = 0
        start_time = asyncio.get_event_loop().time()
        
        async def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry_with_strategy(retry_strategy, test_function)
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        
        assert result == "success"
        assert attempt_count == 2
        # Should have waited at least the base delay
        assert elapsed_time >= retry_strategy.base_delay
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_delay_timing",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_non_retryable_error(self, retry_strategy):
        """Test retry with non-retryable error."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_non_retryable_error",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        # Mock should_retry to return False
        retry_strategy.should_retry = Mock(return_value=False)
        
        async def test_function():
            raise ValueError("Non-retryable error")
        
        with pytest.raises(ValueError):
            await retry_with_strategy(retry_strategy, test_function)
        
        # Should not have incremented attempts
        assert retry_strategy.get_attempt_count() == 0
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_non_retryable_error",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))
    
    @pytest.mark.asyncio
    async def test_retry_with_strategy_reset_on_success(self, retry_strategy):
        """Test retry strategy reset on success."""
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_reset_on_success",
            "status": "in_progress",
            "details": {"test_type": "unit", "component": "retry_strategy"}
        }))
        
        attempt_count = 0
        
        async def test_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        # First call with retries
        result = await retry_with_strategy(retry_strategy, test_function)
        assert result == "success"
        assert retry_strategy.get_attempt_count() == 1  # 1 retry
        
        # Reset attempt count
        attempt_count = 0
        
        # Second call should start fresh
        result = await retry_with_strategy(retry_strategy, test_function)
        assert result == "success"
        assert retry_strategy.get_attempt_count() == 1  # 1 retry again
        
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "task": "6.1",
            "action": "test_retry_with_strategy_reset_on_success",
            "status": "completed",
            "details": {"test_type": "unit", "component": "retry_strategy", "result": "passed"}
        }))