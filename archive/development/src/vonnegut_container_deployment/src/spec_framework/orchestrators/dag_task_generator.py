#!/usr/bin/env python3
"""
DAG Task Generator for Prepare Spec for Execution
================================================

Converts specification data into executable DAG task definitions using the existing
ParallelExecutionEngine infrastructure. Optimizes for parallel execution and efficiency.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.spec_framework.performance import performance_monitor, parallel_process
from src.dag_orchestration.execution.parallel_execution_engine import (
    TaskDefinition, 
    ExecutionStrategy,
    TaskExecutionStatus
)
from src.spec_framework.core.spec_analyzer import SpecAnalyzer, SpecificationData, TaskItem


@dataclass
class ExecutionGroup:
    """Group of tasks that can execute in parallel."""
    group_id: str
    tasks: List[TaskDefinition] = field(default_factory=list)
    estimated_duration: float = 0.0
    dependencies: Set[str] = field(default_factory=set)
    phase: str = "implementation"


@dataclass
class DAGExecutionPlan:
    """Complete DAG execution plan for a specification."""
    spec_name: str
    total_tasks: int
    execution_groups: List[ExecutionGroup] = field(default_factory=list)
    task_definitions: List[TaskDefinition] = field(default_factory=list)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    estimated_sequential_time: float = 0.0
    estimated_parallel_time: float = 0.0
    efficiency_gain: float = 0.0
    execution_strategy: ExecutionStrategy = ExecutionStrategy.CONSERVATIVE
    metadata: Dict[str, Any] = field(default_factory=dict)


class DAGTaskGenerator(ReflectiveModule):
    """Converts specifications into executable DAG task definitions."""
    
    def __init__(self):
        super().__init__()
        self.spec_analyzer = SpecAnalyzer()
        self.default_task_duration = 2.0  # hours
        self.task_duration_estimates = {
            # Common task patterns and their estimated durations
            'implement': 4.0,
            'create': 3.0,
            'build': 3.5,
            'add': 2.0,
            'setup': 1.5,
            'configure': 1.0,
            'test': 2.0,
            'validate': 1.0,
            'generate': 1.5,
            'integrate': 3.0,
            'deploy': 2.0,
            'monitor': 1.0,
            'document': 1.5,
            'fix': 2.5,
            'optimize': 3.0,
            'refactor': 4.0
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'conversion_types': ['spec_to_dag', 'task_optimization', 'parallel_grouping'],
            'execution_strategies': ['conservative', 'aggressive', 'sequential'],
            'optimization_features': ['dependency_analysis', 'parallel_grouping', 'efficiency_calculation'],
            'output_formats': ['TaskDefinition', 'ExecutionPlan', 'JSON']
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy',
            'spec_analyzer_ready': True,
            'task_patterns_loaded': len(self.task_duration_estimates)
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'DAGTaskGenerator',
            'version': '1.0.0',
            'description': 'Converts specifications into executable DAG task definitions',
            'dependencies': ['SpecAnalyzer', 'ParallelExecutionEngine'],
            'workflow_control': 'prepare-spec-for-execution'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_conversion'],
            'recommendation': 'Use sequential execution strategy'
        }
    
    @performance_monitor("generate_dag_execution_plan")
    def generate_dag_execution_plan(self, spec_path: str, 
                                   execution_strategy: str = "conservative") -> DAGExecutionPlan:
        """Generate complete DAG execution plan from specification."""
        # Convert string strategy to ExecutionStrategy enum
        strategy_lower = execution_strategy.lower()
        if strategy_lower == "aggressive":
            strategy_enum = ExecutionStrategy.AGGRESSIVE
        elif strategy_lower == "sequential":
            strategy_enum = ExecutionStrategy.SEQUENTIAL
        else:
            strategy_enum = ExecutionStrategy.CONSERVATIVE
        
        # Analyze specification
        spec_data = self.spec_analyzer.analyze_specification(spec_path)
        
        if spec_data.validation_errors:
            raise ValueError(f"Specification validation errors: {spec_data.validation_errors}")
        
        # Convert tasks to TaskDefinitions
        task_definitions = self._convert_tasks_to_definitions(spec_data)
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(spec_data, task_definitions)
        
        # Calculate execution groups for parallel optimization
        execution_groups = self._calculate_execution_groups(task_definitions, dependency_graph)
        
        # Calculate timing estimates
        sequential_time = sum(self._estimate_task_duration(task) for task in task_definitions)
        parallel_time = self._calculate_parallel_execution_time(execution_groups)
        efficiency_gain = ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0
        
        # Create execution plan
        execution_plan = DAGExecutionPlan(
            spec_name=spec_data.spec_name,
            total_tasks=len(task_definitions),
            execution_groups=execution_groups,
            task_definitions=task_definitions,
            dependency_graph=dependency_graph,
            estimated_sequential_time=sequential_time,
            estimated_parallel_time=parallel_time,
            efficiency_gain=efficiency_gain,
            execution_strategy=strategy_enum,
            metadata={
                'spec_path': str(spec_data.spec_path),
                'completeness_score': spec_data.completeness_score,
                'generation_timestamp': datetime.now().isoformat(),
                'requirements_count': len(spec_data.requirements),
                'design_sections_count': len(spec_data.design_sections)
            }
        )
        
        return execution_plan
    
    def _convert_tasks_to_definitions(self, spec_data: SpecificationData) -> List[TaskDefinition]:
        """Convert specification tasks to TaskDefinition objects."""
        task_definitions = []
        
        for task in spec_data.tasks:
            # Convert main task
            task_def = self._create_task_definition(task, spec_data)
            task_definitions.append(task_def)
            
            # Convert subtasks
            for subtask in task.subtasks:
                subtask_def = self._create_task_definition(subtask, spec_data, parent_id=task.id)
                task_definitions.append(subtask_def)
        
        return task_definitions
    
    def _create_task_definition(self, task: TaskItem, spec_data: SpecificationData, 
                               parent_id: Optional[str] = None) -> TaskDefinition:
        """Create TaskDefinition from TaskItem."""
        # Generate execution function placeholder
        def task_execution_function(*args, **kwargs):
            """Placeholder execution function for task."""
            import time
            import random
            
            # Simulate realistic execution time
            duration = self._estimate_task_duration_from_item(task)
            # Add some randomness (±20%)
            actual_duration = duration * (0.8 + random.random() * 0.4)
            
            print(f"Executing task: {task.title}")
            print(f"Description: {task.description}")
            print(f"Requirements: {task.requirements}")
            
            # Simulate work with progress updates
            steps = 10
            for i in range(steps):
                time.sleep(actual_duration * 3600 / steps)  # Convert hours to seconds
                progress = (i + 1) / steps * 100
                print(f"Progress: {progress:.1f}%")
            
            return {
                'task_id': task.id,
                'status': 'completed',
                'duration_hours': actual_duration,
                'requirements_addressed': task.requirements
            }
        
        # Build dependencies
        dependencies = task.dependencies.copy()
        if parent_id:
            dependencies.add(parent_id)
        
        # Estimate resource requirements
        resource_requirements = {
            'cpu_cores': 1,
            'memory_mb': 512,
            'disk_mb': 100,
            'estimated_duration_hours': self._estimate_task_duration_from_item(task)
        }
        
        # Determine timeout (3x estimated duration)
        timeout_seconds = self._estimate_task_duration_from_item(task) * 3600 * 3
        
        return TaskDefinition(
            task_id=task.id,
            name=task.title,
            dependencies=dependencies,
            execution_function=task_execution_function,
            execution_args=(),
            execution_kwargs={
                'task_item': task,
                'spec_data': spec_data
            },
            resource_requirements=resource_requirements,
            timeout_seconds=timeout_seconds,
            max_retries=2 if not task.optional else 1,
            priority=0 if task.optional else 1
        )
    
    def _estimate_task_duration_from_item(self, task: TaskItem) -> float:
        """Estimate task duration in hours based on task content."""
        if task.estimated_hours:
            return task.estimated_hours
        
        # Analyze task title and description for keywords
        text = f"{task.title} {task.description}".lower()
        
        # Look for duration patterns
        for keyword, duration in self.task_duration_estimates.items():
            if keyword in text:
                return duration
        
        # Adjust based on task complexity indicators
        base_duration = self.default_task_duration
        
        # Longer tasks for complex operations
        if any(word in text for word in ['comprehensive', 'complete', 'full', 'entire']):
            base_duration *= 1.5
        
        # Shorter tasks for simple operations
        if any(word in text for word in ['simple', 'basic', 'quick', 'minor']):
            base_duration *= 0.7
        
        # Optional tasks typically take less time
        if task.optional:
            base_duration *= 0.8
        
        return base_duration
    
    def _estimate_task_duration(self, task_def: TaskDefinition) -> float:
        """Estimate task duration from TaskDefinition."""
        return task_def.resource_requirements.get('estimated_duration_hours', self.default_task_duration)
    
    def _build_dependency_graph(self, spec_data: SpecificationData, 
                               task_definitions: List[TaskDefinition]) -> Dict[str, Set[str]]:
        """Build dependency graph from task definitions."""
        dependency_graph = {}
        
        for task_def in task_definitions:
            dependency_graph[task_def.task_id] = task_def.dependencies.copy()
        
        return dependency_graph
    
    def _calculate_execution_groups(self, task_definitions: List[TaskDefinition], 
                                   dependency_graph: Dict[str, Set[str]]) -> List[ExecutionGroup]:
        """Calculate optimal execution groups for parallel execution."""
        # Topological sort to determine execution levels
        execution_levels = self._calculate_execution_levels(task_definitions, dependency_graph)
        
        execution_groups = []
        
        for level, tasks in execution_levels.items():
            # Group tasks by estimated duration for load balancing
            tasks_by_duration = sorted(tasks, key=self._estimate_task_duration, reverse=True)
            
            # Create execution group
            group = ExecutionGroup(
                group_id=f"phase_{level}",
                tasks=tasks_by_duration,
                estimated_duration=max(self._estimate_task_duration(task) for task in tasks) if tasks else 0,
                phase=self._determine_phase(level, len(execution_levels))
            )
            
            # Calculate group dependencies
            for task in tasks:
                group.dependencies.update(dependency_graph.get(task.task_id, set()))
            
            execution_groups.append(group)
        
        return execution_groups
    
    def _calculate_execution_levels(self, task_definitions: List[TaskDefinition], 
                                   dependency_graph: Dict[str, Set[str]]) -> Dict[int, List[TaskDefinition]]:
        """Calculate execution levels using topological sorting."""
        # Create task lookup
        task_lookup = {task.task_id: task for task in task_definitions}
        
        # Calculate in-degrees
        in_degree = {task.task_id: 0 for task in task_definitions}
        for task_id, deps in dependency_graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[task_id] += 1
        
        # Level assignment
        levels = {}
        current_level = 0
        remaining_tasks = set(task.task_id for task in task_definitions)
        
        while remaining_tasks:
            # Find tasks with no dependencies at current level
            ready_tasks = [
                task_id for task_id in remaining_tasks 
                if in_degree[task_id] == 0
            ]
            
            if not ready_tasks:
                # Handle circular dependencies by breaking them
                # Choose task with minimum dependencies
                ready_tasks = [min(remaining_tasks, key=lambda t: len(dependency_graph.get(t, set())))]
            
            # Assign to current level
            levels[current_level] = [task_lookup[task_id] for task_id in ready_tasks]
            
            # Remove from remaining and update in-degrees
            for task_id in ready_tasks:
                remaining_tasks.remove(task_id)
                
                # Update in-degrees for dependent tasks
                for other_task_id in remaining_tasks:
                    if task_id in dependency_graph.get(other_task_id, set()):
                        in_degree[other_task_id] -= 1
            
            current_level += 1
        
        return levels
    
    def _determine_phase(self, level: int, total_levels: int) -> str:
        """Determine execution phase based on level."""
        if level == 0:
            return "initialization"
        elif level < total_levels * 0.3:
            return "setup"
        elif level < total_levels * 0.7:
            return "implementation"
        elif level < total_levels * 0.9:
            return "integration"
        else:
            return "finalization"
    
    def _calculate_parallel_execution_time(self, execution_groups: List[ExecutionGroup]) -> float:
        """Calculate total parallel execution time."""
        return sum(group.estimated_duration for group in execution_groups)
    
    def generate_task_scripts(self, execution_plan: DAGExecutionPlan, 
                             output_dir: Optional[str] = None) -> Dict[str, str]:
        """Generate task execution scripts from execution plan."""
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        scripts = {}
        
        for task_def in execution_plan.task_definitions:
            script_content = self._generate_task_script(task_def, execution_plan)
            script_name = f"{task_def.task_id.replace('.', '_')}_task.py"
            scripts[script_name] = script_content
            
            if output_dir:
                script_path = output_path / script_name
                script_path.write_text(script_content)
        
        return scripts
    
    def _generate_task_script(self, task_def: TaskDefinition, execution_plan: DAGExecutionPlan) -> str:
        """Generate individual task execution script."""
        return f'''#!/usr/bin/env python3
"""
Generated Task Script: {task_def.name}
=====================================

