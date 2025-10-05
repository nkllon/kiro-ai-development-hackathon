#!/usr/bin/env python3
"""
DAG Structure Optimizer for DAG Orchestration
=============================================

Automatic DAG structure optimization based on execution history
with recommendations for improved performance and efficiency.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition


class OptimizationType(Enum):
    """Types of DAG optimizations."""
    DEPENDENCY_REDUCTION = "dependency_reduction"
    PARALLELIZATION_IMPROVEMENT = "parallelization_improvement"
    TASK_CONSOLIDATION = "task_consolidation"
    TASK_SPLITTING = "task_splitting"
    CRITICAL_PATH_OPTIMIZATION = "critical_path_optimization"
    RESOURCE_BALANCING = "resource_balancing"


@dataclass
class OptimizationRecommendation:
    """A specific optimization recommendation."""
    recommendation_id: str
    optimization_type: OptimizationType
    title: str
    description: str
    affected_tasks: List[str]
    expected_improvement: Dict[str, float]  # e.g., {'execution_time': -0.2, 'cost': -0.1}
    confidence: float  # 0.0 to 1.0
    implementation_effort: str  # low, medium, high
    priority: int  # 1-10, higher is more important
    rationale: str
    implementation_steps: List[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    """Result of DAG optimization analysis."""
    optimization_id: str
    analysis_timestamp: datetime
    original_dag_metrics: Dict[str, Any]
    recommendations: List[OptimizationRecommendation]
    potential_improvements: Dict[str, float]
    analysis_duration: float
    dag_complexity_score: float


class DAGOptimizer(ReflectiveModule):
    """
    Optimizer for DAG structure and execution patterns.
    
    Features:
    - Automatic DAG structure analysis
    - Dependency optimization recommendations
    - Parallelization improvement suggestions
    - Critical path analysis and optimization
    - Resource balancing recommendations
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "DAGOptimizer"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Optimization state
        self._dag_history: List[Dict[str, Any]] = []
        self._optimization_history: List[OptimizationResult] = []
        self._applied_optimizations: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self._total_optimizations = 0
        self._recommendations_generated = 0
        self._optimizations_applied = 0
        
        self._logger.info("DAGOptimizer initialized")
    
    def record_dag_execution(self, dag_data: Dict[str, Any]) -> None:
        """Record DAG execution data for optimization analysis."""
        dag_record = {
            'timestamp': datetime.now(),
            'dag_id': dag_data.get('dag_id', str(uuid.uuid4())),
            'tasks': dag_data.get('tasks', []),
            'dependencies': dag_data.get('dependencies', {}),
            'execution_metrics': dag_data.get('execution_metrics', {}),
            'resource_usage': dag_data.get('resource_usage', {}),
            'critical_path': dag_data.get('critical_path', []),
            'parallelization_factor': dag_data.get('parallelization_factor', 1.0),
            'metadata': dag_data.get('metadata', {})
        }
        
        self._dag_history.append(dag_record)
        
        # Keep only recent history (last 100 DAG executions)
        if len(self._dag_history) > 100:
            self._dag_history = self._dag_history[-100:]
        
        self._logger.debug(f"Recorded DAG execution {dag_record['dag_id']}")
    
    async def optimize_dag_structure(self, current_dag: Dict[str, Any]) -> OptimizationResult:
        """Analyze DAG structure and provide optimization recommendations."""
        with self.trace_operation("optimize_dag_structure",
                                dag_id=current_dag.get('dag_id')) as trace:
            
            start_time = datetime.now()
            optimization_id = str(uuid.uuid4())
            
            try:
                # Analyze current DAG metrics
                original_metrics = self._analyze_dag_metrics(current_dag)
                
                # Generate optimization recommendations
                recommendations = []
                
                # Dependency optimization
                dependency_recs = self._analyze_dependency_optimization(current_dag)
                recommendations.extend(dependency_recs)
                
                # Parallelization improvements
                parallel_recs = self._analyze_parallelization_opportunities(current_dag)
                recommendations.extend(parallel_recs)
                
                # Task consolidation/splitting
                task_recs = self._analyze_task_structure_optimization(current_dag)
                recommendations.extend(task_recs)
                
                # Critical path optimization
                critical_path_recs = self._analyze_critical_path_optimization(current_dag)
                recommendations.extend(critical_path_recs)
                
                # Resource balancing
                resource_recs = self._analyze_resource_balancing(current_dag)
                recommendations.extend(resource_recs)
                
                # Sort recommendations by priority
                recommendations.sort(key=lambda r: r.priority, reverse=True)
                
                # Calculate potential improvements
                potential_improvements = self._calculate_potential_improvements(recommendations)
                
                # Calculate DAG complexity score
                complexity_score = self._calculate_dag_complexity(current_dag)
                
                # Calculate analysis duration
                end_time = datetime.now()
                analysis_duration = (end_time - start_time).total_seconds()
                
                # Create optimization result
                result = OptimizationResult(
                    optimization_id=optimization_id,
                    analysis_timestamp=start_time,
                    original_dag_metrics=original_metrics,
                    recommendations=recommendations,
                    potential_improvements=potential_improvements,
                    analysis_duration=analysis_duration,
                    dag_complexity_score=complexity_score
                )
                
                # Update statistics
                self._total_optimizations += 1
                self._recommendations_generated += len(recommendations)
                
                # Store optimization result
                self._optimization_history.append(result)
                
                # Keep only recent optimization history
                if len(self._optimization_history) > 50:
                    self._optimization_history = self._optimization_history[-50:]
                
                trace.output_result = {
                    'optimization_id': optimization_id,
                    'recommendations_count': len(recommendations),
                    'complexity_score': complexity_score,
                    'analysis_duration': analysis_duration,
                    'potential_time_improvement': potential_improvements.get('execution_time', 0)
                }
                
                self._logger.info(f"DAG optimization {optimization_id} completed: "
                                f"{len(recommendations)} recommendations generated")
                
                return result
                
            except Exception as e:
                self._logger.error(f"DAG optimization failed: {e}")
                trace.output_result = {'error': str(e)}
                raise e
    
    def _analyze_dag_metrics(self, dag: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current DAG metrics."""
        tasks = dag.get('tasks', [])
        dependencies = dag.get('dependencies', {})
        execution_metrics = dag.get('execution_metrics', {})
        
        # Basic structure metrics
        task_count = len(tasks)
        dependency_count = sum(len(deps) for deps in dependencies.values())
        
        # Calculate parallelization metrics
        max_parallel_tasks = self._calculate_max_parallelism(tasks, dependencies)
        actual_parallelism = dag.get('parallelization_factor', 1.0)
        
        # Calculate critical path length
        critical_path_length = len(dag.get('critical_path', []))
        
        return {
            'task_count': task_count,
            'dependency_count': dependency_count,
            'max_parallel_tasks': max_parallel_tasks,
            'actual_parallelism': actual_parallelism,
            'critical_path_length': critical_path_length,
            'execution_time': execution_metrics.get('total_duration', 0),
            'success_rate': execution_metrics.get('success_rate', 1.0),
            'resource_efficiency': execution_metrics.get('resource_efficiency', 0.5)
        }
    
    def _analyze_dependency_optimization(self, dag: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze opportunities to optimize task dependencies."""
        recommendations = []
        
        tasks = dag.get('tasks', [])
        dependencies = dag.get('dependencies', {})
        
        # Find unnecessary dependencies
        for task_id, deps in dependencies.items():
            if len(deps) > 3:  # Task with many dependencies
                # Check if some dependencies are transitive
                transitive_deps = self._find_transitive_dependencies(task_id, dependencies)
                
                if transitive_deps:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        optimization_type=OptimizationType.DEPENDENCY_REDUCTION,
                        title=f"Remove transitive dependencies for task {task_id}",
                        description=f"Task {task_id} has {len(transitive_deps)} transitive dependencies that can be removed",
                        affected_tasks=[task_id],
                        expected_improvement={'execution_time': -0.1, 'complexity': -0.2},
                        confidence=0.8,
                        implementation_effort="low",
                        priority=6,
                        rationale="Removing transitive dependencies simplifies the DAG without affecting correctness",
                        implementation_steps=[
                            f"Remove dependencies {transitive_deps} from task {task_id}",
                            "Verify that task execution order remains correct",
                            "Test the optimized DAG structure"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_parallelization_opportunities(self, dag: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze opportunities to improve parallelization."""
        recommendations = []
        
        tasks = dag.get('tasks', [])
        dependencies = dag.get('dependencies', {})
        max_parallel = self._calculate_max_parallelism(tasks, dependencies)
        actual_parallel = dag.get('parallelization_factor', 1.0)
        
        if max_parallel > actual_parallel * 1.5:  # Significant parallelization opportunity
            # Find independent task groups
            independent_groups = self._find_independent_task_groups(tasks, dependencies)
            
            if len(independent_groups) > 1:
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    optimization_type=OptimizationType.PARALLELIZATION_IMPROVEMENT,
                    title="Improve task parallelization",
                    description=f"DAG can support up to {max_parallel} parallel tasks but currently uses {actual_parallel}",
                    affected_tasks=[task['task_id'] for group in independent_groups for task in group],
                    expected_improvement={'execution_time': -0.3, 'resource_utilization': 0.2},
                    confidence=0.9,
                    implementation_effort="medium",
                    priority=8,
                    rationale=f"Increasing parallelization from {actual_parallel} to {max_parallel} can significantly reduce execution time",
                    implementation_steps=[
                        "Identify independent task groups",
                        "Increase worker pool size to support higher parallelism",
                        "Optimize resource allocation for parallel execution",
                        "Monitor resource usage during parallel execution"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_task_structure_optimization(self, dag: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze opportunities for task consolidation or splitting."""
        recommendations = []
        
        tasks = dag.get('tasks', [])
        execution_metrics = dag.get('execution_metrics', {})
        
        # Find very short tasks that could be consolidated
        short_tasks = []
        for task in tasks:
            task_duration = execution_metrics.get('task_durations', {}).get(task.get('task_id'), 0)
            if task_duration < 5:  # Tasks shorter than 5 seconds
                short_tasks.append(task)
        
        if len(short_tasks) > 3:  # Multiple short tasks
            recommendation = OptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                optimization_type=OptimizationType.TASK_CONSOLIDATION,
                title="Consolidate short-running tasks",
                description=f"Found {len(short_tasks)} tasks with execution time < 5 seconds",
                affected_tasks=[task.get('task_id') for task in short_tasks],
                expected_improvement={'execution_time': -0.15, 'overhead': -0.3},
                confidence=0.7,
                implementation_effort="medium",
                priority=5,
                rationale="Consolidating short tasks reduces scheduling overhead and improves efficiency",
                implementation_steps=[
                    "Identify logically related short tasks",
                    "Combine compatible tasks into single execution units",
                    "Update dependencies to reflect consolidated structure",
                    "Test consolidated task execution"
                ]
            )
            recommendations.append(recommendation)
        
        # Find very long tasks that could be split
        long_tasks = []
        for task in tasks:
            task_duration = execution_metrics.get('task_durations', {}).get(task.get('task_id'), 0)
            if task_duration > 300:  # Tasks longer than 5 minutes
                long_tasks.append(task)
        
        if long_tasks:
            for task in long_tasks:
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    optimization_type=OptimizationType.TASK_SPLITTING,
                    title=f"Consider splitting long-running task {task.get('task_id')}",
                    description=f"Task {task.get('task_id')} runs for {execution_metrics.get('task_durations', {}).get(task.get('task_id'), 0):.1f} seconds",
                    affected_tasks=[task.get('task_id')],
                    expected_improvement={'parallelization': 0.2, 'fault_tolerance': 0.3},
                    confidence=0.6,
                    implementation_effort="high",
                    priority=4,
                    rationale="Splitting long tasks can improve parallelization and fault tolerance",
                    implementation_steps=[
                        f"Analyze task {task.get('task_id')} for logical split points",
                        "Create sub-tasks with appropriate dependencies",
                        "Implement data passing between sub-tasks",
                        "Test split task execution and error handling"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_critical_path_optimization(self, dag: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze opportunities to optimize the critical path."""
        recommendations = []
        
        critical_path = dag.get('critical_path', [])
        execution_metrics = dag.get('execution_metrics', {})
        
        if not critical_path:
            return recommendations
        
        # Find bottleneck tasks in critical path
        task_durations = execution_metrics.get('task_durations', {})
        critical_path_durations = [(task_id, task_durations.get(task_id, 0)) for task_id in critical_path]
        critical_path_durations.sort(key=lambda x: x[1], reverse=True)
        
        # Focus on the slowest task in critical path
        if critical_path_durations:
            slowest_task, duration = critical_path_durations[0]
            total_critical_path_time = sum(d for _, d in critical_path_durations)
            
            if duration > total_critical_path_time * 0.3:  # Task takes >30% of critical path time
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    optimization_type=OptimizationType.CRITICAL_PATH_OPTIMIZATION,
                    title=f"Optimize critical path bottleneck: {slowest_task}",
                    description=f"Task {slowest_task} takes {duration:.1f}s ({duration/total_critical_path_time*100:.1f}% of critical path)",
                    affected_tasks=[slowest_task],
                    expected_improvement={'execution_time': -0.2, 'critical_path_time': -0.3},
                    confidence=0.8,
                    implementation_effort="medium",
                    priority=9,
                    rationale="Optimizing the critical path bottleneck has the highest impact on overall execution time",
                    implementation_steps=[
                        f"Profile task {slowest_task} to identify performance bottlenecks",
                        "Optimize algorithm or implementation",
                        "Consider increasing resources for this specific task",
                        "Explore parallel processing within the task if possible"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_resource_balancing(self, dag: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Analyze opportunities for better resource balancing."""
        recommendations = []
        
        tasks = dag.get('tasks', [])
        resource_usage = dag.get('resource_usage', {})
        
        # Analyze resource usage patterns
        cpu_usages = []
        memory_usages = []
        
        for task in tasks:
            task_id = task.get('task_id')
            task_resources = resource_usage.get(task_id, {})
            cpu_usages.append(task_resources.get('cpu', 1.0))
            memory_usages.append(task_resources.get('memory', 1.0))
        
        if cpu_usages and memory_usages:
            # Check for resource imbalance
            max_cpu = max(cpu_usages)
            min_cpu = min(cpu_usages)
            max_memory = max(memory_usages)
            min_memory = min(memory_usages)
            
            if max_cpu > min_cpu * 3 or max_memory > min_memory * 3:  # Significant imbalance
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    optimization_type=OptimizationType.RESOURCE_BALANCING,
                    title="Balance resource usage across tasks",
                    description=f"Resource usage varies significantly: CPU {min_cpu:.1f}-{max_cpu:.1f}, Memory {min_memory:.1f}-{max_memory:.1f}",
                    affected_tasks=[task.get('task_id') for task in tasks],
                    expected_improvement={'resource_efficiency': 0.2, 'cost': -0.1},
                    confidence=0.7,
                    implementation_effort="medium",
                    priority=6,
                    rationale="Balancing resource usage can improve overall efficiency and reduce costs",
                    implementation_steps=[
                        "Identify resource-intensive and resource-light tasks",
                        "Consider task scheduling to balance resource usage",
                        "Optimize resource allocation per task type",
                        "Monitor resource utilization after optimization"
                    ]
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_max_parallelism(self, tasks: List[Dict[str, Any]], 
                                 dependencies: Dict[str, List[str]]) -> int:
        """Calculate maximum possible parallelism for the DAG."""
        if not tasks:
            return 0
        
        # Simple approach: find the maximum number of tasks that can run simultaneously
        # This is a simplified version - a full implementation would use topological analysis
        
        task_ids = {task.get('task_id') for task in tasks}
        independent_tasks = []
        
        for task in tasks:
            task_id = task.get('task_id')
            task_deps = dependencies.get(task_id, [])
            
            # Count how many dependencies this task has
            if not task_deps:
                independent_tasks.append(task_id)
        
        # This is a simplified calculation
        # In reality, we'd need to do a proper topological sort and level analysis
        return max(len(independent_tasks), 1)
    
    def _find_transitive_dependencies(self, task_id: str, 
                                    dependencies: Dict[str, List[str]]) -> List[str]:
        """Find transitive dependencies that can be removed."""
        direct_deps = set(dependencies.get(task_id, []))
        transitive_deps = []
        
        # For each direct dependency, check if it's also reachable through other dependencies
        for dep in direct_deps:
            # Check if this dependency is reachable through other paths
            other_deps = direct_deps - {dep}
            for other_dep in other_deps:
                if self._is_reachable(other_dep, dep, dependencies):
                    transitive_deps.append(dep)
                    break
        
        return transitive_deps
    
    def _is_reachable(self, start: str, target: str, dependencies: Dict[str, List[str]]) -> bool:
        """Check if target is reachable from start through dependencies."""
        visited = set()
        stack = [start]
        
        while stack:
            current = stack.pop()
            if current == target:
                return True
            
            if current in visited:
                continue
            
            visited.add(current)
            stack.extend(dependencies.get(current, []))
        
        return False
    
    def _find_independent_task_groups(self, tasks: List[Dict[str, Any]], 
                                    dependencies: Dict[str, List[str]]) -> List[List[Dict[str, Any]]]:
        """Find groups of independent tasks that can run in parallel."""
        # Simplified implementation - group tasks by dependency level
        groups = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            current_group = []
            tasks_to_remove = []
            
            for task in remaining_tasks:
                task_id = task.get('task_id')
                task_deps = dependencies.get(task_id, [])
                
                # Check if all dependencies are satisfied (not in remaining tasks)
                remaining_task_ids = {t.get('task_id') for t in remaining_tasks}
                if not any(dep in remaining_task_ids for dep in task_deps):
                    current_group.append(task)
                    tasks_to_remove.append(task)
            
            if current_group:
                groups.append(current_group)
                for task in tasks_to_remove:
                    remaining_tasks.remove(task)
            else:
                # Avoid infinite loop if there are circular dependencies
                break
        
        return groups
    
    def _calculate_potential_improvements(self, recommendations: List[OptimizationRecommendation]) -> Dict[str, float]:
        """Calculate potential improvements from all recommendations."""
        improvements = {}
        
        for rec in recommendations:
            for metric, improvement in rec.expected_improvement.items():
                if metric not in improvements:
                    improvements[metric] = 0
                
                # Weight improvement by confidence
                weighted_improvement = improvement * rec.confidence
                improvements[metric] += weighted_improvement
        
        return improvements
    
    def _calculate_dag_complexity(self, dag: Dict[str, Any]) -> float:
        """Calculate a complexity score for the DAG."""
        tasks = dag.get('tasks', [])
        dependencies = dag.get('dependencies', {})
        
        task_count = len(tasks)
        dependency_count = sum(len(deps) for deps in dependencies.values())
        
        # Simple complexity score based on structure
        if task_count == 0:
            return 0.0
        
        # Normalize by task count
        dependency_ratio = dependency_count / task_count
        
        # Score from 0 to 1, where higher means more complex
        complexity_score = min(dependency_ratio / 3.0, 1.0)  # Assume 3 deps per task is high complexity
        
        return complexity_score
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        return {
            'total_optimizations': self._total_optimizations,
            'recommendations_generated': self._recommendations_generated,
            'optimizations_applied': self._optimizations_applied,
            'dag_executions_recorded': len(self._dag_history),
            'optimization_history_count': len(self._optimization_history)
        }


# Convenience functions
def create_dag_optimizer() -> DAGOptimizer:
    """Factory function to create DAG optimizer."""
    return DAGOptimizer()