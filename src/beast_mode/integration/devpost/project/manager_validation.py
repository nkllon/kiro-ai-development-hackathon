"""
Manager Validation

This module was extracted from manager.py
as part of RM-DDD compliance refactoring.
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from ..models import DevpostProject, ProjectMetadata, DevpostConfig, ProjectConnection, SyncStatus, ValidationResult
from ..interfaces import ProjectManagerInterface
from ..config import DevpostConfigManager
from ....core.exceptions import ConfigurationError, ValidationError
import tomllib
import tomli as tomllib
from src.rm_ddd.core.health import ModuleHealth


def validate_project(self) -> ValidationResult:
    """Validate project against Devpost requirements.
        
        Returns:
            ValidationResult with validation status and issues
        """
    metadata = self.get_project_metadata()
    missing_fields = []
    validation_errors = []
    warnings = []
    if not metadata.title:
        missing_fields.append('title')
    if not metadata.description or len(metadata.description) < 50:
        missing_fields.append('description (minimum 50 characters)')
    if not metadata.repository_url and (not metadata.demo_url):
        missing_fields.append('repository_url or demo_url')
    media_files = self._find_media_files()
    if not media_files:
        warnings.append('No media files found (screenshots, videos, etc.)')
    readme_issues = self._validate_readme()
    validation_errors.extend(readme_issues)
    project_files = self._check_project_files()
    if project_files['missing']:
        warnings.extend([f'Missing {file}' for file in project_files['missing']])
    is_valid = len(missing_fields) == 0 and len(validation_errors) == 0
    return ValidationResult(is_valid=is_valid, missing_fields=missing_fields, validation_errors=validation_errors, warnings=warnings)

def _validate_readme(self) -> List[str]:
    """Validate README file quality."""
    issues = []
    readme_data = self._extract_readme_metadata()
    if not readme_data:
        issues.append('No README file found')
        return issues
    readme_path = readme_data['path']
    try:
        content = readme_path.read_text(encoding='utf-8')
        if len(content) < 200:
            issues.append('README is too short (minimum 200 characters recommended)')
        content_lower = content.lower()
        recommended_sections = ['installation', 'usage', 'description']
        missing_sections = []
        for section in recommended_sections:
            if section not in content_lower:
                missing_sections.append(section)
        if missing_sections:
            issues.append(f"README missing recommended sections: {', '.join(missing_sections)}")
    except Exception:
        issues.append('Could not read README file')
    return issues

def _check_project_files(self) -> Dict[str, List[str]]:
    """Check for common project files."""
    common_files = {'LICENSE': ['LICENSE', 'LICENSE.txt', 'LICENSE.md'], 'CHANGELOG': ['CHANGELOG.md', 'CHANGELOG.txt', 'HISTORY.md'], 'CONTRIBUTING': ['CONTRIBUTING.md', 'CONTRIBUTING.txt']}
    found = []
    missing = []
    for file_type, patterns in common_files.items():
        file_found = False
        for pattern in patterns:
            if (self.project_root / pattern).exists():
                found.append(pattern)
                file_found = True
                break
        if not file_found:
            missing.append(file_type)
    return {'found': found, 'missing': missing}
