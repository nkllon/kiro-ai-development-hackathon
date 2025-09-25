"""
Integration tests for Doctor Status Manager

Tests the integration between DoctorStatusManager, database, and feature flags.
"""

import pytest
import asyncio
import tempfile
import os
from datetime import datetime, timedelta

from src.beast_mode.observatory.ai_consultation.doctor_status_manager import DoctorStatusManager
from src.beast_mode.observatory.ai_consultation.database import DatabaseManager
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.models import DoctorStatusReason


class TestDoctorStatusIntegration:
    """Integration tests for doctor status management"""
    
    @pytest.fixture
    async def integrated_system(self):
        """Set up integrated system with real database"""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Initialize database
            db_manager = DatabaseManager(database_path=db_path)
            await feature_flags.set_flag(FeatureFlag.RESULTS_STORAGE.value, True)
            await db_manager.initialize()
            
            # Create status manager
            status_manager = DoctorStatusManager(
                daily_budget=10.0,
                monthly_budget=100.0,
                cost_per_token=0.0001
            )
            
            # Enable feature flags
            await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, True)
            await feature_flags.set_flag(FeatureFlag.COST_TRACKING.value, True)
            await feature_flags.set_flag(FeatureFlag.BUDGET_ENFORCEMENT.value, True)
            
            # Initialize status manager
            await status_manager.initialize()
            
            yield {
                'status_manager': status_manager,
                'db_manager': db_manager,
                'db_path': db_path
            }
            
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_status_persistence(self, integrated_system):
        """Test that status changes are persisted to database"""
        status_manager = integrated_system['status_manager']
        db_manager = integrated_system['db_manager']
        
        # Set status manually
        await status_manager.set_status_manual(True, "test_user")
        
        # Verify status is persisted
        results = await db_manager.execute_query(
            "SELECT * FROM ai_consultation_doctor_status ORDER BY last_updated DESC LIMIT 1"
        )
        
        assert len(results) > 0
        latest_status = results[0]
        assert latest_status['is_available'] == 1  # SQLite stores boolean as int
        assert latest_status['reason'] == 'manual'
    
    @pytest.mark.asyncio
    async def test_cost_tracking_with_database(self, integrated_system):
        """Test cost tracking with real database operations"""
        status_manager = integrated_system['status_manager']
        db_manager = integrated_system['db_manager']
        
        # Track some costs
        await status_manager.track_cost("session1", 1000, 1.0)
        await status_manager.track_cost("session2", 2000, 2.0)
        
        # Verify budget is updated in database
        results = await db_manager.execute_query(
            "SELECT * FROM ai_consultation_budget ORDER BY date DESC LIMIT 1"
        )
        
        assert len(results) > 0
        budget_data = results[0]
        assert budget_data['daily_spent'] == 3.0
        assert budget_data['monthly_spent'] == 3.0
    
    @pytest.mark.asyncio
    async def test_budget_enforcement_integration(self, integrated_system):
        """Test budget enforcement with database and feature flags"""
        status_manager = integrated_system['status_manager']
        
        # Set status to available
        await status_manager.set_status_manual(True, "test_user")
        
        # Exhaust budget
        await status_manager.track_cost("expensive_session", 100000, 15.0)
        
        # Status should automatically become unavailable
        status = await status_manager.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.BUDGET_EXHAUSTED
        
        # Verify this is persisted
        db_manager = integrated_system['db_manager']
        results = await db_manager.execute_query(
            "SELECT * FROM ai_consultation_doctor_status ORDER BY last_updated DESC LIMIT 1"
        )
        
        latest_status = results[0]
        assert latest_status['is_available'] == 0
        assert latest_status['reason'] == 'budget_exhausted'
    
    @pytest.mark.asyncio
    async def test_feature_flag_integration(self, integrated_system):
        """Test feature flag integration affects status"""
        status_manager = integrated_system['status_manager']
        
        # Disable status management
        await feature_flags.set_flag(FeatureFlag.DOCTOR_STATUS_MANAGEMENT.value, False)
        
        # Status should become unavailable
        status = await status_manager.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.FEATURE_DISABLED
    
    @pytest.mark.asyncio
    async def test_status_recovery_after_budget_reset(self, integrated_system):
        """Test automatic status recovery after budget reset"""
        status_manager = integrated_system['status_manager']
        
        # Set initial status
        await status_manager.set_status_manual(True, "test_user")
        
        # Exhaust budget
        await status_manager.track_cost("expensive", 100000, 15.0)
        
        # Verify status is unavailable
        status = await status_manager.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.BUDGET_EXHAUSTED
        
        # Reset budget
        await status_manager.reset_daily_budget()
        
        # Status should automatically recover
        status = await status_manager.get_status()
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.AUTOMATIC
    
    @pytest.mark.asyncio
    async def test_concurrent_cost_tracking(self, integrated_system):
        """Test concurrent cost tracking operations"""
        status_manager = integrated_system['status_manager']
        
        # Run multiple cost tracking operations concurrently
        tasks = []
        for i in range(10):
            task = status_manager.track_cost(f"session_{i}", 1000, 0.1)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Verify final budget state
        budget_status = await status_manager.get_budget_status()
        assert budget_status.daily_spent == 1.0  # 10 * 0.1
        assert budget_status.monthly_spent == 1.0
    
    @pytest.mark.asyncio
    async def test_status_history_tracking(self, integrated_system):
        """Test that status changes create history records"""
        status_manager = integrated_system['status_manager']
        db_manager = integrated_system['db_manager']
        
        # Make several status changes
        await status_manager.set_status_manual(True, "user1")
        await status_manager.set_status_manual(False, "user2")
        await status_manager.set_status_manual(True, "user3")
        
        # Check that multiple records exist
        results = await db_manager.execute_query(
            "SELECT * FROM ai_consultation_doctor_status ORDER BY last_updated"
        )
        
        # Should have at least 4 records (initial + 3 changes)
        assert len(results) >= 4
        
        # Verify the sequence
        assert results[-3]['reason'] == 'manual'  # First manual change
        assert results[-2]['reason'] == 'manual'  # Second manual change  
        assert results[-1]['reason'] == 'manual'  # Third manual change
    
    @pytest.mark.asyncio
    async def test_system_health_integration(self, integrated_system):
        """Test system health monitoring integration"""
        status_manager = integrated_system['status_manager']
        
        # Set initial available status
        await status_manager.set_status_manual(True, "admin")
        
        # Simulate system health issue
        await status_manager.set_system_health(False, "Database connection lost")
        
        # Status should become unavailable
        status = await status_manager.get_status()
        assert status.is_available is False
        assert status.reason == DoctorStatusReason.SYSTEM_ERROR
        
        # Restore system health
        await status_manager.set_system_health(True)
        
        # Should automatically recover
        status = await status_manager.get_status()
        assert status.is_available is True
        assert status.reason == DoctorStatusReason.AUTOMATIC


if __name__ == "__main__":
    pytest.main([__file__])