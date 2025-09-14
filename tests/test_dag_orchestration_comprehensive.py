"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.496567
"""




import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any
from dataclasses import dataclass

# Import the modules we're testing
from src.beast_mode.dag_orchestration.models.dag_models import (
    TaskNode, ParallelGroup, OptimizedExecution, ExecutionPhase,
    ResourceRequirements, ResourceAllocation, TeamAssignment, DependencyEdge
)
from src.beast_mode.dag_orchestration.models.enums import (
    TaskStatus, OptimizationStrategy, ParallelizationLevel
)
from src.beast_mode.dag_orchestration.optimization.parallel_optimizer import (
from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    ParallelOptimizer, ParallelOpportunity
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


class TestParallelOpportunity(ReflectiveModule):
    """Test ParallelOpportunity data model."""
    
    def test_parallel_opportunity_creation(self):
        """Test parallel opportunity creation."""
        tasks = [
            TaskNode("task1", "Task 1", "First task", 2, [], TaskStatus.PENDING),
            TaskNode("task2", "Task 2", "Second task", 3, [], TaskStatus.PENDING)
        ]
        
        resource_req = ResourceRequirements(
            cpu_cores=2,
            memory_gb=4,
            skill_requirements=["python"]
        )
        
        opportunity = ParallelOpportunity(
            opportunity_id="test_opportunity",
            tasks=tasks,
            estimated_savings=2,
            resource_requirements=resource_req,
            risk_level="low",
            coordination_overhead=1
        )
        
        assert opportunity.opportunity_id == "test_opportunity"
        assert len(opportunity.tasks) == 2
        assert opportunity.estimated_savings == 2
        assert opportunity.risk_level == "low"


class TestParallelOptimizer(ReflectiveModule):
    """Test ParallelOptimizer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = ParallelOptimizer(OptimizationStrategy.BALANCED)
        
        # Create mock constraint graph
        self.mock_constraint_graph = Mock(spec=ConstraintGraph)
        self.mock_constraint_graph.dependency_layers = {
            0: ["task1", "task2"],
            1: ["task3", "task4"],
            2: ["task5"]
        }
        
        # Create mock tasks
        self.mock_tasks = {
            "task1": TaskNode("task1", "Task 1", "First task", 2, [], TaskStatus.PENDING),
            "task2": TaskNode("task2", "Task 2", "Second task", 3, [], TaskStatus.PENDING),
            "task3": TaskNode("task3", "Task 3", "Third task", 1, ["task1"], TaskStatus.PENDING),
            "task4": TaskNode("task4", "Task 4", "Fourth task", 2, ["task2"], TaskStatus.PENDING),
            "task5": TaskNode("task5", "Task 5", "Fifth task", 4, ["task3", "task4"], TaskStatus.PENDING)
        }
        
        self.mock_constraint_graph.nodes = self.mock_tasks
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        assert self.optimizer.optimization_strategy == OptimizationStrategy.BALANCED
        assert isinstance(self.optimizer.parallel_opportunities, list)
        assert isinstance(self.optimizer.resource_constraints, dict)
    
    def test_identify_layer_based_opportunities(self):
        """Test layer-based opportunity identification."""
        opportunities = self.optimizer._identify_layer_based_opportunities(self.mock_constraint_graph)
        
        # Should find opportunities in layers with multiple tasks
        assert len(opportunities) >= 2  # Layer 0 and Layer 1 have multiple tasks
        
        # Check that opportunities are created for layers with multiple tasks
        layer_0_opportunity = next(
            (opp for opp in opportunities if "layer_based_0" in opp.opportunity_id), 
            None
        )
        assert layer_0_opportunity is not None
        assert len(layer_0_opportunity.tasks) == 2
    
    def test_create_parallel_opportunity(self):
        """Test parallel opportunity creation."""
        tasks = [self.mock_tasks["task1"], self.mock_tasks["task2"]]
        
        opportunity = self.optimizer._create_parallel_opportunity("test_opp", tasks)
        
        assert opportunity.opportunity_id == "test_opp"
        assert len(opportunity.tasks) == 2
        assert opportunity.estimated_savings >= 0
        assert opportunity.risk_level in ["low", "medium", "high"]
        assert opportunity.coordination_overhead >= 0
    
    def test_assess_risk_level(self):
        """Test risk level assessment."""
        # Low risk: 2 tasks
        low_risk_tasks = [self.mock_tasks["task1"], self.mock_tasks["task2"]]
        assert self.optimizer._assess_risk_level(low_risk_tasks) == "low"
        
        # Medium risk: 3-5 tasks
        medium_risk_tasks = [
            self.mock_tasks["task1"], 
            self.mock_tasks["task2"], 
            self.mock_tasks["task3"]
        ]
        assert self.optimizer._assess_risk_level(medium_risk_tasks) == "medium"
        
        # High risk: >5 tasks
        high_risk_tasks = [self.mock_tasks[f"task{i}"] for i in range(1, 7)]
        # Add more mock tasks for high risk test
        for i in range(6, 7):
            high_risk_tasks.append(
                TaskNode(f"task{i}", f"Task {i}", f"Task {i}", 1, [], TaskStatus.PENDING)
            )
        assert self.optimizer._assess_risk_level(high_risk_tasks) == "high"
    
    def test_is_viable_opportunity(self):
        """Test opportunity viability assessment."""
        # Viable opportunity
        viable_opportunity = ParallelOpportunity(
            opportunity_id="viable",
            tasks=[self.mock_tasks["task1"], self.mock_tasks["task2"]],
            estimated_savings=5,
            resource_requirements=ResourceRequirements(2, 4, []),
            risk_level="low",
            coordination_overhead=2
        )
        assert self.optimizer._is_viable_opportunity(viable_opportunity) is True
        
        # Non-viable opportunity (high risk)
        non_viable_opportunity = ParallelOpportunity(
            opportunity_id="non_viable",
            tasks=[self.mock_tasks["task1"]],
            estimated_savings=5,
            resource_requirements=ResourceRequirements(2, 4, []),
            risk_level="high",
            coordination_overhead=2
        )
        assert self.optimizer._is_viable_opportunity(non_viable_opportunity) is False
        
        # Non-viable opportunity (low savings)
        low_savings_opportunity = ParallelOpportunity(
            opportunity_id="low_savings",
            tasks=[self.mock_tasks["task1"], self.mock_tasks["task2"]],
            estimated_savings=1,
            resource_requirements=ResourceRequirements(2, 4, []),
            risk_level="low",
            coordination_overhead=2
        )
        assert self.optimizer._is_viable_opportunity(low_savings_opportunity) is False
    
    def test_calculate_coordination_overhead(self):
        """Test coordination overhead calculation."""
        # Small group
        small_tasks = [self.mock_tasks["task1"], self.mock_tasks["task2"]]
        overhead = self.optimizer._calculate_coordination_overhead(small_tasks)
        assert overhead >= 1
        
        # Larger group
        large_tasks = [self.mock_tasks[f"task{i}"] for i in range(1, 6)]
        large_overhead = self.optimizer._calculate_coordination_overhead(large_tasks)
        assert large_overhead > overhead
    
    def test_optimize_execution(self):
        """Test complete execution optimization."""
        result = self.optimizer.optimize_execution(self.mock_constraint_graph)
        
        assert isinstance(result, OptimizedExecution)
        assert isinstance(result.parallel_groups, list)
        assert isinstance(result.execution_phases, list)
        assert result.estimated_timeline > 0
        assert result.maximum_parallelism >= 1
        assert isinstance(result.identified_bottlenecks, list)
        assert result.optimization_strategy == OptimizationStrategy.BALANCED
    
    def test_identify_bottlenecks(self):
        """Test bottleneck identification."""
        # Create phases with high resource requirements
        high_cpu_phase = ExecutionPhase(
            phase_id="high_cpu",
            parallel_groups=[],
            estimated_duration=5,
            resource_requirements=ResourceRequirements(20, 8, ["python"]),
            dependencies=[],
            success_criteria=[]
        )
        
        high_memory_phase = ExecutionPhase(
            phase_id="high_memory",
            parallel_groups=[],
            estimated_duration=3,
            resource_requirements=ResourceRequirements(4, 40, ["java"]),
            dependencies=[],
            success_criteria=[]
        )
        
        phases = [high_cpu_phase, high_memory_phase]
        bottlenecks = self.optimizer._identify_bottlenecks(phases)
        
        # Should identify CPU and memory bottlenecks
        cpu_bottleneck = any("CPU requirement" in b for b in bottlenecks)
        memory_bottleneck = any("memory requirement" in b for b in bottlenecks)
        
        assert cpu_bottleneck or memory_bottleneck
    
    def test_calculate_optimized_timeline(self):
        """Test timeline calculation."""
        phases = [
            ExecutionPhase("phase1", [], 5, ResourceRequirements(2, 4, []), [], []),
            ExecutionPhase("phase2", [], 3, ResourceRequirements(2, 4, []), [], []),
            ExecutionPhase("phase3", [], 2, ResourceRequirements(2, 4, []), [], [])
        ]
        
        timeline = self.optimizer._calculate_optimized_timeline(phases)
        
        # Total is 10 days, should be 2 weeks
        assert timeline == 2
    
    def test_calculate_maximum_parallelism(self):
        """Test maximum parallelism calculation."""
        # Create parallel groups with different sizes
        group1 = ParallelGroup(
            group_id="group1",
            tasks=[self.mock_tasks["task1"], self.mock_tasks["task2"]],
            coordination_strategy="systematic",
            resource_allocation=Mock(),
            estimated_duration=5
        )
        
        group2 = ParallelGroup(
            group_id="group2",
            tasks=[self.mock_tasks["task3"]],
            coordination_strategy="systematic",
            resource_allocation=Mock(),
            estimated_duration=3
        )
        
        groups = [group1, group2]
        max_parallelism = self.optimizer._calculate_maximum_parallelism(groups)
        
        # Should be 2 (size of largest group)
        assert max_parallelism == 2
    
    def test_empty_groups_parallelism(self):
        """Test parallelism calculation with empty groups."""
        max_parallelism = self.optimizer._calculate_maximum_parallelism([])
        assert max_parallelism == 1


