#!/usr/bin/env python3
"""
Beast Mode Task List Converter
=============================

Converts legacy sequential task lists to Beast Mode hierarchical format
with parallel execution capabilities.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import re
import hashlib
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


@dataclass
class LegacyTask:
    """Represents a legacy sequential task"""
    number: str
    title: str
    description: List[str]
    dependencies: List[str]
    status: str
    line_number: int


@dataclass
class BeastModeTask:
    """Represents a Beast Mode hierarchical task"""
    phase: int
    task_number: int
    hierarchical_number: str  # e.g., "1.1", "2.3"
    title: str
    description: List[str]
    dependencies: List[str]
    status: str
    hash_id: str
    parallel_group: bool
    annotations: List[str]


@dataclass
class ConversionResult:
    """Result of task list conversion"""
    success: bool
    original_tasks: int
    converted_tasks: int
    parallel_phases: int
    time_reduction_estimate: float
    beast_mode_content: str
    conversion_report: Dict[str, Any]
    error_message: Optional[str] = None


class BeastModeConverter(ReflectiveModule):
    """
    Beast Mode Task List Converter - RM-DDD Compliant
    
    Converts legacy sequential task lists to Beast Mode hierarchical format
    enabling parallel execution and systematic task management.
    
    Single Responsibility: Convert task lists to Beast Mode format
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "BeastModeConverter"
        self._config = config or {}
        self._logger = logging.getLogger(f"beast_mode.task_dag.{self.__class__.__name__}")
        
        # Legacy task parsing patterns
        self._legacy_task_pattern = re.compile(r'^- \[(.)\] (\d+)\. (.+?)(?:\s+\[([^\]]+)\])?.*$')
        self._dependency_pattern = re.compile(r'\*\*Dependencies\*\*:\s*(.+)')
        
        # Conversion statistics
        self._conversions_performed = 0
        self._total_time_saved = 0.0
        
        self._logger.info(f"BeastModeConverter initialized")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "BeastModeConverter",
            "version": "1.0.0",
            "description": "Converts legacy task lists to Beast Mode hierarchical format",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "conversions_performed": self._conversions_performed,
            "estimated_time_saved": self._total_time_saved
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
            # Test conversion capability
            test_content = "- [ ] 1. Test Task\n  - Test description"
            result = self._parse_legacy_tasks(test_content)
            
            if len(result) > 0:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            else:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = ["No tasks parsed in test"]
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Conversion test failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=self._get_current_timestamp(),
            uptime_seconds=self._get_uptime()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, can still do basic conversion
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION  # May lose dependency analysis
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
    
    def convert_task_file(self, input_file: str, output_file: Optional[str] = None) -> ConversionResult:
        """
        Convert legacy task file to Beast Mode format
        
        Args:
            input_file: Path to legacy tasks.md file
            output_file: Optional output path (defaults to input_file with backup)
            
        Returns:
            ConversionResult with conversion details and Beast Mode content
        """
        with self.trace_operation("convert_task_file") as trace:
            try:
                input_path = Path(input_file)
                if not input_path.exists():
                    raise FileNotFoundError(f"Input file not found: {input_file}")
                
                # Read and parse legacy content
                content = input_path.read_text(encoding='utf-8')
                legacy_tasks = self._parse_legacy_tasks(content)
                
                if not legacy_tasks:
                    return ConversionResult(
                        success=False,
                        original_tasks=0,
                        converted_tasks=0,
                        parallel_phases=0,
                        time_reduction_estimate=0.0,
                        beast_mode_content="",
                        conversion_report={},
                        error_message="No legacy tasks found to convert"
                    )
                
                # Analyze dependencies and create parallel phases
                beast_mode_tasks = self._create_beast_mode_structure(legacy_tasks)
                
                # Generate Beast Mode content
                beast_mode_content = self._generate_beast_mode_content(beast_mode_tasks, content)
                
                # Calculate performance improvements
                parallel_phases = len(set(task.phase for task in beast_mode_tasks))
                time_reduction = self._estimate_time_reduction(beast_mode_tasks)
                
                # Create conversion report
                conversion_report = self._create_conversion_report(legacy_tasks, beast_mode_tasks)
                
                # Write output if specified
                if output_file:
                    output_path = Path(output_file)
                    output_path.write_text(beast_mode_content, encoding='utf-8')
                
                result = ConversionResult(
                    success=True,
                    original_tasks=len(legacy_tasks),
                    converted_tasks=len(beast_mode_tasks),
                    parallel_phases=parallel_phases,
                    time_reduction_estimate=time_reduction,
                    beast_mode_content=beast_mode_content,
                    conversion_report=conversion_report
                )
                
                # Update statistics
                self._conversions_performed += 1
                self._total_time_saved += time_reduction
                
                trace.output_result = {
                    'original_tasks': len(legacy_tasks),
                    'converted_tasks': len(beast_mode_tasks),
                    'parallel_phases': parallel_phases,
                    'time_reduction': time_reduction
                }
                
                self._logger.info(f"Converted {len(legacy_tasks)} tasks to Beast Mode format")
                return result
                
            except Exception as e:
                self._logger.error(f"Conversion failed: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                return ConversionResult(
                    success=False,
                    original_tasks=0,
                    converted_tasks=0,
                    parallel_phases=0,
                    time_reduction_estimate=0.0,
                    beast_mode_content="",
                    conversion_report={},
                    error_message=str(e)
                )
    
    def _parse_legacy_tasks(self, content: str) -> List[LegacyTask]:
        """Parse legacy sequential tasks from content"""
        lines = content.split('\n')
        tasks = []
        current_task = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Parse task line
            task_match = self._legacy_task_pattern.match(line)
            if task_match:
                if current_task:
                    tasks.append(current_task)
                
                status_char, number, title, hash_id = task_match.groups()
                current_task = LegacyTask(
                    number=number,
                    title=title,
                    description=[],
                    dependencies=[],
                    status=status_char,
                    line_number=line_num
                )
            
            # Parse description lines
            elif current_task and line.startswith('- ') and not line.startswith('- ['):
                current_task.description.append(line)
            
            # Parse dependencies
            elif current_task and '**Dependencies**:' in line:
                deps = self._parse_dependencies(line)
                current_task.dependencies = deps
        
        # Add final task
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def _parse_dependencies(self, line: str) -> List[str]:
        """Parse task dependencies from line"""
        match = self._dependency_pattern.search(line)
        if not match:
            return []
        
        deps_text = match.group(1)
        # Extract task numbers from dependencies
        dep_numbers = re.findall(r'(\d+)', deps_text)
        return dep_numbers
    
    def _create_beast_mode_structure(self, legacy_tasks: List[LegacyTask]) -> List[BeastModeTask]:
        """Create Beast Mode hierarchical structure with parallel phases"""
        beast_mode_tasks = []
        
        # Analyze dependencies to create phases
        phases = self._analyze_parallel_phases(legacy_tasks)
        
        for phase_num, phase_tasks in phases.items():
            for task_num, legacy_task in enumerate(phase_tasks, 1):
                # Generate hash ID
                hash_id = self._generate_hash_id(legacy_task.title)
                
                # Determine if task can run in parallel
                parallel_group = len(phase_tasks) > 1
                
                # Create annotations
                annotations = []
                if parallel_group:
                    annotations.append("⚡ PARALLEL")
                else:
                    annotations.append("🔄 SEQUENTIAL")
                
                if legacy_task.dependencies:
                    dep_refs = ", ".join(f"{dep}" for dep in legacy_task.dependencies)
                    annotations.append(f"(depends on {dep_refs})")
                
                beast_mode_task = BeastModeTask(
                    phase=phase_num,
                    task_number=task_num,
                    hierarchical_number=f"{phase_num}.{task_num}",
                    title=legacy_task.title,
                    description=legacy_task.description,
                    dependencies=legacy_task.dependencies,
                    status=legacy_task.status,
                    hash_id=hash_id,
                    parallel_group=parallel_group,
                    annotations=annotations
                )
                
                beast_mode_tasks.append(beast_mode_task)
        
        return beast_mode_tasks
    
    def _analyze_parallel_phases(self, tasks: List[LegacyTask]) -> Dict[int, List[LegacyTask]]:
        """Analyze task dependencies to create parallel execution phases"""
        phases = {}
        task_map = {task.number: task for task in tasks}
        processed = set()
        phase_num = 1
        
        while len(processed) < len(tasks):
            # Find tasks with no unmet dependencies
            ready_tasks = []
            for task in tasks:
                if task.number in processed:
                    continue
                
                # Check if all dependencies are satisfied
                deps_met = all(dep in processed for dep in task.dependencies)
                if deps_met:
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Handle circular dependencies or missing deps
                remaining = [t for t in tasks if t.number not in processed]
                ready_tasks = remaining[:1]  # Force progress
            
            phases[phase_num] = ready_tasks
            processed.update(task.number for task in ready_tasks)
            phase_num += 1
        
        return phases
    
    def _generate_hash_id(self, title: str) -> str:
        """Generate unique hash ID for task"""
        # Create hash from title
        hash_obj = hashlib.md5(title.encode())
        hash_hex = hash_obj.hexdigest()[:4]
        
        # Create prefix from title
        words = title.lower().split()
        if len(words) >= 2:
            prefix = words[0][:2] + words[1][:2]
        else:
            prefix = words[0][:4] if words else "task"
        
        return f"{prefix}-{hash_hex}"
    
    def _generate_beast_mode_content(self, beast_mode_tasks: List[BeastModeTask], original_content: str) -> str:
        """Generate Beast Mode formatted content"""
        # Extract header content (everything before tasks)
        lines = original_content.split('\n')
        header_lines = []
        task_section_started = False
        
        for line in lines:
            if re.match(r'^- \[.\] \d+\.', line.strip()):
                task_section_started = True
                break
            if not task_section_started:
                header_lines.append(line)
        
        # Build Beast Mode content
        content_lines = header_lines.copy()
        content_lines.append("")
        content_lines.append("## Beast Mode Hierarchical Implementation Tasks")
        content_lines.append("")
        
        # Group tasks by phase
        phases = {}
        for task in beast_mode_tasks:
            if task.phase not in phases:
                phases[task.phase] = []
            phases[task.phase].append(task)
        
        # Generate phase sections
        for phase_num in sorted(phases.keys()):
            phase_tasks = phases[phase_num]
            
            # Determine phase type
            if len(phase_tasks) > 1:
                phase_type = "Parallel Execution ⚡ PARALLEL EXECUTION"
            else:
                phase_type = "Sequential Integration 🔄 SEQUENTIAL"
            
            content_lines.append(f"### Phase {phase_num}: {phase_type}")
            content_lines.append("")
            
            # Add tasks
            for task in phase_tasks:
                status_char = task.status
                annotations = " ".join(task.annotations)
                
                task_line = f"- [{status_char}] {task.hierarchical_number} {task.title} [{task.hash_id}] {annotations}"
                content_lines.append(task_line)
                
                # Add description lines
                for desc_line in task.description:
                    content_lines.append(f"  {desc_line}")
                
                content_lines.append("")
        
        return '\n'.join(content_lines)
    
    def _estimate_time_reduction(self, beast_mode_tasks: List[BeastModeTask]) -> float:
        """Estimate time reduction from parallel execution"""
        total_tasks = len(beast_mode_tasks)
        phases = len(set(task.phase for task in beast_mode_tasks))
        
        # Simple estimation: sequential time vs parallel time
        sequential_time = total_tasks  # Assume 1 time unit per task
        parallel_time = phases  # Assume phases can run in parallel
        
        if sequential_time > 0:
            time_reduction = (sequential_time - parallel_time) / sequential_time
            return min(time_reduction, 0.8)  # Cap at 80% improvement
        
        return 0.0
    
    def _create_conversion_report(self, legacy_tasks: List[LegacyTask], beast_mode_tasks: List[BeastModeTask]) -> Dict[str, Any]:
        """Create detailed conversion report"""
        phases = {}
        for task in beast_mode_tasks:
            if task.phase not in phases:
                phases[task.phase] = []
            phases[task.phase].append(task)
        
        parallel_phases = sum(1 for tasks in phases.values() if len(tasks) > 1)
        sequential_phases = len(phases) - parallel_phases
        
        return {
            "conversion_summary": {
                "original_tasks": len(legacy_tasks),
                "converted_tasks": len(beast_mode_tasks),
                "total_phases": len(phases),
                "parallel_phases": parallel_phases,
                "sequential_phases": sequential_phases
            },
            "parallel_opportunities": {
                "max_parallel_tasks": max(len(tasks) for tasks in phases.values()),
                "total_parallel_tasks": sum(len(tasks) for tasks in phases.values() if len(tasks) > 1),
                "parallelization_ratio": parallel_phases / len(phases) if phases else 0
            },
            "phase_breakdown": {
                f"phase_{phase_num}": {
                    "tasks": len(tasks),
                    "parallel": len(tasks) > 1,
                    "task_numbers": [task.hierarchical_number for task in tasks]
                }
                for phase_num, tasks in phases.items()
            }
        }
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now()
    
    def _get_uptime(self):
        """Get uptime in seconds"""
        from datetime import datetime
        return (datetime.now() - self._start_time).total_seconds()