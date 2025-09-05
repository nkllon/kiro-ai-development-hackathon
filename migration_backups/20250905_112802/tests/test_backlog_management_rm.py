"""
Unit tests for BacklogManagementRM

Tests RM compliance, health monitoring, and graceful degradation
as required by task 2 specifications.
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime

from src.beast_mode.backlog.backlog_management_rm import BacklogManagementRM
from src.beast_mode.core.reflective_module import HealthStatus, ReflectiveModule


class TestBacklogManagementRMCompliance:
    """Test RM interface compliance requirements"""
    
    def test_inherits_from_reflective_module(self):
        """Test that BacklogManagementRM inherits from ReflectiveModule"""
        rm = BacklogManagementRM()
        assert isinstance(rm, ReflectiveModule)
        assert rm.module_name == "BacklogManagementRM"
        
    def test_implements_required_rm_methods(self):
        """Test that all required RM interface methods are implemented"""
        rm = BacklogManagementRM()
        
        # Test get_module_status exists and returns dict
        status = rm.get_module_status()
        assert isinstance(status, dict)
        assert "module_name" in status
        assert status["module_name"] == "BacklogManagementRM"
        
        # Test is_healthy exists and returns bool
        health = rm.is_healthy()
        assert isinstance(health, bool)
        
        # Test get_health_indicators exists and returns dict
        indicators = rm.get_health_indicators()
        assert isinstance(indicators, dict)
        assert "health_indicators" in indicators
        assert "overall_health" in indicators
        
    def test_primary_responsibility_defined(self):
        """Test that primary responsibility is clearly defined"""
        rm = BacklogManagementRM()
        responsibility = rm._get_primary_responsibility()
        assert isinstance(responsibility, str)
        assert len(responsibility) > 0
        assert "backlog" in responsibility.lower()
        assert "orchestration" in responsibility.lower()


class TestBacklogManagementRMHealthMonitoring:
    """Test health monitoring and reporting capabilities"""
    
    def test_initial_health_status(self):
        """Test that RM starts in healthy state"""
        rm = BacklogManagementRM()
        assert rm.is_healthy() is True
        
        status = rm.get_module_status()
        assert status["status"] == "healthy"
        assert status["degradation_active"] is False
        
    def test_health_indicators_structure(self):
        """Test health indicators have proper structure"""
        rm = BacklogManagementRM()
        indicators = rm.get_health_indicators()
        
        assert "health_indicators" in indicators
        assert "overall_health" in indicators
        assert "degradation_active" in indicators
        assert "metrics" in indicators
        
        # Check that health indicators have required fields
        for name, indicator in indicators["health_indicators"].items():
            assert "status" in indicator
            assert "value" in indicator
            assert "message" in indicator
            assert "timestamp" in indicator
            assert indicator["status"] in ["healthy", "degraded", "unhealthy", "unknown"]
            
    def test_performance_monitoring(self):
        """Test performance metrics tracking"""
        rm = BacklogManagementRM()
        
        # Initial state
        indicators = rm.get_health_indicators()
        assert "metrics" in indicators
        assert "avg_response_time" in indicators["metrics"]
        
        # Simulate operation timing
        rm._health_monitor.record_operation_time(0.1)  # 100ms operation
        
        indicators = rm.get_health_indicators()
        assert indicators["metrics"]["avg_response_time"] > 0
        
    def test_performance_degradation_detection(self):
        """Test that performance issues are detected"""
        rm = BacklogManagementRM()
        
        # Simulate slow operations
        for _ in range(10):
            rm._health_monitor.record_operation_time(0.6)  # 600ms operations (over 500ms limit)
            
        # Should detect performance issues
        assert rm.is_healthy() is False
        
        indicators = rm.get_health_indicators()
        perf_indicator = indicators["health_indicators"]["performance"]
        assert perf_indicator["status"] in ["degraded", "unhealthy"]
        
    def test_data_consistency_validation(self):
        """Test data consistency checking"""
        rm = BacklogManagementRM()
        
        # Initially should be consistent (empty data)
        assert rm._health_monitor.validate_data_consistency(rm._backlog_items) is True
        
        # Test with invalid data
        rm._backlog_items["test"] = Mock()
        rm._backlog_items["test"].item_id = "different_id"  # Inconsistent
        rm._backlog_items["test"].title = "Test"
        rm._backlog_items["test"].created_by = "test_user"
        
        assert rm._health_monitor.validate_data_consistency(rm._backlog_items) is False
        
    def test_capacity_monitoring(self):
        """Test capacity monitoring and alerting"""
        rm = BacklogManagementRM()
        
        # Simulate high capacity usage
        for i in range(8000):  # 80% of assumed 10k capacity
            rm._backlog_items[f"item_{i}"] = Mock()
            rm._backlog_items[f"item_{i}"].item_id = f"item_{i}"
            rm._backlog_items[f"item_{i}"].title = f"Item {i}"
            rm._backlog_items[f"item_{i}"].created_by = "test_user"
            
        indicators = rm.get_health_indicators()
        capacity_indicator = indicators["health_indicators"]["capacity"]
        assert capacity_indicator["status"] == "degraded"


class TestBacklogManagementRMGracefulDegradation:
    """Test graceful degradation handling"""
    
    def test_graceful_degradation_activation(self):
        """Test graceful degradation can be activated"""
        rm = BacklogManagementRM()
        
        # Initially not in degradation mode
        assert rm._degradation_mode is False
        assert rm.is_healthy() is True
        
        # Activate degradation
        failure_context = {"error": "test_failure", "component": "test"}
        result = rm.degrade_gracefully(failure_context)
        
        assert result.degradation_applied is True
        assert isinstance(result.reduced_functionality, list)
        assert len(result.reduced_functionality) > 0
        assert result.recovery_strategy is not None
        assert result.estimated_recovery_time is not None
        
    def test_degradation_affects_operations(self):
        """Test that degradation mode affects operations"""
        rm = BacklogManagementRM()
        
        # Enable degradation mode
        rm._degradation_mode = True
        
        # Operations should be affected
        with pytest.raises(RuntimeError, match="unavailable during degradation"):
            rm.create_backlog_item(Mock())
            
        with pytest.raises(RuntimeError, match="unavailable during degradation"):
            rm.mark_beast_ready("test_id", Mock())
            
    def test_degradation_status_reporting(self):
        """Test that degradation status is properly reported"""
        rm = BacklogManagementRM()
        
        # Normal state
        status = rm.get_module_status()
        assert status["degradation_active"] is False
        assert status["status"] == "healthy"
        
        # Degraded state
        rm._degradation_mode = True
        status = rm.get_module_status()
        assert status["degradation_active"] is True
        assert status["status"] == "degraded"
        
        indicators = rm.get_health_indicators()
        assert indicators["degradation_active"] is True
        
    def test_operational_capabilities_during_degradation(self):
        """Test operational capabilities change during degradation"""
        rm = BacklogManagementRM()
        
        # Normal capabilities
        status = rm.get_module_status()
        normal_capabilities = status["operational_capabilities"]
        assert "backlog_item_management" in normal_capabilities
        assert "beast_readiness_validation" in normal_capabilities
        
        # Degraded capabilities
        rm._degradation_mode = True
        status = rm.get_module_status()
        degraded_capabilities = status["operational_capabilities"]
        assert "graceful_degradation_active" in degraded_capabilities
        assert "beast_readiness_validation" not in degraded_capabilities


class TestBacklogManagementRMOperationalVisibility:
    """Test operational visibility requirements (R6.4)"""
    
    def test_module_status_completeness(self):
        """Test that module status provides complete operational information"""
        rm = BacklogManagementRM()
        status = rm.get_module_status()
        
        # Required fields for external systems
        required_fields = [
            "module_name", "status", "uptime_seconds", "total_backlog_items",
            "beast_ready_items", "degradation_active", "last_operation_timestamp",
            "avg_response_time_ms", "tracks_managed", "operational_capabilities"
        ]
        
        for field in required_fields:
            assert field in status, f"Missing required field: {field}"
            
    def test_status_accuracy_over_time(self):
        """Test that status remains accurate over time"""
        rm = BacklogManagementRM()
        
        # Initial status
        status1 = rm.get_module_status()
        initial_uptime = status1["uptime_seconds"]
        
        # Wait a bit
        time.sleep(0.1)
        
        # Status should update
        status2 = rm.get_module_status()
        updated_uptime = status2["uptime_seconds"]
        
        assert updated_uptime > initial_uptime
        
    def test_tracks_managed_reporting(self):
        """Test that managed tracks are properly reported"""
        rm = BacklogManagementRM()
        
        # Initially no tracks
        status = rm.get_module_status()
        assert status["tracks_managed"] == []
        
        # Add mock items with different tracks
        from src.beast_mode.backlog.enums import StrategicTrack
        
        item1 = Mock()
        item1.track = StrategicTrack.PR_GATE
        item2 = Mock()
        item2.track = StrategicTrack.COMMUNITY
        
        rm._backlog_items["item1"] = item1
        rm._backlog_items["item2"] = item2
        
        status = rm.get_module_status()
        tracks = status["tracks_managed"]
        assert "pr_gate" in tracks
        assert "community" in tracks
        assert len(tracks) == 2


class TestBacklogManagementRMBoundaryCompliance:
    """Test single responsibility and boundary compliance (R6.5)"""
    
    def test_single_responsibility_score(self):
        """Test single responsibility adherence scoring"""
        rm = BacklogManagementRM()
        
        responsibility_info = rm.maintain_single_responsibility()
        
        assert "module_name" in responsibility_info
        assert "primary_responsibility" in responsibility_info
        assert "boundary_violations" in responsibility_info
        assert "single_responsibility_score" in responsibility_info
        
        # Score should be between 0.0 and 1.0
        score = responsibility_info["single_responsibility_score"]
        assert 0.0 <= score <= 1.0
        
    def test_boundary_violation_detection(self):
        """Test boundary violation detection"""
        rm = BacklogManagementRM()
        
        violations = rm._check_boundary_violations()
        assert isinstance(violations, list)
        
        # Initially should have no violations
        assert len(violations) == 0
        
    def test_responsibility_clarity(self):
        """Test that responsibility is clearly defined and focused"""
        rm = BacklogManagementRM()
        
        responsibility = rm._get_primary_responsibility()
        
        # Should be specific to backlog management
        assert "backlog" in responsibility.lower()
        # Should indicate orchestration role
        assert "orchestration" in responsibility.lower()
        # Should mention RM compliance
        assert "compliance" in responsibility.lower()


class TestBacklogManagementRMErrorHandling:
    """Test error handling and recovery"""
    
    def test_health_check_exception_handling(self):
        """Test that health check handles exceptions gracefully"""
        rm = BacklogManagementRM()
        
        # Mock a method to raise exception
        with patch.object(rm._health_monitor, 'validate_data_consistency', side_effect=Exception("Test error")):
            # Should not crash, should return False
            health = rm.is_healthy()
            assert health is False
            
    def test_operation_timing_exception_handling(self):
        """Test that operation timing handles exceptions"""
        rm = BacklogManagementRM()
        
        # Should not crash when recording invalid times
        rm._health_monitor.record_operation_time(-1.0)  # Invalid time
        rm._health_monitor.record_operation_time(float('inf'))  # Invalid time
        
        # Should still be able to get metrics
        indicators = rm.get_health_indicators()
        assert "metrics" in indicators
        
    def test_status_reporting_resilience(self):
        """Test that status reporting is resilient to data issues"""
        rm = BacklogManagementRM()
        
        # Add invalid data
        rm._backlog_items["invalid"] = None
        
        # Should still be able to report status
        status = rm.get_module_status()
        assert isinstance(status, dict)
        assert "module_name" in status


if __name__ == "__main__":
    pytest.main([__file__])