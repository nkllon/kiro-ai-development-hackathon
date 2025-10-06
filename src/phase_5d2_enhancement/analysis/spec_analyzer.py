"""
Specification analyzer for Phase 5D2 Enhancement System
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..config import get_config


@dataclass
class SpecMetadata:
    """Metadata extracted from a specification."""
    spec_name: str
    spec_path: str
    has_requirements: bool
    has_design: bool
    has_tasks: bool
    file_count: int
    total_lines: int
    encoding: str = "utf-8"
    last_modified: Optional[str] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if spec has all required files."""
        return self.has_requirements and self.has_design and self.has_tasks
    
    @property
    def completeness_score(self) -> float:
        """Calculate completeness score (0-100)."""
        components = [self.has_requirements, self.has_design, self.has_tasks]
        return sum(components) / len(components) * 100


@dataclass
class SpecContent:
    """Content structure of a specification."""
    requirements_content: str = ""
    design_content: str = ""
    tasks_content: str = ""
    metadata: Optional[SpecMetadata] = None
    
    def get_total_content_length(self) -> int:
        """Get total character count of all content."""
        return len(self.requirements_content) + len(self.design_content) + len(self.tasks_content)
    
    def get_content_distribution(self) -> Dict[str, int]:
        """Get distribution of content across files."""
        return {
            "requirements": len(self.requirements_content),
            "design": len(self.design_content),
            "tasks": len(self.tasks_content)
        }