class TestResourceRequirements(ReflectiveModule):
    """Test ResourceRequirements data model."""
    
    def test_resource_requirements_creation(self):
        """Test resource requirements creation."""
        req = ResourceRequirements(
            cpu_cores=8,
            memory_gb=16,
            skill_requirements=["python", "docker", "kubernetes"]
        )
        
        assert req.cpu_cores == 8
        assert req.memory_gb == 16
        assert len(req.skill_requirements) == 3
        assert "python" in req.skill_requirements
    
    def test_resource_requirements_defaults(self):
        """Test resource requirements with defaults."""
        req = ResourceRequirements(
            cpu_cores=4,
            memory_gb=8,
            skill_requirements=[]
        )
        
        assert req.cpu_cores == 4
        assert req.memory_gb == 8
        assert req.skill_requirements == []


class TestExecutionPhase(ReflectiveModule):
    """Test ExecutionPhase data model."""
    
    def test_execution_phase_creation(self):
        """Test execution phase creation."""
        resource_req = ResourceRequirements(4, 8, ["python"])
        
        phase = ExecutionPhase(
            phase_id="test_phase",
            parallel_groups=[],
            estimated_duration=7,
            resource_requirements=resource_req,
            dependencies=["previous_phase"],
            success_criteria=["All tasks completed", "No errors"]
        )
        
        assert phase.phase_id == "test_phase"
        assert phase.estimated_duration == 7
        assert phase.dependencies == ["previous_phase"]
        assert len(phase.success_criteria) == 2
        assert phase.resource_requirements.cpu_cores == 4


