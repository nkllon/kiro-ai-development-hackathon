"""
Unit tests for Circuit Breaker implementation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta

from src.beast_mode.observatory.ai_consultation.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerManager,
    with_circuit_breaker
)
from src.beast_mode.observatory.ai_consultation.exceptions import CircuitBreakerOpenError


class TestCircuitBreaker:
    """Test CircuitBreaker class"""
    
    @pytest.fixture
    def circuit_breaker(self):
        """Create a circuit breaker for testing"""
        return CircuitBreaker(
            name="test_breaker",
            failure_threshold=3,
            failure_rate_threshold=90.0,  # Higher threshold to test consecutive failures
            recovery_timeout=5
        )
    
    @pytest.mark.asyncio
    async def test_initial_state(self, circuit_breaker):
        """Test circuit breaker initial state"""
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.stats.total_calls == 0
        assert circuit_breaker.stats.successful_calls == 0
        assert circuit_breaker.stats.failed_calls == 0
        assert circuit_breaker.stats.consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_successful_call(self, circuit_breaker):
        """Test successful function call"""
        async def success_func():
            return "success"
        
        result = await circuit_breaker.call(success_func)
        
        assert result == "success"
        assert circuit_breaker.stats.total_calls == 1
        assert circuit_breaker.stats.successful_calls == 1
        assert circuit_breaker.stats.failed_calls == 0
        assert circuit_breaker.stats.consecutive_failures == 0
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_failed_call(self, circuit_breaker):
        """Test failed function call"""
        async def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.stats.total_calls == 1
        assert circuit_breaker.stats.successful_calls == 0
        assert circuit_breaker.stats.failed_calls == 1
        assert circuit_breaker.stats.consecutive_failures == 1
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, circuit_breaker):
        """Test circuit opens after failure threshold"""
        async def success_func():
            return "success"
        
        async def failing_func():
            raise ValueError("Test error")
        
        # First have some successes to avoid failure rate trigger
        for _ in range(10):
            result = await circuit_breaker.call(success_func)
            assert result == "success"
        
        # Now fail 3 times (threshold) - circuit should still be closed
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # Circuit should still be closed after exactly threshold failures
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.stats.consecutive_failures == 3
        
        # One more failure should open the circuit (but the call itself still executes)
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing_func)
        
        # Now the circuit should be open
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.stats.consecutive_failures == 4
        
        # Next call should be rejected
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_rejects_calls_when_open(self, circuit_breaker):
        """Test circuit rejects calls when open"""
        async def success_func():
            return "success"
        
        async def failing_func():
            raise ValueError("Test error")
        
        # First have some successes to avoid failure rate trigger
        for _ in range(10):
            result = await circuit_breaker.call(success_func)
            assert result == "success"
        
        # Force circuit to open (need 4 failures for threshold of 3)
        for _ in range(4):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Now calls should be rejected
        async def any_func():
            return "should not execute"
        
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.call(any_func)
    
    @pytest.mark.asyncio
    async def test_fallback_function(self):
        """Test fallback function execution when circuit is open"""
        async def fallback_func(*args, **kwargs):
            return "fallback result"
        
        circuit_breaker = CircuitBreaker(
            name="test_breaker",
            failure_threshold=2,
            failure_rate_threshold=90.0,  # Higher threshold to avoid rate trigger
            fallback_function=fallback_func
        )
        
        async def success_func():
            return "success"
        
        # Force circuit to open (need 3 failures for threshold of 2)
        async def failing_func():
            raise ValueError("Test error")
        
        # First have some successes to avoid failure rate trigger
        for _ in range(10):
            result = await circuit_breaker.call(success_func)
            assert result == "success"
        
        # First 2 failures should raise ValueError
        for _ in range(2):
            with pytest.raises(ValueError):
                await circuit_breaker.call(failing_func)
        
        # Circuit should still be closed
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        
        # 3rd failure should open circuit (but still execute and raise)
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Now subsequent calls should use fallback
        async def any_func():
            return "should not execute"
        
        result = await circuit_breaker.call(any_func)
        assert result == "fallback result"
    
    @pytest.mark.asyncio
    async def test_circuit_recovery(self, circuit_breaker):
        """Test circuit recovery after timeout"""
        # Force circuit to open
        async def failing_func():
            raise ValueError("Test error")
        
        # Need 4 failures for threshold of 3
        for i in range(4):
            if i < 3:
                with pytest.raises(ValueError):
                    await circuit_breaker.call(failing_func)
            else:
                # 4th call should open circuit
                with pytest.raises((ValueError, CircuitBreakerOpenError)):
                    await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Manually set state change time to simulate timeout
        circuit_breaker._stats.state_changed_at = datetime.utcnow() - timedelta(seconds=10)
        
        # Next call should transition to half-open
        async def success_func():
            return "success"
        
        result = await circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.stats.consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_half_open_failure_reopens_circuit(self, circuit_breaker):
        """Test that failure in half-open state reopens circuit"""
        # Force circuit to open
        async def failing_func():
            raise ValueError("Test error")
        
        # Need 4 failures for threshold of 3
        for i in range(4):
            if i < 3:
                with pytest.raises(ValueError):
                    await circuit_breaker.call(failing_func)
            else:
                # 4th call should open circuit
                with pytest.raises((ValueError, CircuitBreakerOpenError)):
                    await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Manually transition to half-open
        await circuit_breaker._transition_to_half_open()
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN
        
        # Failure in half-open should reopen circuit
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
    
    @pytest.mark.asyncio
    async def test_sync_function_support(self, circuit_breaker):
        """Test circuit breaker works with synchronous functions"""
        def sync_success_func():
            return "sync success"
        
        def sync_failing_func():
            raise ValueError("Sync error")
        
        # Test successful sync function
        result = await circuit_breaker.call(sync_success_func)
        assert result == "sync success"
        
        # Test failing sync function
        with pytest.raises(ValueError, match="Sync error"):
            await circuit_breaker.call(sync_failing_func)
    
    @pytest.mark.asyncio
    async def test_reset_circuit(self, circuit_breaker):
        """Test manual circuit reset"""
        # Force circuit to open
        async def failing_func():
            raise ValueError("Test error")
        
        # Need 4 failures for threshold of 3
        for i in range(4):
            if i < 3:
                with pytest.raises(ValueError):
                    await circuit_breaker.call(failing_func)
            else:
                # 4th call should open circuit
                with pytest.raises((ValueError, CircuitBreakerOpenError)):
                    await circuit_breaker.call(failing_func)
        
        assert circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Reset circuit
        await circuit_breaker.reset()
        
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.stats.consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_get_stats(self, circuit_breaker):
        """Test getting circuit breaker statistics"""
        async def success_func():
            return "success"
        
        await circuit_breaker.call(success_func)
        
        stats = await circuit_breaker.get_stats()
        
        assert stats['name'] == 'test_breaker'
        assert stats['state'] == CircuitBreakerState.CLOSED.value
        assert stats['total_calls'] == 1
        assert stats['successful_calls'] == 1
        assert stats['failed_calls'] == 0
        assert stats['failure_rate'] == 0.0
        assert stats['success_rate'] == 100.0


class TestCircuitBreakerManager:
    """Test CircuitBreakerManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create a circuit breaker manager for testing"""
        return CircuitBreakerManager()
    
    @pytest.mark.asyncio
    async def test_get_breaker(self, manager):
        """Test getting circuit breaker from manager"""
        breaker = await manager.get_breaker("test_breaker")
        
        assert breaker.name == "test_breaker"
        assert isinstance(breaker, CircuitBreaker)
        
        # Getting same breaker should return same instance
        breaker2 = await manager.get_breaker("test_breaker")
        assert breaker is breaker2
    
    @pytest.mark.asyncio
    async def test_get_all_stats(self, manager):
        """Test getting all circuit breaker statistics"""
        breaker1 = await manager.get_breaker("breaker1")
        breaker2 = await manager.get_breaker("breaker2")
        
        stats = await manager.get_all_stats()
        
        assert "breaker1" in stats
        assert "breaker2" in stats
        assert len(stats) == 2
    
    @pytest.mark.asyncio
    async def test_reset_all(self, manager):
        """Test resetting all circuit breakers"""
        breaker = await manager.get_breaker("test_breaker", failure_threshold=2)
        
        # Force circuit to open (need 3 failures for threshold of 2)
        async def failing_func():
            raise ValueError("Test error")
        
        for i in range(3):
            if i < 2:
                with pytest.raises(ValueError):
                    await breaker.call(failing_func)
            else:
                # 3rd call should open circuit
                with pytest.raises((ValueError, CircuitBreakerOpenError)):
                    await breaker.call(failing_func)
        
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Reset all breakers
        await manager.reset_all()
        
        assert breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_get_open_breakers(self, manager):
        """Test getting list of open circuit breakers"""
        breaker1 = await manager.get_breaker("breaker1", failure_threshold=2)
        breaker2 = await manager.get_breaker("breaker2", failure_threshold=2)
        
        # Force breaker1 to open (need 3 failures for threshold of 2)
        async def failing_func():
            raise ValueError("Test error")
        
        for i in range(3):
            if i < 2:
                with pytest.raises(ValueError):
                    await breaker1.call(failing_func)
            else:
                # 3rd call should open circuit
                with pytest.raises((ValueError, CircuitBreakerOpenError)):
                    await breaker1.call(failing_func)
        
        open_breakers = await manager.get_open_breakers()
        
        assert "breaker1" in open_breakers
        assert "breaker2" not in open_breakers
        assert len(open_breakers) == 1


class TestWithCircuitBreaker:
    """Test with_circuit_breaker convenience function"""
    
    @pytest.mark.asyncio
    async def test_with_circuit_breaker_success(self):
        """Test successful call with convenience function"""
        async def success_func(value):
            return f"success: {value}"
        
        result = await with_circuit_breaker(
            "test_convenience",
            success_func,
            "test_value"
        )
        
        assert result == "success: test_value"
    
    @pytest.mark.asyncio
    async def test_with_circuit_breaker_failure(self):
        """Test failed call with convenience function"""
        async def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            await with_circuit_breaker(
                "test_convenience_fail",
                failing_func
            )


if __name__ == "__main__":
    pytest.main([__file__])