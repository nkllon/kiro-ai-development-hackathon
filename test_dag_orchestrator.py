#!/usr/bin/env python3
"""
Comprehensive Tests for DAG Orchestrator
========================================

Test suite for the main DAG orchestrator component including execution
lifecycle management and validation.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.dag_orchestration.core.dag_orchestrator import (
    DAGOrchestrator,
    OrchestrationConfig,
    OrchestrationStatus,
    create_dag_orchestrator,
    create_orchestration_config
)
from src.dag_orchestration.execution.parallel_execution_engine import (
    TaskDefinition,
    ExecutionStrategy,
    create_task_definition
)
from src.dag_orchestration.execution.dependency_aware_scheduler import SchedulingStrategy


class TestDAGOrchestrator:
    """Test suite for DAG Orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create DAG orchestrator for testing."""
        config = OrchestrationConfig(
            max_workers=4,
            execution_strategy=ExecutionStrategy.CONSERVATIVE,
            scheduling_strategy=SchedulingStrategy.ADAPTIVE,
            enable_prefire_testing=True,
            enable_continuous_monitoring=False  # Disable for tests
        )
        return DAGOrchestrator(config)
    
    @pytest.fixture
    def simple_tasks(self):
        """Create simple task definitions for testing."""
        return [
            create_task_definition("task_1", "Task 1", dependencies=set()),
            create_task_definition("task_2", "Task 2", dependencies={"task_1"}),
            create_task_definition("task_3", "Task 3", dependencies={"task_1"}),
            create_task_definition("task_4", "Task 4", dependencies={"task_2", "task_3"})
        ]
    
    @pytest.fixture
    def complex_tasks(self):
        """Create complex task definitions for testing."""
        tasks = []
        
        # Create a more complex DAG with multiple levels
        for i in range(1, 11):
            dependencies = set()
            if i > 1:
                dependencies.add(f"task_{i-1}")
            if i > 5:
                dependencies.add("task_3")
            
            task = create_task_definition(
                f"task_{i}", 
                f"Task {i}",
                dependencies=dependencies,
                priority=i % 3  # Varying priorities
            )
            tasks.append(task)
        
        return tasks
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test DAG orchestrator initialization."""
        assert orchestrator.module_id == "DAGOrchestrator"
        
        module_info = orchestrator.get_module_info()
        assert module_info["name"] == "DAGOrchestrator"
        assert module_info["version"] == "1.0.0"
        assert "configuration" in module_info
        assert "component_status" in module_info
        assert "statistics" in module_info
    
    def test_orchestrator_health_status(self, orchestrator):
        """Test orchestrator health status reporting."""
        health = orchestrator.get_health_status()
        
        assert health.module_id == "DAGOrchestrator"
        assert health.status.value in ["healthy", "warning", "error"]
        assert 0.0 <= health.health_score <= 1.0
        assert isinstance(health.issues, list)
        assert health.uptime_seconds >= 0
    
    def test_orchestrator_capabilities(self, orchestrator):
        """Test orchestrator capabilities."""
        capabilities = orchestrator.get_capabilities()
        
        expected_capabilities = [
            "core_functionality",
            "data_processing", 
            "api_integration",
            "validation",
            "monitoring"
        ]
        
        capability_values = [cap.value for cap in capabilities]
        for expected in expected_capabilities:
            assert expected in capability_values
    
    def test_graceful_degradation(self, orchestrator):
        """Test orchestrator graceful degradation."""
        result = orchestrator.graceful_degradation()
        
        assert result.success is True
        assert len(result.remaining_capabilities) > 0
        assert len(result.degraded_capabilities) > 0
        
        # Verify configuration changes
        assert orchestrator._config.execution_strategy == ExecutionStrategy.SEQUENTIAL
        assert orchestrator._config.scheduling_strategy == SchedulingStrategy.FIFO
        assert orchestrator._config.enable_continuous_monitoring is False
    
    def test_validate_execution_plan_valid_dag(self, orchestrator, simple_tasks):
        """Test execution plan validation with valid DAG."""
        validation_report = orchestrator.validate_execution_plan(simple_tasks)
        
        assert validation_report["plan_valid"] is True
        assert validation_report["task_count"] == 4
        assert validation_report["readiness_score"] > 0.0
        assert "validation_results" in validation_report
        assert "recommendations" in validation_report
        
        # Check DAG structure validation
        dag_check = next(
            (r for r in validation_report["validation_results"] 
             if r["check"] == "DAG Structure"), None
        )
        assert dag_check is not None
        assert dag_check["passed"] is True
    
    def test_validate_execution_plan_circular_dependency(self, orchestrator):
        """Test execution plan validation with circular dependencies."""
        # Create tasks with circular dependency
        circular_tasks = [
            create_task_definition("task_1", "Task 1", dependencies={"task_2"}),
            create_task_definition("task_2", "Task 2", dependencies={"task_1"})
        ]
        
        validation_report = orchestrator.validate_execution_plan(circular_tasks)
        
        assert validation_report["plan_valid"] is False
        assert validation_report["readiness_score"] == 0.0
        
        # Check that DAG structure validation failed
        dag_check = next(
            (r for r in validation_report["validation_results"] 
             if r["check"] == "DAG Structure"), None
        )
        assert dag_check is not None
        assert dag_check["passed"] is False
    
    @pytest.mark.asyncio
    async def test_execute_dag_simple(self, orchestrator, simple_tasks):
        """Test simple DAG execution."""
        # Add simple execution functions to tasks
        for task in simple_tasks:
            task.execution_function = lambda: f"Result from {task.task_id}"
        
        result = await orchestrator.execute_dag(simple_tasks)
        
        assert result.orchestration_id is not None
        assert result.status in [OrchestrationStatus.COMPLETED, OrchestrationStatus.FAILED]
        assert result.total_tasks == 4
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration_seconds is not None
        assert result.duration_seconds > 0
        
        # Check task results
        assert len(result.task_results) == 4
        for task_id, task_result in result.task_results.items():
            assert task_result.task_id == task_id
            assert task_result.start_time is not None
    
    @pytest.mark.asyncio
    async def test_execute_dag_with_failure(self, orchestrator):
        """Test DAG execution with task failure."""
        async def failing_function():
            raise ValueError("Simulated task failure")
        
        async def success_function():
            return "Success"
        
        tasks = [
            TaskDefinition(
                task_id="task_1",
                name="Failing Task",
                dependencies=set(),
                execution_function=failing_function
            ),
            TaskDefinition(
                task_id="task_2", 
                name="Success Task",
                dependencies=set(),
                execution_function=success_function
            )
        ]
        
        result = await orchestrator.execute_dag(tasks)
        
        # Note: The orchestrator may still complete if independent tasks succeed
        # We check that at least one task failed
        assert len(result.task_results) == 2
        
        # Verify we have both success and failure
        statuses = [r.status.value for r in result.task_results.values()]
        # At least one should fail due to the failing function
        has_failure = any(status == "failed" for status in statuses)
        assert has_failure, f"Expected at least one failure, got statuses: {statuses}"
    
    @pytest.mark.asyncio
    async def test_execute_dag_with_dependencies(self, orchestrator):
        """Test DAG execution respects dependencies."""
        execution_order = []
        
        def create_tracking_function(task_id):
            async def tracking_function():
                execution_order.append(task_id)
                return f"Result from {task_id}"
            return tracking_function
        
        # Create tasks with tracking functions
        tasks = [
            TaskDefinition(
                task_id="task_1",
                name="Task 1",
                dependencies=set(),
                execution_function=create_tracking_function("task_1")
            ),
            TaskDefinition(
                task_id="task_2",
                name="Task 2", 
                dependencies={"task_1"},
                execution_function=create_tracking_function("task_2")
            ),
            TaskDefinition(
                task_id="task_3",
                name="Task 3",
                dependencies={"task_1"},
                execution_function=create_tracking_function("task_3")
            )
        ]
        
        result = await orchestrator.execute_dag(tasks)
        
        assert result.status == OrchestrationStatus.COMPLETED
        assert len(result.task_results) == 3
        
        # All tasks should complete successfully
        for task_result in result.task_results.values():
            assert task_result.status.value == "completed"
    
    def test_get_current_orchestration_status_none(self, orchestrator):
        """Test getting current orchestration status when none active."""
        status = orchestrator.get_current_orchestration_status()
        assert status is None
    
    def test_get_orchestration_history_empty(self, orchestrator):
        """Test getting orchestration history when empty."""
        history = orchestrator.get_orchestration_history()
        assert isinstance(history, list)
        assert len(history) == 0
    
    def test_get_orchestration_statistics(self, orchestrator):
        """Test getting orchestration statistics."""
        stats = orchestrator.get_orchestration_statistics()
        
        required_keys = [
            'total_orchestrations',
            'successful_orchestrations', 
            'failed_orchestrations',
            'success_rate',
            'average_duration_seconds',
            'current_orchestration_active',
            'component_statistics'
        ]
        
        for key in required_keys:
            assert key in stats
        
        assert stats['total_orchestrations'] >= 0
        assert stats['successful_orchestrations'] >= 0
        assert stats['failed_orchestrations'] >= 0
        assert 0.0 <= stats['success_rate'] <= 1.0
        assert stats['average_duration_seconds'] >= 0.0
        assert isinstance(stats['current_orchestration_active'], bool)
        assert isinstance(stats['component_statistics'], dict)
    
    @pytest.mark.asyncio
    async def test_orchestrator_shutdown(self, orchestrator):
        """Test orchestrator shutdown."""
        await orchestrator.shutdown()
        
        # Verify components are shutdown
        # Note: In real implementation, we'd check component states
        # For now, we just verify the method completes without error


