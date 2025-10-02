#!/usr/bin/env python3
"""
Task List Converter - Seamless Integration Component
==================================================

Converts sequential task lists from existing specs to DAG representations
for parallel execution by the DAG orchestration system.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)
from src.rm_ddd.core.dag_registry import DAGRegistry

logger = logging.getLogger(__name__)


@dataclass
class TaskDefinition:
    """Task definition for DAG orchestration."""
    id: str
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)
    requirements_refs: List[str] = field(default_factory=list)


@dataclass
class ConversionResult:
    """Result of task list conversion."""
    success: bool
    task_definitions: List[TaskDefinition] = field(default_factory=list)
    dag_validation: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class TaskListConverter(ReflectiveModule):
    """
    Converts sequential task lists to DAG representations.
    
    Provides seamless integration with existing task execution systems
    by automatically converting markdown task lists to DAG-orchestrated
    parallel execution definitions.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "TaskListConverter"
        self.dag_registry = DAGRegistry()
        self.task_patterns = {
            'checkbox': re.compile(r'^- \[([ x])\] (.+)$', re.MULTILINE),
            'numbered': re.compile(r'^(\d+\.(?:\d+\.)*) (.+)$', re.MULTILINE),
            'dependency': re.compile(r'_Requirements: (.+)_'),
            'description': re.compile(r'- (.+)$', re.MULTILINE)
        }
        
        # Statistics
        self._total_conversions = 0
        self._successful_conversions = 0
        self._total_exports = 0
        self._successful_exports = 0
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "Task List Converter",
            "version": "1.0.0",
            "description": "Converts sequential task lists to DAG representations",
            "statistics": {
                "total_conversions": self._total_conversions,
                "successful_conversions": self._successful_conversions,
                "conversion_success_rate": self._successful_conversions / max(self._total_conversions, 1),
                "total_exports": self._total_exports,
                "successful_exports": self._successful_exports,
                "export_success_rate": self._successful_exports / max(self._total_exports, 1)
            }
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
            issues = []
            health_score = 1.0
            
            # Check conversion success rate
            if self._total_conversions > 0:
                conversion_rate = self._successful_conversions / self._total_conversions
                if conversion_rate < 0.9:
                    issues.append(f"Low conversion success rate: {conversion_rate:.1%}")
                    health_score *= 0.8
            
            # Check export success rate
            if self._total_exports > 0:
                export_rate = self._successful_exports / self._total_exports
                if export_rate < 0.9:
                    issues.append(f"Low export success rate: {export_rate:.1%}")
                    health_score *= 0.8
            
            # Determine overall status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.WARNING
            else:
                status = ModuleStatus.ERROR
                
        except Exception as e:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = [f"Health check failed: {str(e)}"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION
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
        
    def convert_spec_tasks(self, spec_path: str) -> ConversionResult:
        """
        Convert tasks from a spec file to DAG representation.
        
        Args:
            spec_path: Path to the spec tasks.md file
            
        Returns:
            ConversionResult with task definitions and validation
        """
        with self.trace_operation("convert_spec_tasks", spec_path=spec_path) as trace:
            try:
                self._total_conversions += 1
                
                spec_file = Path(spec_path)
                if not spec_file.exists():
                    trace.output_result = {'success': False, 'error': 'File not found'}
                    return ConversionResult(
                        success=False,
                        errors=[f"Spec file not found: {spec_path}"]
                    )
                
                content = spec_file.read_text()
                result = self._parse_task_content(content, spec_path)
                
                if result.success:
                    self._successful_conversions += 1
                
                trace.output_result = {
                    'success': result.success,
                    'task_count': len(result.task_definitions),
                    'errors': len(result.errors)
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Error converting spec tasks: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                return ConversionResult(
                    success=False,
                    errors=[f"Conversion error: {str(e)}"]
                )
    
    def _parse_task_content(self, content: str, spec_path: str) -> ConversionResult:
        """Parse task content and extract task definitions."""
        tasks = []
        errors = []
        warnings = []
        
        # Extract checkbox tasks
        checkbox_matches = self.task_patterns['checkbox'].findall(content)
        
        for i, (status, task_text) in enumerate(checkbox_matches):
            try:
                task_def = self._parse_task_line(task_text, i, spec_path)
                if task_def:
                    tasks.append(task_def)
            except Exception as e:
                errors.append(f"Error parsing task '{task_text}': {str(e)}")
        
        # Analyze dependencies
        dependency_graph = self._analyze_dependencies(tasks)
        
        # Validate DAG structure
        dag_validation = self._validate_dag_structure(dependency_graph)
        
        if dag_validation.get('has_cycles', False):
            errors.extend(dag_validation.get('cycle_errors', []))
        
        return ConversionResult(
            success=len(errors) == 0,
            task_definitions=tasks,
            dag_validation=dag_validation,
            errors=errors,
            warnings=warnings
        )
    
    def _parse_task_line(self, task_text: str, index: int, spec_path: str) -> Optional[TaskDefinition]:
        """Parse individual task line into TaskDefinition."""
        # Extract task number and name
        numbered_match = re.match(r'^(\d+\.(?:\d+\.)*)\s*(.+)$', task_text)
        if numbered_match:
            task_id = numbered_match.group(1).rstrip('.')
            task_name = numbered_match.group(2)
        else:
            task_id = f"task_{index + 1}"
            task_name = task_text
        
        # Extract requirements references
        req_match = self.task_patterns['dependency'].search(task_text)
        requirements_refs = []
        if req_match:
            requirements_refs = [r.strip() for r in req_match.group(1).split(',')]
        
        # Determine dependencies based on task numbering
        dependencies = self._infer_dependencies(task_id)
        
        # Estimate resource requirements
        resource_requirements = self._estimate_resources(task_name)
        
        return TaskDefinition(
            id=task_id,
            name=task_name,
            description=task_name,  # Could be enhanced with more parsing
            dependencies=dependencies,
            resource_requirements=resource_requirements,
            execution_context={
                'spec_path': spec_path,
                'task_type': self._classify_task_type(task_name),
                'priority': self._determine_priority(task_name)
            },
            requirements_refs=requirements_refs
        )
    
    def _infer_dependencies(self, task_id: str) -> List[str]:
        """Infer task dependencies based on numbering scheme."""
        dependencies = []
        
        # Parse task ID (e.g., "1.2.3" -> ["1", "2", "3"])
        parts = task_id.split('.')
        
        if len(parts) > 1:
            # Sub-task depends on parent task
            parent_id = '.'.join(parts[:-1])
            dependencies.append(parent_id)
        
        # Sequential dependency within same level
        if len(parts) >= 1:
            try:
                current_num = int(parts[-1])
                if current_num > 1:
                    prev_parts = parts[:-1] + [str(current_num - 1)]
                    prev_id = '.'.join(prev_parts)
                    dependencies.append(prev_id)
            except ValueError:
                pass  # Non-numeric task ID
        
        return dependencies
    
    def _classify_task_type(self, task_name: str) -> str:
        """Classify task type based on name content."""
        name_lower = task_name.lower()
        
        if any(word in name_lower for word in ['test', 'validate', 'verify']):
            return 'testing'
        elif any(word in name_lower for word in ['implement', 'create', 'build']):
            return 'implementation'
        elif any(word in name_lower for word in ['deploy', 'install', 'configure']):
            return 'deployment'
        elif any(word in name_lower for word in ['monitor', 'observe', 'track']):
            return 'monitoring'
        else:
            return 'general'
    
    def _determine_priority(self, task_name: str) -> str:
        """Determine task priority based on content."""
        name_lower = task_name.lower()
        
        if any(word in name_lower for word in ['critical', 'essential', 'core']):
            return 'high'
        elif any(word in name_lower for word in ['optional', 'enhancement', 'nice']):
            return 'low'
        else:
            return 'medium'
    
    def _estimate_resources(self, task_name: str) -> Dict[str, Any]:
        """Estimate resource requirements based on task type."""
        name_lower = task_name.lower()
        
        # Base requirements
        resources = {
            'cpu_cores': 1,
            'memory_mb': 512,
            'disk_mb': 100,
            'estimated_duration_minutes': 30
        }
        
        # Adjust based on task complexity
        if any(word in name_lower for word in ['complex', 'comprehensive', 'advanced']):
            resources['cpu_cores'] = 2
            resources['memory_mb'] = 1024
            resources['estimated_duration_minutes'] = 60
        
        if any(word in name_lower for word in ['test', 'validate']):
            resources['estimated_duration_minutes'] = 15
        
        if any(word in name_lower for word in ['deploy', 'build']):
            resources['estimated_duration_minutes'] = 45
        
        return resources
    
    def _analyze_dependencies(self, tasks: List[TaskDefinition]) -> Dict[str, Set[str]]:
        """Analyze task dependencies and build dependency graph."""
        dependency_graph = {}
        
        for task in tasks:
            dependency_graph[task.id] = set(task.dependencies)
        
        return dependency_graph
    
    def _validate_dag_structure(self, dependency_graph: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Validate that dependency graph forms a valid DAG."""
        validation_result = {
            'is_valid_dag': True,
            'has_cycles': False,
            'cycle_errors': [],
            'topological_order': [],
            'critical_path': []
        }
        
        try:
            # Register dependencies in DAG registry for validation
            for task_id, deps in dependency_graph.items():
                self.dag_registry.register_module(task_id, deps)
            
            # Get topological order
            validation_result['topological_order'] = list(dependency_graph.keys())
            
            # Find critical path (longest path through dependencies)
            validation_result['critical_path'] = self._find_critical_path(dependency_graph)
            
        except Exception as e:
            validation_result['is_valid_dag'] = False
            validation_result['has_cycles'] = True
            validation_result['cycle_errors'].append(str(e))
        
        return validation_result
    
    def _find_critical_path(self, dependency_graph: Dict[str, Set[str]]) -> List[str]:
        """Find the critical path (longest dependency chain)."""
        # Simple implementation - could be enhanced with proper critical path algorithm
        max_path = []
        
        for task_id in dependency_graph:
            path = self._get_dependency_chain(task_id, dependency_graph)
            if len(path) > len(max_path):
                max_path = path
        
        return max_path
    
    def _get_dependency_chain(self, task_id: str, dependency_graph: Dict[str, Set[str]]) -> List[str]:
        """Get the full dependency chain for a task."""
        chain = [task_id]
        visited = {task_id}
        
        deps = dependency_graph.get(task_id, set())
        for dep in deps:
            if dep not in visited:
                dep_chain = self._get_dependency_chain(dep, dependency_graph)
                if len(dep_chain) > 0:
                    chain = dep_chain + chain
                    break
        
        return chain
    
    def export_dag_definition(self, conversion_result: ConversionResult, output_path: str) -> bool:
        """Export DAG definition to JSON file for orchestration."""
        with self.trace_operation("export_dag_definition", output_path=output_path) as trace:
            try:
                self._total_exports += 1
                
                if not conversion_result.success:
                    logger.error("Cannot export failed conversion result")
                    trace.output_result = {'success': False, 'error': 'Conversion result failed'}
                    return False
                
                dag_definition = {
                    'execution_plan': {
                        'plan_id': f"converted_spec_{Path(output_path).stem}",
                        'created_at': self._get_current_timestamp(),
                        'description': 'Converted from sequential task list to DAG representation',
                        'total_tasks': len(conversion_result.task_definitions),
                        'parallelization_strategy': 'dependency_aware'
                    },
                    'task_definitions': [
                        {
                            'id': task.id,
                            'name': task.name,
                            'description': task.description,
                            'dependencies': task.dependencies,
                            'resource_requirements': task.resource_requirements,
                            'execution_context': task.execution_context
                        }
                        for task in conversion_result.task_definitions
                    ],
                    'dag_validation': conversion_result.dag_validation
                }
                
                with open(output_path, 'w') as f:
                    json.dump(dag_definition, f, indent=2)
                
                self._successful_exports += 1
                
                trace.output_result = {
                    'success': True,
                    'output_path': output_path,
                    'task_count': len(conversion_result.task_definitions)
                }
                
                logger.info(f"DAG definition exported to {output_path}")
                return True
                
            except Exception as e:
                logger.error(f"Error exporting DAG definition: {e}")
                trace.output_result = {'success': False, 'error': str(e)}
                return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


def create_task_list_converter() -> TaskListConverter:
    """Factory function to create TaskListConverter instance."""
    return TaskListConverter()


if __name__ == "__main__":
    # Example usage
    converter = create_task_list_converter()
    
    # Convert a spec file
    result = converter.convert_spec_tasks(".kiro/specs/dag-orchestrated-parallel-execution/tasks.md")
    
    if result.success:
        print(f"✅ Converted {len(result.task_definitions)} tasks successfully")
        converter.export_dag_definition(result, "converted_dag_definition.json")
    else:
        print(f"❌ Conversion failed: {result.errors}")