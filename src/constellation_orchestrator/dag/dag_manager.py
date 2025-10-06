"""DAG Manager for Constellation Orchestrator."""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
import structlog

from ..models.task_definition import TaskDefinition, TaskBatch
from ..core.config import ConstellationConfig
from .graph_algorithms import GraphAlgorithms


@dataclass
class DAGValidationResult:
    """Result of DAG validation."""
    is_valid: bool
    cycles: List[List[str]]
    orphaned_tasks: List[str]
    execution_order: List[str]
    validation_errors: List[str]
    validation_warnings: List[str]
    statistics: Dict[str, Any]


class DAGManager:
    """Manages DAG construction, validation, and execution ordering."""
    
    def __init__(self, config: ConstellationConfig):
        """Initialize DAG manager."""
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self.graph_algorithms = GraphAlgorithms()
        
        # Task storage
        self.tasks: Dict[str, TaskDefinition] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # Cached results
        self._cached_validation_result: Optional[DAGValidationResult] = None
        self._cached_execution_order: Optional[List[str]] = None
        self._cached_execution_batches: Optional[List[List[str]]] = None
        
        self.logger.info("dag_manager_initialized")
    
    async def initialize(self) -> bool:
        """Initialize DAG manager."""
        try:
            self.logger.info("dag_manager_initializing")
            return True
        except Exception as e:
            self.logger.error(
                "dag_manager_initialization_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def load_tasks(self, task_definitions: List[TaskDefinition]) -> bool:
        """Load task definitions and build dependency graph."""
        try:
            self.logger.info(
                "dag_loading_tasks",
                task_count=len(task_definitions)
            )
            
            # Clear existing data
            self.tasks.clear()
            self.dependency_graph.clear()
            self._clear_cache()
            
            # Validate task uniqueness
            task_ids = [task.task_id for task in task_definitions]
            if len(task_ids) != len(set(task_ids)):
                duplicate_ids = [tid for tid in set(task_ids) if task_ids.count(tid) > 1]
                self.logger.error(
                    "dag_duplicate_task_ids",
                    duplicate_ids=duplicate_ids
                )
                return False
            
            # Load tasks
            for task in task_definitions:
                self.tasks[task.task_id] = task
                self.dependency_graph[task.task_id] = task.dependencies.copy()
            
            self.logger.info(
                "dag_tasks_loaded",
                task_count=len(self.tasks),
                total_dependencies=sum(len(deps) for deps in self.dependency_graph.values())
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "dag_task_loading_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def load_task_batch(self, task_batch: TaskBatch) -> bool:
        """Load tasks from a task batch."""
        try:
            # Validate batch dependencies
            dependency_errors = task_batch.validate_dependencies()
            if dependency_errors:
                self.logger.error(
                    "dag_batch_dependency_errors",
                    batch_id=task_batch.batch_id,
                    errors=dependency_errors
                )
                return False
            
            return await self.load_tasks(task_batch.tasks)
            
        except Exception as e:
            self.logger.error(
                "dag_batch_loading_failed",
                batch_id=task_batch.batch_id if hasattr(task_batch, 'batch_id') else 'unknown',
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def validate_dag(self) -> DAGValidationResult:
        """Validate DAG structure and return comprehensive results."""
        if self._cached_validation_result:
            return self._cached_validation_result
        
        try:
            self.logger.info("dag_validation_starting")
            
            # Perform comprehensive graph validation
            validation_results = self.graph_algorithms.validate_graph_structure(self.dependency_graph)
            
            # Get execution order (will be None if cycles exist)
            execution_order = self.graph_algorithms.topological_sort(self.dependency_graph)
            
            # Create validation result
            result = DAGValidationResult(
                is_valid=validation_results['is_valid'] and execution_order is not None,
                cycles=self.graph_algorithms.detect_cycles(self.dependency_graph),
                orphaned_tasks=self.graph_algorithms.find_orphaned_nodes(self.dependency_graph),
                execution_order=execution_order or [],
                validation_errors=validation_results['errors'],
                validation_warnings=validation_results['warnings'],
                statistics=validation_results['statistics']
            )
            
            # Cache result
            self._cached_validation_result = result
            
            self.logger.info(
                "dag_validation_completed",
                is_valid=result.is_valid,
                cycle_count=len(result.cycles),
                orphaned_count=len(result.orphaned_tasks),
                execution_order_length=len(result.execution_order),
                error_count=len(result.validation_errors),
                warning_count=len(result.validation_warnings)
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "dag_validation_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Return failed validation result
            return DAGValidationResult(
                is_valid=False,
                cycles=[],
                orphaned_tasks=[],
                execution_order=[],
                validation_errors=[f"Validation failed: {str(e)}"],
                validation_warnings=[],
                statistics={}
            )
    
    async def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """Get tasks ready for execution based on completed dependencies."""
        try:
            ready_tasks = self.graph_algorithms.find_ready_nodes(
                self.dependency_graph, 
                completed_tasks
            )
            
            # Filter out tasks that don't exist (safety check)
            valid_ready_tasks = [task_id for task_id in ready_tasks if task_id in self.tasks]
            
            if len(valid_ready_tasks) != len(ready_tasks):
                invalid_tasks = set(ready_tasks) - set(valid_ready_tasks)
                self.logger.warning(
                    "dag_invalid_ready_tasks_filtered",
                    invalid_tasks=list(invalid_tasks)
                )
            
            self.logger.debug(
                "dag_ready_tasks_identified",
                ready_count=len(valid_ready_tasks),
                completed_count=len(completed_tasks),
                ready_tasks=valid_ready_tasks[:10]  # Log first 10 for debugging
            )
            
            return valid_ready_tasks
            
        except Exception as e:
            self.logger.error(
                "dag_ready_tasks_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    async def get_execution_order(self) -> List[str]:
        """Get topologically sorted execution order."""
        if self._cached_execution_order:
            return self._cached_execution_order
        
        try:
            execution_order = self.graph_algorithms.topological_sort(self.dependency_graph)
            
            if execution_order:
                self._cached_execution_order = execution_order
                
                self.logger.debug(
                    "dag_execution_order_generated",
                    order_length=len(execution_order),
                    first_tasks=execution_order[:5],
                    last_tasks=execution_order[-5:] if len(execution_order) > 5 else []
                )
            else:
                self.logger.error("dag_execution_order_failed_cycles_detected")
            
            return execution_order or []
            
        except Exception as e:
            self.logger.error(
                "dag_execution_order_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    async def get_execution_batches(self) -> List[List[str]]:
        """Get tasks grouped into parallel execution batches."""
        if self._cached_execution_batches:
            return self._cached_execution_batches
        
        try:
            batches = self.graph_algorithms.get_execution_batches(self.dependency_graph)
            
            if batches:
                self._cached_execution_batches = batches
                
                self.logger.debug(
                    "dag_execution_batches_generated",
                    batch_count=len(batches),
                    batch_sizes=[len(batch) for batch in batches],
                    max_parallelism=max(len(batch) for batch in batches) if batches else 0
                )
            
            return batches
            
        except Exception as e:
            self.logger.error(
                "dag_execution_batches_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    def get_task_by_id(self, task_id: str) -> Optional[TaskDefinition]:
        """Get task definition by ID."""
        return self.tasks.get(task_id)
    
    def get_task_dependencies(self, task_id: str) -> List[str]:
        """Get dependencies for a specific task."""
        return self.dependency_graph.get(task_id, [])
    
    def get_task_dependents(self, task_id: str) -> List[str]:
        """Get tasks that depend on the given task."""
        dependents = []
        for task, deps in self.dependency_graph.items():
            if task_id in deps:
                dependents.append(task)
        return dependents
    
    def get_task_count(self) -> int:
        """Get total number of tasks."""
        return len(self.tasks)
    
    def has_tasks(self) -> bool:
        """Check if any tasks are loaded."""
        return len(self.tasks) > 0
    
    def get_root_tasks(self) -> List[str]:
        """Get tasks with no dependencies."""
        return [task_id for task_id, deps in self.dependency_graph.items() if not deps]
    
    def get_leaf_tasks(self) -> List[str]:
        """Get tasks that no other tasks depend on."""
        all_dependencies = set()
        for deps in self.dependency_graph.values():
            all_dependencies.update(deps)
        
        return [task_id for task_id in self.tasks.keys() if task_id not in all_dependencies]
    
    def get_task_level(self, task_id: str) -> int:
        """Get the level of a task in the DAG (distance from root)."""
        levels = self.graph_algorithms.calculate_node_levels(self.dependency_graph)
        return levels.get(task_id, -1)
    
    def get_critical_path(self) -> List[str]:
        """Get the critical path (longest path through the DAG)."""
        try:
            levels = self.graph_algorithms.calculate_node_levels(self.dependency_graph)
            if not levels:
                return []
            
            # Find the task with the highest level
            max_level = max(levels.values())
            end_tasks = [task for task, level in levels.items() if level == max_level]
            
            if not end_tasks:
                return []
            
            # Trace back the critical path from one of the end tasks
            def trace_path(task_id: str, path: List[str]) -> List[str]:
                path = path + [task_id]
                dependencies = self.dependency_graph.get(task_id, [])
                
                if not dependencies:
                    return path
                
                # Find the dependency with the highest level
                dep_levels = [(dep, levels.get(dep, 0)) for dep in dependencies]
                critical_dep = max(dep_levels, key=lambda x: x[1])[0]
                
                return trace_path(critical_dep, path)
            
            critical_path = trace_path(end_tasks[0], [])
            critical_path.reverse()  # Reverse to get root-to-leaf order
            
            self.logger.debug(
                "dag_critical_path_calculated",
                path_length=len(critical_path),
                critical_path=critical_path
            )
            
            return critical_path
            
        except Exception as e:
            self.logger.error(
                "dag_critical_path_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return []
    
    def get_dag_statistics(self) -> Dict[str, Any]:
        """Get comprehensive DAG statistics."""
        try:
            validation_result = self.graph_algorithms.validate_graph_structure(self.dependency_graph)
            levels = self.graph_algorithms.calculate_node_levels(self.dependency_graph)
            
            stats = {
                'total_tasks': len(self.tasks),
                'total_dependencies': sum(len(deps) for deps in self.dependency_graph.values()),
                'root_tasks': len(self.get_root_tasks()),
                'leaf_tasks': len(self.get_leaf_tasks()),
                'max_depth': max(levels.values()) if levels else 0,
                'avg_dependencies': validation_result['statistics'].get('avg_dependencies', 0),
                'max_dependencies': validation_result['statistics'].get('max_dependencies', 0),
                'critical_path_length': len(self.get_critical_path()),
                'has_cycles': len(self.graph_algorithms.detect_cycles(self.dependency_graph)) > 0,
                'orphaned_tasks': len(self.graph_algorithms.find_orphaned_nodes(self.dependency_graph))
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(
                "dag_statistics_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return {}
    
    def _clear_cache(self) -> None:
        """Clear cached results."""
        self._cached_validation_result = None
        self._cached_execution_order = None
        self._cached_execution_batches = None
    
    async def health_check(self) -> bool:
        """Health check for DAG manager."""
        try:
            # Basic health checks
            if not hasattr(self, 'tasks') or not hasattr(self, 'dependency_graph'):
                return False
            
            # If we have tasks, validate the DAG structure
            if self.has_tasks():
                validation_result = await self.validate_dag()
                return validation_result.is_valid
            
            return True
            
        except Exception as e:
            self.logger.error(
                "dag_health_check_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    async def shutdown(self) -> None:
        """Shutdown DAG manager."""
        try:
            self.logger.info("dag_manager_shutting_down")
            
            # Clear all data
            self.tasks.clear()
            self.dependency_graph.clear()
            self._clear_cache()
            
            self.logger.info("dag_manager_shutdown_complete")
            
        except Exception as e:
            self.logger.error(
                "dag_manager_shutdown_error",
                error=str(e),
                error_type=type(e).__name__
            )