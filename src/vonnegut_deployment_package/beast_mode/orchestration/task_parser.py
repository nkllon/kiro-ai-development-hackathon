#!/usr/bin/env python3
"""
Task Parser - Convert markdown task lists to DAG format.

Parses the parallelized task list format and converts it to TaskNode
format suitable for DAG validation and execution.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.beast_mode.core.beastly_module import BeastlyModule
from .dag_validator import TaskNode


@dataclass
class ParsedTask:
    """Parsed task information from markdown"""
    task_id: str
    title: str
    description: List[str]
    dependencies: List[str]
    phase: str
    parallel_group: Optional[str]
    requirements: List[str]
    completed: bool


class TaskParser(BeastlyModule):
    """
    Parse markdown task lists into DAG-compatible format.
    
    Handles the parallelized task format with phases, dependencies,
    and parallel execution groups.
    """
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(f"beast_mode.orchestration.{self.__class__.__name__}")
        
        # Parsing patterns
        self._task_pattern = re.compile(r'^- \[([x ])\] (\d+\.\d+) (.+)$')
        self._phase_pattern = re.compile(r'^## Phase \d+: (.+)$')
        self._dependency_pattern = re.compile(r'\*\*Dependencies\*\*:\s*(.+)')
        self._parallel_pattern = re.compile(r'\*\*Parallel\*\*:\s*(.+)')
        self._requirements_pattern = re.compile(r'_Requirements:\s*([^_]+)_')
        
        self._logger.info("TaskParser initialized")
    
    def get_capabilities(self) -> List[Any]:
        """Get module capabilities"""
        return ["TASK_PARSING", "DEPENDENCY_RESOLUTION", "MARKDOWN_PROCESSING"]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get module health status"""
        return {
            "status": "healthy",
            "parser_initialized": True
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation"""
        return {
            "success": True,
            "degraded_capabilities": [],
            "remaining_capabilities": ["TASK_PARSING", "DEPENDENCY_RESOLUTION"]
        }
    
    def parse_task_file(self, file_path: str) -> Dict[str, TaskNode]:
        """
        Parse markdown task file into TaskNode format.
        
        Args:
            file_path: Path to the markdown task file
            
        Returns:
            Dictionary of task_id -> TaskNode
        """
        with self.trace_operation("parse_task_file") as trace:
            try:
                path = Path(file_path)
                if not path.exists():
                    raise FileNotFoundError(f"Task file not found: {file_path}")
                
                content = path.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Parse tasks
                parsed_tasks = self._parse_tasks(lines)
                
                # Convert to TaskNode format
                task_nodes = self._convert_to_task_nodes(parsed_tasks)
                
                # Resolve dependencies
                self._resolve_dependencies(task_nodes, parsed_tasks)
                
                trace.output_result = {
                    'tasks_parsed': len(task_nodes),
                    'file_path': file_path
                }
                
                self._logger.info(f"Parsed {len(task_nodes)} tasks from {file_path}")
                return task_nodes
                
            except Exception as e:
                self._logger.error(f"Failed to parse task file {file_path}: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                raise
    
    def _parse_tasks(self, lines: List[str]) -> List[ParsedTask]:
        """Parse individual tasks from markdown lines"""
        tasks = []
        current_task = None
        current_phase = ""
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Parse phase headers
            phase_match = self._phase_pattern.match(line)
            if phase_match:
                current_phase = phase_match.group(1)
                continue
            
            # Parse task lines
            task_match = self._task_pattern.match(line)
            if task_match:
                completed = task_match.group(1) == 'x'
                task_number = task_match.group(2)
                title = task_match.group(3)
                
                current_task = ParsedTask(
                    task_id=f"task_{task_number}",
                    title=title,
                    description=[],
                    dependencies=[],
                    phase=current_phase,
                    parallel_group=None,
                    requirements=[],
                    completed=completed
                )
                tasks.append(current_task)
                continue
            
            # Parse task details
            if current_task and line.startswith('-'):
                # Task description line
                current_task.description.append(line[1:].strip())
                
                # Check for special markers
                if '**Dependencies**:' in line:
                    deps = self._extract_dependencies(line)
                    current_task.dependencies.extend(deps)
                
                if '**Parallel**:' in line:
                    parallel_info = self._extract_parallel_info(line)
                    current_task.parallel_group = parallel_info
                
                if '_Requirements:' in line:
                    reqs = self._extract_requirements(line)
                    current_task.requirements.extend(reqs)
        
        return tasks
    
    def _extract_dependencies(self, line: str) -> List[str]:
        """Extract dependencies from a line"""
        match = self._dependency_pattern.search(line)
        if not match:
            return []
        
        deps_text = match.group(1)
        
        # Handle different dependency formats
        if "Phase" in deps_text:
            # Phase dependency - extract phase number
            phase_match = re.search(r'Phase (\d+)', deps_text)
            if phase_match:
                phase_num = phase_match.group(1)
                return [f"phase_{phase_num}_complete"]
        
        # Task-specific dependencies
        task_deps = re.findall(r'(\d+\.\d+)', deps_text)
        return [f"task_{dep}" for dep in task_deps]
    
    def _extract_parallel_info(self, line: str) -> Optional[str]:
        """Extract parallel execution information"""
        match = self._parallel_pattern.search(line)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_requirements(self, line: str) -> List[str]:
        """Extract requirement references"""
        match = self._requirements_pattern.search(line)
        if not match:
            return []
        
        reqs_text = match.group(1)
        # Extract requirement numbers
        req_numbers = re.findall(r'(\d+\.\d+)', reqs_text)
        return req_numbers
    
    def _convert_to_task_nodes(self, parsed_tasks: List[ParsedTask]) -> Dict[str, TaskNode]:
        """Convert parsed tasks to TaskNode format"""
        task_nodes = {}
        
        for task in parsed_tasks:
            node = TaskNode(
                task_id=task.task_id,
                dependencies=[],  # Will be resolved later
                dependents=[],    # Will be calculated
                metadata={
                    'title': task.title,
                    'description': task.description,
                    'phase': task.phase,
                    'parallel_group': task.parallel_group,
                    'requirements': task.requirements,
                    'completed': task.completed,
                    'task_number': task.task_id.replace('task_', '')
                }
            )
            task_nodes[task.task_id] = node
        
        return task_nodes
    
    def _resolve_dependencies(self, task_nodes: Dict[str, TaskNode], 
                            parsed_tasks: List[ParsedTask]):
        """Resolve task dependencies and build dependency graph"""
        
        # Create mapping from parsed tasks to nodes
        task_map = {task.task_id: task for task in parsed_tasks}
        
        # Resolve explicit dependencies
        for task_id, node in task_nodes.items():
            parsed_task = task_map[task_id]
            
            # Add explicit dependencies
            for dep in parsed_task.dependencies:
                if dep in task_nodes:
                    node.dependencies.append(dep)
        
        # Resolve phase dependencies
        self._resolve_phase_dependencies(task_nodes, parsed_tasks)
        
        # Calculate dependents (reverse dependencies)
        for task_id, node in task_nodes.items():
            for dep in node.dependencies:
                if dep in task_nodes:
                    task_nodes[dep].dependents.append(task_id)
    
    def _resolve_phase_dependencies(self, task_nodes: Dict[str, TaskNode], 
                                  parsed_tasks: List[ParsedTask]):
        """Resolve phase-based dependencies"""
        
        # Group tasks by phase
        phase_tasks = {}
        for task in parsed_tasks:
            if task.phase not in phase_tasks:
                phase_tasks[task.phase] = []
            phase_tasks[task.phase].append(task.task_id)
        
        # Define phase order based on our task structure
        phase_order = [
            "Infrastructure (Completed)",
            "Preparation & Schema (Parallel Execution)",
            "Schema Implementation (Sequential within, Parallel between)",
            "Component Integration (Parallel Execution)",
            "Synchronization (Sequential)",
            "Final Integration Testing (Parallel Test Execution)"
        ]
        
        # Add phase dependencies
        for i, phase in enumerate(phase_order[1:], 1):
            if phase in phase_tasks and phase_order[i-1] in phase_tasks:
                # All tasks in current phase depend on all tasks in previous phase
                current_phase_tasks = phase_tasks[phase]
                previous_phase_tasks = phase_tasks[phase_order[i-1]]
                
                for current_task in current_phase_tasks:
                    if current_task in task_nodes:
                        for prev_task in previous_phase_tasks:
                            if prev_task in task_nodes and prev_task not in task_nodes[current_task].dependencies:
                                task_nodes[current_task].dependencies.append(prev_task)
    
    def create_task_functions(self, task_nodes: Dict[str, TaskNode]) -> Dict[str, callable]:
        """Create executable functions for tasks"""
        task_functions = {}
        
        for task_id, node in task_nodes.items():
            # Create a function that represents the task execution
            def create_task_function(task_node: TaskNode):
                def task_function():
                    # This would be replaced with actual task implementation
                    task_title = task_node.metadata.get('title', 'Unknown Task')
                    self._logger.info(f"Executing task: {task_title}")
                    
                    # Simulate task execution
                    import time
                    time.sleep(1)
                    
                    return f"Task {task_node.task_id} completed successfully"
                
                return task_function
            
            task_functions[task_id] = create_task_function(node)
        
        return task_functions