"""
Unit tests for Doctor Status Manager

Tests status management, cost tracking, budget enforcement,
and feature flag integration.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import os

from src.beast_mode.observatory.ai_consultation.doctor_status_manager import (
    DoctorStatusManager,
    StatusTransition,
    StatusChangeEvent,
    status_manager,
    get_doctor_status,
    initialize_status_manager,
    cleanup_status_manager
)
from src.beast_mode.observatory.ai_consultation.models import (
    DoctorStatus, DoctorStatusReason, BudgetStatus, CostAnalytics
)
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.exceptions import ConsultationError


class TestDoctorStatusManager:
    """Test DoctorStatusManager class"""
    
    @pytest.fixture
    async def status_manager_instance(self):
        """Create a test status manager instance"""
        manager = DoctorStatusManager(
            daily_budget=10.0,
            monthly_budget=100.0,
            cost_per_token=0.0001,
            warning_threshold=0.8,
            critical_threshold=0.95
        )
        
        # Mock database operations
        with patch('src.beast_mode.observatory.ai_consultation.doctor_status_manager.db_manager') as mock_db:
            mock_db.execute_query = AsyncMock(return_value=[])
            mock_db.execute_update = AsyncMock(return_value=1)
            
            # Enable feature flags for testing
            await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, True)
            await feature_flags.set_flag(FeatureFlag.COST_TRACKING.value, True)
            await feature_flags.set_flag(FeatureFlag.BUDGET_ENFORCEMENT.value, True)
            
            yield manager
    
    @pytest.mark.asyncio
    async def test_initialization(self, status_manager_instance):
        """Test status manager initialization"""
        await status_manager_instance.initialize()
        
        status = await status_manager_instance.get_status()
        assert isinstance(status, DoctorStatus)
        assert status.daily_usage == 0.0
        assert status.monthly_usage == 0.0
        assert status.cost_budget_remaining == 10.0
    
    @pytest.mark.asyncio
    async def test_manual_status_control(self, status_manager_instance):
        """Test manual status enable/disable"""
        await status_manager_instance.initialize()
        
        # Enable manually
        status = await status_manager_instance.set_status_manual(True, "test_user")
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.MANUAL
        
        # Disable manually
        status = await status_manager_instance.set_status_manual(False, "test_user")
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.MANUAL
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self, status_manager_instance):
        """Test cost tracking functionality"""
        await status_manager_instance.initialize()
        
        # Track some costs
        await status_manager_instance.track_cost("session1", 1000, 0.10)
        await status_manager_instance.track_cost("session1", 500, 0.05)
        await status_manager_instance.track_cost("session2", 2000, 0.20)
        
        # Check session costs
        session1_cost = await status_manager_instance.get_session_cost("session1")
        session2_cost = await status_manager_instance.get_session_cost("session2")
        
        assert session1_cost == 0.15
        assert session2_cost == 0.20
        
        # Check budget status
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_spent == 0.35
        assert budget_status.monthly_spent == 0.35
    
    @pytest.mark.asyncio
    async def test_budget_enforcement(self, status_manager_instance):
        """Test budget limit enforcement"""
        await status_manager_instance.initialize()
        
        # Set status to available
        await status_manager_instance.set_status_manual(True, "test_user")
        
        # Exhaust daily budget
        await status_manager_instance.track_cost("expensive_session", 100000, 10.0)
        
        # Status should automatically become unavailable
        status = await status_manager_instance.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.BUDGET_EXHAUSTED
    
    @pytest.mark.asyncio
    async def test_budget_status_calculation(self, status_manager_instance):
        """Test budget status calculations"""
        await status_manager_instance.initialize()
        
        # Track some usage
        await status_manager_instance.track_cost("session1", 5000, 5.0)  # 50% of daily budget
        
        budget_status = await status_manager_instance.get_budget_status()
        
        assert budget_status.daily_budget == 10.0
        assert budget_status.monthly_budget == 100.0
        assert budget_status.daily_spent == 5.0
        assert budget_status.daily_remaining == 5.0
        assert budget_status.daily_percentage == 0.5
        assert budget_status.daily_warning is False  # Below 80% threshold
        assert budget_status.daily_critical is False  # Below 95% threshold
        assert budget_status.daily_exhausted is False
        
        # Track more usage to trigger warning
        await status_manager_instance.track_cost("session2", 3000, 3.0)  # Total 80%
        
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_warning is True
        assert budget_status.daily_critical is False
        
        # Track more to trigger critical
        await status_manager_instance.track_cost("session3", 1500, 1.5)  # Total 95%
        
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_critical is True
        assert budget_status.daily_exhausted is False
        
        # Exhaust budget
        await status_manager_instance.track_cost("session4", 1000, 1.0)  # Total 105%
        
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_exhausted is True
    
    @pytest.mark.asyncio
    async def test_feature_flag_integration(self, status_manager_instance):
        """Test feature flag integration"""
        await status_manager_instance.initialize()
        
        # Disable status management
        await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, False)
        
        # Status should become unavailable
        status = await status_manager_instance.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.FEATURE_DISABLED
        
        # Try to enable manually (should fail)
        with pytest.raises(ConsultationError) as exc_info:
            await status_manager_instance.set_status_manual(True, "test_user")
        assert "Manual status control is disabled" in str(exc_info.value)
        
        # Re-enable feature flag
        await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, True)
        
        # Should be able to control manually again
        status = await status_manager_instance.set_status_manual(True, "test_user")
        assert status.is_available is True
    
    @pytest.mark.asyncio
    async def test_cost_tracking_feature_flag(self, status_manager_instance):
        """Test cost tracking with feature flag disabled"""
        await status_manager_instance.initialize()
        
        # Disable cost tracking
        await feature_flags.set_flag(FeatureFlag.COST_TRACKING.value, False)
        
        # Track cost (should be ignored)
        await status_manager_instance.track_cost("session1", 1000, 1.0)
        
        # Cost should not be tracked
        session_cost = await status_manager_instance.get_session_cost("session1")
        assert session_cost == 0.0
        
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_spent == 0.0
    
    @pytest.mark.asyncio
    async def test_budget_enforcement_feature_flag(self, status_manager_instance):
        """Test budget enforcement with feature flag disabled"""
        await status_manager_instance.initialize()
        
        # Set status to available
        await status_manager_instance.set_status_manual(True, "test_user")
        
        # Disable budget enforcement
        await feature_flags.set_flag(FeatureFlag.BUDGET_ENFORCEMENT.value, False)
        
        # Exhaust budget
        await status_manager_instance.track_cost("expensive_session", 100000, 15.0)
        
        # Status should remain available (enforcement disabled)
        status = await status_manager_instance.get_status()
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.MANUAL
    
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, status_manager_instance):
        """Test system health monitoring"""
        await status_manager_instance.initialize()
        
        # Set status to available
        await status_manager_instance.set_status_manual(True, "test_user")
        
        # Set system unhealthy
        await status_manager_instance.set_system_health(False, "Database connection failed")
        
        # Status should become unavailable
        status = await status_manager_instance.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.SYSTEM_ERROR
        
        # Restore system health
        await status_manager_instance.set_system_health(True)
        
        # Status should become available again (automatic recovery)
        status = await status_manager_instance.get_status()
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.AUTOMATIC
    
    @pytest.mark.asyncio
    async def test_status_change_listeners(self, status_manager_instance):
        """Test status change event listeners"""
        await status_manager_instance.initialize()
        
        events = []
        
        def status_listener(event: StatusChangeEvent):
            events.append(event)
        
        # Add listener
        status_manager_instance.add_status_listener(status_listener)
        
        # Change status
        await status_manager_instance.set_status_manual(True, "test_user")
        await status_manager_instance.set_status_manual(False, "test_user")
        
        # Check events
        assert len(events) == 2
        
        assert events[0].old_status is False
        assert events[0].new_status is True
        assert events[0].transition_type == StatusTransition.MANUAL_ENABLE
        assert events[0].triggered_by == "test_user"
        
        assert events[1].old_status is True
        assert events[1].new_status is False
        assert events[1].transition_type == StatusTransition.MANUAL_DISABLE
        assert events[1].triggered_by == "test_user"
        
        # Remove listener
        status_manager_instance.remove_status_listener(status_listener)
        
        # Change status again
        await status_manager_instance.set_status_manual(True, "test_user")
        
        # No new events should be recorded
        assert len(events) == 2
    
    @pytest.mark.asyncio
    async def test_session_and_queue_tracking(self, status_manager_instance):
        """Test session and queue tracking"""
        await status_manager_instance.initialize()
        
        # Update session count
        await status_manager_instance.update_session_count(5)
        
        # Update queue length
        await status_manager_instance.update_queue_length(10)
        
        # Check status reflects updates
        status = await status_manager_instance.get_status()
        assert status.active_sessions == 5
        assert status.queue_length == 10
    
    @pytest.mark.asyncio
    async def test_daily_budget_reset(self, status_manager_instance):
        """Test daily budget reset functionality"""
        await status_manager_instance.initialize()
        
        # Track some usage
        await status_manager_instance.track_cost("session1", 5000, 5.0)
        
        # Verify usage is tracked
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_spent == 5.0
        
        # Reset daily budget
        await status_manager_instance.reset_daily_budget()
        
        # Verify usage is reset
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_spent == 0.0
        
        # Session costs should be cleared
        session_cost = await status_manager_instance.get_session_cost("session1")
        assert session_cost == 0.0
    
    @pytest.mark.asyncio
    async def test_cost_analytics(self, status_manager_instance):
        """Test cost analytics generation"""
        await status_manager_instance.initialize()
        
        # Mock database results for analytics
        mock_results = [
            {'date': '2024-01-01', 'daily_cost': 2.0, 'daily_tokens': 2000, 'daily_queries': 10},
            {'date': '2024-01-02', 'daily_cost': 3.0, 'daily_tokens': 3000, 'daily_queries': 15},
            {'date': '2024-01-03', 'daily_cost': 1.5, 'daily_tokens': 1500, 'daily_queries': 8},
        ]
        
        with patch('src.beast_mode.observatory.ai_consultation.doctor_status_manager.db_manager') as mock_db:
            mock_db.execute_query = AsyncMock(return_value=mock_results)
            
            analytics = await status_manager_instance.get_cost_analytics(30)
            
            assert analytics.period_days == 30
            assert analytics.total_cost == 6.5
            assert analytics.total_tokens == 6500
            assert analytics.total_queries == 33
            assert analytics.avg_cost_per_query == 6.5 / 33
            assert analytics.avg_cost_per_token == 6.5 / 6500
            assert len(analytics.daily_costs) == 3
    
    @pytest.mark.asyncio
    async def test_error_handling(self, status_manager_instance):
        """Test error handling in various scenarios"""
        # Test initialization with database error
        with patch('src.beast_mode.observatory.ai_consultation.doctor_status_manager.db_manager') as mock_db:
            mock_db.execute_query = AsyncMock(side_effect=Exception("Database error"))
            
            # Should not raise, but create default status
            await status_manager_instance.initialize()
            
            status = await status_manager_instance.get_status()
            assert status.reason == DoctorStatusReason.SYSTEM_ERROR
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, status_manager_instance):
        """Test concurrent status operations"""
        await status_manager_instance.initialize()
        
        # Run multiple operations concurrently
        tasks = [
            status_manager_instance.track_cost(f"session{i}", 1000, 0.1)
            for i in range(10)
        ]
        
        await asyncio.gather(*tasks)
        
        # Check final state
        budget_status = await status_manager_instance.get_budget_status()
        assert budget_status.daily_spent == 1.0  # 10 * 0.1


class TestGlobalStatusManager:
    """Test global status manager functions"""
    
    @pytest.mark.asyncio
    async def test_global_functions(self):
        """Test global status manager functions"""
        with patch('src.beast_mode.observatory.ai_consultation.doctor_status_manager.status_manager') as mock_manager:
            mock_status = DoctorStatus(
                is_available=True,
                reason=DoctorStatusReason.MANUAL,
                cost_budget_remaining=10.0,
                daily_usage=0.0,
                monthly_usage=0.0,
                last_updated=datetime.utcnow(),
                active_sessions=0,
                queue_length=0
            )
            
            mock_manager.get_status = AsyncMock(return_value=mock_status)
            mock_manager.initialize = AsyncMock()
            mock_manager.cleanup = AsyncMock()
            
            # Test get_doctor_status
            status = await get_doctor_status()
            assert status.is_available is True
            mock_manager.get_status.assert_called_once()
            
            # Test initialize_status_manager
            await initialize_status_manager()
            mock_manager.initialize.assert_called_once()
            
            # Test cleanup_status_manager
            await cleanup_status_manager()
            mock_manager.cleanup.assert_called_once()


class TestStatusTransitions:
    """Test status transition logic"""
    
    @pytest.fixture
    async def manager_with_mocked_db(self):
        """Create manager with mocked database"""
        manager = DoctorStatusManager(daily_budget=10.0, monthly_budget=100.0)
        
        with patch('src.beast_mode.observatory.ai_consultation.doctor_status_manager.db_manager') as mock_db:
            mock_db.execute_query = AsyncMock(return_value=[])
            mock_db.execute_update = AsyncMock(return_value=1)
            
            await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, True)
            await feature_flags.set_flag(FeatureFlag.BUDGET_ENFORCEMENT.value, True)
            
            yield manager
    
    @pytest.mark.asyncio
    async def test_automatic_recovery_from_budget_exhaustion(self, manager_with_mocked_db):
        """Test automatic recovery when budget is restored"""
        await manager_with_mocked_db.initialize()
        
        # Exhaust budget
        await manager_with_mocked_db.track_cost("expensive", 100000, 15.0)
        
        status = await manager_with_mocked_db.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.BUDGET_EXHAUSTED
        
        # Reset budget
        await manager_with_mocked_db.reset_daily_budget()
        
        # Should automatically recover
        status = await manager_with_mocked_db.get_status()
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.AUTOMATIC
    
    @pytest.mark.asyncio
    async def test_manual_override_preserved(self, manager_with_mocked_db):
        """Test that manual status is preserved during evaluations"""
        await manager_with_mocked_db.initialize()
        
        # Set manual status
        await manager_with_mocked_db.set_status_manual(False, "admin")
        
        # Trigger status evaluation (should not change manual status)
        await manager_with_mocked_db.update_session_count(5)
        
        status = await manager_with_mocked_db.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.MANUAL


if __name__ == "__main__":
    pytest.main([__file__])