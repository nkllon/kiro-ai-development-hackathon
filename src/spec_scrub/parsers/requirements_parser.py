"""
Requirements Parser for Spec Scrub RDI Consistency System

Parses requirements documents to extract structured requirement data
for RDI traceability validation.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.spec_framework.core.base import ReflectiveModule


@dataclass
class Requirement:
    """Requirement entity with identity and traceability"""
    requirement_id: str
    user_story: str
    acceptance_criteria: List[str]
    priority: int
    category: str
    source_file: Path
    line_number: int


@dataclass
class RequirementMetadata:
    """Metadata for requirement including dependencies and priorities"""
    requirement_id: str
    dependencies: List[str]
    priority: int
    category: str
    tags: List[str]
    complexity: str


class RequirementsParser(ReflectiveModule):
    """
    Parses requirements documents to extract structured requirement data.
    
    Implements systematic parsing of markdown requirements documents following
    the EARS format (Easy Approach to Requirements Syntax) for RDI traceability.
    """
    
    def __init__(self):
        """Initialize the requirements parser."""
        super().__init__()
        self._requirements_pattern = re.compile(
            r'^### Requirement (\d+(?:\.\d+)*):?\s*(.+?)$', 
            re.MULTILINE
        )
        self._user_story_pattern = re.compile(
            r'\*\*User Story:\*\*\s*(.+?)(?=\n|$)', 
            re.IGNORECASE
        )
        self._acceptance_criteria_pattern = re.compile(
            r'#### Acceptance Criteria\s*\n(.*?)(?=\n###|\n##|$)', 
            re.DOTALL | re.IGNORECASE
        )
        self._criteria_item_pattern = re.compile(
            r'^\d+\.\s+(.+?)$', 
            re.MULTILINE
        )
        
    def health(self) -> Dict[str, Any]:
        """Return health status of the requirements parser."""
        return {
            "status": "healthy",
            "patterns_loaded": 4,
            "last_parse_success": True,
            "component": "RequirementsParser"
        }
    
    def ready(self) -> bool:
        """Check if parser is ready for operation."""
        return True
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "parse_success_rate": 1.0,
            "average_requirements_per_doc": 10.0,
            "parsing_time_ms": 50.0
        }
    
    def status(self) -> str:
        """Return current operational status."""
        return "ready"
    
    def parse_requirements(self, requirements_path: Path) -> List[Requirement]:
        """
        Parse requirements document and extract structured requirements.
        
        Args:
            requirements_path: Path to requirements markdown document
            
        Returns:
            List of Requirement objects with IDs, user stories, acceptance criteria
            
        Raises:
            FileNotFoundError: If requirements file doesn't exist
            ValueError: If requirements format is invalid
        """
        if not requirements_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {requirements_path}")
        
        try:
            content = requirements_path.read_text(encoding='utf-8')
            requirements = []
            
            # Find all requirement sections
            requirement_matches = list(self._requirements_pattern.finditer(content))
            
            for i, match in enumerate(requirement_matches):
                req_id = match.group(1)
                req_title = match.group(2).strip()
                start_pos = match.end()
                
                # Find end position (next requirement or end of file)
                if i + 1 < len(requirement_matches):
                    end_pos = requirement_matches[i + 1].start()
                else:
                    end_pos = len(content)
                
                req_section = content[start_pos:end_pos]
                
                # Extract user story
                user_story = self._extract_user_story(req_section)
                
                # Extract acceptance criteria
                acceptance_criteria = self._extract_acceptance_criteria(req_section)
                
                # Calculate line number
                line_number = content[:match.start()].count('\n') + 1
                
                # Create requirement object
                requirement = Requirement(
                    requirement_id=req_id,
                    user_story=user_story or req_title,
                    acceptance_criteria=acceptance_criteria,
                    priority=self._extract_priority(req_section),
                    category=self._extract_category(req_section),
                    source_file=requirements_path,
                    line_number=line_number
                )
                
                requirements.append(requirement)
            
            return requirements
            
        except Exception as e:
            raise ValueError(f"Failed to parse requirements from {requirements_path}: {e}")
    
    def extract_requirement_metadata(self, requirement: Requirement) -> RequirementMetadata:
        """
        Extract metadata including dependencies, priorities, and categories.
        
        Args:
            requirement: Requirement object to extract metadata from
            
        Returns:
            RequirementMetadata with dependencies, priorities, and categories
        """
        # Read the source file to get full context
        content = requirement.source_file.read_text(encoding='utf-8')
        
        # Find the requirement section
        req_pattern = re.compile(
            f"### Requirement {re.escape(requirement.requirement_id)}.*?(?=\n###|\n##|$)", 
            re.DOTALL | re.IGNORECASE
        )
        match = req_pattern.search(content)
        
        if not match:
            # Return basic metadata if section not found
            return RequirementMetadata(
                requirement_id=requirement.requirement_id,
                dependencies=[],
                priority=requirement.priority,
                category=requirement.category,
                tags=[],
                complexity="medium"
            )
        
        section = match.group(0)
        
        return RequirementMetadata(
            requirement_id=requirement.requirement_id,
            dependencies=self._extract_dependencies(section),
            priority=self._extract_priority(section),
            category=self._extract_category(section),
            tags=self._extract_tags(section),
            complexity=self._extract_complexity(section)
        )
    
    def _extract_user_story(self, section: str) -> Optional[str]:
        """Extract user story from requirement section."""
        match = self._user_story_pattern.search(section)
        return match.group(1).strip() if match else None
    
    def _extract_acceptance_criteria(self, section: str) -> List[str]:
        """Extract acceptance criteria from requirement section."""
        criteria_match = self._acceptance_criteria_pattern.search(section)
        if not criteria_match:
            return []
        
        criteria_text = criteria_match.group(1)
        criteria_items = self._criteria_item_pattern.findall(criteria_text)
        
        return [item.strip() for item in criteria_items if item.strip()]
    
    def _extract_priority(self, section: str) -> int:
        """Extract priority from requirement section."""
        priority_pattern = re.compile(r'priority:\s*(\d+)', re.IGNORECASE)
        match = priority_pattern.search(section)
        return int(match.group(1)) if match else 3  # Default medium priority
    
    def _extract_category(self, section: str) -> str:
        """Extract category from requirement section."""
        category_pattern = re.compile(r'category:\s*([^\n]+)', re.IGNORECASE)
        match = category_pattern.search(section)
        return match.group(1).strip() if match else "functional"
    
    def _extract_dependencies(self, section: str) -> List[str]:
        """Extract dependencies from requirement section."""
        deps_pattern = re.compile(r'dependencies?:\s*([^\n]+)', re.IGNORECASE)
        match = deps_pattern.search(section)
        if not match:
            return []
        
        deps_text = match.group(1)
        # Split on commas and clean up
        deps = [dep.strip() for dep in deps_text.split(',')]
        return [dep for dep in deps if dep]
    
    def _extract_tags(self, section: str) -> List[str]:
        """Extract tags from requirement section."""
        tags_pattern = re.compile(r'tags?:\s*([^\n]+)', re.IGNORECASE)
        match = tags_pattern.search(section)
        if not match:
            return []
        
        tags_text = match.group(1)
        # Split on commas and clean up
        tags = [tag.strip() for tag in tags_text.split(',')]
        return [tag for tag in tags if tag]
    
    def _extract_complexity(self, section: str) -> str:
        """Extract complexity from requirement section."""
        complexity_pattern = re.compile(r'complexity:\s*([^\n]+)', re.IGNORECASE)
        match = complexity_pattern.search(section)
        return match.group(1).strip().lower() if match else "medium"