#!/usr/bin/env python3
"""
Hierarchical Task Parser - Beast Mode DAG Execution
==================================================

Parses hierarchical task numbering (1.1, 1.2, 2.1) and creates execution DAGs
for parallel task execution. Integrates with existing PDCA orchestrator.

Author: Beast Mode Framework  
Date: 2025-01-16
Version: 1.0
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)


class TaskStatus(Enum):
    """Task execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class HierarchicalTask:
    """Represents a hierarchical task with dependencies"""
    task_id: str
    number: str  # e.g., "1.1", "2.3"
    title: str
    description: str
    dependencies: List[str]
    status: TaskStatus
    file_path: str
    line_number: int
    hash_id: Optional[str] = None


@dataclass
class TaskDAG:
    """Directed Acyclic Graph of tasks with parallel execution waves"""
    tasks: Dict[str, HierarchicalTask]
    execution_waves: List[List[str]]  # Tasks that can run in parallel
    dependency_map: Dict[str, List[str]]


class HierarchicalTaskParser(ReflectiveModule):
    """
    Hierarchical Task Parser - RM-DDD Compliant
    
    Parses markdown task files with hierarchical numbering and creates
    execution DAGs for parallel task execution.
    
    Single Responsibility: Parse hierarchical tasks and create execution DAGs
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "HierarchicalTaskParser"
        self._config = config or {}
        self._logger = logging.getLogger(f"beast_mode.task_dag.{self.__class__.__name__}")
        
        # Task parsing patterns
        self._task_pattern = re.compile(r'^- \[(.)\] (\d+(?:\.\d+)*) (.+?) \[([^\]]+)\]')
        self._dependency_pattern = re.compile(r'\*\*Dependencies\*\*:\s*(.+)')
        
        # Parsed tasks storage
        self._tasks: Dict[str, HierarchicalTask] = {}
        self._task_dag: Optional[TaskDAG] = None
        
        self._logger.info(f"HierarchicalTaskParser initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "HierarchicalTaskParser",
            "version": "1.0.0",
            "description": "Parses hierarchical task numbering and creates execution DAGs",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "tasks_parsed": len(self._tasks),
            "dag_created": self._task_dag is not None
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        try:
            # Test parsing capability
            test_line = "- [ ] 1.1 Test Task [test-123]"
            self._parse_task_line(test_line, 1)
            
            status = ModuleStatus.HEALTHY
            health_score = 1.0
            issues = []
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Task parsing failed: {str(e)}"]
        
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
            # In degraded mode, we can still parse simple tasks
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = []
            
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
    
    def parse_task_file(self, file_path: str) -> TaskDAG:
        """
        Parse hierarchical tasks from markdown file and create execution DAG
        
        Args:
            file_path: Path to tasks.md file
            
        Returns:
            TaskDAG with parsed tasks and execution waves
        """
        with self.trace_operation("parse_task_file") as trace:
            try:
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"Task file not found: {file_path}")
                
                content = path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                self._tasks.clear()
                current_task = None
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # Parse task line
                    task_match = self._task_pattern.match(line)
                    if task_match:
                        current_task = self._parse_task_line(line, line_num)
                        if current_task:
                            self._tasks[current_task.task_id] = current_task
                    
                    # Parse dependencies for current task
                    elif current_task and line.startswith('- **Dependencies**:'):
                        deps = self._parse_dependencies(line)
                        current_task.dependencies = deps
                
                # Create DAG from parsed tasks
                self._task_dag = self._create_task_dag()
                
                trace.output_result = {
                    'tasks_parsed': len(self._tasks),
                    'execution_waves': len(self._task_dag.execution_waves),
                    'file_path': file_path
                }
                
                self._logger.info(f"Parsed {len(self._tasks)} tasks from {file_path}")
                return self._task_dag
                
            except Exception as e:
                self._logger.error(f"Failed to parse task file {file_path}: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                raise
    
    def _parse_task_line(self, line: str, line_num: int) -> Optional[HierarchicalTask]:
        """Parse individual task line"""
        match = self._task_pattern.match(line)
        if not match:
            return None
        
        status_char, number, title, hash_id = match.groups()
        
        # Map status character to enum
        status_map = {
            ' ': TaskStatus.NOT_STARTED,
            '-': TaskStatus.IN_PROGRESS, 
            'x': TaskStatus.COMPLETED,
            '!': TaskStatus.FAILED,
            '#': TaskStatus.BLOCKED
        }
        
        status = status_map.get(status_char, TaskStatus.NOT_STARTED)
        task_id = f"{number}_{title.replace(' ', '_').lower()}"
        
        return HierarchicalTask(
            task_id=task_id,
            number=number,
            title=title,
            description="",  # Will be filled from subsequent lines
            dependencies=[],
            status=status,
            file_path="",
            line_number=line_num,
            hash_id=hash_id
        )
    
    def _parse_dependencies(self, line: str) -> List[str]:
        """Parse task dependencies from line"""
        match = self._dependency_pattern.search(line)
        if not match:
            return []
        
        deps_text = match.group(1)
        # Extract task numbers from dependencies
        dep_numbers = re.findall(r'(\d+(?:\.\d+)*)', deps_text)
        return dep_numbers
    
    def _create_task_dag(self) -> TaskDAG:
        """Create DAG with parallel execution waves"""
        # Build dependency map
        dependency_map = {}
        for task in self._tasks.values():
            dependency_map[task.number] = task.dependencies
        
        # Create execution waves for parallel execution
        execution_waves = []
        remaining_tasks = set(self._tasks.keys())
        completed_tasks = set()
        
        while remaining_tasks:
            # Find tasks with no unmet dependencies
            ready_tasks = []
            for task_id in remaining_tasks:
                task = self._tasks[task_id]
                deps_met = all(dep in [t.number for t in self._tasks.values() if t.task_id in completed_tasks] 
                              for dep in task.dependencies)
                if deps_met:
                    ready_tasks.append(task_id)
            
            if not ready_tasks:
                # Circular dependency or missing dependency
                self._logger.warning(f"Circular dependency detected in remaining tasks: {remaining_tasks}")
                ready_tasks = list(remaining_tasks)  # Force execution
            
            execution_waves.append(ready_tasks)
            completed_tasks.update(ready_tasks)
            remaining_tasks -= set(ready_tasks)
        
        return TaskDAG(
            tasks=self._tasks,
            execution_waves=execution_waves,
            dependency_map=dependency_map
        )
    
    def get_parallel_execution_plan(self) -> Dict[str, Any]:
        """Get parallel execution plan for DAG"""
        if not self._task_dag:
            return {"error": "No DAG created. Parse task file first."}
        
        plan = {
            "total_tasks": len(self._task_dag.tasks),
            "execution_waves": len(self._task_dag.execution_waves),
            "max_parallelism": max(len(wave) for wave in self._task_dag.execution_waves),
            "waves": []
        }
        
        for i, wave in enumerate(self._task_dag.execution_waves):
            wave_info = {
                "wave_number": i + 1,
                "parallel_tasks": len(wave),
                "tasks": [
                    {
                        "task_id": task_id,
                        "number": self._task_dag.tasks[task_id].number,
                        "title": self._task_dag.tasks[task_id].title,
                        "status": self._task_dag.tasks[task_id].status.value,
                        "hash_id": self._task_dag.tasks[task_id].hash_id
                    }
                    for task_id in wave
                ]
            }
            plan["waves"].append(wave_info)
        
        return plan