Auto-generated from specification: {execution_plan.spec_name}
Task ID: {task_def.task_id}
Dependencies: {list(task_def.dependencies)}

Generated: {datetime.now().isoformat()}
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def execute_task():
    """Execute the task implementation."""
    print(f"🚀 Starting task: {task_def.name}")
    print(f"📋 Task ID: {task_def.task_id}")
    print(f"🔗 Dependencies: {list(task_def.dependencies)}")
    
    # TODO: Implement actual task logic here
    # This is a placeholder implementation
    
    estimated_duration = {task_def.resource_requirements.get('estimated_duration_hours', 2.0)}
    print(f"⏱️  Estimated duration: {{estimated_duration}} hours")
    
    # Simulate work progress
    steps = 10
    for i in range(steps):
        progress = (i + 1) / steps * 100
        print(f"📊 Progress: {{progress:.1f}}%")
        time.sleep(0.1)  # Simulate work
    
    print(f"✅ Task completed: {task_def.name}")
    
    return {{
        'task_id': '{task_def.task_id}',
        'status': 'completed',
        'duration_hours': estimated_duration,
        'timestamp': time.time()
    }}

if __name__ == "__main__":
    try:
        result = execute_task()
        print(f"🎉 Task result: {{result}}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Task failed: {{e}}")
        sys.exit(1)