class SpecAnalyzer(ReflectiveModule):
    """
    Analyzer for parsing and analyzing specification content.
    
    Provides utilities for extracting metadata, content structure analysis,
    and encoding handling for specification files.
    """
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        
        self.logger.info(
            "SpecAnalyzer initialized",
            extra={
                "spec_repository_path": self.config.spec_repository_path
            }
        )
    
    def analyze_spec_metadata(self, spec_path: str) -> SpecMetadata:
        """
        Analyze specification metadata and structure.
        
        Args:
            spec_path: Path to the specification directory
            
        Returns:
            SpecMetadata with structure information
        """
        spec_dir = Path(spec_path)
        spec_name = spec_dir.name
        
        # Check for required files
        requirements_file = spec_dir / "requirements.md"
        design_file = spec_dir / "design.md"
        tasks_file = spec_dir / "tasks.md"
        
        has_requirements = requirements_file.exists()
        has_design = design_file.exists()
        has_tasks = tasks_file.exists()
        
        # Count files and lines
        file_count = 0
        total_lines = 0
        encoding = "utf-8"
        last_modified = None
        
        for file_path in [requirements_file, design_file, tasks_file]:
            if file_path.exists():
                file_count += 1
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        total_lines += len(content.splitlines())
                    
                    # Update last modified time
                    mod_time = file_path.stat().st_mtime
                    if last_modified is None or mod_time > last_modified:
                        last_modified = mod_time
                        
                except UnicodeDecodeError:
                    # Try different encodings
                    for enc in ['latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            with open(file_path, 'r', encoding=enc) as f:
                                content = f.read()
                                total_lines += len(content.splitlines())
                                encoding = enc
                                break
                        except UnicodeDecodeError:
                            continue
                    else:
                        self.logger.warning(f"Could not decode file {file_path}")
        
        # Convert timestamp to ISO format
        last_modified_iso = None
        if last_modified:
            from datetime import datetime
            last_modified_iso = datetime.fromtimestamp(last_modified).isoformat()
        
        metadata = SpecMetadata(
            spec_name=spec_name,
            spec_path=str(spec_path),
            has_requirements=has_requirements,
            has_design=has_design,
            has_tasks=has_tasks,
            file_count=file_count,
            total_lines=total_lines,
            encoding=encoding,
            last_modified=last_modified_iso
        )
        
        self.logger.debug(
            "Analyzed spec metadata",
            extra={
                "spec_name": spec_name,
                "is_complete": metadata.is_complete,
                "file_count": file_count,
                "total_lines": total_lines
            }
        )
        
        return metadata
    
    def load_spec_content(self, spec_path: str) -> SpecContent:
        """
        Load complete specification content.
        
        Args:
            spec_path: Path to the specification directory
            
        Returns:
            SpecContent with all file contents
        """
        spec_dir = Path(spec_path)
        
        # Load metadata first
        metadata = self.analyze_spec_metadata(spec_path)
        
        # Load file contents
        requirements_content = ""
        design_content = ""
        tasks_content = ""
        
        # Load requirements
        requirements_file = spec_dir / "requirements.md"
        if requirements_file.exists():
            requirements_content = self._load_file_content(requirements_file, metadata.encoding)
        
        # Load design
        design_file = spec_dir / "design.md"
        if design_file.exists():
            design_content = self._load_file_content(design_file, metadata.encoding)
        
        # Load tasks
        tasks_file = spec_dir / "tasks.md"
        if tasks_file.exists():
            tasks_content = self._load_file_content(tasks_file, metadata.encoding)
        
        spec_content = SpecContent(
            requirements_content=requirements_content,
            design_content=design_content,
            tasks_content=tasks_content,
            metadata=metadata
        )
        
        self.logger.debug(
            "Loaded spec content",
            extra={
                "spec_name": metadata.spec_name,
                "total_content_length": spec_content.get_total_content_length(),
                "content_distribution": spec_content.get_content_distribution()
            }
        )
        
        return spec_content
    
    def _load_file_content(self, file_path: Path, encoding: str = "utf-8") -> str:
        """Load content from a file with proper encoding handling."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try alternative encodings
            for alt_encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=alt_encoding) as f:
                        content = f.read()
                        self.logger.warning(f"Used {alt_encoding} encoding for {file_path}")
                        return content
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, return empty string and log error
            self.logger.error(f"Could not decode file {file_path} with any encoding")
            return ""
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return ""
    
    def find_complete_specs(self, repository_path: Optional[str] = None) -> List[str]:
        """
        Find all complete specifications in the repository.
        
        Args:
            repository_path: Optional path to spec repository (uses config default if None)
            
        Returns:
            List of paths to complete specifications
        """
        if repository_path is None:
            repository_path = self.config.spec_repository_path
        
        repo_dir = Path(repository_path)
        complete_specs = []
        
        if not repo_dir.exists():
            self.logger.warning(f"Spec repository not found: {repository_path}")
            return complete_specs
        
        # Scan all subdirectories
        for spec_dir in repo_dir.iterdir():
            if spec_dir.is_dir() and not spec_dir.name.startswith('.'):
                metadata = self.analyze_spec_metadata(str(spec_dir))
                if metadata.is_complete:
                    complete_specs.append(str(spec_dir))
        
        self.logger.info(
            "Found complete specifications",
            extra={
                "repository_path": repository_path,
                "complete_specs_count": len(complete_specs),
                "total_directories_scanned": len([d for d in repo_dir.iterdir() if d.is_dir()])
            }
        )
        
        return complete_specs
    
    def analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze the structure of specification content.
        
        Args:
            content: Specification content to analyze
            
        Returns:
            Dictionary with structure analysis
        """
        lines = content.splitlines()
        
        # Count different types of content
        headers = [line for line in lines if line.strip().startswith('#')]
        code_blocks = content.count('```')
        bullet_points = len([line for line in lines if line.strip().startswith(('-', '*', '+'))])
        numbered_lists = len([line for line in lines if line.strip() and line.strip()[0].isdigit() and '.' in line.strip()[:5]])
        
        # Analyze header hierarchy
        header_levels = {}
        for header in headers:
            level = len(header) - len(header.lstrip('#'))
            if level > 0:
                header_levels[level] = header_levels.get(level, 0) + 1
        
        # Calculate content metrics
        word_count = len(content.split())
        char_count = len(content)
        line_count = len(lines)
        
        structure_analysis = {
            "metrics": {
                "line_count": line_count,
                "word_count": word_count,
                "char_count": char_count
            },
            "structure": {
                "headers_count": len(headers),
                "header_levels": header_levels,
                "code_blocks": code_blocks // 2,  # Divide by 2 since each block has opening and closing
                "bullet_points": bullet_points,
                "numbered_lists": numbered_lists
            },
            "content_density": {
                "words_per_line": word_count / line_count if line_count > 0 else 0,
                "chars_per_line": char_count / line_count if line_count > 0 else 0,
                "structure_ratio": (len(headers) + bullet_points + numbered_lists) / line_count if line_count > 0 else 0
            }
        }
        
        return structure_analysis
    
    def extract_requirements_count(self, requirements_content: str) -> int:
        """Extract the number of requirements from requirements content."""
        lines = requirements_content.splitlines()
        
        # Look for requirement patterns
        requirement_patterns = [
            "### Requirement",
            "## Requirement", 
            "# Requirement",
            "**Requirement",
            "Requirement "
        ]
        
        requirement_count = 0
        for line in lines:
            line_stripped = line.strip()
            for pattern in requirement_patterns:
                if line_stripped.startswith(pattern):
                    requirement_count += 1
                    break
        
        return requirement_count
    
    def extract_task_count(self, tasks_content: str) -> int:
        """Extract the number of tasks from tasks content."""
        lines = tasks_content.splitlines()
        
        # Look for task patterns (checkboxes)
        task_count = 0
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('- [ ]') or line_stripped.startswith('- [x]') or line_stripped.startswith('- [-]'):
                task_count += 1
        
        return task_count
    
    def get_repository_summary(self, repository_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive summary of the specification repository.
        
        Args:
            repository_path: Optional path to spec repository
            
        Returns:
            Repository summary with statistics
        """
        if repository_path is None:
            repository_path = self.config.spec_repository_path
        
        repo_dir = Path(repository_path)
        
        if not repo_dir.exists():
            return {"error": f"Repository not found: {repository_path}"}
        
        # Analyze all specs
        all_specs = []
        complete_specs = []
        incomplete_specs = []
        
        total_requirements = 0
        total_tasks = 0
        total_lines = 0
        
        for spec_dir in repo_dir.iterdir():
            if spec_dir.is_dir() and not spec_dir.name.startswith('.'):
                try:
                    metadata = self.analyze_spec_metadata(str(spec_dir))
                    all_specs.append(metadata)
                    
                    if metadata.is_complete:
                        complete_specs.append(metadata)
                        
                        # Load content for complete specs to get detailed stats
                        content = self.load_spec_content(str(spec_dir))
                        total_requirements += self.extract_requirements_count(content.requirements_content)
                        total_tasks += self.extract_task_count(content.tasks_content)
                    else:
                        incomplete_specs.append(metadata)
                    
                    total_lines += metadata.total_lines
                    
                except Exception as e:
                    self.logger.warning(f"Error analyzing spec {spec_dir.name}: {e}")
        
        # Calculate statistics
        summary = {
            "repository_path": repository_path,
            "total_specs": len(all_specs),
            "complete_specs": len(complete_specs),
            "incomplete_specs": len(incomplete_specs),
            "completeness_percentage": len(complete_specs) / len(all_specs) * 100 if all_specs else 0,
            "statistics": {
                "total_requirements": total_requirements,
                "total_tasks": total_tasks,
                "total_lines": total_lines,
                "average_lines_per_spec": total_lines / len(complete_specs) if complete_specs else 0
            },
            "complete_spec_names": [spec.spec_name for spec in complete_specs],
            "incomplete_spec_names": [spec.spec_name for spec in incomplete_specs]
        }
        
        self.logger.info(
            "Generated repository summary",
            extra={
                "total_specs": summary["total_specs"],
                "complete_specs": summary["complete_specs"],
                "completeness_percentage": summary["completeness_percentage"]
            }
        )
        
        return summary