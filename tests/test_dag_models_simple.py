"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.513298
"""




import pytest
from src.beast_mode.dag_orchestration.models.dag_models import (
    TaskNode, DependencyEdge, ParallelGroup, ResourceRequirements,
    ExecutionPhase, TeamAssignment, OptimizedExecution, ResourceAllocation
)
from src.beast_mode.dag_orchestration.models.enums import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    TaskStatus, OptimizationStrategy, ParallelizationLevel
)


class TestTaskNode(ReflectiveModule):
    """Test TaskNode data model."""
    
    def test_task_node_creation(self):
        """Test basic task node creation."""
        task = TaskNode(
            task_id="test_task_1",
            spec_name="test_spec",
            task_name="Test Task",
            description="A test task",
            estimated_effort=5,
            completion_status=TaskStatus.NOT_STARTED,
            dependencies=["task_0"]
        )
        
        assert task.task_id == "test_task_1"
        assert task.spec_name == "test_spec"
        assert task.task_name == "Test Task"
        assert task.estimated_effort == 5
        assert task.dependencies == ["task_0"]
        assert task.completion_status == TaskStatus.NOT_STARTED
    
    def test_task_node_with_priority(self):
        """Test task node with priority and complexity."""
        task = TaskNode(
            task_id="priority_task",
            spec_name="test_spec",
            task_name="Priority Task",
            description="Task with priority",
            estimated_effort=3,
            completion_status=TaskStatus.NOT_STARTED,
            dependencies=[],
            priority=2,
            complexity=2.5
        )
        
        assert task.priority == 2
        assert task.complexity == 2.5
        assert task.estimated_effort == 3
    
    def test_task_node_validation(self):
        """Test task node validation."""
        # Test negative effort validation
        with pytest.raises(ValueError, match="Estimated effort cannot be negative"):
            TaskNode(
                task_id="invalid_task",
                spec_name="test_spec",
                task_name="Invalid Task",
                description="Invalid task",
                estimated_effort=-1,
                completion_status=TaskStatus.NOT_STARTED
            )
        
        # Test invalid priority validation
        with pytest.raises(ValueError, match="Priority must be between 1 and 5"):
            TaskNode(
                task_id="invalid_priority",
                spec_name="test_spec",
                task_name="Invalid Priority",
                description="Invalid priority",
                estimated_effort=5,
                completion_status=TaskStatus.NOT_STARTED,
                priority=10
            )


class TestDependencyEdge(ReflectiveModule):
    """Test DependencyEdge data model."""
    
    def test_dependency_edge_creation(self):
        """Test dependency edge creation."""
        edge = DependencyEdge(
            source_id="task1",
            target_id="task2",
            dependency_type="requires",
            weight=1.5
        )
        
        assert edge.source_id == "task1"
        assert edge.target_id == "task2"
        assert edge.dependency_type == "requires"
        assert edge.weight == 1.5
    
    def test_dependency_edge_defaults(self):
        """Test dependency edge with default values."""
        edge = DependencyEdge(
            source_id="task1",
            target_id="task2"
        )
        
        assert edge.dependency_type == "requires"
        assert edge.weight == 1.0


class TestResourceRequirements(ReflectiveModule):
    """Test ResourceRequirements data model."""
    
    def test_resource_requirements_creation(self):
        """Test resource requirements creation."""
        req = ResourceRequirements(
            developers_needed=3,
            skill_requirements=["python", "docker"],
            estimated_hours=40,
            tools_required=["pytest", "docker"]
        )
        
        assert req.developers_needed == 3
        assert req.skill_requirements == ["python", "docker"]
        assert req.estimated_hours == 40
        assert req.tools_required == ["pytest", "docker"]
    
    def test_resource_requirements_validation(self):
        """Test resource requirements validation."""
        # Test negative developers validation
        with pytest.raises(ValueError, match="Developers needed cannot be negative"):
            ResourceRequirements(
                developers_needed=-1,
                skill_requirements=["python"],
                estimated_hours=10
            )
        
        # Test negative hours validation
        with pytest.raises(ValueError, match="Estimated hours cannot be negative"):
            ResourceRequirements(
                developers_needed=2,
                skill_requirements=["python"],
                estimated_hours=-5
            )


class TestParallelGroup(ReflectiveModule):
    """Test ParallelGroup data model."""
    
    def test_parallel_group_creation(self):
        """Test parallel group creation."""
        task1 = TaskNode(
            task_id="task1",
            spec_name="spec1",
            task_name="Task 1",
            description="First task",
            estimated_effort=5,
            completion_status=TaskStatus.NOT_STARTED
        )
        
        task2 = TaskNode(
            task_id="task2",
            spec_name="spec1",
            task_name="Task 2",
            description="Second task",
            estimated_effort=3,
            completion_status=TaskStatus.NOT_STARTED
        )
        
        group = ParallelGroup(
            group_id="parallel_group_1",
            tasks=[task1, task2],
            estimated_duration=5
        )
        
        assert group.group_id == "parallel_group_1"
        assert len(group.tasks) == 2
        assert group.estimated_duration == 5
        assert group.tasks[0].task_id == "task1"
        assert group.tasks[1].task_id == "task2"


class TestExecutionPhase(ReflectiveModule):
    """Test ExecutionPhase data model."""
    
    def test_execution_phase_creation(self):
        """Test execution phase creation."""
        task = TaskNode(
            task_id="phase_task",
            spec_name="spec1",
            task_name="Phase Task",
            description="Task in phase",
            estimated_effort=8,
            completion_status=TaskStatus.NOT_STARTED
        )
        
        resource_req = ResourceRequirements(
            developers_needed=1,
            skill_requirements=["python"],
            estimated_hours=16
        )
        
        phase = ExecutionPhase(
            phase_name="Phase 1",
            tasks=[task],
            parallel_groups=[],
            dependencies_satisfied=["Phase 0"],
            estimated_duration=2,
            resource_requirements=resource_req
        )
        
        assert phase.phase_name == "Phase 1"
        assert len(phase.tasks) == 1
        assert phase.dependencies_satisfied == ["Phase 0"]
        assert phase.estimated_duration == 2


class TestTeamAssignment(ReflectiveModule):
    """Test TeamAssignment data model."""
    
    def test_team_assignment_creation(self):
        """Test team assignment creation."""
        assignment = TeamAssignment(
            team_name="Backend Team",
            team_members=["Alice", "Bob"],
            assigned_tasks=["task1", "task2"],
            capabilities=["python", "testing"],
            availability=0.85
        )
        
        assert assignment.team_name == "Backend Team"
        assert assignment.assigned_tasks == ["task1", "task2"]
        assert assignment.availability == 0.85
        assert assignment.capabilities == ["python", "testing"]


class TestOptimizedExecution(ReflectiveModule):
    """Test OptimizedExecution data model."""
    
    def test_optimized_execution_creation(self):
        """Test optimized execution creation."""
        resource_alloc = ResourceAllocation(teams=[], resource_utilization=0.8)
        
        execution = OptimizedExecution(
            execution_id="exec_001",
            execution_phases=[],
            resource_allocation=resource_alloc,
            parallel_groups=[],
            estimated_timeline=4,
            maximum_parallelism=2
        )
        
        assert execution.execution_id == "exec_001"
        assert execution.estimated_timeline == 4
        assert execution.maximum_parallelism == 2
        assert isinstance(execution.parallel_groups, list)
        assert isinstance(execution.execution_phases, list)


class TestEnums(ReflectiveModule):
    """Test enum values."""
    
    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.NOT_STARTED.value == "not_started"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.BLOCKED.value == "blocked"
    
    def test_optimization_strategy_enum(self):
        """Test OptimizationStrategy enum values."""
        assert OptimizationStrategy.SPEED_OPTIMIZED.value == "speed_optimized"
        assert OptimizationStrategy.RESOURCE_OPTIMIZED.value == "resource_optimized"
        assert OptimizationStrategy.BALANCED.value == "balanced"
    
    def test_parallelization_level_enum(self):
        """Test ParallelizationLevel enum values."""
        assert ParallelizationLevel.NONE.value == "none"
        assert ParallelizationLevel.LOW.value == "low"
        assert ParallelizationLevel.MEDIUM.value == "medium"
        assert ParallelizationLevel.HIGH.value == "high"


class TestIntegrationScenarios(ReflectiveModule):
    """Test integration scenarios with multiple models."""
    
    def test_complete_workflow_models(self):
        """Test complete workflow using multiple models."""
        # Create tasks
        task1 = TaskNode(
            task_id="setup_task",
            spec_name="setup_spec",
            task_name="Setup Environment",
            description="Set up development environment",
            estimated_effort=8,
            completion_status=TaskStatus.NOT_STARTED,
            priority=1
        )
        
        task2 = TaskNode(
            task_id="dev_task",
            spec_name="dev_spec",
            task_name="Development",
            description="Core development work",
            estimated_effort=40,
            completion_status=TaskStatus.NOT_STARTED,
            dependencies=["setup_task"],
            priority=2
        )
        
        # Create dependency edge
        edge = DependencyEdge(
            source_id="setup_task",
            target_id="dev_task",
            dependency_type="requires"
        )
        
        # Create resource requirements
        resources = ResourceRequirements(
            developers_needed=2,
            skill_requirements=["python", "testing"],
            estimated_hours=48,
            tools_required=["pytest", "coverage"]
        )
        
        # Create parallel group
        parallel_group = ParallelGroup(
            group_id="dev_group",
            tasks=[task2],
            estimated_duration=8
        )
        
        # Create team assignment
        team = TeamAssignment(
            team_name="Development Team",
            team_members=["Alice", "Bob"],
            assigned_tasks=["setup_task", "dev_task"],
            capabilities=["python", "testing"],
            availability=0.90
        )
        
        # Create resource allocation
        resource_alloc = ResourceAllocation(teams=[team], resource_utilization=0.85)
        
        # Create execution phase
        phase = ExecutionPhase(
            phase_name="Development Phase",
            tasks=[task1, task2],
            parallel_groups=[parallel_group],
            dependencies_satisfied=[],
            estimated_duration=3,
            resource_requirements=resources
        )
        
        # Create optimized execution
        execution = OptimizedExecution(
            execution_id="project_exec",
            execution_phases=[phase],
            resource_allocation=resource_alloc,
            parallel_groups=[parallel_group],
            estimated_timeline=2,
            maximum_parallelism=2
        )
        
        # Verify the complete workflow
        assert len(execution.parallel_groups) == 1
        assert len(execution.execution_phases) == 1
        assert execution.parallel_groups[0].group_id == "dev_group"
        assert execution.execution_phases[0].phase_name == "Development Phase"
        assert edge.source_id == task1.task_id
        assert edge.target_id == task2.task_id
        assert resources.developers_needed == 2
        assert team.team_name == "Development Team"


if __name__ == "__main__":

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }
        
    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())
            
    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }
        
    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

    pytest.main([__file__, "-v"])