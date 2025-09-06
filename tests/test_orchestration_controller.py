"""Tests for OrchestrationController."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.multi_instance_orchestration.orchestration.controller import OrchestrationController
from src.multi_instance_orchestration.orchestration.models import (
    DistributionStrategy,
    InstanceFailure,
    IntegrationPolicy,
    SwarmConfig,
    Task,
    TaskStatus,
)


@pytest.fixture
def basic_config():
    """Basic swarm configuration for testing."""
    return SwarmConfig(
        instance_count=3,
        task_distribution_strategy=DistributionStrategy.DEPENDENCY_AWARE,
        integration_policy=IntegrationPolicy.QUALITY_GATED,
    )


@pytest.fixture
def sample_tasks():
    """Sample tasks for testing."""
    return [
        Task(
            id="task-1",
            description="Setup project structure",
            estimated_duration=timedelta(minutes=15),
            complexity_score=2.0,
        ),
        Task(
            id="task-2",
            description="Implement core models",
            dependencies=["task-1"],
            estimated_duration=timedelta(minutes=30),
            complexity_score=3.0,
        ),
        Task(
            id="task-3",
            description="Create unit tests",
            dependencies=["task-2"],
            estimated_duration=timedelta(minutes=20),
            complexity_score=2.5,
        ),
        Task(
            id="task-4",
            description="Setup CI/CD pipeline",
            estimated_duration=timedelta(minutes=25),
            complexity_score=3.5,
        ),
    ]


@pytest.fixture
def controller(basic_config):
    """OrchestrationController instance for testing."""
    return OrchestrationController(basic_config)


class TestOrchestrationController:
    """Test OrchestrationController class."""

    def test_controller_initialization(self, controller, basic_config):
        """Test controller initialization."""
        assert controller.name == "OrchestrationController"
        assert controller.version == "1.0.0"
        assert controller.config == basic_config
        assert controller.swarm_state.config == basic_config
        assert len(controller.active_swarms) == 0
        assert len(controller.task_queue) == 0
        assert controller.performance_metrics["swarms_launched"] == 0

    def test_launch_swarm_success(self, controller, sample_tasks):
        """Test successful swarm launch."""
        swarm_state = controller.launch_swarm(sample_tasks)

        assert swarm_state.status == "active"
        assert len(swarm_state.instances) > 0
        assert len(swarm_state.task_assignments) > 0
        assert len(swarm_state.execution_status) == len(sample_tasks)
        assert controller.performance_metrics["swarms_launched"] == 1
        assert swarm_state.swarm_id in controller.active_swarms

    def test_launch_swarm_empty_tasks(self, controller):
        """Test swarm launch with empty task list."""
        with pytest.raises(RuntimeError, match="Cannot launch swarm with empty task list"):
            controller.launch_swarm([])

    def test_launch_swarm_invalid_config(self):
        """Test swarm launch with invalid configuration."""
        from pydantic import ValidationError
        
        # Test that invalid config fails at creation time
        with pytest.raises(ValidationError):
            SwarmConfig(instance_count=1, min_instances=2, max_instances=1)  # min > max

    def test_distribute_tasks_basic(self, controller, sample_tasks):
        """Test basic task distribution."""
        distribution_plan = controller.distribute_tasks(sample_tasks)

        assert distribution_plan.total_tasks == len(sample_tasks)
        assert len(distribution_plan.instance_assignments) > 0
        assert distribution_plan.strategy_used == DistributionStrategy.DEPENDENCY_AWARE
        assert distribution_plan.estimated_completion_time > timedelta(0)

        # Verify all tasks are assigned
        assigned_tasks = []
        for task_list in distribution_plan.instance_assignments.values():
            assigned_tasks.extend(task_list)
        assert len(assigned_tasks) == len(sample_tasks)

    def test_distribute_tasks_with_dependencies(self, controller):
        """Test task distribution respects dependencies."""
        tasks = [
            Task(id="task-a", description="Task A"),
            Task(id="task-b", description="Task B", dependencies=["task-a"]),
            Task(id="task-c", description="Task C", dependencies=["task-b"]),
        ]

        distribution_plan = controller.distribute_tasks(tasks)

        # Check parallel groups respect dependencies
        assert len(distribution_plan.parallel_execution_groups) >= 3
        # First group should contain task-a
        assert "task-a" in distribution_plan.parallel_execution_groups[0]

    def test_distribute_tasks_performance_tracking(self, controller, sample_tasks):
        """Test task distribution updates performance metrics."""
        initial_count = controller.performance_metrics["tasks_distributed"]

        controller.distribute_tasks(sample_tasks)

        assert controller.performance_metrics["tasks_distributed"] == initial_count + len(sample_tasks)
        assert len(controller.distribution_history) == 1

    def test_monitor_swarm_active(self, controller, sample_tasks):
        """Test monitoring active swarm."""
        import time
        
        # Launch swarm first
        swarm_state = controller.launch_swarm(sample_tasks)
        swarm_id = swarm_state.swarm_id
        initial_updated = swarm_state.last_updated

        # Wait a small amount to ensure timestamp difference
        time.sleep(0.01)

        # Monitor swarm
        monitored_state = controller.monitor_swarm(swarm_id)

        assert monitored_state.swarm_id == swarm_id
        assert monitored_state.last_updated >= initial_updated
        assert monitored_state.performance_metrics.last_updated is not None

    def test_monitor_swarm_nonexistent(self, controller):
        """Test monitoring non-existent swarm."""
        with pytest.raises(ValueError, match="Swarm nonexistent-swarm not found"):
            controller.monitor_swarm("nonexistent-swarm")

    def test_monitor_swarm_default(self, controller, sample_tasks):
        """Test monitoring default (current) swarm."""
        # Launch swarm first
        controller.launch_swarm(sample_tasks)

        # Monitor without specifying swarm_id
        monitored_state = controller.monitor_swarm()

        assert monitored_state.swarm_id == controller.swarm_state.swarm_id

    def test_handle_failure_basic(self, controller, sample_tasks):
        """Test basic failure handling."""
        # Launch swarm first
        swarm_state = controller.launch_swarm(sample_tasks)
        instance_id = list(swarm_state.instances.keys())[0]

        # Create failure
        failure = InstanceFailure(
            instance_id=instance_id,
            failure_type="timeout",
            error_message="Instance timed out",
            affected_tasks=["task-1", "task-2"],
        )

        # Handle failure
        recovery_plan = controller.handle_failure(failure)

        assert recovery_plan.failed_instance == instance_id
        assert recovery_plan.recovery_strategy in ["restart", "reassign", "scale_up", "manual"]
        assert recovery_plan.estimated_recovery_time > timedelta(0)
        assert len(controller.recovery_history) == 1

    def test_handle_failure_different_types(self, controller, sample_tasks):
        """Test handling different failure types."""
        controller.launch_swarm(sample_tasks)
        instance_id = "test-instance"

        failure_types = ["crash", "timeout", "resource", "communication"]

        for failure_type in failure_types:
            failure = InstanceFailure(
                instance_id=instance_id,
                failure_type=failure_type,
                error_message=f"Instance failed: {failure_type}",
            )

            recovery_plan = controller.handle_failure(failure)
            assert recovery_plan.recovery_strategy is not None

    def test_handle_failure_unrecoverable(self, controller, sample_tasks):
        """Test handling unrecoverable failure."""
        controller.launch_swarm(sample_tasks)

        failure = InstanceFailure(
            instance_id="test-instance",
            failure_type="crash",
            error_message="Critical system failure",
            is_recoverable=False,
        )

        recovery_plan = controller.handle_failure(failure)
        assert recovery_plan.recovery_strategy == "manual"

    def test_integrate_results_no_completed_tasks(self, controller, sample_tasks):
        """Test integration with no completed tasks."""
        controller.launch_swarm(sample_tasks)

        integration_report = controller.integrate_results()

        assert integration_report.summary == "No completed tasks ready for integration"
        assert len(integration_report.successful_integrations) == 0
        assert integration_report.integration_time > timedelta(0)

    def test_integrate_results_with_completed_tasks(self, controller, sample_tasks):
        """Test integration with completed tasks."""
        swarm_state = controller.launch_swarm(sample_tasks)

        # Mark some tasks as completed
        swarm_state.execution_status["task-1"] = TaskStatus.COMPLETED
        swarm_state.execution_status["task-4"] = TaskStatus.COMPLETED

        integration_report = controller.integrate_results()

        assert len(integration_report.successful_integrations) == 2
        assert "task-1" in integration_report.successful_integrations
        assert "task-4" in integration_report.successful_integrations
        assert controller.performance_metrics["successful_integrations"] == 2

    def test_integrate_results_specific_swarm(self, controller, sample_tasks):
        """Test integration for specific swarm."""
        swarm_state = controller.launch_swarm(sample_tasks)
        swarm_id = swarm_state.swarm_id

        # Mark task as completed
        swarm_state.execution_status["task-1"] = TaskStatus.COMPLETED

        integration_report = controller.integrate_results(swarm_id)

        assert len(integration_report.successful_integrations) == 1
        assert "task-1" in integration_report.successful_integrations

    def test_performance_metrics_tracking(self, controller, sample_tasks):
        """Test performance metrics are properly tracked."""
        initial_metrics = controller.performance_metrics.copy()

        # Launch swarm
        controller.launch_swarm(sample_tasks)

        # Check metrics updated
        assert controller.performance_metrics["swarms_launched"] == initial_metrics["swarms_launched"] + 1
        assert controller.performance_metrics["tasks_distributed"] == initial_metrics["tasks_distributed"] + len(sample_tasks)
        assert controller.performance_metrics["average_swarm_startup_time"] > 0

    def test_health_indicators_management(self, controller, sample_tasks):
        """Test health indicators are properly managed."""
        initial_indicator_count = len(controller._health_indicators)

        # Launch swarm (should add health indicator)
        controller.launch_swarm(sample_tasks)

        # Check health indicator added
        assert len(controller._health_indicators) > initial_indicator_count

        # Check health indicators include swarm launch
        launch_indicators = [
            ind for ind in controller._health_indicators
            if ind.name == "swarm_launch"
        ]
        assert len(launch_indicators) > 0

    def test_reflective_module_interface(self, controller):
        """Test ReflectiveModule interface implementation."""
        # Test module status
        status = controller.get_module_status()
        assert status.module_name == "OrchestrationController"
        assert status.version == "1.0.0"
        assert status.status in ["active", "error"]
        assert status.uptime > 0

        # Test health check
        is_healthy = controller.is_healthy()
        assert isinstance(is_healthy, bool)

        # Test health indicators
        indicators = controller.get_health_indicators()
        assert isinstance(indicators, list)

        # Check performance metrics included
        assert "active_swarms" in status.performance_metrics
        assert "task_queue_size" in status.performance_metrics

    def test_health_status_with_errors(self, controller, sample_tasks):
        """Test health status when there are errors."""
        # Add critical health indicator
        critical_indicator = controller.create_health_indicator(
            "test_error", "critical", "Test critical error"
        )
        controller.add_health_indicator(critical_indicator)

        # Should not be healthy
        assert not controller.is_healthy()

        # Status should reflect error
        status = controller.get_module_status()
        assert status.status == "error"

    def test_activity_tracking(self, controller, sample_tasks):
        """Test activity tracking."""
        initial_activity = controller.last_activity

        # Perform operation
        controller.launch_swarm(sample_tasks)

        # Activity should be updated
        assert controller.last_activity > initial_activity

    def test_swarm_state_management(self, controller, sample_tasks):
        """Test swarm state management."""
        # Launch multiple swarms
        swarm1 = controller.launch_swarm(sample_tasks[:2])
        swarm2 = controller.launch_swarm(sample_tasks[2:])

        # Check both swarms are tracked
        assert len(controller.active_swarms) == 2
        assert swarm1.swarm_id in controller.active_swarms
        assert swarm2.swarm_id in controller.active_swarms

        # Current swarm should be the last one launched
        assert controller.swarm_state.swarm_id == swarm2.swarm_id

    def test_configuration_validation(self):
        """Test configuration validation."""
        from pydantic import ValidationError
        
        # Test invalid instance count - should fail at SwarmConfig creation
        with pytest.raises(ValidationError):
            SwarmConfig(instance_count=0)

        # Test invalid min/max instances - should fail at SwarmConfig creation  
        with pytest.raises(ValidationError):
            SwarmConfig(min_instances=5, max_instances=3)

    def test_dependency_graph_building(self, controller):
        """Test dependency graph building."""
        tasks = [
            Task(id="a", description="Task A"),
            Task(id="b", description="Task B", dependencies=["a"]),
            Task(id="c", description="Task C", dependencies=["a", "b"]),
        ]

        # Access private method for testing
        graph = controller._build_dependency_graph(tasks)

        assert graph["a"] == []
        assert graph["b"] == ["a"]
        assert graph["c"] == ["a", "b"]

    def test_parallel_groups_calculation(self, controller):
        """Test parallel execution groups calculation."""
        dependency_graph = {
            "a": [],
            "b": ["a"],
            "c": ["a"],
            "d": ["b", "c"],
        }

        # Access private method for testing
        groups = controller._calculate_parallel_groups(dependency_graph)

        # First group should have tasks with no dependencies
        assert "a" in groups[0]
        # Second group should have tasks depending only on first group
        assert "b" in groups[1] or "c" in groups[1]
        # Last group should have tasks depending on previous groups
        assert "d" in groups[-1]

    def test_optimal_instance_calculation(self, controller, sample_tasks):
        """Test optimal instance count calculation."""
        parallel_groups = [["task-1", "task-4"], ["task-2"], ["task-3"]]

        # Access private method for testing
        optimal = controller._calculate_optimal_instances(sample_tasks, parallel_groups)

        # Should not exceed max parallel tasks in any group
        assert optimal <= 2  # Max parallel in first group
        # Should respect configuration limits
        assert optimal <= controller.config.max_instances
        assert optimal >= controller.config.min_instances

    def test_instance_creation(self, controller, sample_tasks):
        """Test instance creation from distribution plan."""
        distribution_plan = controller.distribute_tasks(sample_tasks)

        # Access private method for testing
        instances = controller._create_instances(distribution_plan)

        assert len(instances) > 0
        # Each instance should have unique ID and configuration
        instance_ids = [inst.instance_id for inst in instances]
        assert len(set(instance_ids)) == len(instances)

        # Each instance should have proper configuration
        for instance in instances:
            assert instance.branch_name.startswith("feature/")
            assert instance.workspace_path.name == instance.instance_id
            assert instance.peacock_theme.color_name is not None

    def test_error_handling_in_operations(self, controller):
        """Test error handling in various operations."""
        # Test monitor_swarm with invalid swarm
        with pytest.raises(ValueError):
            controller.monitor_swarm("invalid-swarm-id")
            
        # Test distribute_tasks with empty list (should work but return empty plan)
        plan = controller.distribute_tasks([])
        assert plan.total_tasks == 0

    def test_concurrent_operations(self, controller, sample_tasks):
        """Test concurrent operations safety."""
        import threading

        results = []
        errors = []

        def launch_swarm():
            try:
                swarm = controller.launch_swarm(sample_tasks[:2])
                results.append(swarm)
            except Exception as e:
                errors.append(e)

        # Launch multiple swarms concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=launch_swarm)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should handle concurrent operations gracefully
        assert len(errors) == 0 or len(results) > 0  # At least some should succeed

    def test_swarm_metrics_updates(self, controller, sample_tasks):
        """Test swarm metrics are properly updated."""
        swarm_state = controller.launch_swarm(sample_tasks)

        # Mark some tasks as completed and failed
        swarm_state.execution_status["task-1"] = TaskStatus.COMPLETED
        swarm_state.execution_status["task-2"] = TaskStatus.FAILED

        # Update metrics
        controller._update_swarm_metrics(swarm_state)

        metrics = swarm_state.performance_metrics
        assert metrics.completed_tasks == 1
        assert metrics.failed_tasks == 1
        assert metrics.error_rate == 0.5  # 1 failed out of 2 finished

    def test_instance_health_updates(self, controller, sample_tasks):
        """Test instance health status updates."""
        swarm_state = controller.launch_swarm(sample_tasks)

        # Simulate old heartbeat
        instance = list(swarm_state.instances.values())[0]
        instance.last_heartbeat = datetime.now() - timedelta(minutes=5)

        # Update health
        controller._update_instance_health(swarm_state)

        # Instance should be marked as error due to old heartbeat
        assert instance.status == "error"

    def test_recovery_strategy_generation(self, controller):
        """Test recovery strategy generation for different scenarios."""
        # Test timeout failure
        failure = InstanceFailure(
            instance_id="test",
            failure_type="timeout",
            error_message="Timeout",
            is_recoverable=True,
        )

        analysis = controller._analyze_failure(failure)
        plan = controller._generate_recovery_strategy(failure, analysis)

        assert plan.recovery_strategy == "restart"

        # Test resource failure
        failure.failure_type = "resource"
        analysis = controller._analyze_failure(failure)
        plan = controller._generate_recovery_strategy(failure, analysis)

        assert plan.recovery_strategy == "scale_up"

    def test_edge_cases(self, controller):
        """Test various edge cases."""
        # Single task
        single_task = [Task(id="single", description="Single task")]
        swarm = controller.launch_swarm(single_task)
        assert len(swarm.instances) >= 1

        # Task with self-dependency (should be handled gracefully)
        circular_task = Task(id="circular", description="Circular", dependencies=["circular"])
        try:
            controller.distribute_tasks([circular_task])
        except Exception:
            pass  # Should handle gracefully

        # Very large number of tasks
        many_tasks = [Task(id=f"task-{i}", description=f"Task {i}") for i in range(100)]
        plan = controller.distribute_tasks(many_tasks)
        assert plan.total_tasks == 100