'''
    
    def to_dict(self, execution_plan: DAGExecutionPlan) -> Dict[str, Any]:
        """Convert execution plan to dictionary."""
        return {
            'spec_name': execution_plan.spec_name,
            'total_tasks': execution_plan.total_tasks,
            'execution_groups': [
                {
                    'group_id': group.group_id,
                    'task_count': len(group.tasks),
                    'estimated_duration': group.estimated_duration,
                    'dependencies': list(group.dependencies),
                    'phase': group.phase,
                    'tasks': [
                        {
                            'task_id': task.task_id,
                            'name': task.name,
                            'dependencies': list(task.dependencies),
                            'estimated_duration': self._estimate_task_duration(task),
                            'optional': task.priority == 0
                        }
                        for task in group.tasks
                    ]
                }
                for group in execution_plan.execution_groups
            ],
            'timing_estimates': {
                'sequential_time_hours': execution_plan.estimated_sequential_time,
                'parallel_time_hours': execution_plan.estimated_parallel_time,
                'efficiency_gain_percent': execution_plan.efficiency_gain
            },
            'execution_strategy': execution_plan.execution_strategy.value,
            'metadata': execution_plan.metadata
        }


# Convenience functions
def generate_dag_plan(spec_path: str, strategy: str = "conservative") -> DAGExecutionPlan:
    """Generate DAG execution plan for a specification."""
    generator = DAGTaskGenerator()
    
    # Convert string strategy to ExecutionStrategy enum
    strategy_lower = strategy.lower()
    if strategy_lower == "aggressive":
        execution_strategy = ExecutionStrategy.AGGRESSIVE
    elif strategy_lower == "sequential":
        execution_strategy = ExecutionStrategy.SEQUENTIAL
    else:
        execution_strategy = ExecutionStrategy.CONSERVATIVE
    
    return generator.generate_dag_execution_plan(spec_path, execution_strategy)


def generate_task_definitions(spec_path: str) -> List[TaskDefinition]:
    """Generate TaskDefinition objects for a specification."""
    generator = DAGTaskGenerator()
    execution_plan = generator.generate_dag_execution_plan(spec_path)
    return execution_plan.task_definitions


def calculate_efficiency_gain(spec_path: str) -> float:
    """Calculate potential efficiency gain from parallel execution."""
    generator = DAGTaskGenerator()
    execution_plan = generator.generate_dag_execution_plan(spec_path)
    return execution_plan.efficiency_gain