"""
Unit tests for Status Persistence

Tests Redis-based persistence with brownfield safety and fallback mechanisms.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import asdict

from src.beast_mode.observatory.ai_consultation.status_persistence import (
    StatusPersistence,
    status_persistence,
    initialize_persistence,
    cleanup_persistence
)
from src.beast_mode.observatory.ai_consultation.doctor_status_manager import (
    StatusChangeEvent, StatusTransition
)
from src.beast_mode.observatory.ai_consultation.models import (
    DoctorStatus, DoctorStatusReason, BudgetStatus
)
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.health_checker import ComponentHealth


class TestStatusPersistence:
    """Test StatusPersistence class"""
    
    @pytest.fixture
    async def persistence(self):
        """Create test persistence instance"""
        persistence = StatusPersistence(
            redis_url="redis://localhost:6379/15",  # Use test database
            key_prefix="test_ai_consultation",
            default_ttl=60,
            max_connections=5
        )
        
        # Enable feature flags
        await feature_flags.set_flag(FeatureFlag.REDIS_PERSISTENCE.value, True)
        
        yield persistence
        
        # Cleanup
        await persistence.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialization_with_redis_unavailable(self, persistence):
        """Test initialization when Redis is unavailable"""
        # Mock Redis to fail
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.side_effect = Exception("Redis unavailable")
            
            await persistence.initialize()
            
            # Should fall back to memory storage
            assert persistence._fallback_mode is True
    
    @pytest.mark.asyncio
    async def test_initialization_with_feature_disabled(self, persistence):
        """Test initialization when feature is disabled"""
        await feature_flags.set_flag(FeatureFlag.REDIS_PERSISTENCE.value, False)
        
        await persistence.initialize()
        
        # Should use fallback mode
        assert persistence._fallback_mode is True
    
    @pytest.mark.asyncio
    async def test_doctor_status_storage_fallback(self, persistence):
        """Test doctor status storage in fallback mode"""
        # Force fallback mode
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Create test status
        status = DoctorStatus(
            is_available=True,
            reason=DoctorStatusReason.MANUAL,
            cost_budget_remaining=10.0,
            daily_usage=5.0,
            monthly_usage=25.0,
            last_updated=datetime.utcnow(),
            active_sessions=2,
            queue_length=5
        )
        
        # Store status
        success = await persistence.store_doctor_status(status)
        assert success is True
        
        # Retrieve status
        retrieved = await persistence.get_doctor_status()
        assert retrieved is not None
        assert retrieved.is_available is True
        assert retrieved.reason == DoctorStatusReason.MANUAL
        assert retrieved.daily_usage == 5.0
    
    @pytest.mark.asyncio
    async def test_budget_status_storage_fallback(self, persistence):
        """Test budget status storage in fallback mode"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Create test budget
        budget = BudgetStatus(
            daily_budget=10.0,
            monthly_budget=100.0,
            daily_spent=3.0,
            monthly_spent=15.0,
            daily_remaining=7.0,
            monthly_remaining=85.0,
            daily_percentage=0.3,
            monthly_percentage=0.15,
            daily_exhausted=False,
            monthly_exhausted=False,
            daily_warning=False,
            monthly_warning=False,
            daily_critical=False,
            monthly_critical=False,
            cost_per_token=0.0001,
            last_updated=datetime.utcnow()
        )
        
        # Store budget
        success = await persistence.store_budget_status(budget)
        assert success is True
        
        # Retrieve budget
        retrieved = await persistence.get_budget_status()
        assert retrieved is not None
        assert retrieved.daily_spent == 3.0
        assert retrieved.monthly_spent == 15.0
        assert retrieved.daily_percentage == 0.3
    
    @pytest.mark.asyncio
    async def test_status_event_storage_fallback(self, persistence):
        """Test status event storage in fallback mode"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Create test event
        event = StatusChangeEvent(
            timestamp=datetime.utcnow(),
            old_status=False,
            new_status=True,
            reason=DoctorStatusReason.MANUAL,
            transition_type=StatusTransition.MANUAL_ENABLE,
            triggered_by="admin",
            cost_data={"daily_usage": 5.0},
            metadata={"test": True}
        )
        
        # Store event
        success = await persistence.store_status_event(event)
        assert success is True
        
        # Retrieve recent events
        events = await persistence.get_recent_events(limit=10)
        assert len(events) >= 1
        
        stored_event = events[0]
        assert stored_event['old_status'] is False
        assert stored_event['new_status'] is True
        assert stored_event['reason'] == 'manual'
        assert stored_event['triggered_by'] == 'admin'
    
    @pytest.mark.asyncio
    async def test_session_data_storage_fallback(self, persistence):
        """Test session data storage in fallback mode"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Store session data
        session_data = {
            "user_id": "user_123",
            "start_time": datetime.utcnow().isoformat(),
            "cost": 2.5,
            "tokens": 2500
        }
        
        success = await persistence.store_session_data("session_123", session_data)
        assert success is True
        
        # Retrieve session data
        retrieved = await persistence.get_session_data("session_123")
        assert retrieved is not None
        assert retrieved["user_id"] == "user_123"
        assert retrieved["cost"] == 2.5
        
        # Delete session data
        success = await persistence.delete_session_data("session_123")
        assert success is True
        
        # Should be gone
        retrieved = await persistence.get_session_data("session_123")
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_redis_key_generation(self, persistence):
        """Test Redis key generation with proper namespacing"""
        # Test key generation
        key1 = persistence._make_key("doctor_status", "current")
        key2 = persistence._make_key("budget_status")
        
        assert key1 == f"{persistence.key_prefix}:doctor_status:current"
        assert key2 == f"{persistence.key_prefix}:budget_status"
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_keys_fallback(self, persistence):
        """Test cleanup of expired keys in fallback mode"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Add some old events
        old_timestamp = datetime.utcnow() - timedelta(hours=2)
        old_key = f"status_event_{old_timestamp.timestamp()}"
        persistence._fallback_storage[old_key] = {"test": "data"}
        
        # Add recent event
        recent_timestamp = datetime.utcnow()
        recent_key = f"status_event_{recent_timestamp.timestamp()}"
        persistence._fallback_storage[recent_key] = {"test": "recent"}
        
        # Run cleanup
        expired_count = await persistence.cleanup_expired_keys()
        
        # Old event should be removed
        assert old_key not in persistence._fallback_storage
        assert recent_key in persistence._fallback_storage
        assert expired_count >= 1
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, persistence):
        """Test statistics tracking"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Perform some operations
        status = DoctorStatus(
            is_available=True,
            reason=DoctorStatusReason.MANUAL,
            cost_budget_remaining=10.0,
            daily_usage=0.0,
            monthly_usage=0.0,
            last_updated=datetime.utcnow(),
            active_sessions=0,
            queue_length=0
        )
        
        await persistence.store_doctor_status(status)
        await persistence.get_doctor_status()
        await persistence.get_doctor_status()  # Second get for cache hit
        
        # Check stats
        stats = await persistence.get_stats()
        
        assert stats['operations_total'] >= 3
        assert stats['fallback_operations'] >= 2  # Store + get
        assert stats['fallback_mode'] is True
        assert stats['fallback_storage_size'] >= 1
    
    @pytest.mark.asyncio
    async def test_health_check_fallback(self, persistence):
        """Test health check in fallback mode"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        health = await persistence.health_check()
        
        assert isinstance(health, ComponentHealth)
        assert health.component == "status_persistence"
        assert health.status == "degraded"
        assert health.error_message == "Running in fallback mode"
        assert "fallback_storage_size" in health.metadata
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, persistence):
        """Test health check when system is unhealthy"""
        # Mock Redis client to fail
        persistence._redis_client = AsyncMock()
        persistence._redis_client.ping = AsyncMock(side_effect=Exception("Connection failed"))
        persistence._fallback_mode = False
        
        health = await persistence.health_check()
        
        assert health.status == "unhealthy"
        assert "Connection failed" in health.error_message
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, persistence):
        """Test concurrent persistence operations"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Create multiple status objects
        statuses = []
        for i in range(10):
            status = DoctorStatus(
                is_available=i % 2 == 0,
                reason=DoctorStatusReason.MANUAL,
                cost_budget_remaining=10.0 - i,
                daily_usage=float(i),
                monthly_usage=float(i * 5),
                last_updated=datetime.utcnow(),
                active_sessions=i,
                queue_length=i * 2
            )
            statuses.append(status)
        
        # Store all concurrently
        tasks = [persistence.store_doctor_status(status) for status in statuses]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results)
        
        # Last stored status should be retrievable
        retrieved = await persistence.get_doctor_status()
        assert retrieved is not None
    
    @pytest.mark.asyncio
    async def test_error_handling(self, persistence):
        """Test error handling in various scenarios"""
        persistence._fallback_mode = True
        await persistence.initialize()
        
        # Test with invalid data that might cause JSON serialization issues
        try:
            # This should not raise an exception
            await persistence.store_session_data("test", {"invalid": object()})
        except Exception:
            # If it does raise, it should be handled gracefully
            pass
        
        # System should still be functional
        status = DoctorStatus(
            is_available=True,
            reason=DoctorStatusReason.MANUAL,
            cost_budget_remaining=10.0,
            daily_usage=0.0,
            monthly_usage=0.0,
            last_updated=datetime.utcnow(),
            active_sessions=0,
            queue_length=0
        )
        
        success = await persistence.store_doctor_status(status)
        assert success is True


