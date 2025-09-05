"""
Validation schemas and utilities for Devpost integration.

This module provides validation functions and schemas to ensure data
integrity and compliance with Devpost requirements.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from urllib.parse import urlparse

from .models import ProjectMetadata, DevpostProject, ValidationResult


class DevpostValidator:
    """Validator for Devpost project data and requirements."""
    
    # Devpost field requirements
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 100
    MAX_TAGLINE_LENGTH = 120
    MIN_DESCRIPTION_LENGTH = 50
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TAGS = 10
    MAX_TEAM_MEMBERS = 10
    
    # URL validation patterns
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    @classmethod
    def validate_project_metadata(cls, metadata: ProjectMetadata) -> ValidationResult:
        """Validate project metadata against Devpost requirements.
        
        Args:
            metadata: ProjectMetadata instance to validate.
            
        Returns:
            ValidationResult with validation status and any errors.
        """
        errors = []
        warnings = []
        missing_fields = []
        
        # Title validation
        if not metadata.title or not metadata.title.strip():
            missing_fields.append("title")
        elif len(metadata.title) < cls.MIN_TITLE_LENGTH:
            errors.append(f"Title must be at least {cls.MIN_TITLE_LENGTH} characters")
        elif len(metadata.title) > cls.MAX_TITLE_LENGTH:
            errors.append(f"Title must be no more than {cls.MAX_TITLE_LENGTH} characters")
        
        # Tagline validation
        if not metadata.tagline or not metadata.tagline.strip():
            missing_fields.append("tagline")
        elif len(metadata.tagline) > cls.MAX_TAGLINE_LENGTH:
            errors.append(f"Tagline must be no more than {cls.MAX_TAGLINE_LENGTH} characters")
        
        # Description validation
        if not metadata.description or not metadata.description.strip():
            missing_fields.append("description")
        elif len(metadata.description) < cls.MIN_DESCRIPTION_LENGTH:
            errors.append(f"Description must be at least {cls.MIN_DESCRIPTION_LENGTH} characters")
        elif len(metadata.description) > cls.MAX_DESCRIPTION_LENGTH:
            errors.append(f"Description must be no more than {cls.MAX_DESCRIPTION_LENGTH} characters")
        
        # Tags validation
        if len(metadata.tags) > cls.MAX_TAGS:
            errors.append(f"Maximum {cls.MAX_TAGS} tags allowed")
        
        # Team members validation
        if len(metadata.team_members) > cls.MAX_TEAM_MEMBERS:
            errors.append(f"Maximum {cls.MAX_TEAM_MEMBERS} team members allowed")
        
        # URL validations
        if metadata.repository_url and not cls._is_valid_url(metadata.repository_url):
            errors.append("Repository URL is not valid")
        
        if metadata.demo_url and not cls._is_valid_url(metadata.demo_url):
            errors.append("Demo URL is not valid")
        
        if metadata.video_url and not cls._is_valid_url(metadata.video_url):
            errors.append("Video URL is not valid")
        
        # Warnings for optional but recommended fields
        if not metadata.repository_url:
            warnings.append("Repository URL is recommended for better project visibility")
        
        if not metadata.tags:
            warnings.append("Tags help with project discoverability")
        
        is_valid = len(errors) == 0 and len(missing_fields) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            validation_errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def validate_devpost_project(cls, project: DevpostProject) -> ValidationResult:
        """Validate a complete Devpost project.
        
        Args:
            project: DevpostProject instance to validate.
            
        Returns:
            ValidationResult with validation status and any errors.
        """
        # Convert to metadata for validation
        metadata = ProjectMetadata(
            title=project.title,
            tagline=project.tagline,
            description=project.description,
            tags=project.tags,
            team_members=[member.username for member in project.team_members]
        )
        
        # Add repository URL from links if available
        for link in project.links:
            if link.link_type == "repository":
                metadata.repository_url = link.url
                break
        
        return cls.validate_project_metadata(metadata)
    
    @classmethod
    def validate_file_paths(cls, file_paths: List[Path]) -> ValidationResult:
        """Validate that required project files exist.
        
        Args:
            file_paths: List of file paths to check.
            
        Returns:
            ValidationResult with validation status.
        """
        errors = []
        missing_fields = []
        warnings = []
        
        # Check for README file
        readme_files = [p for p in file_paths if p.name.lower().startswith('readme')]
        if not readme_files:
            missing_fields.append("README file")
        
        # Check for common project files
        project_files = [p.name.lower() for p in file_paths]
        
        if not any(f in project_files for f in ['package.json', 'pyproject.toml', 'requirements.txt', 'pom.xml']):
            warnings.append("No package/dependency file found (package.json, pyproject.toml, etc.)")
        
        if not any(f in project_files for f in ['license', 'license.txt', 'license.md']):
            warnings.append("No license file found")
        
        is_valid = len(errors) == 0 and len(missing_fields) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            validation_errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def _is_valid_url(cls, url: str) -> bool:
        """Check if a URL is valid.
        
        Args:
            url: URL string to validate.
            
        Returns:
            True if URL is valid, False otherwise.
        """
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and cls.URL_PATTERN.match(url)
        except Exception:
            return False
    
    @classmethod
    def get_validation_requirements(cls) -> Dict[str, Any]:
        """Get validation requirements for reference.
        
        Returns:
            Dictionary of validation requirements.
        """
        return {
            "title": {
                "required": True,
                "min_length": cls.MIN_TITLE_LENGTH,
                "max_length": cls.MAX_TITLE_LENGTH
            },
            "tagline": {
                "required": True,
                "max_length": cls.MAX_TAGLINE_LENGTH
            },
            "description": {
                "required": True,
                "min_length": cls.MIN_DESCRIPTION_LENGTH,
                "max_length": cls.MAX_DESCRIPTION_LENGTH
            },
            "tags": {
                "required": False,
                "max_count": cls.MAX_TAGS
            },
            "team_members": {
                "required": False,
                "max_count": cls.MAX_TEAM_MEMBERS
            },
            "urls": {
                "pattern": cls.URL_PATTERN.pattern
            }
        }