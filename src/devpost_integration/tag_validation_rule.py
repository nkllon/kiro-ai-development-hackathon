#!/usr/bin/env python3
"""
Tag Validation Rule - Project tag validation

Extracted from validation_rules_extended.py for RM-DDD compliance.
Single responsibility: Project tag validation and categorization.
"""

import re
from typing import List, Optional, Dict, Any

from .models import ProjectMetadata
from .validation_models import (
    ValidationRule, ValidationIssue, ValidationSeverity, 
    ValidationCategory, ValidationContext
)


class TagValidationRule(ValidationRule):
    """Validation rule for project tags."""
    
    def __init__(self):
        super().__init__(
            name="tag_validation",
            description="Validates project tags and categorization",
            category=ValidationCategory.TAGS
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate project tags."""
        issues = []
        
        if not metadata.tags:
            issues.append(ValidationIssue(
                field="tags",
                message="No project tags provided",
                severity=ValidationSeverity.HIGH,
                category=ValidationCategory.TAGS,
                suggestion="Add relevant project tags",
                fix_action="Specify project tags for better categorization"
            ))
            return issues
        
        # Check tag count
        tag_count = len(metadata.tags)
        if tag_count < 3:
            issues.append(ValidationIssue(
                field="tags",
                message="Too few tags (minimum 3 recommended)",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TAGS,
                suggestion="Add more relevant tags",
                fix_action="Include at least 3 project tags"
            ))
        elif tag_count > 15:
            issues.append(ValidationIssue(
                field="tags",
                message="Too many tags (maximum 15 recommended)",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TAGS,
                suggestion="Use most relevant tags only",
                fix_action="Reduce tags to most important ones"
            ))
        
        # Validate individual tags
        for i, tag in enumerate(metadata.tags):
            tag_issues = self._validate_single_tag(tag, i)
            issues.extend(tag_issues)
        
        # Check for tag relevance
        relevance_issues = self._check_tag_relevance(metadata)
        issues.extend(relevance_issues)
        
        return issues
    
    def _validate_single_tag(self, tag: str, index: int) -> List[ValidationIssue]:
        """Validate individual tag."""
        issues = []
        
        if not tag or not tag.strip():
            issues.append(ValidationIssue(
                field=f"tags[{index}]",
                message="Empty tag",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TAGS,
                suggestion="Remove empty tags",
                fix_action="Delete empty tag entries"
            ))
            return issues
        
        tag = tag.strip()
        
        # Check tag length
        if len(tag) < 2:
            issues.append(ValidationIssue(
                field=f"tags[{index}]",
                message="Tag is too short (minimum 2 characters)",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TAGS,
                suggestion="Use longer, more descriptive tags",
                fix_action="Expand tag to at least 2 characters"
            ))
        elif len(tag) > 30:
            issues.append(ValidationIssue(
                field=f"tags[{index}]",
                message="Tag is too long (maximum 30 characters)",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TAGS,
                suggestion="Use shorter, more concise tags",
                fix_action="Shorten tag to 30 characters or less"
            ))
        
        # Check tag format
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', tag):
            issues.append(ValidationIssue(
                field=f"tags[{index}]",
                message="Tag contains invalid characters",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TAGS,
                suggestion="Use only letters, numbers, spaces, hyphens, and underscores",
                fix_action="Remove special characters from tag"
            ))
        
        # Check for proper capitalization
        if tag != tag.lower() and tag != tag.title():
            issues.append(ValidationIssue(
                field=f"tags[{index}]",
                message="Tag should be lowercase or title case",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TAGS,
                suggestion="Use consistent capitalization",
                fix_action="Convert tag to lowercase or title case"
            ))
        
        return issues
    
    def _check_tag_relevance(self, metadata: ProjectMetadata) -> List[ValidationIssue]:
        """Check if tags are relevant to project content."""
        issues = []
        
        if not metadata.tags or not metadata.description:
            return issues
        
        # Common technology tags
        tech_tags = {'python', 'javascript', 'react', 'node', 'java', 'c++', 'html', 'css', 'sql', 'mongodb'}
        project_tags = {tag.lower() for tag in metadata.tags}
        description_lower = metadata.description.lower()
        
        # Check if technology tags match description
        mentioned_techs = set()
        for tech in tech_tags:
            if tech in description_lower:
                mentioned_techs.add(tech)
        
        relevant_tech_tags = project_tags.intersection(tech_tags)
        if relevant_tech_tags and not mentioned_techs:
            issues.append(ValidationIssue(
                field="tags",
                message="Technology tags don't match project description",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TAGS,
                suggestion="Ensure tags reflect technologies used in project",
                fix_action="Update tags or description for consistency"
            ))
        
        return issues
