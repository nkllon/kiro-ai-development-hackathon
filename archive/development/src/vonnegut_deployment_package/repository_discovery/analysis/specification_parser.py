"""
Specification Parser - Extract Requirements and Metadata from Specs

This module provides systematic parsing of specification files to extract structured data
including requirements, user stories, acceptance criteria, and task lists from markdown specs.
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class UserStory:
    """Represents a user story extracted from specifications."""
    role: str
    feature: str
    benefit: str
    raw_text: str
    section: str
    requirement_id: Optional[str] = None


@dataclass
class AcceptanceCriteria:
    """Represents acceptance criteria in EARS format."""
    criteria_id: str
    text: str
    ears_type: str  # WHEN, IF, WHERE, etc.
    condition: str
    system: str
    response: str
    requirement_id: Optional[str] = None


@dataclass
class Task:
    """Represents a task extracted from task lists."""
    task_id: str
    title: str
    description: str
    status: str  # completed, in_progress, not_started
    dependencies: List[str] = field(default_factory=list)
    requirements_refs: List[str] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)


@dataclass
class Requirement:
    """Represents a requirement extracted from specifications."""
    requirement_id: str
    title: str
    description: str
    user_story: Optional[UserStory] = None
    acceptance_criteria: List[AcceptanceCriteria] = field(default_factory=list)
    section: str = ""
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)


@dataclass
class SpecificationMetadata:
    """Metadata about a specification file."""
    spec_name: str
    file_path: str
    title: str
    description: str
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    status: str = "active"
    tags: List[str] = field(default_factory=list)


@dataclass
class ParsedSpecification:
    """Complete parsed specification with all extracted data."""
    metadata: SpecificationMetadata
    requirements: List[Requirement] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    raw_content: str = ""
    parsing_errors: List[str] = field(default_factory=list)
    parsing_warnings: List[str] = field(default_factory=list)


class SpecificationParser(ReflectiveModule):
    """
    Systematic specification parser for extracting structured data from markdown specs.
    
    This parser extracts requirements, user stories, acceptance criteria, and tasks
    from specification files, providing comprehensive traceability and validation.
    """
    
    def __init__(self):
        """Initialize the SpecificationParser with Beast Mode observability."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Regex patterns for parsing different elements
        self.patterns = {
            'user_story': re.compile(
                r'(?:\*\*User Story:\*\*|User Story:)\s*As an?\s+([^,]+),\s*I want\s+([^,]+),\s*so that\s+(.+?)(?:\n|$)',
                re.IGNORECASE | re.MULTILINE
            ),
            'requirement_header': re.compile(
                r'^#{1,4}\s+Requirement\s+(\d+(?:\.\d+)*):?\s*(.+?)$',
                re.MULTILINE | re.IGNORECASE
            ),
            'ears_criteria': re.compile(
                r'^\s*(\d+(?:\.\d+)*)\.\s+(WHEN|IF|WHERE|WHILE)\s+(.+?)\s+THEN\s+(.+?)\s+SHALL\s+(.+?)(?:\n|$)',
                re.MULTILINE | re.IGNORECASE
            ),
            'task_item': re.compile(
                r'^(\s*)-\s*\[([x\s])\]\s*(\d+(?:\.\d+)*)\s+(.+?)$',
                re.MULTILINE
            ),
            'requirements_ref': re.compile(
                r'_Requirements?:\s*([\d\.,\s]+)_',
                re.IGNORECASE
            )
        }
        
        self.logger.info("SpecificationParser initialized with Beast Mode observability")
    
    def parse_spec_file(self, file_path: str) -> ParsedSpecification:
        """
        Parse a specification file and extract all structured data.
        
        Args:
            file_path: Path to the specification file
            
        Returns:
            ParsedSpecification with extracted data and metadata
        """
        try:
            self.logger.info(f"Parsing specification file: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, content)
            
            # Create parsed specification
            parsed_spec = ParsedSpecification(
                metadata=metadata,
                raw_content=content
            )
            
            # Extract requirements
            parsed_spec.requirements = self._extract_requirements(content)
            
            # Extract tasks if this is a tasks file
            if 'tasks.md' in file_path.lower():
                parsed_spec.tasks = self._extract_tasks(content)
            
            # Validate and cross-reference
            self._validate_and_cross_reference(parsed_spec)
            
            self.logger.info(f"Successfully parsed {file_path}: {len(parsed_spec.requirements)} requirements, {len(parsed_spec.tasks)} tasks")
            
            return parsed_spec
            
        except Exception as e:
            error_msg = f"Failed to parse specification file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            
            # Return minimal parsed spec with error
            metadata = SpecificationMetadata(
                spec_name=Path(file_path).stem,
                file_path=file_path,
                title="Parse Error",
                description=f"Failed to parse: {str(e)}"
            )
            
            return ParsedSpecification(
                metadata=metadata,
                parsing_errors=[error_msg]
            )
    
    def _extract_metadata(self, file_path: str, content: str) -> SpecificationMetadata:
        """Extract metadata from specification file."""
        path_obj = Path(file_path)
        
        # Extract title from first header or filename
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else path_obj.stem.replace('-', ' ').title()
        
        # Extract description from introduction section
        intro_match = re.search(
            r'##\s+(?:Introduction|Overview)\s*\n\n(.+?)(?=\n##|\n#|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        description = intro_match.group(1).strip() if intro_match else ""
        
        # Get file stats
        stat = path_obj.stat()
        created_date = datetime.fromtimestamp(stat.st_ctime)
        updated_date = datetime.fromtimestamp(stat.st_mtime)
        
        # Extract tags from content
        tags = self._extract_tags(content)
        
        return SpecificationMetadata(
            spec_name=path_obj.parent.name,  # Directory name
            file_path=file_path,
            title=title,
            description=description,
            created_date=created_date,
            updated_date=updated_date,
            tags=tags
        )
    
    def _extract_requirements(self, content: str) -> List[Requirement]:
        """Extract requirements with user stories and acceptance criteria."""
        requirements = []
        
        # Find all requirement sections
        req_matches = list(self.patterns['requirement_header'].finditer(content))
        
        for i, match in enumerate(req_matches):
            req_id = match.group(1)
            req_title = match.group(2).strip()
            
            # Get content between this requirement and the next
            start_pos = match.end()
            end_pos = req_matches[i + 1].start() if i + 1 < len(req_matches) else len(content)
            req_content = content[start_pos:end_pos]
            
            # Extract user story
            user_story = self._extract_user_story(req_content, req_id)
            
            # Extract acceptance criteria
            acceptance_criteria = self._extract_acceptance_criteria(req_content, req_id)
            
            # Extract description (everything before user story or acceptance criteria)
            description = self._extract_requirement_description(req_content)
            
            requirement = Requirement(
                requirement_id=req_id,
                title=req_title,
                description=description,
                user_story=user_story,
                acceptance_criteria=acceptance_criteria,
                section=f"Requirement {req_id}"
            )
            
            requirements.append(requirement)
        
        return requirements
    
    def _extract_user_story(self, content: str, req_id: str) -> Optional[UserStory]:
        """Extract user story from requirement content."""
        match = self.patterns['user_story'].search(content)
        if not match:
            return None
        
        return UserStory(
            role=match.group(1).strip(),
            feature=match.group(2).strip(),
            benefit=match.group(3).strip(),
            raw_text=match.group(0),
            section=f"Requirement {req_id}",
            requirement_id=req_id
        )
    
    def _extract_acceptance_criteria(self, content: str, req_id: str) -> List[AcceptanceCriteria]:
        """Extract EARS format acceptance criteria."""
        criteria = []
        
        # Find acceptance criteria section
        ac_section_match = re.search(
            r'(?:####?\s*Acceptance Criteria|Acceptance Criteria:)\s*\n(.*?)(?=\n###|\n##|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not ac_section_match:
            return criteria
        
        ac_content = ac_section_match.group(1)
        
        # Extract EARS format criteria
        for match in self.patterns['ears_criteria'].finditer(ac_content):
            criteria_id = match.group(1)
            ears_type = match.group(2).upper()
            condition = match.group(3).strip()
            system = match.group(4).strip()
            response = match.group(5).strip()
            
            criteria.append(AcceptanceCriteria(
                criteria_id=f"{req_id}.{criteria_id}",
                text=match.group(0).strip(),
                ears_type=ears_type,
                condition=condition,
                system=system,
                response=response,
                requirement_id=req_id
            ))
        
        return criteria
    
    def _extract_requirement_description(self, content: str) -> str:
        """Extract requirement description text."""
        # Get text before user story or acceptance criteria
        user_story_pos = content.find('**User Story:**')
        if user_story_pos == -1:
            user_story_pos = content.find('User Story:')
        
        ac_pos = content.find('Acceptance Criteria')
        
        # Find the earliest position
        end_pos = len(content)
        if user_story_pos != -1:
            end_pos = min(end_pos, user_story_pos)
        if ac_pos != -1:
            end_pos = min(end_pos, ac_pos)
        
        description = content[:end_pos].strip()
        
        # Clean up markdown formatting
        description = re.sub(r'^#+\s*', '', description, flags=re.MULTILINE)
        description = re.sub(r'\*\*([^*]+)\*\*', r'\1', description)
        
        return description.strip()
    
    def _extract_tasks(self, content: str) -> List[Task]:
        """Extract tasks from task list content."""
        tasks = []
        
        # Find all task items
        for match in self.patterns['task_item'].finditer(content):
            indent = match.group(1)
            status_char = match.group(2)
            task_id = match.group(3)
            title = match.group(4).strip()
            
            # Determine status
            status = 'completed' if status_char.lower() == 'x' else 'not_started'
            
            # Extract task description (lines following the task)
            description = self._extract_task_description(content, match.end())
            
            # Extract requirements references
            req_refs = self._extract_requirements_references(description)
            
            task = Task(
                task_id=task_id,
                title=title,
                description=description,
                status=status,
                requirements_refs=req_refs
            )
            
            tasks.append(task)
        
        return tasks
    
    def _extract_task_description(self, content: str, start_pos: int) -> str:
        """Extract task description from content following task header."""
        # Get lines following the task until next task or section
        lines = content[start_pos:].split('\n')
        description_lines = []
        
        for line in lines:
            # Stop at next task or major section
            if re.match(r'^\s*-\s*\[[x\s]\]', line) or re.match(r'^#+\s', line):
                break
            
            # Include indented content
            if line.strip() and (line.startswith('  ') or line.startswith('\t')):
                description_lines.append(line.strip())
            elif not line.strip():
                # Include empty lines within description
                if description_lines:
                    description_lines.append('')
            else:
                # Stop at non-indented content
                break
        
        return '\n'.join(description_lines).strip()
    
    def _extract_requirements_references(self, text: str) -> List[str]:
        """Extract requirements references from text."""
        refs = []
        
        for match in self.patterns['requirements_ref'].finditer(text):
            ref_text = match.group(1)
            # Split by commas and clean up
            for ref in ref_text.split(','):
                ref = ref.strip()
                if ref:
                    refs.append(ref)
        
        return refs
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        tags = []
        
        # Look for common tag patterns
        tag_patterns = [
            r'(?:Tags?|Keywords?):\s*([^\n]+)',
            r'(?:Category|Type):\s*([^\n]+)',
            r'(?:Priority):\s*([^\n]+)'
        ]
        
        for pattern in tag_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Split by commas and clean up
                for tag in match.split(','):
                    tag = tag.strip().lower()
                    if tag and tag not in tags:
                        tags.append(tag)
        
        return tags
    
    def _validate_and_cross_reference(self, parsed_spec: ParsedSpecification) -> None:
        """Validate parsed data and create cross-references."""
        # Validate requirements have proper structure
        for req in parsed_spec.requirements:
            if not req.user_story and not req.acceptance_criteria:
                parsed_spec.parsing_warnings.append(
                    f"Requirement {req.requirement_id} has no user story or acceptance criteria"
                )
        
        # Validate task references
        req_ids = {req.requirement_id for req in parsed_spec.requirements}
        for task in parsed_spec.tasks:
            for ref in task.requirements_refs:
                if ref not in req_ids:
                    parsed_spec.parsing_warnings.append(
                        f"Task {task.task_id} references unknown requirement {ref}"
                    )
    
    def extract_requirements(self, spec_path: str) -> List[Requirement]:
        """
        Extract requirements with traceability from a specification file.
        
        Args:
            spec_path: Path to specification file
            
        Returns:
            List of extracted requirements with full traceability
        """
        parsed_spec = self.parse_spec_file(spec_path)
        return parsed_spec.requirements
    
    def parse_all_specs(self, specs_directory: str) -> Dict[str, ParsedSpecification]:
        """
        Parse all specifications in a directory.
        
        Args:
            specs_directory: Path to directory containing spec directories
            
        Returns:
            Dictionary mapping spec names to parsed specifications
        """
        parsed_specs = {}
        specs_path = Path(specs_directory)
        
        if not specs_path.exists():
            self.logger.error(f"Specs directory does not exist: {specs_directory}")
            return parsed_specs
        
        # Find all spec directories
        for spec_dir in specs_path.iterdir():
            if not spec_dir.is_dir():
                continue
            
            spec_name = spec_dir.name
            self.logger.info(f"Processing spec directory: {spec_name}")
            
            # Parse each markdown file in the spec directory
            spec_files = {}
            for md_file in spec_dir.glob('*.md'):
                file_type = md_file.stem  # requirements, design, tasks
                parsed_spec = self.parse_spec_file(str(md_file))
                spec_files[file_type] = parsed_spec
            
            # Combine into single specification if multiple files
            if spec_files:
                # Use requirements.md as primary, merge others
                primary_spec = spec_files.get('requirements') or list(spec_files.values())[0]
                
                # Merge tasks from tasks.md
                if 'tasks' in spec_files:
                    primary_spec.tasks.extend(spec_files['tasks'].tasks)
                
                parsed_specs[spec_name] = primary_spec
        
        self.logger.info(f"Parsed {len(parsed_specs)} specifications")
        return parsed_specs
    
    def health_check(self) -> Dict[str, Any]:
        """Beast Mode health monitoring implementation."""
        return {
            "status": "healthy",
            "parser_patterns": len(self.patterns),
            "supported_formats": ["markdown", "requirements", "tasks"],
            "extraction_capabilities": [
                "requirements", "user_stories", "acceptance_criteria", 
                "tasks", "metadata", "traceability"
            ]
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Beast Mode metrics collection implementation."""
        return {
            "parser_patterns_count": len(self.patterns),
            "supported_elements": [
                "requirements", "user_stories", "acceptance_criteria",
                "tasks", "metadata", "cross_references"
            ]
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get parser capabilities for Beast Mode integration."""
        return {
            "parsing": ["markdown", "requirements", "tasks", "user_stories"],
            "extraction": ["metadata", "traceability", "cross_references"],
            "validation": ["ears_format", "structure", "references"],
            "formats": ["requirements.md", "design.md", "tasks.md"]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status for Beast Mode monitoring."""
        return {
            "component": "SpecificationParser",
            "status": "operational",
            "patterns_loaded": len(self.patterns),
            "last_check": datetime.now().isoformat(),
            "capabilities": self.get_capabilities()
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information for Beast Mode registry."""
        return {
            "name": "SpecificationParser",
            "version": "1.0.0",
            "description": "Systematic specification parser for extracting structured data",
            "dependencies": ["re", "pathlib", "datetime"],
            "capabilities": self.get_capabilities()
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self.logger.error(f"SpecificationParser degradation: {str(error)}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_text_extraction",
            "available_functions": ["parse_spec_file", "extract_metadata"]
        }