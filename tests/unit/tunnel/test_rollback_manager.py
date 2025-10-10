"""
Unit tests for RollbackManager
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta

from src.beast_mode.observatory.tunnel.rollback_manager import RollbackManager, RollbackPlan


class TestRollbackManager:
    """Test cases for RollbackManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test-config.yml"
        self.rollback_dir = Path(self.temp_dir) / "rollback_plans"
        
        self.manager = RollbackManager(str(self.config_path), str(self.rollback_dir))
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_init(self):
        """Test rollback manager initialization."""
        manager = RollbackManager("test-config.yml", "test-rollback")
        assert manager is not None
        assert manager.config_path == Path("test-config.yml")
        assert manager.rollback_dir == Path("test-rollback")
        
    def test_create_rollback_plan_success(self):
        """Test successful rollback plan creation."""
        success, plan_id = self.manager.create_rollback_plan(
            target_version="test-version-123",
            rollback_reason="Test rollback"
        )
        
        assert success is True
        assert plan_id is not None
        assert plan_id.startswith("rollback_")
        
        # Verify plan file was created
        plan_file = self.rollback_dir / f"{plan_id}.json"
        assert plan_file.exists()
        
        # Verify plan content
        with open(plan_file, 'r') as f:
            plan_data = json.load(f)
        
        assert plan_data["target_version"] == "test-version-123"
        assert plan_data["rollback_reason"] == "Test rollback"
        assert plan_data["status"] == "pending"
        
    def test_create_rollback_plan_with_custom_safety_checks(self):
        """Test rollback plan creation with custom safety checks."""
        custom_checks = ["custom_check1", "custom_check2"]
        
        success, plan_id = self.manager.create_rollback_plan(
            target_version="test-version-456",
            rollback_reason="Custom rollback",
            safety_checks=custom_checks
        )
        
        assert success is True
        
        # Verify custom safety checks were saved
        plan_file = self.rollback_dir / f"{plan_id}.json"
        with open(plan_file, 'r') as f:
            plan_data = json.load(f)
        
        assert plan_data["safety_checks"] == custom_checks
        
    def test_execute_rollback_plan_success(self):
        """Test successful rollback plan execution."""
        # Create rollback plan
        success, plan_id = self.manager.create_rollback_plan(
            target_version="test-version-789",
            rollback_reason="Test execution"
        )
        assert success is True
        
        # Execute rollback plan
        execute_success, message = self.manager.execute_rollback_plan(plan_id)
        
        assert execute_success is True
        assert "executed successfully" in message
        
        # Verify plan status was updated
        plan_file = self.rollback_dir / f"{plan_id}.json"
        with open(plan_file, 'r') as f:
            plan_data = json.load(f)
        
        assert plan_data["status"] == "completed"
        assert plan_data["executed_at"] is not None
        
    def test_execute_rollback_plan_not_found(self):
        """Test execution of non-existent rollback plan."""
        execute_success, message = self.manager.execute_rollback_plan("non-existent-plan")
        
        assert execute_success is False
        assert "not found" in message
        
    def test_execute_rollback_plan_with_force(self):
        """Test rollback plan execution with force flag."""
        # Create rollback plan
        success, plan_id = self.manager.create_rollback_plan(
            target_version="test-version-force",
            rollback_reason="Force test"
        )
        assert success is True
        
        # Execute with force=True
        execute_success, message = self.manager.execute_rollback_plan(plan_id, force=True)
        
        assert execute_success is True
        assert "executed successfully" in message
        
    def test_quick_rollback_success(self):
        """Test successful quick rollback."""
        success, message = self.manager.quick_rollback(
            target_version="quick-version-123",
            reason="Quick rollback test"
        )
        
        assert success is True
        assert "executed successfully" in message
        
    def test_emergency_rollback_success(self):
        """Test successful emergency rollback."""
        success, message = self.manager.emergency_rollback("emergency-version-456")
        
        assert success is True
        assert "executed successfully" in message
        
    def test_list_rollback_plans_empty(self):
        """Test listing rollback plans when none exist."""
        plans = self.manager.list_rollback_plans()
        assert plans == []
        
    def test_list_rollback_plans_with_data(self):
        """Test listing rollback plans with data."""
        # Create multiple plans
        success1, plan_id1 = self.manager.create_rollback_plan(
            target_version="version1", rollback_reason="Plan 1"
        )
        success2, plan_id2 = self.manager.create_rollback_plan(
            target_version="version2", rollback_reason="Plan 2"
        )
        
        assert success1 is True
        assert success2 is True
        
        plans = self.manager.list_rollback_plans()
        
        assert len(plans) == 2
        assert all(isinstance(p, RollbackPlan) for p in plans)
        
        # Should be sorted by creation time (newest first)
        plan_ids = [p.plan_id for p in plans]
        assert plan_id2 in plan_ids
        assert plan_id1 in plan_ids
        
    def test_list_rollback_plans_with_status_filter(self):
        """Test listing rollback plans with status filter."""
        # Create plan
        success, plan_id = self.manager.create_rollback_plan(
            target_version="filter-version", rollback_reason="Filter test"
        )
        assert success is True
        
        # List pending plans
        pending_plans = self.manager.list_rollback_plans(status="pending")
        assert len(pending_plans) == 1
        assert pending_plans[0].plan_id == plan_id
        
        # List completed plans
        completed_plans = self.manager.list_rollback_plans(status="completed")
        assert len(completed_plans) == 0
        
    def test_get_rollback_plan_success(self):
        """Test successful rollback plan retrieval."""
        success, plan_id = self.manager.create_rollback_plan(
            target_version="get-version-123",
            rollback_reason="Get test"
        )
        assert success is True
        
        plan = self.manager.get_rollback_plan(plan_id)
        
        assert plan is not None
        assert isinstance(plan, RollbackPlan)
        assert plan.plan_id == plan_id
        assert plan.target_version == "get-version-123"
        assert plan.rollback_reason == "Get test"
        
    def test_get_rollback_plan_not_found(self):
        """Test rollback plan retrieval for non-existent plan."""
        plan = self.manager.get_rollback_plan("non-existent-plan")
        assert plan is None
        
    def test_validate_rollback_safety_safe(self):
        """Test rollback safety validation for safe rollback."""
        validation = self.manager.validate_rollback_safety("safe-version-123")
        
        assert "target_version" in validation
        assert validation["target_version"] == "safe-version-123"
        assert "is_safe" in validation
        assert "safety_checks" in validation
        
    def test_cleanup_old_plans(self):
        """Test cleanup of old rollback plans."""
        # Create multiple plans
        for i in range(5):
            success, plan_id = self.manager.create_rollback_plan(
                target_version=f"cleanup-version-{i}",
                rollback_reason=f"Cleanup plan {i}"
            )
            assert success is True
        
        # Cleanup with keep_days=0 (should keep none)
        deleted_count, deleted_plans = self.manager.cleanup_old_plans(keep_days=0)
        
        # All plans should be deleted
        remaining_plans = self.manager.list_rollback_plans()
        assert len(remaining_plans) == 0
        assert deleted_count == 5
        
    def test_rollback_plan_to_dict(self):
        """Test RollbackPlan to_dict method."""
        timestamp = datetime.now()
        plan = RollbackPlan(
            plan_id="test-plan",
            target_version="test-version",
            current_version="current-version",
            rollback_reason="Test reason",
            safety_checks=["check1", "check2"],
            estimated_downtime=30,
            created_at=timestamp
        )
        
        plan_dict = plan.to_dict()
        
        assert plan_dict["plan_id"] == "test-plan"
        assert plan_dict["target_version"] == "test-version"
        assert plan_dict["current_version"] == "current-version"
        assert plan_dict["rollback_reason"] == "Test reason"
        assert plan_dict["safety_checks"] == ["check1", "check2"]
        assert plan_dict["estimated_downtime"] == 30
        assert plan_dict["created_at"] == timestamp.isoformat()
        assert plan_dict["status"] == "pending"
        assert plan_dict["executed_at"] is None
        assert plan_dict["error_message"] is None
        
    def test_rollback_plan_with_execution(self):
        """Test RollbackPlan with execution details."""
        timestamp = datetime.now()
        executed_at = timestamp + timedelta(minutes=5)
        
        plan = RollbackPlan(
            plan_id="executed-plan",
            target_version="executed-version",
            current_version="current-version",
            rollback_reason="Execution test",
            safety_checks=["check1"],
            estimated_downtime=60,
            created_at=timestamp
        )
        
        plan.status = "completed"
        plan.executed_at = executed_at
        
        plan_dict = plan.to_dict()
        
        assert plan_dict["status"] == "completed"
        assert plan_dict["executed_at"] == executed_at.isoformat()
        
    def test_rollback_plan_with_error(self):
        """Test RollbackPlan with error details."""
        timestamp = datetime.now()
        
        plan = RollbackPlan(
            plan_id="error-plan",
            target_version="error-version",
            current_version="current-version",
            rollback_reason="Error test",
            safety_checks=["check1"],
            estimated_downtime=30,
            created_at=timestamp
        )
        
        plan.status = "failed"
        plan.error_message = "Test error occurred"
        
        plan_dict = plan.to_dict()
        
        assert plan_dict["status"] == "failed"
        assert plan_dict["error_message"] == "Test error occurred"
        
    @patch('builtins.print')
    def test_log_action(self, mock_print):
        """Test logging functionality."""
        self.manager.log_action("test_action", "completed", {"test": "data"})
        
        # Verify print was called
        mock_print.assert_called_once()
        
        # Verify log format
        log_call = mock_print.call_args[0][0]
        log_data = eval(log_call)  # Convert string back to dict
        
        assert log_data["task"] == "7.1"
        assert log_data["action"] == "RollbackManager.test_action"
        assert log_data["status"] == "completed"
        assert log_data["details"]["test"] == "data"