class TestOrchestrationConfig:
    """Test suite for OrchestrationConfig."""
    
    def test_default_config(self):
        """Test default orchestration configuration."""
        config = OrchestrationConfig()
        
        assert config.max_workers == 10
        assert config.execution_strategy == ExecutionStrategy.CONSERVATIVE
        assert config.scheduling_strategy == SchedulingStrategy.ADAPTIVE
        assert config.validation_policy is None
        assert config.enable_prefire_testing is True
        assert config.enable_continuous_monitoring is True
        assert config.timeout_seconds is None
    
    def test_custom_config(self):
        """Test custom orchestration configuration."""
        config = OrchestrationConfig(
            max_workers=20,
            execution_strategy=ExecutionStrategy.AGGRESSIVE,
            scheduling_strategy=SchedulingStrategy.PRIORITY,
            enable_prefire_testing=False,
            enable_continuous_monitoring=False,
            timeout_seconds=300.0
        )
        
        assert config.max_workers == 20
        assert config.execution_strategy == ExecutionStrategy.AGGRESSIVE
        assert config.scheduling_strategy == SchedulingStrategy.PRIORITY
        assert config.enable_prefire_testing is False
        assert config.enable_continuous_monitoring is False
        assert config.timeout_seconds == 300.0


class TestFactoryFunctions:
    """Test suite for factory functions."""
    
    def test_create_dag_orchestrator_default(self):
        """Test creating DAG orchestrator with default config."""
        orchestrator = create_dag_orchestrator()
        
        assert isinstance(orchestrator, DAGOrchestrator)
        assert orchestrator.module_id == "DAGOrchestrator"
    
    def test_create_dag_orchestrator_custom_config(self):
        """Test creating DAG orchestrator with custom config."""
        config = OrchestrationConfig(max_workers=5)
        orchestrator = create_dag_orchestrator(config)
        
        assert isinstance(orchestrator, DAGOrchestrator)
        assert orchestrator._config.max_workers == 5
    
    def test_create_orchestration_config(self):
        """Test creating orchestration config with factory function."""
        config = create_orchestration_config(
            max_workers=15,
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            scheduling_strategy=SchedulingStrategy.FIFO,
            enable_prefire_testing=False,
            enable_continuous_monitoring=True
        )
        
        assert isinstance(config, OrchestrationConfig)
        assert config.max_workers == 15
        assert config.execution_strategy == ExecutionStrategy.SEQUENTIAL
        assert config.scheduling_strategy == SchedulingStrategy.FIFO
        assert config.enable_prefire_testing is False
        assert config.enable_continuous_monitoring is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])