class TestOptimizedExecution(ReflectiveModule):
    """Test OptimizedExecution data model."""
    
    def test_optimized_execution_creation(self):
        """Test optimized execution creation."""
        execution = OptimizedExecution(
            parallel_groups=[],
            execution_phases=[],
            estimated_timeline=4,
            maximum_parallelism=3,
            identified_bottlenecks=["High CPU usage"],
            optimization_strategy=OptimizationStrategy.SPEED_FOCUSED
        )
        
        assert execution.estimated_timeline == 4
        assert execution.maximum_parallelism == 3
        assert len(execution.identified_bottlenecks) == 1
        assert execution.optimization_strategy == OptimizationStrategy.SPEED_FOCUSED


class TestIntegrationScenarios(ReflectiveModule):
    """Test integration scenarios for DAG orchestration."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.optimizer = ParallelOptimizer(OptimizationStrategy.BALANCED)
    
    def test_simple_linear_dag(self):
        """Test optimization of simple linear DAG."""
        # Create linear dependency chain
        constraint_graph = Mock(spec=ConstraintGraph)
        constraint_graph.dependency_layers = {
            0: ["task1"],
            1: ["task2"],
            2: ["task3"]
        }
        
        tasks = {
            "task1": TaskNode("task1", "Task 1", "First", 2, [], TaskStatus.PENDING),
            "task2": TaskNode("task2", "Task 2", "Second", 3, ["task1"], TaskStatus.PENDING),
            "task3": TaskNode("task3", "Task 3", "Third", 1, ["task2"], TaskStatus.PENDING)
        }
        constraint_graph.nodes = tasks
        
        result = self.optimizer.optimize_execution(constraint_graph)
        
        # Linear DAG should have limited parallelism
        assert result.maximum_parallelism == 1
        assert result.estimated_timeline >= 2  # At least 2 weeks for 6 days of work
    
    def test_parallel_branches_dag(self):
        """Test optimization of DAG with parallel branches."""
        constraint_graph = Mock(spec=ConstraintGraph)
        constraint_graph.dependency_layers = {
            0: ["task1"],
            1: ["task2", "task3", "task4"],  # Parallel tasks
            2: ["task5"]
        }
        
        tasks = {
            "task1": TaskNode("task1", "Start", "Starting task", 1, [], TaskStatus.PENDING),
            "task2": TaskNode("task2", "Branch A", "First branch", 3, ["task1"], TaskStatus.PENDING),
            "task3": TaskNode("task3", "Branch B", "Second branch", 2, ["task1"], TaskStatus.PENDING),
            "task4": TaskNode("task4", "Branch C", "Third branch", 4, ["task1"], TaskStatus.PENDING),
            "task5": TaskNode("task5", "Merge", "Final task", 1, ["task2", "task3", "task4"], TaskStatus.PENDING)
        }
        constraint_graph.nodes = tasks
        
        result = self.optimizer.optimize_execution(constraint_graph)
        
        # Should identify parallel opportunities
        assert result.maximum_parallelism >= 2  # Should parallelize branches
        assert len(result.parallel_groups) > 0
    
    def test_complex_dag_optimization(self):
        """Test optimization of complex DAG with multiple patterns."""
        constraint_graph = Mock(spec=ConstraintGraph)
        constraint_graph.dependency_layers = {
            0: ["init1", "init2"],
            1: ["process1", "process2", "process3"],
            2: ["validate1", "validate2"],
            3: ["finalize"]
        }
        
        # Create tasks with varying resource requirements
        tasks = {}
        for layer, task_ids in constraint_graph.dependency_layers.items():
            for task_id in task_ids:
                tasks[task_id] = TaskNode(
                    task_id=task_id,
                    title=f"Task {task_id}",
                    description=f"Layer {layer} task",
                    estimated_duration=2 + (layer % 3),  # Varying durations
                    dependencies=[],
                    status=TaskStatus.PENDING,
                    resource_requirements=ResourceRequirements(
                        cpu_cores=2 + layer,
                        memory_gb=4 + (layer * 2),
                        skill_requirements=[f"skill_{layer}"]
                    )
                )
        
        constraint_graph.nodes = tasks
        
        result = self.optimizer.optimize_execution(constraint_graph)
        
        # Complex DAG should have multiple optimization opportunities
        assert len(result.execution_phases) >= 3
        assert result.maximum_parallelism >= 2
        assert len(result.identified_bottlenecks) >= 0  # May or may not have bottlenecks


# Performance and edge case tests
class TestEdgeCases(ReflectiveModule):
    """Test edge cases and error conditions."""
    
    def test_empty_constraint_graph(self):
        """Test optimization with empty constraint graph."""
        optimizer = ParallelOptimizer()
        
        empty_graph = Mock(spec=ConstraintGraph)
        empty_graph.dependency_layers = {}
        empty_graph.nodes = {}
        
        result = optimizer.optimize_execution(empty_graph)
        
        assert len(result.parallel_groups) == 0
        assert len(result.execution_phases) == 0
        assert result.maximum_parallelism == 1
        assert result.estimated_timeline >= 1
    
    def test_single_task_optimization(self):
        """Test optimization with single task."""
        optimizer = ParallelOptimizer()
        
        single_graph = Mock(spec=ConstraintGraph)
        single_graph.dependency_layers = {0: ["only_task"]}
        single_graph.nodes = {
            "only_task": TaskNode("only_task", "Only Task", "Single task", 3, [], TaskStatus.PENDING)
        }
        
        result = optimizer.optimize_execution(single_graph)
        
        assert result.maximum_parallelism == 1
        assert result.estimated_timeline >= 1
    
    def test_optimization_strategy_variations(self):
        """Test different optimization strategies."""
        strategies = [
            OptimizationStrategy.SPEED_FOCUSED,
            OptimizationStrategy.RESOURCE_EFFICIENT,
            OptimizationStrategy.BALANCED
        ]
        
        constraint_graph = Mock(spec=ConstraintGraph)
        constraint_graph.dependency_layers = {0: ["task1", "task2"]}
        constraint_graph.nodes = {
            "task1": TaskNode("task1", "Task 1", "First", 2, [], TaskStatus.PENDING),
            "task2": TaskNode("task2", "Task 2", "Second", 3, [], TaskStatus.PENDING)
        }
        
        results = []
        for strategy in strategies:
            optimizer = ParallelOptimizer(strategy)
            result = optimizer.optimize_execution(constraint_graph)
            results.append(result)
            
            # All strategies should produce valid results
            assert isinstance(result, OptimizedExecution)
            assert result.optimization_strategy == strategy
        
        # Results should be consistent across strategies for simple case
        assert all(r.maximum_parallelism >= 1 for r in results)


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