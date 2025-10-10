#!/usr/bin/env python3
"""
DAG Task Executor - Beast Mode Task Execution
=============================================

Executes hierarchical tasks with parallel execution support and task status updates.
Integrates with existing PDCA orchestrator for systematic task execution.

Author: Beast Mode Framework
Date: 2025-01-16  
Version: 1.0
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability, 
    GracefulDegradationResult
)
from .hierarchical_task_parser import HierarchicalTaskParser, TaskDAG, TaskStatus, HierarchicalTask


@dataclass
class TaskUpdateResult:
    """Result of task status update operation"""
    success: bool
    task_id: str
    old_status: TaskStatus
    new_status: TaskStatus
    file_updated: bool
    error_message: Optional[str] = None


class DAGTaskExecutor(ReflectiveModule):
    """
    DAG Task Executor - RM-DDD Compliant
    
    Executes hierarchical tasks with parallel execution and status updates.
    Provides the missing taskStatus functionality for hierarchical numbering.
    
    Single Responsibility: Execute and update hierarchical task status
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "DAGTaskExecutor"
        self._config = config or {}
        self._logger = logging.getLogger(f"beast_mode.task_dag.{self.__class__.__name__}")
        
        # Initialize parser
        self._parser = HierarchicalTaskParser(config)
        self._current_dag: Optional[TaskDAG] = None
        self._current_file_path: Optional[str] = None
        
        # Task status mapping for file updates
        self._status_chars = {
            TaskStatus.NOT_STARTED: ' ',
            TaskStatus.IN_PROGRESS: '-',
            TaskStatus.COMPLETED: 'x',
            TaskStatus.FAILED: '!',
            TaskStatus.BLOCKED: '#'
        }
        
        self._logger.info(f"DAGTaskExecutor initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "DAGTaskExecutor", 
            "version": "1.0.0",
            "description": "Executes hierarchical tasks with parallel execution and status updates",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "current_dag_loaded": self._current_dag is not None,
            "current_file": self._current_file_path
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Test parser health
            parser_health = self._parser.get_health_status()
            
            if parser_health.status == ModuleStatus.HEALTHY:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = [f"Parser issues: {parser_health.issues}"]
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"DAG executor failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=self._get_current_time(),
            uptime_seconds=self._get_uptime_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still update task status manually
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.API_INTEGRATION  # May lose parallel execution
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def load_task_file(self, file_path: str) -> TaskDAG:
        """
        Load and parse hierarchical task file
        
        Args:
            file_path: Path to tasks.md file
            
        Returns:
            TaskDAG with parsed tasks
        """
        with self.trace_operation("load_task_file") as trace:
            try:
                self._current_dag = self._parser.parse_task_file(file_path)
                self._current_file_path = file_path
                
                trace.output_result = {
                    'file_path': file_path,
                    'tasks_loaded': len(self._current_dag.tasks),
                    'execution_waves': len(self._current_dag.execution_waves)
                }
                
                self._logger.info(f"Loaded task file: {file_path}")
                return self._current_dag
                
            except Exception as e:
                self._logger.error(f"Failed to load task file {file_path}: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                raise
    
    def update_task_status(self, task_file_path: str, task_identifier: str, new_status: str) -> TaskUpdateResult:
        """
        Update task status in both memory and file
        
        Args:
            task_file_path: Path to tasks.md file
            task_identifier: Task number (e.g., "1.1") or full task name
            new_status: New status ("not_started", "in_progress", "completed", etc.)
            
        Returns:
            TaskUpdateResult with operation details
        """
        with self.trace_operation("update_task_status") as trace:
            try:
                # Load task file if not already loaded or different file
                if not self._current_dag or self._current_file_path != task_file_path:
                    self.load_task_file(task_file_path)
                
                # Find task by identifier
                task = self._find_task_by_identifier(task_identifier)
                if not task:
                    raise ValueError(f"Task not found: {task_identifier}")
                
                # Parse new status
                try:
                    new_status_enum = TaskStatus(new_status)
                except ValueError:
                    raise ValueError(f"Invalid status: {new_status}")
                
                old_status = task.status
                
                # Update task in memory
                task.status = new_status_enum
                
                # Update file
                file_updated = self._update_task_in_file(task, new_status_enum)
                
                result = TaskUpdateResult(
                    success=True,
                    task_id=task.task_id,
                    old_status=old_status,
                    new_status=new_status_enum,
                    file_updated=file_updated
                )
                
                trace.output_result = {
                    'task_id': task.task_id,
                    'old_status': old_status.value,
                    'new_status': new_status_enum.value,
                    'file_updated': file_updated
                }
                
                self._logger.info(f"Updated task {task.number} from {old_status.value} to {new_status_enum.value}")
                return result
                
            except Exception as e:
                self._logger.error(f"Failed to update task status: {e}")
                result = TaskUpdateResult(
                    success=False,
                    task_id=task_identifier,
                    old_status=TaskStatus.NOT_STARTED,
                    new_status=TaskStatus.NOT_STARTED,
                    file_updated=False,
                    error_message=str(e)
                )
                trace.output_result = {'success': False, 'error': str(e)}
                return result
    
    def _find_task_by_identifier(self, identifier: str) -> Optional[HierarchicalTask]:
        """Find task by number or name"""
        if not self._current_dag:
            return None
        
        # Try to find by task number first
        for task in self._current_dag.tasks.values():
            if task.number == identifier:
                return task
        
        # Try to find by task title
        for task in self._current_dag.tasks.values():
            if identifier in task.title:
                return task
        
        # Try to find by task ID
        return self._current_dag.tasks.get(identifier)
    
    def _update_task_in_file(self, task: HierarchicalTask, new_status: TaskStatus) -> bool:
        """Update task status in the markdown file"""
        try:
            if not self._current_file_path:
                return False
            
            file_path = Path(self._current_file_path)
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Find and update the task line
            status_char = self._status_chars[new_status]
            task_pattern = re.compile(rf'^- \[.\] {re.escape(task.number)}\. {re.escape(task.title)}')
            
            updated = False
            for i, line in enumerate(lines):
                if task_pattern.match(line.strip()):
                    # Replace status character
                    lines[i] = re.sub(r'^- \[.\]', f'- [{status_char}]', line)
                    updated = True
                    break
            
            if updated:
                # Write back to file
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Failed to update file: {e}")
            return False
    
    def get_task_status(self, task_identifier: str) -> Optional[Dict[str, Any]]:
        """Get current task status and details"""
        task = self._find_task_by_identifier(task_identifier)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "number": task.number,
            "title": task.title,
            "status": task.status.value,
            "dependencies": task.dependencies,
            "hash_id": task.hash_id
        }
    
    def get_execution_plan(self) -> Optional[Dict[str, Any]]:
        """Get parallel execution plan"""
        if not self._current_dag:
            return None
        
        return self._parser.get_parallel_execution_plan()
    
    def get_next_ready_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that are ready to execute (dependencies met)"""
        if not self._current_dag:
            return []
        
        ready_tasks = []
        for task in self._current_dag.tasks.values():
            if task.status == TaskStatus.NOT_STARTED:
                # Check if dependencies are met
                deps_met = all(
                    self._find_task_by_identifier(dep) and 
                    self._find_task_by_identifier(dep).status == TaskStatus.COMPLETED
                    for dep in task.dependencies
                )
                
                if deps_met:
                    ready_tasks.append({
                        "task_id": task.task_id,
                        "number": task.number,
                        "title": task.title,
                        "hash_id": task.hash_id
                    })
        
        return ready_tasks