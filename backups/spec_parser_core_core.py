"""
Spec Parser Core Core

This module was extracted from spec_parser_core.py
as part of RM-DDD compliance refactoring.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..models.dag_models import SpecificationNode, TaskNode
from ..models.enums import TaskStatus


@dataclass
class ParsedSpec:
    """Parsed specification with metadata."""

    spec_name: str
    spec_path: str
    requirements_count: int
    tasks_count: int
    completion_percentage: float
    dependencies: List[str]
    raw_content: str


class SpecParser:
    """
    Systematic specification parser for DAG analysis.

    Parses specification files to extract tasks, dependencies,
    requirements traceability, and completion status.
    """

    def __init__(self):
        self.task_patterns = [
            "^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]\\s*(.+)$",
            "^\\s*\\d+\\.\\s*(.+)$",
            "^\\s*\\*\\s*(.+)$",
        ]
        self.requirement_patterns = [
            "_Requirements?:\\s*([^_]+)_",
            "Requirements?\\s*(\\d+(?:\\.\\d+)?(?:,\\s*\\d+(?:\\.\\d+)?)*)",
        ]
        self.dependency_patterns = [
            "depends?:\\s*([^)]+)",
            "requires?:\\s*([^)]+)",
            "after:\\s*([^)]+)",
        ]

    def parse_specification_directory(self, spec_directory: str) -> List[ParsedSpec]:
        """
        Parse all specifications in a directory.

        Args:
            spec_directory: Root directory containing specifications

        Returns:
            List[ParsedSpec]: All parsed specifications
        """
        parsed_specs = []
        spec_path = Path(spec_directory)
        if not spec_path.exists():
            raise FileNotFoundError(
                f"Specification directory not found: {spec_directory}"
            )
        for spec_file in spec_path.rglob("*.md"):
            if self._is_spec_file(spec_file):
                try:
                    parsed_spec = self.parse_specification_file(str(spec_file))
                    parsed_specs.append(parsed_spec)
                except Exception as e:
                    print(f"Warning: Failed to parse {spec_file}: {e}")
        return parsed_specs

    def parse_specification_file(self, spec_file_path: str) -> ParsedSpec:
        """
        Parse a single specification file.

        Args:
            spec_file_path: Path to specification file

        Returns:
            ParsedSpec: Parsed specification data
        """
        spec_path = Path(spec_file_path)
        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_file_path}")
        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()
        spec_name = self._extract_spec_name(spec_path)
        requirements_count = self._count_requirements(content)
        tasks_count = self._count_tasks(content)
        completion_percentage = self._calculate_completion_percentage(content)
        dependencies = self._extract_spec_dependencies(content, spec_path)
        return ParsedSpec(
            spec_name=spec_name,
            spec_path=str(spec_path),
            requirements_count=requirements_count,
            tasks_count=tasks_count,
            completion_percentage=completion_percentage,
            dependencies=dependencies,
            raw_content=content,
        )

    def extract_tasks_from_spec(self, parsed_spec: ParsedSpec) -> List[TaskNode]:
        """
        Extract task nodes from parsed specification.

        Args:
            parsed_spec: Parsed specification data

        Returns:
            List[TaskNode]: Extracted task nodes
        """
        tasks = []
        content = parsed_spec.raw_content
        lines = content.split("\n")
        current_task_id = 0
        for i, line in enumerate(lines):
            task_match = self._match_task_pattern(line)
            if task_match:
                current_task_id += 1
                is_completed, task_text = task_match
                task_id = f"{parsed_spec.spec_name}_{current_task_id}"
                requirements_traced = self._extract_requirements_from_task(
                    task_text, lines, i
                )
                dependencies = self._extract_task_dependencies(task_text, lines, i)
                estimated_effort = self._estimate_task_effort(task_text)
                status = (
                    TaskStatus.COMPLETED if is_completed else TaskStatus.NOT_STARTED
                )
                task_node = TaskNode(
                    task_id=task_id,
                    spec_name=parsed_spec.spec_name,
                    task_name=task_text.strip(),
                    description=task_text.strip(),
                    estimated_effort=estimated_effort,
                    completion_status=status,
                    dependencies=dependencies,
                    dependents=[],
                    requirements_traced=requirements_traced,
                )
                tasks.append(task_node)
        return tasks

    def _is_spec_file(self, file_path: Path) -> bool:
        """Check if file is a specification file."""
        spec_indicators = ["requirements.md", "design.md", "tasks.md", "spec.md"]
        return any(
            (indicator in file_path.name.lower() for indicator in spec_indicators)
        )

    def _extract_spec_name(self, spec_path: Path) -> str:
        """Extract specification name from file path."""
        if spec_path.parent.name != ".kiro":
            return spec_path.parent.name
        else:
            return spec_path.stem

    def _count_requirements(self, content: str) -> int:
        """Count requirements in specification content."""
        requirement_count = 0
        requirement_headers = re.findall(
            "###\\s*Requirement\\s+\\d+", content, re.IGNORECASE
        )
        requirement_count += len(requirement_headers)
        acceptance_criteria = re.findall(
            "^\\s*\\d+\\.\\s*WHEN.*THEN.*SHALL", content, re.MULTILINE | re.IGNORECASE
        )
        requirement_count += len(acceptance_criteria)
        return max(requirement_count, 1)

    def _count_tasks(self, content: str) -> int:
        """Count tasks in specification content."""
        task_count = 0
        for pattern in self.task_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            task_count += len(matches)
        return task_count

    def _calculate_completion_percentage(self, content: str) -> float:
        """Calculate completion percentage based on completed tasks."""
        total_tasks = 0
        completed_tasks = 0
        checkbox_pattern = "^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]"
        matches = re.findall(checkbox_pattern, content, re.MULTILINE)
        for match in matches:
            total_tasks += 1
            if match.lower() == "x":
                completed_tasks += 1
        if total_tasks == 0:
            return 0.0
        return completed_tasks / total_tasks * 100.0

    def _extract_spec_dependencies(self, content: str, spec_path: Path) -> List[str]:
        """Extract specification-level dependencies."""
        dependencies = []
        dependency_patterns = [
            "depends on\\s+([^.\\n]+)",
            "requires\\s+([^.\\n]+)",
            "after\\s+([^.\\n]+)",
            "builds on\\s+([^.\\n]+)",
        ]
        for pattern in dependency_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dependencies.extend(matches)
        cleaned_dependencies = []
        for dep in dependencies:
            cleaned_dep = dep.strip().lower().replace(" ", "-")
            if cleaned_dep and cleaned_dep not in cleaned_dependencies:
                cleaned_dependencies.append(cleaned_dep)
        return cleaned_dependencies

    def _match_task_pattern(self, line: str) -> Optional[Tuple[bool, str]]:
        """Match line against task patterns."""
        checkbox_match = re.match("^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]\\s*(.+)$", line)
        if checkbox_match:
            is_completed = checkbox_match.group(1).lower() == "x"
            task_text = checkbox_match.group(2)
            return (is_completed, task_text)
        numbered_match = re.match("^\\s*\\d+\\.\\s*(.+)$", line)
        if numbered_match:
            return (False, numbered_match.group(1))
        return None

    def _extract_requirements_from_task(
        self, task_text: str, lines: List[str], line_index: int
    ) -> List[str]:
        """Extract requirements traceability from task."""
        requirements = []
        for pattern in self.requirement_patterns:
            matches = re.findall(pattern, task_text)
            for match in matches:
                req_ids = [req.strip() for req in match.split(",")]
                requirements.extend(req_ids)
        for i in range(line_index + 1, min(line_index + 5, len(lines))):
            line = lines[i]
            if line.strip().startswith("-") and (not line.strip().startswith("- [")):
                for pattern in self.requirement_patterns:
                    matches = re.findall(pattern, line)
                    for match in matches:
                        req_ids = [req.strip() for req in match.split(",")]
                        requirements.extend(req_ids)
            elif line.strip() and (not line.startswith(" ")):
                break
        return list(set(requirements))

    def _extract_task_dependencies(
        self, task_text: str, lines: List[str], line_index: int
    ) -> List[str]:
        """Extract task dependencies."""
        dependencies = []
        for pattern in self.dependency_patterns:
            matches = re.findall(pattern, task_text, re.IGNORECASE)
            dependencies.extend(matches)
        for i in range(line_index + 1, min(line_index + 3, len(lines))):
            line = lines[i]
            if line.strip().startswith("-") and (not line.strip().startswith("- [")):
                for pattern in self.dependency_patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    dependencies.extend(matches)
        cleaned_deps = []
        for dep in dependencies:
            cleaned_dep = dep.strip()
            if cleaned_dep and cleaned_dep not in cleaned_deps:
                cleaned_deps.append(cleaned_dep)
        return cleaned_deps

    def _estimate_task_effort(self, task_text: str) -> int:
        """Estimate task effort in hours based on complexity indicators."""
        base_effort = 4
        complexity_keywords = {
            "implement": 2,
            "create": 2,
            "build": 3,
            "design": 2,
            "integrate": 3,
            "optimize": 4,
            "test": 2,
            "framework": 3,
            "system": 3,
            "engine": 4,
            "comprehensive": 2,
            "complete": 2,
            "advanced": 3,
            "complex": 3,
        }
        text_lower = task_text.lower()
        effort_multiplier = 1.0
        for keyword, multiplier in complexity_keywords.items():
            if keyword in text_lower:
                effort_multiplier += (multiplier - 1) * 0.5
        if len(task_text) > 100:
            effort_multiplier += 0.5
        return int(base_effort * effort_multiplier)


def __init__(self):
    self.task_patterns = [
        "^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]\\s*(.+)$",
        "^\\s*\\d+\\.\\s*(.+)$",
        "^\\s*\\*\\s*(.+)$",
    ]
    self.requirement_patterns = [
        "_Requirements?:\\s*([^_]+)_",
        "Requirements?\\s*(\\d+(?:\\.\\d+)?(?:,\\s*\\d+(?:\\.\\d+)?)*)",
    ]
    self.dependency_patterns = [
        "depends?:\\s*([^)]+)",
        "requires?:\\s*([^)]+)",
        "after:\\s*([^)]+)",
    ]


def extract_tasks_from_spec(self, parsed_spec: ParsedSpec) -> List[TaskNode]:
    """
    Extract task nodes from parsed specification.

    Args:
        parsed_spec: Parsed specification data

    Returns:
        List[TaskNode]: Extracted task nodes
    """
    tasks = []
    content = parsed_spec.raw_content
    lines = content.split("\n")
    current_task_id = 0
    for i, line in enumerate(lines):
        task_match = self._match_task_pattern(line)
        if task_match:
            current_task_id += 1
            is_completed, task_text = task_match
            task_id = f"{parsed_spec.spec_name}_{current_task_id}"
            requirements_traced = self._extract_requirements_from_task(
                task_text, lines, i
            )
            dependencies = self._extract_task_dependencies(task_text, lines, i)
            estimated_effort = self._estimate_task_effort(task_text)
            status = TaskStatus.COMPLETED if is_completed else TaskStatus.NOT_STARTED
            task_node = TaskNode(
                task_id=task_id,
                spec_name=parsed_spec.spec_name,
                task_name=task_text.strip(),
                description=task_text.strip(),
                estimated_effort=estimated_effort,
                completion_status=status,
                dependencies=dependencies,
                dependents=[],
                requirements_traced=requirements_traced,
            )
            tasks.append(task_node)
    return tasks


def _is_spec_file(self, file_path: Path) -> bool:
    """Check if file is a specification file."""
    spec_indicators = ["requirements.md", "design.md", "tasks.md", "spec.md"]
    return any((indicator in file_path.name.lower() for indicator in spec_indicators))


def _extract_spec_name(self, spec_path: Path) -> str:
    """Extract specification name from file path."""
    if spec_path.parent.name != ".kiro":
        return spec_path.parent.name
    else:
        return spec_path.stem


def _count_requirements(self, content: str) -> int:
    """Count requirements in specification content."""
    requirement_count = 0
    requirement_headers = re.findall(
        "###\\s*Requirement\\s+\\d+", content, re.IGNORECASE
    )
    requirement_count += len(requirement_headers)
    acceptance_criteria = re.findall(
        "^\\s*\\d+\\.\\s*WHEN.*THEN.*SHALL", content, re.MULTILINE | re.IGNORECASE
    )
    requirement_count += len(acceptance_criteria)
    return max(requirement_count, 1)


def _count_tasks(self, content: str) -> int:
    """Count tasks in specification content."""
    task_count = 0
    for pattern in self.task_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        task_count += len(matches)
    return task_count


def _calculate_completion_percentage(self, content: str) -> float:
    """Calculate completion percentage based on completed tasks."""
    total_tasks = 0
    completed_tasks = 0
    checkbox_pattern = "^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]"
    matches = re.findall(checkbox_pattern, content, re.MULTILINE)
    for match in matches:
        total_tasks += 1
        if match.lower() == "x":
            completed_tasks += 1
    if total_tasks == 0:
        return 0.0
    return completed_tasks / total_tasks * 100.0


def _extract_spec_dependencies(self, content: str, spec_path: Path) -> List[str]:
    """Extract specification-level dependencies."""
    dependencies = []
    dependency_patterns = [
        "depends on\\s+([^.\\n]+)",
        "requires\\s+([^.\\n]+)",
        "after\\s+([^.\\n]+)",
        "builds on\\s+([^.\\n]+)",
    ]
    for pattern in dependency_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        dependencies.extend(matches)
    cleaned_dependencies = []
    for dep in dependencies:
        cleaned_dep = dep.strip().lower().replace(" ", "-")
        if cleaned_dep and cleaned_dep not in cleaned_dependencies:
            cleaned_dependencies.append(cleaned_dep)
    return cleaned_dependencies


def _match_task_pattern(self, line: str) -> Optional[Tuple[bool, str]]:
    """Match line against task patterns."""
    checkbox_match = re.match("^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]\\s*(.+)$", line)
    if checkbox_match:
        is_completed = checkbox_match.group(1).lower() == "x"
        task_text = checkbox_match.group(2)
        return (is_completed, task_text)
    numbered_match = re.match("^\\s*\\d+\\.\\s*(.+)$", line)
    if numbered_match:
        return (False, numbered_match.group(1))
    return None


def _extract_requirements_from_task(
    self, task_text: str, lines: List[str], line_index: int
) -> List[str]:
    """Extract requirements traceability from task."""
    requirements = []
    for pattern in self.requirement_patterns:
        matches = re.findall(pattern, task_text)
        for match in matches:
            req_ids = [req.strip() for req in match.split(",")]
            requirements.extend(req_ids)
    for i in range(line_index + 1, min(line_index + 5, len(lines))):
        line = lines[i]
        if line.strip().startswith("-") and (not line.strip().startswith("- [")):
            for pattern in self.requirement_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    req_ids = [req.strip() for req in match.split(",")]
                    requirements.extend(req_ids)
        elif line.strip() and (not line.startswith(" ")):
            break
    return list(set(requirements))


def _extract_task_dependencies(
    self, task_text: str, lines: List[str], line_index: int
) -> List[str]:
    """Extract task dependencies."""
    dependencies = []
    for pattern in self.dependency_patterns:
        matches = re.findall(pattern, task_text, re.IGNORECASE)
        dependencies.extend(matches)
    for i in range(line_index + 1, min(line_index + 3, len(lines))):
        line = lines[i]
        if line.strip().startswith("-") and (not line.strip().startswith("- [")):
            for pattern in self.dependency_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                dependencies.extend(matches)
    cleaned_deps = []
    for dep in dependencies:
        cleaned_dep = dep.strip()
        if cleaned_dep and cleaned_dep not in cleaned_deps:
            cleaned_deps.append(cleaned_dep)
    return cleaned_deps


def _estimate_task_effort(self, task_text: str) -> int:
    """Estimate task effort in hours based on complexity indicators."""
    base_effort = 4
    complexity_keywords = {
        "implement": 2,
        "create": 2,
        "build": 3,
        "design": 2,
        "integrate": 3,
        "optimize": 4,
        "test": 2,
        "framework": 3,
        "system": 3,
        "engine": 4,
        "comprehensive": 2,
        "complete": 2,
        "advanced": 3,
        "complex": 3,
    }
    text_lower = task_text.lower()
    effort_multiplier = 1.0
    for keyword, multiplier in complexity_keywords.items():
        if keyword in text_lower:
            effort_multiplier += (multiplier - 1) * 0.5
    if len(task_text) > 100:
        effort_multiplier += 0.5
    return int(base_effort * effort_multiplier)


def __init__(self):
    self.task_patterns = [
        "^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]\\s*(.+)$",
        "^\\s*\\d+\\.\\s*(.+)$",
        "^\\s*\\*\\s*(.+)$",
    ]
    self.requirement_patterns = [
        "_Requirements?:\\s*([^_]+)_",
        "Requirements?\\s*(\\d+(?:\\.\\d+)?(?:,\\s*\\d+(?:\\.\\d+)?)*)",
    ]
    self.dependency_patterns = [
        "depends?:\\s*([^)]+)",
        "requires?:\\s*([^)]+)",
        "after:\\s*([^)]+)",
    ]


def extract_tasks_from_spec(self, parsed_spec: ParsedSpec) -> List[TaskNode]:
    """
    Extract task nodes from parsed specification.

    Args:
        parsed_spec: Parsed specification data

    Returns:
        List[TaskNode]: Extracted task nodes
    """
    tasks = []
    content = parsed_spec.raw_content
    lines = content.split("\n")
    current_task_id = 0
    for i, line in enumerate(lines):
        task_match = self._match_task_pattern(line)
        if task_match:
            current_task_id += 1
            is_completed, task_text = task_match
            task_id = f"{parsed_spec.spec_name}_{current_task_id}"
            requirements_traced = self._extract_requirements_from_task(
                task_text, lines, i
            )
            dependencies = self._extract_task_dependencies(task_text, lines, i)
            estimated_effort = self._estimate_task_effort(task_text)
            status = TaskStatus.COMPLETED if is_completed else TaskStatus.NOT_STARTED
            task_node = TaskNode(
                task_id=task_id,
                spec_name=parsed_spec.spec_name,
                task_name=task_text.strip(),
                description=task_text.strip(),
                estimated_effort=estimated_effort,
                completion_status=status,
                dependencies=dependencies,
                dependents=[],
                requirements_traced=requirements_traced,
            )
            tasks.append(task_node)
    return tasks


def _is_spec_file(self, file_path: Path) -> bool:
    """Check if file is a specification file."""
    spec_indicators = ["requirements.md", "design.md", "tasks.md", "spec.md"]
    return any((indicator in file_path.name.lower() for indicator in spec_indicators))


def _extract_spec_name(self, spec_path: Path) -> str:
    """Extract specification name from file path."""
    if spec_path.parent.name != ".kiro":
        return spec_path.parent.name
    else:
        return spec_path.stem


def _count_requirements(self, content: str) -> int:
    """Count requirements in specification content."""
    requirement_count = 0
    requirement_headers = re.findall(
        "###\\s*Requirement\\s+\\d+", content, re.IGNORECASE
    )
    requirement_count += len(requirement_headers)
    acceptance_criteria = re.findall(
        "^\\s*\\d+\\.\\s*WHEN.*THEN.*SHALL", content, re.MULTILINE | re.IGNORECASE
    )
    requirement_count += len(acceptance_criteria)
    return max(requirement_count, 1)


def _count_tasks(self, content: str) -> int:
    """Count tasks in specification content."""
    task_count = 0
    for pattern in self.task_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        task_count += len(matches)
    return task_count


def _calculate_completion_percentage(self, content: str) -> float:
    """Calculate completion percentage based on completed tasks."""
    total_tasks = 0
    completed_tasks = 0
    checkbox_pattern = "^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]"
    matches = re.findall(checkbox_pattern, content, re.MULTILINE)
    for match in matches:
        total_tasks += 1
        if match.lower() == "x":
            completed_tasks += 1
    if total_tasks == 0:
        return 0.0
    return completed_tasks / total_tasks * 100.0


def _extract_spec_dependencies(self, content: str, spec_path: Path) -> List[str]:
    """Extract specification-level dependencies."""
    dependencies = []
    dependency_patterns = [
        "depends on\\s+([^.\\n]+)",
        "requires\\s+([^.\\n]+)",
        "after\\s+([^.\\n]+)",
        "builds on\\s+([^.\\n]+)",
    ]
    for pattern in dependency_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        dependencies.extend(matches)
    cleaned_dependencies = []
    for dep in dependencies:
        cleaned_dep = dep.strip().lower().replace(" ", "-")
        if cleaned_dep and cleaned_dep not in cleaned_dependencies:
            cleaned_dependencies.append(cleaned_dep)
    return cleaned_dependencies


def _match_task_pattern(self, line: str) -> Optional[Tuple[bool, str]]:
    """Match line against task patterns."""
    checkbox_match = re.match("^\\s*-\\s*\\[\\s*([x\\s])\\s*\\]\\s*(.+)$", line)
    if checkbox_match:
        is_completed = checkbox_match.group(1).lower() == "x"
        task_text = checkbox_match.group(2)
        return (is_completed, task_text)
    numbered_match = re.match("^\\s*\\d+\\.\\s*(.+)$", line)
    if numbered_match:
        return (False, numbered_match.group(1))
    return None


def _extract_requirements_from_task(
    self, task_text: str, lines: List[str], line_index: int
) -> List[str]:
    """Extract requirements traceability from task."""
    requirements = []
    for pattern in self.requirement_patterns:
        matches = re.findall(pattern, task_text)
        for match in matches:
            req_ids = [req.strip() for req in match.split(",")]
            requirements.extend(req_ids)
    for i in range(line_index + 1, min(line_index + 5, len(lines))):
        line = lines[i]
        if line.strip().startswith("-") and (not line.strip().startswith("- [")):
            for pattern in self.requirement_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    req_ids = [req.strip() for req in match.split(",")]
                    requirements.extend(req_ids)
        elif line.strip() and (not line.startswith(" ")):
            break
    return list(set(requirements))


def _extract_task_dependencies(
    self, task_text: str, lines: List[str], line_index: int
) -> List[str]:
    """Extract task dependencies."""
    dependencies = []
    for pattern in self.dependency_patterns:
        matches = re.findall(pattern, task_text, re.IGNORECASE)
        dependencies.extend(matches)
    for i in range(line_index + 1, min(line_index + 3, len(lines))):
        line = lines[i]
        if line.strip().startswith("-") and (not line.strip().startswith("- [")):
            for pattern in self.dependency_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                dependencies.extend(matches)
    cleaned_deps = []
    for dep in dependencies:
        cleaned_dep = dep.strip()
        if cleaned_dep and cleaned_dep not in cleaned_deps:
            cleaned_deps.append(cleaned_dep)
    return cleaned_deps


def _estimate_task_effort(self, task_text: str) -> int:
    """Estimate task effort in hours based on complexity indicators."""
    base_effort = 4
    complexity_keywords = {
        "implement": 2,
        "create": 2,
        "build": 3,
        "design": 2,
        "integrate": 3,
        "optimize": 4,
        "test": 2,
        "framework": 3,
        "system": 3,
        "engine": 4,
        "comprehensive": 2,
        "complete": 2,
        "advanced": 3,
        "complex": 3,
    }
    text_lower = task_text.lower()
    effort_multiplier = 1.0
    for keyword, multiplier in complexity_keywords.items():
        if keyword in text_lower:
            effort_multiplier += (multiplier - 1) * 0.5
    if len(task_text) > 100:
        effort_multiplier += 0.5
    return int(base_effort * effort_multiplier)
