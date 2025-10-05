#!/usr/bin/env python3
"""
Dynamic DAG Modifier for DAG Orchestration
==========================================

Implementation of dynamic DAG modification during execution with
consistency validation and safe modification operations.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from copy import deepcopy
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.rm_ddd.core.dag_registry import DAGRegistry
from src.dag_orchestration.execution.parallel_execution_engine import TaskDefinition


class ModificationType(Enum):
    """Types of DAG modifications."""
    ADD_TASK = "add_task"
    REMOVE_TASK = "remove_task"
    MODIFY_TASK = "modify_task"
    ADD_DEPENDENCY = "add_dependency"
    REMOVE_DEPENDENCY = "remove_dependency"
    REPLACE_TASK = "replace_task"


class ModificationStatus(Enum):
    """Status of DAG modifications."""
    PENDING = "pending"
    VALIDATING = "validating"
    APPLYING = "applying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DAGModification:
    """Definition of a DAG modification operation."""
    modification_id: str
    modification_type: ModificationType
    target_task_id: Optional[str] = None
    new_task: Optional[TaskDefinition] = None
    dependency_source: Optional[str] = None
    dependency_target: Optional[str] = None
    modification_data: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: ModificationStatus = ModificationStatus.PENDING
    validation_result: Optional[Dict[str, Any]] = None
    rollback_data: Optional[Dict[str, Any]] = None


@dataclass
class DAGSnapshot:
    """Snapshot of DAG state for rollback purposes."""
    snapshot_id: str
    timestamp: datetime
    tasks: Dict[str, TaskDefinition]
    dependencies: Dict[str, Set[str]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DAGConsistencyValidator:
    """Validator for DAG consistency during modifications."""
    
    def __init__(self):
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        self._dag_registry = DAGRegistry()
    
    def validate_modification(self, current_dag: Dict[str, TaskDefinition],
                            modification: DAGModification) -> Dict[str, Any]:
        """Validate a DAG modification for consistency."""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'affected_tasks': [],
            'cycle_check_passed': True,
            'dependency_check_passed': True
        }
        
        try:
            # Create a copy of the DAG for validation
            test_dag = deepcopy(current_dag)
            
            # Apply modification to test DAG
            self._apply_modification_to_test_dag(test_dag, modification)
            
            # Check for cycles using DAG registry
            temp_registry = DAGRegistry()
            for task_id, task in test_dag.items():
                temp_registry.register_module(task_id, task.dependencies)
            
            if not temp_registry.validate_dag():
                validation_result['is_valid'] = False
                validation_result['cycle_check_passed'] = False
                validation_result['errors'].append("Modification would create cycles in DAG")
            
            # Validate dependencies exist
            for task_id, task in test_dag.items():
                for dep_id in task.dependencies:
                    if dep_id not in test_dag:
                        validation_result['is_valid'] = False
                        validation_result['dependency_check_passed'] = False
                        validation_result['errors'].append(f"Task {task_id} depends on non-existent task {dep_id}")
            
            # Identify affected tasks
            validation_result['affected_tasks'] = self._identify_affected_tasks(
                current_dag, test_dag, modification
            )
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation failed: {str(e)}")
            self._logger.error(f"DAG modification validation failed: {e}")
        
        return validation_result
    
    def _apply_modification_to_test_dag(self, test_dag: Dict[str, TaskDefinition],
                                      modification: DAGModification) -> None:
        """Apply modification to test DAG for validation."""
        if modification.modification_type == ModificationType.ADD_TASK:
            if modification.new_task:
                test_dag[modification.new_task.task_id] = modification.new_task
        
        elif modification.modification_type == ModificationType.REMOVE_TASK:
            if modification.target_task_id and modification.target_task_id in test_dag:
                del test_dag[modification.target_task_id]
                # Remove dependencies to this task
                for task in test_dag.values():
                    task.dependencies.discard(modification.target_task_id)
        
        elif modification.modification_type == ModificationType.ADD_DEPENDENCY:
            if (modification.dependency_source and modification.dependency_target and
                modification.dependency_target in test_dag):
                test_dag[modification.dependency_target].dependencies.add(modification.dependency_source)
        
        elif modification.modification_type == ModificationType.REMOVE_DEPENDENCY:
            if (modification.dependency_source and modification.dependency_target and
                modification.dependency_target in test_dag):
                test_dag[modification.dependency_target].dependencies.discard(modification.dependency_source)
    
    def _identify_affected_tasks(self, original_dag: Dict[str, TaskDefinition],
                               modified_dag: Dict[str, TaskDefinition],
                               modification: DAGModification) -> List[str]:
        """Identify tasks affected by the modification."""
        affected_tasks = set()
        
        # Direct target of modification
        if modification.target_task_id:
            affected_tasks.add(modification.target_task_id)
        
        # New task being added
        if modification.new_task:
            affected_tasks.add(modification.new_task.task_id)
        
        # Tasks with changed dependencies
        for task_id in original_dag:
            if task_id in modified_dag:
                original_deps = original_dag[task_id].dependencies
                modified_deps = modified_dag[task_id].dependencies
                if original_deps != modified_deps:
                    affected_tasks.add(task_id)
        
        return list(affected_tasks)


class DynamicDAGModifier(ReflectiveModule):
    """
    Dynamic DAG modifier for runtime DAG modifications.
    
    Features:
    - Safe DAG modifications during execution
    - Consistency validation before applying changes
    - Rollback capabilities
    - Modification history tracking
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "DynamicDAGModifier"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Components
        self._validator = DAGConsistencyValidator()
        
        # State management
        self._current_dag: Dict[str, TaskDefinition] = {}
        self._modification_history: List[DAGModification] = []
        self._snapshots: Dict[str, DAGSnapshot] = {}
        
        # Statistics
        self._total_modifications = 0
        self._successful_modifications = 0
        self._failed_modifications = 0
        
        self._logger.info("DynamicDAGModifier initialized")
    
    def initialize_dag(self, tasks: List[TaskDefinition]) -> str:
        """Initialize DAG with initial set of tasks."""
        self._current_dag = {task.task_id: task for task in tasks}
        snapshot_id = self._create_snapshot("initial_dag")
        self._logger.info(f"Initialized DAG with {len(tasks)} tasks")
        return snapshot_id
    
    async def apply_modification(self, modification: DAGModification) -> Dict[str, Any]:
        """Apply a DAG modification with validation."""
        self._total_modifications += 1
        
        try:
            # Create snapshot before modification
            snapshot_id = self._create_snapshot(f"before_{modification.modification_id}")
            
            # Validate modification
            validation_result = self._validator.validate_modification(self._current_dag, modification)
            
            if not validation_result['is_valid']:
                self._failed_modifications += 1
                return {
                    'success': False,
                    'modification_id': modification.modification_id,
                    'validation_result': validation_result,
                    'error': 'Modification failed validation'
                }
            
            # Apply modification
            await self._apply_modification_to_dag(modification)
            self._successful_modifications += 1
            self._modification_history.append(modification)
            
            return {
                'success': True,
                'modification_id': modification.modification_id,
                'validation_result': validation_result,
                'affected_tasks': validation_result['affected_tasks'],
                'snapshot_id': snapshot_id
            }
            
        except Exception as e:
            self._failed_modifications += 1
            self._logger.error(f"Failed to apply modification: {e}")
            return {
                'success': False,
                'modification_id': modification.modification_id,
                'error': str(e)
            }
    
    async def _apply_modification_to_dag(self, modification: DAGModification) -> None:
        """Apply modification to the current DAG."""
        if modification.modification_type == ModificationType.ADD_TASK:
            if modification.new_task:
                self._current_dag[modification.new_task.task_id] = modification.new_task
        
        elif modification.modification_type == ModificationType.REMOVE_TASK:
            if modification.target_task_id and modification.target_task_id in self._current_dag:
                del self._current_dag[modification.target_task_id]
                # Remove dependencies to this task
                for task in self._current_dag.values():
                    task.dependencies.discard(modification.target_task_id)
        
        elif modification.modification_type == ModificationType.ADD_DEPENDENCY:
            if (modification.dependency_source and modification.dependency_target and
                modification.dependency_target in self._current_dag):
                self._current_dag[modification.dependency_target].dependencies.add(modification.dependency_source)
        
        elif modification.modification_type == ModificationType.REMOVE_DEPENDENCY:
            if (modification.dependency_source and modification.dependency_target and
                modification.dependency_target in self._current_dag):
                self._current_dag[modification.dependency_target].dependencies.discard(modification.dependency_source)
    
    def _create_snapshot(self, reason: str) -> str:
        """Create a snapshot of the current DAG state."""
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        snapshot = DAGSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            tasks=deepcopy(self._current_dag),
            dependencies={task_id: task.dependencies.copy() for task_id, task in self._current_dag.items()},
            metadata={'reason': reason, 'dag_size': len(self._current_dag)}
        )
        
        self._snapshots[snapshot_id] = snapshot
        return snapshot_id
    
    def create_add_task_modification(self, task: TaskDefinition, reason: str = "") -> DAGModification:
        """Create a modification to add a task."""
        return DAGModification(
            modification_id=str(uuid.uuid4()),
            modification_type=ModificationType.ADD_TASK,
            new_task=task,
            reason=reason
        )
    
    def create_remove_task_modification(self, task_id: str, reason: str = "") -> DAGModification:
        """Create a modification to remove a task."""
        return DAGModification(
            modification_id=str(uuid.uuid4()),
            modification_type=ModificationType.REMOVE_TASK,
            target_task_id=task_id,
            reason=reason
        )
    
    def get_current_dag(self) -> Dict[str, TaskDefinition]:
        """Get current DAG state."""
        return deepcopy(self._current_dag)
    
    def get_modification_statistics(self) -> Dict[str, Any]:
        """Get modification statistics."""
        success_rate = self._successful_modifications / max(self._total_modifications, 1)
        
        return {
            'total_modifications': self._total_modifications,
            'successful_modifications': self._successful_modifications,
            'failed_modifications': self._failed_modifications,
            'success_rate': success_rate,
            'current_dag_size': len(self._current_dag),
            'snapshots_stored': len(self._snapshots)
        }


# Convenience functions
def create_dynamic_dag_modifier() -> DynamicDAGModifier:
    """Factory function to create dynamic DAG modifier."""
    return DynamicDAGModifier()


def create_dag_consistency_validator() -> DAGConsistencyValidator:
    """Factory function to create DAG consistency validator."""
    return DAGConsistencyValidator()