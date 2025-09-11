#!/usr/bin/env python3
"""
Link Validation Rule - Project link validation

Extracted from validation_rules_extended.py for RM-DDD compliance.
Single responsibility: Project link validation and URL checking.
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import requests

from .models import ProjectMetadata, ProjectLink
from .validation_models import (
    ValidationRule, ValidationIssue, ValidationSeverity, 
    ValidationCategory, ValidationContext
)


class LinkValidationRule(ValidationRule):
    """Validation rule for project links."""
    
    def __init__(self):
        super().__init__(
            name="link_validation",
            description="Validates project links and URLs",
            category=ValidationCategory.LINKS
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate project links."""
        issues = []
        
        if not metadata.links:
            issues.append(ValidationIssue(
                field="links",
                message="No project links provided",
                severity=ValidationSeverity.HIGH,
                category=ValidationCategory.LINKS,
                suggestion="Add project links (GitHub, demo, documentation)",
                fix_action="Provide at least one project link"
            ))
            return issues
        
        # Check for required link types
        link_types = {link.link_type for link in metadata.links}
        required_types = {'github', 'demo', 'documentation'}
        missing_types = required_types - link_types
        
        for missing_type in missing_types:
            issues.append(ValidationIssue(
                field="links",
                message=f"Missing {missing_type} link",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.LINKS,
                suggestion=f"Add a {missing_type} link to your project",
                fix_action=f"Provide {missing_type} URL in project links"
            ))
        
        # Validate individual links
        for i, link in enumerate(metadata.links):
            link_issues = self._validate_single_link(link, i, context)
            issues.extend(link_issues)
        
        return issues
    
    def _validate_single_link(self, link: ProjectLink, index: int, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate a single project link."""
        issues = []
        
        # Check URL format
        if not link.url or not self._is_valid_url(link.url):
            issues.append(ValidationIssue(
                field=f"links[{index}].url",
                message="Invalid URL format",
                severity=ValidationSeverity.HIGH,
                category=ValidationCategory.LINKS,
                suggestion="Provide a valid URL",
                fix_action="Enter a properly formatted URL"
            ))
            return issues
        
        # Check link type specific validation
        if link.link_type == 'github':
            if not self._is_github_url(link.url):
                issues.append(ValidationIssue(
                    field=f"links[{index}].url",
                    message="GitHub link should point to GitHub repository",
                    severity=ValidationSeverity.MEDIUM,
                    category=ValidationCategory.LINKS,
                    suggestion="Use a GitHub repository URL",
                    fix_action="Update URL to point to GitHub repository"
                ))
        
        elif link.link_type == 'demo':
            if not self._is_demo_url(link.url):
                issues.append(ValidationIssue(
                    field=f"links[{index}].url",
                    message="Demo link should be accessible",
                    severity=ValidationSeverity.MEDIUM,
                    category=ValidationCategory.LINKS,
                    suggestion="Ensure demo URL is working and accessible",
                    fix_action="Verify demo URL is accessible"
                ))
        
        # Check URL accessibility (optional, can be slow)
        if context and context.custom_metadata.get('check_url_accessibility', False):
            if not self._is_url_accessible(link.url):
                issues.append(ValidationIssue(
                    field=f"links[{index}].url",
                    message="URL is not accessible",
                    severity=ValidationSeverity.LOW,
                    category=ValidationCategory.LINKS,
                    suggestion="Verify URL is working and accessible",
                    fix_action="Check URL accessibility and fix if needed"
                ))
        
        return issues
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_github_url(self, url: str) -> bool:
        """Check if URL is a GitHub repository."""
        return 'github.com' in url.lower() and '/repos/' not in url
    
    def _is_demo_url(self, url: str) -> bool:
        """Check if URL appears to be a demo."""
        demo_indicators = ['demo', 'example', 'live', 'app', 'site']
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in demo_indicators)
    
    def _is_url_accessible(self, url: str) -> bool:
        """Check if URL is accessible (with timeout)."""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code < 400
        except Exception:
            return False
