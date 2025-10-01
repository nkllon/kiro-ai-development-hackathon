#!/usr/bin/env python3
"""
Specification Analyzer for Prepare Spec for Execution
====================================================

Comprehensive analyzer for parsing requirements, design, and tasks files from any specification.
Extracts structured data, validates completeness, and generates traceability matrices.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class TaskStatus(Enum):
    """Task completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class RequirementItem:
    """Individual requirement with traceability."""
    id: str
    title: str
    user_story: str
    acceptance_criteria: List[str]
    priority: str = "medium"
    category: str = "functional"
    source_line: int = 0


@dataclass
class TaskItem:
    """Individual task with dependencies and metadata."""
    id: str
    title: str
    description: str
    dependencies: Set[str] = field(default_factory=set)
    requirements: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.NOT_STARTED
    optional: bool = False
    estimated_hours: Optional[float] = None
    source_line: int = 0
    subtasks: List['TaskItem'] = field(default_factory=list)


@dataclass
class DesignSection:
    """Design document section."""
    title: str
    content: str
    subsections: List['DesignSection'] = field(default_factory=list)
    source_line: int = 0


@dataclass
class SpecificationData:
    """Complete specification data structure."""
    spec_name: str
    spec_path: Path
    requirements: List[RequirementItem] = field(default_factory=list)
    design_sections: List[DesignSection] = field(default_factory=list)
    tasks: List[TaskItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    completeness_score: float = 0.0


class SpecAnalyzer(ReflectiveModule):
    """Comprehensive specification analyzer and parser."""
    
    def __init__(self):
        super().__init__()
        self.spec_cache: Dict[str, SpecificationData] = {}
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Return component capabilities."""
        return {
            'spec_parsing': ['requirements', 'design', 'tasks'],
            'formats_supported': ['markdown'],
            'validation_types': ['completeness', 'structure', 'traceability'],
            'output_formats': ['json', 'dict', 'dataclass']
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return component health status."""
        return {
            'status': 'healthy',
            'cached_specs': len(self.spec_cache),
            'parser_ready': True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information."""
        return {
            'name': 'SpecAnalyzer',
            'version': '1.0.0',
            'description': 'Comprehensive specification analyzer and parser',
            'dependencies': ['ReflectiveModule'],
            'workflow_control': 'prepare-spec-for-execution'
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        return {
            'degraded_mode': True,
            'error': str(error),
            'available_functions': ['basic_parsing'],
            'recommendation': 'Check file permissions and format'
        }
    
    def analyze_specification(self, spec_path: str) -> SpecificationData:
        """Analyze a complete specification directory."""
        spec_path = Path(spec_path)
        
        if not spec_path.exists():
            raise FileNotFoundError(f"Specification path not found: {spec_path}")
        
        # Check cache first
        cache_key = str(spec_path.absolute())
        if cache_key in self.spec_cache:
            return self.spec_cache[cache_key]
        
        spec_data = SpecificationData(
            spec_name=spec_path.name,
            spec_path=spec_path
        )
        
        # Parse each component
        self._parse_requirements(spec_data)
        self._parse_design(spec_data)
        self._parse_tasks(spec_data)
        
        # Validate and calculate completeness
        self._validate_specification(spec_data)
        self._calculate_completeness(spec_data)
        
        # Cache result
        self.spec_cache[cache_key] = spec_data
        
        return spec_data
    
    def _parse_requirements(self, spec_data: SpecificationData) -> None:
        """Parse requirements.md file."""
        req_file = spec_data.spec_path / "requirements.md"
        if not req_file.exists():
            spec_data.validation_errors.append("requirements.md file not found")
            return
        
        try:
            content = req_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            current_requirement = None
            in_acceptance_criteria = False
            line_num = 0
            
            for line in lines:
                line_num += 1
                line = line.strip()
                
                # Match requirement headers (### Requirement N)
                req_match = re.match(r'^###\s+Requirement\s+(\d+(?:\.\d+)?)', line, re.IGNORECASE)
                if req_match:
                    if current_requirement:
                        spec_data.requirements.append(current_requirement)
                    
                    req_id = req_match.group(1)
                    current_requirement = RequirementItem(
                        id=req_id,
                        title=line,
                        user_story="",
                        acceptance_criteria=[],
                        source_line=line_num
                    )
                    in_acceptance_criteria = False
                    continue
                
                if current_requirement:
                    # Match user story
                    story_match = re.match(r'^\*\*User Story:\*\*\s*(.+)', line)
                    if story_match:
                        current_requirement.user_story = story_match.group(1)
                        continue
                    
                    # Match acceptance criteria section
                    if re.match(r'^####?\s+Acceptance Criteria', line, re.IGNORECASE):
                        in_acceptance_criteria = True
                        continue
                    
                    # Match acceptance criteria items
                    if in_acceptance_criteria and re.match(r'^\d+\.\s+', line):
                        criteria = re.sub(r'^\d+\.\s+', '', line)
                        current_requirement.acceptance_criteria.append(criteria)
            
            # Add final requirement
            if current_requirement:
                spec_data.requirements.append(current_requirement)
                
        except Exception as e:
            spec_data.validation_errors.append(f"Error parsing requirements: {str(e)}")
    
    def _parse_design(self, spec_data: SpecificationData) -> None:
        """Parse design.md file."""
        design_file = spec_data.spec_path / "design.md"
        if not design_file.exists():
            spec_data.validation_errors.append("design.md file not found")
            return
        
        try:
            content = design_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            current_section = None
            section_stack = []
            line_num = 0
            
            for line in lines:
                line_num += 1
                original_line = line
                line = line.strip()
                
                # Match headers (## or ###)
                header_match = re.match(r'^(#{2,4})\s+(.+)', line)
                if header_match:
                    level = len(header_match.group(1))
                    title = header_match.group(2)
                    
                    # Create new section
                    new_section = DesignSection(
                        title=title,
                        content="",
                        source_line=line_num
                    )
                    
                    # Handle nesting
                    if level == 2:  # Top level
                        if current_section:
                            spec_data.design_sections.append(current_section)
                        current_section = new_section
                        section_stack = [current_section]
                    elif level > 2 and section_stack:  # Subsection
                        # Find appropriate parent
                        target_level = level - 3  # Adjust for 0-based indexing
                        if target_level < len(section_stack):
                            parent = section_stack[target_level]
                            parent.subsections.append(new_section)
                            # Update stack
                            section_stack = section_stack[:target_level + 1] + [new_section]
                        else:
                            section_stack.append(new_section)
                    continue
                
                # Add content to current section
                if current_section and line:
                    if current_section.content:
                        current_section.content += "\n"
                    current_section.content += original_line
            
            # Add final section
            if current_section:
                spec_data.design_sections.append(current_section)
                
        except Exception as e:
            spec_data.validation_errors.append(f"Error parsing design: {str(e)}")
    
    def _parse_tasks(self, spec_data: SpecificationData) -> None:
        """Parse tasks.md file."""
        tasks_file = spec_data.spec_path / "tasks.md"
        if not tasks_file.exists():
            spec_data.validation_errors.append("tasks.md file not found")
            return
        
        try:
            content = tasks_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            current_task = None
            task_stack = []
            line_num = 0
            
            for line in lines:
                line_num += 1
                original_line = line.strip()
                
                # Match task items (- [ ] or - [x] or - [-])
                task_match = re.match(r'^(\s*)-\s*\[([x\-\s])\]\s*(.+)', original_line)
                if task_match:
                    indent = len(task_match.group(1))
                    status_char = task_match.group(2)
                    task_text = task_match.group(3)
                    
                    # Determine status
                    if status_char.lower() == 'x':
                        status = TaskStatus.COMPLETED
                    elif status_char == '-':
                        status = TaskStatus.IN_PROGRESS
                    else:
                        status = TaskStatus.NOT_STARTED
                    
                    # Check if optional (ends with *)
                    optional = task_text.endswith('*')
                    if optional:
                        task_text = task_text.rstrip('*').strip()
                    
                    # Extract task ID and title
                    id_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)', task_text)
                    if id_match:
                        task_id = id_match.group(1)
                        title = id_match.group(2)
                    else:
                        task_id = f"task_{line_num}"
                        title = task_text
                    
                    # Create task
                    task = TaskItem(
                        id=task_id,
                        title=title,
                        description="",
                        status=status,
                        optional=optional,
                        source_line=line_num
                    )
                    
                    # Handle nesting based on indentation
                    level = indent // 2  # Assuming 2-space indentation
                    
                    if level == 0:  # Top level task
                        if current_task:
                            spec_data.tasks.append(current_task)
                        current_task = task
                        task_stack = [current_task]
                    elif level > 0 and task_stack:  # Subtask
                        # Find appropriate parent
                        parent_level = min(level - 1, len(task_stack) - 1)
                        parent = task_stack[parent_level]
                        parent.subtasks.append(task)
                        
                        # Update stack
                        task_stack = task_stack[:parent_level + 1] + [task]
                    
                    continue
                
                # Parse task details (bullets under tasks)
                if current_task and original_line.startswith('  -') and not re.match(r'^\s*-\s*\[', original_line):
                    detail = original_line.strip()[1:].strip()  # Remove leading -
                    
                    # Check for requirements reference
                    req_match = re.search(r'_Requirements?:\s*([^_]+)_', detail)
                    if req_match:
                        req_refs = [r.strip() for r in req_match.group(1).split(',')]
                        current_task.requirements.extend(req_refs)
                    else:
                        # Add to description
                        if current_task.description:
                            current_task.description += "\n"
                        current_task.description += detail
            
            # Add final task
            if current_task:
                spec_data.tasks.append(current_task)
                
        except Exception as e:
            spec_data.validation_errors.append(f"Error parsing tasks: {str(e)}")
    
    def _validate_specification(self, spec_data: SpecificationData) -> None:
        """Validate specification completeness and structure."""
        # Check for required components
        if not spec_data.requirements:
            spec_data.validation_errors.append("No requirements found")
        
        if not spec_data.design_sections:
            spec_data.validation_errors.append("No design sections found")
        
        if not spec_data.tasks:
            spec_data.validation_errors.append("No tasks found")
        
        # Validate requirement structure
        for req in spec_data.requirements:
            if not req.user_story:
                spec_data.validation_errors.append(f"Requirement {req.id} missing user story")
            
            if not req.acceptance_criteria:
                spec_data.validation_errors.append(f"Requirement {req.id} missing acceptance criteria")
        
        # Validate task dependencies
        task_ids = {task.id for task in spec_data.tasks}
        for task in spec_data.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    spec_data.validation_errors.append(f"Task {task.id} has invalid dependency: {dep}")
    
    def _calculate_completeness(self, spec_data: SpecificationData) -> None:
        """Calculate specification completeness score."""
        total_score = 0
        max_score = 0
        
        # Requirements completeness (40% weight)
        req_score = 0
        req_max = len(spec_data.requirements) * 3  # user_story + acceptance_criteria + structure
        
        for req in spec_data.requirements:
            if req.user_story:
                req_score += 1
            if req.acceptance_criteria:
                req_score += 1
            if req.id and req.title:
                req_score += 1
        
        total_score += (req_score / max(req_max, 1)) * 40
        max_score += 40
        
        # Design completeness (30% weight)
        design_score = 30 if spec_data.design_sections else 0
        total_score += design_score
        max_score += 30
        
        # Tasks completeness (30% weight)
        task_score = 0
        task_max = len(spec_data.tasks) * 2  # structure + requirements mapping
        
        for task in spec_data.tasks:
            if task.id and task.title:
                task_score += 1
            if task.requirements:
                task_score += 1
        
        total_score += (task_score / max(task_max, 1)) * 30
        max_score += 30
        
        spec_data.completeness_score = total_score / max_score if max_score > 0 else 0
    
    def generate_traceability_matrix(self, spec_data: SpecificationData) -> Dict[str, Any]:
        """Generate requirements traceability matrix."""
        matrix = {
            'requirements_to_tasks': {},
            'tasks_to_requirements': {},
            'orphaned_requirements': [],
            'orphaned_tasks': [],
            'coverage_stats': {}
        }
        
        # Build mappings
        req_ids = {req.id for req in spec_data.requirements}
        
        for task in spec_data.tasks:
            matrix['tasks_to_requirements'][task.id] = task.requirements
            
            for req_id in task.requirements:
                if req_id not in matrix['requirements_to_tasks']:
                    matrix['requirements_to_tasks'][req_id] = []
                matrix['requirements_to_tasks'][req_id].append(task.id)
        
        # Find orphaned items
        covered_reqs = set(matrix['requirements_to_tasks'].keys())
        matrix['orphaned_requirements'] = list(req_ids - covered_reqs)
        
        tasks_with_reqs = {task_id for task_id, reqs in matrix['tasks_to_requirements'].items() if reqs}
        all_tasks = {task.id for task in spec_data.tasks}
        matrix['orphaned_tasks'] = list(all_tasks - tasks_with_reqs)
        
        # Calculate coverage stats
        matrix['coverage_stats'] = {
            'total_requirements': len(req_ids),
            'covered_requirements': len(covered_reqs),
            'coverage_percentage': (len(covered_reqs) / len(req_ids) * 100) if req_ids else 0,
            'total_tasks': len(all_tasks),
            'tasks_with_requirements': len(tasks_with_reqs)
        }
        
        return matrix
    
    def extract_task_dependencies(self, spec_data: SpecificationData) -> Dict[str, Set[str]]:
        """Extract task dependency graph."""
        dependencies = {}
        
        for task in spec_data.tasks:
            dependencies[task.id] = task.dependencies.copy()
            
            # Add subtask dependencies
            for subtask in task.subtasks:
                dependencies[subtask.id] = subtask.dependencies.copy()
                # Subtasks implicitly depend on parent
                dependencies[subtask.id].add(task.id)
        
        return dependencies
    
    def get_execution_order(self, spec_data: SpecificationData) -> List[str]:
        """Calculate topological execution order for tasks."""
        dependencies = self.extract_task_dependencies(spec_data)
        
        # Topological sort using Kahn's algorithm
        in_degree = {task_id: 0 for task_id in dependencies}
        
        # Calculate in-degrees
        for task_id, deps in dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[task_id] += 1
        
        # Find tasks with no dependencies
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Remove current from dependencies and update in-degrees
            for task_id, deps in dependencies.items():
                if current in deps:
                    in_degree[task_id] -= 1
                    if in_degree[task_id] == 0:
                        queue.append(task_id)
        
        return result
    
    def to_dict(self, spec_data: SpecificationData) -> Dict[str, Any]:
        """Convert specification data to dictionary."""
        return {
            'spec_name': spec_data.spec_name,
            'spec_path': str(spec_data.spec_path),
            'requirements': [
                {
                    'id': req.id,
                    'title': req.title,
                    'user_story': req.user_story,
                    'acceptance_criteria': req.acceptance_criteria,
                    'priority': req.priority,
                    'category': req.category
                }
                for req in spec_data.requirements
            ],
            'design_sections': [
                {
                    'title': section.title,
                    'content': section.content,
                    'subsections': len(section.subsections)
                }
                for section in spec_data.design_sections
            ],
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'dependencies': list(task.dependencies),
                    'requirements': task.requirements,
                    'status': task.status.value,
                    'optional': task.optional,
                    'subtasks': len(task.subtasks)
                }
                for task in spec_data.tasks
            ],
            'validation_errors': spec_data.validation_errors,
            'completeness_score': spec_data.completeness_score,
            'metadata': spec_data.metadata
        }


# Convenience functions
def analyze_spec(spec_path: str) -> SpecificationData:
    """Analyze a specification directory."""
    analyzer = SpecAnalyzer()
    return analyzer.analyze_specification(spec_path)


def get_traceability_matrix(spec_path: str) -> Dict[str, Any]:
    """Get requirements traceability matrix for a specification."""
    analyzer = SpecAnalyzer()
    spec_data = analyzer.analyze_specification(spec_path)
    return analyzer.generate_traceability_matrix(spec_data)


def get_execution_order(spec_path: str) -> List[str]:
    """Get topological execution order for specification tasks."""
    analyzer = SpecAnalyzer()
    spec_data = analyzer.analyze_specification(spec_path)
    return analyzer.get_execution_order(spec_data)