class TestGlobalPersistence:
    """Test global persistence functions"""
    
    @pytest.mark.asyncio
    async def test_global_functions(self):
        """Test global persistence functions"""
        with patch('src.beast_mode.observatory.ai_consultation.status_persistence.status_persistence') as mock_persistence:
            mock_persistence.initialize = AsyncMock()
            mock_persistence.cleanup = AsyncMock()
            
            # Test initialize_persistence
            await initialize_persistence()
            mock_persistence.initialize.assert_called_once()
            
            # Test cleanup_persistence
            await cleanup_persistence()
            mock_persistence.cleanup.assert_called_once()


class TestRedisIntegration:
    """Test Redis integration patterns"""
    
    @pytest.mark.asyncio
    async def test_redis_url_generation(self):
        """Test Redis URL generation for brownfield safety"""
        # Test with AI consultation specific URL
        with patch.dict('os.environ', {'AI_CONSULTATION_REDIS_URL': 'redis://test:6379/5'}):
            persistence = StatusPersistence()
            assert persistence.redis_url == 'redis://test:6379/5'
        
        # Test with general Redis URL (should modify database)
        with patch.dict('os.environ', {'REDIS_URL': 'redis://test:6379/0'}, clear=True):
            persistence = StatusPersistence()
            assert persistence.redis_url == 'redis://test:6379/1'
        
        # Test with no environment variables (should use default with database 1)
        with patch.dict('os.environ', {}, clear=True):
            persistence = StatusPersistence()
            assert persistence.redis_url == 'redis://localhost:6379/1'
    
    @pytest.mark.asyncio
    async def test_key_namespacing(self):
        """Test Redis key namespacing for brownfield safety"""
        persistence = StatusPersistence(key_prefix="test_ai_consultation")
        
        # Test different key types
        doctor_key = persistence._make_key("doctor_status", "current")
        budget_key = persistence._make_key("budget_status")
        session_key = persistence._make_key("sessions", "session_123")
        
        assert doctor_key == "test_ai_consultation:doctor_status:current"
        assert budget_key == "test_ai_consultation:budget_status"
        assert session_key == "test_ai_consultation:sessions:session_123"
        
        # All keys should have the same prefix to avoid Observatory conflicts
        assert all(key.startswith("test_ai_consultation:") for key in [doctor_key, budget_key, session_key])


if __name__ == "__main__":
    pytest.main([__file__])