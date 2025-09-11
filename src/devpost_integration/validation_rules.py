#!/usr/bin/env python3
"""
Validation Rules - Core validation rules and base classes

Extracted from validation_engine.py for RM-DDD compliance.
Single responsibility: Core validation rules and base rule classes.
"""

import re
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from pathlib import Path

from .models import ProjectMetadata, ProjectLink, ProjectTeamMember
from .validation_models import (
    ValidationRule, ValidationIssue, ValidationSeverity, 
    ValidationCategory, ValidationContext
)


class RequiredFieldRule(ValidationRule):
    """Validation rule for required fields."""
    
    def __init__(self):
        super().__init__(
            name="required_fields",
            description="Validates that all required fields are present",
            category=ValidationCategory.REQUIRED_FIELDS
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate required fields."""
        issues = []
        
        # Required fields for DevPost submission
        required_fields = {
            'title': metadata.title,
            'description': metadata.description,
            'technologies': metadata.technologies,
            'team_members': metadata.team_members,
            'links': metadata.links
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or (isinstance(field_value, list) and len(field_value) == 0):
                issues.append(ValidationIssue(
                    field=field_name,
                    message=f"Required field '{field_name}' is missing or empty",
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.REQUIRED_FIELDS,
                    suggestion=f"Provide a value for the {field_name} field",
                    fix_action=f"Set {field_name} in project metadata"
                ))
        
        # Validate title length
        if metadata.title and len(metadata.title.strip()) < 10:
            issues.append(ValidationIssue(
                field="title",
                message="Project title is too short (minimum 10 characters)",
                severity=ValidationSeverity.HIGH,
                category=ValidationCategory.REQUIRED_FIELDS,
                suggestion="Provide a more descriptive project title",
                fix_action="Expand the project title to at least 10 characters"
            ))
        
        # Validate description length
        if metadata.description and len(metadata.description.strip()) < 50:
            issues.append(ValidationIssue(
                field="description",
                message="Project description is too short (minimum 50 characters)",
                severity=ValidationSeverity.HIGH,
                category=ValidationCategory.REQUIRED_FIELDS,
                suggestion="Provide a more detailed project description",
                fix_action="Expand the project description to at least 50 characters"
            ))
        
        return issues


class ContentQualityRule(ValidationRule):
    """Validation rule for content quality."""
    
    def __init__(self):
        super().__init__(
            name="content_quality",
            description="Validates content quality and readability",
            category=ValidationCategory.CONTENT_QUALITY
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate content quality."""
        issues = []
        
        # Check for placeholder text
        placeholder_patterns = [
            r'\b(placeholder|todo|fixme|hack|temp|temporary)\b',
            r'\b(your|add|enter|insert|replace)\s+(here|text|description|title)\b',
            r'\b(coming soon|tbd|tba|under construction)\b'
        ]
        
        for pattern in placeholder_patterns:
            if metadata.title and re.search(pattern, metadata.title, re.IGNORECASE):
                issues.append(ValidationIssue(
                    field="title",
                    message="Project title contains placeholder text",
                    severity=ValidationSeverity.MEDIUM,
                    category=ValidationCategory.CONTENT_QUALITY,
                    suggestion="Replace placeholder text with actual project title",
                    fix_action="Update title with real project information"
                ))
                break
        
        if metadata.description:
            for pattern in placeholder_patterns:
                if re.search(pattern, metadata.description, re.IGNORECASE):
                    issues.append(ValidationIssue(
                        field="description",
                        message="Project description contains placeholder text",
                        severity=ValidationSeverity.MEDIUM,
                        category=ValidationCategory.CONTENT_QUALITY,
                        suggestion="Replace placeholder text with actual project description",
                        fix_action="Update description with real project information"
                    ))
                    break
        
        # Check for proper capitalization
        if metadata.title and not self._is_properly_capitalized(metadata.title):
            issues.append(ValidationIssue(
                field="title",
                message="Project title should use proper capitalization",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.CONTENT_QUALITY,
                suggestion="Use title case for the project title",
                fix_action="Capitalize the first letter of each major word"
            ))
        
        # Check for excessive repetition
        if metadata.description and self._has_excessive_repetition(metadata.description):
            issues.append(ValidationIssue(
                field="description",
                message="Project description has excessive word repetition",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.CONTENT_QUALITY,
                suggestion="Improve description variety and readability",
                fix_action="Rewrite description to reduce repetitive language"
            ))
        
        # Check for minimum word count in description
        if metadata.description:
            word_count = len(metadata.description.split())
            if word_count < 20:
                issues.append(ValidationIssue(
                    field="description",
                    message="Project description is too brief (minimum 20 words recommended)",
                    severity=ValidationSeverity.MEDIUM,
                    category=ValidationCategory.CONTENT_QUALITY,
                    suggestion="Provide a more comprehensive project description",
                    fix_action="Expand description to at least 20 words"
                ))
        
        return issues
    
    def _is_properly_capitalized(self, text: str) -> bool:
        """Check if text uses proper capitalization."""
        # Simple check: first letter should be uppercase
        return text and text[0].isupper()
    
    def _has_excessive_repetition(self, text: str) -> bool:
        """Check for excessive word repetition."""
        words = text.lower().split()
        if len(words) < 10:
            return False
        
        # Count word frequencies
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only check longer words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Check if any word appears more than 20% of the time
        total_words = len([w for w in words if len(w) > 3])
        if total_words == 0:
            return False
        
        for count in word_counts.values():
            if count / total_words > 0.2:
                return True
        
        return False


class FormatValidationRule(ValidationRule):
    """Validation rule for format compliance."""
    
    def __init__(self):
        super().__init__(
            name="format_validation",
            description="Validates format compliance and structure",
            category=ValidationCategory.FORMAT
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate format compliance."""
        issues = []
        
        # Validate title format
        if metadata.title:
            if len(metadata.title) > 100:
                issues.append(ValidationIssue(
                    field="title",
                    message="Project title is too long (maximum 100 characters)",
                    severity=ValidationSeverity.MEDIUM,
                    category=ValidationCategory.FORMAT,
                    suggestion="Shorten the project title",
                    fix_action="Reduce title length to 100 characters or less"
                ))
            
            if not metadata.title.strip():
                issues.append(ValidationIssue(
                    field="title",
                    message="Project title contains only whitespace",
                    severity=ValidationSeverity.HIGH,
                    category=ValidationCategory.FORMAT,
                    suggestion="Provide a non-empty project title",
                    fix_action="Enter a valid project title"
                ))
        
        # Validate description format
        if metadata.description:
            if len(metadata.description) > 2000:
                issues.append(ValidationIssue(
                    field="description",
                    message="Project description is too long (maximum 2000 characters)",
                    severity=ValidationSeverity.MEDIUM,
                    category=ValidationCategory.FORMAT,
                    suggestion="Shorten the project description",
                    fix_action="Reduce description length to 2000 characters or less"
                ))
            
            # Check for proper line breaks
            if '\n' in metadata.description and len(metadata.description.split('\n')) > 20:
                issues.append(ValidationIssue(
                    field="description",
                    message="Project description has too many line breaks",
                    severity=ValidationSeverity.LOW,
                    category=ValidationCategory.FORMAT,
                    suggestion="Use paragraphs instead of many line breaks",
                    fix_action="Reformat description with proper paragraph structure"
                ))
        
        # Validate technologies format
        if metadata.technologies:
            for i, tech in enumerate(metadata.technologies):
                if not tech.strip():
                    issues.append(ValidationIssue(
                        field=f"technologies[{i}]",
                        message="Empty technology entry",
                        severity=ValidationSeverity.MEDIUM,
                        category=ValidationCategory.FORMAT,
                        suggestion="Remove empty technology entries",
                        fix_action="Clean up technology list"
                    ))
                elif len(tech) > 50:
                    issues.append(ValidationIssue(
                        field=f"technologies[{i}]",
                        message="Technology name is too long (maximum 50 characters)",
                        severity=ValidationSeverity.LOW,
                        category=ValidationCategory.FORMAT,
                        suggestion="Use shorter technology names",
                        fix_action="Abbreviate or shorten technology name"
                    ))
        
        return issues


class ConsistencyRule(ValidationRule):
    """Validation rule for consistency checks."""
    
    def __init__(self):
        super().__init__(
            name="consistency",
            description="Validates consistency across project metadata",
            category=ValidationCategory.CONSISTENCY
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate consistency."""
        issues = []
        
        # Check for consistent naming
        if metadata.title and metadata.description:
            title_words = set(metadata.title.lower().split())
            desc_words = set(metadata.description.lower().split())
            
            # Check if key terms from title appear in description
            key_terms = [word for word in title_words if len(word) > 3]
            if key_terms:
                common_terms = title_words.intersection(desc_words)
                if len(common_terms) < len(key_terms) * 0.3:
                    issues.append(ValidationIssue(
                        field="description",
                        message="Description doesn't reference key terms from title",
                        severity=ValidationSeverity.LOW,
                        category=ValidationCategory.CONSISTENCY,
                        suggestion="Include key terms from title in description",
                        fix_action="Update description to reference title concepts"
                    ))
        
        # Check technology consistency
        if metadata.technologies and metadata.description:
            tech_mentioned = 0
            for tech in metadata.technologies:
                if tech.lower() in metadata.description.lower():
                    tech_mentioned += 1
            
            if tech_mentioned < len(metadata.technologies) * 0.5:
                issues.append(ValidationIssue(
                    field="technologies",
                    message="Many technologies not mentioned in description",
                    severity=ValidationSeverity.LOW,
                    category=ValidationCategory.CONSISTENCY,
                    suggestion="Reference technologies in project description",
                    fix_action="Update description to mention key technologies"
                ))
        
        return issues
