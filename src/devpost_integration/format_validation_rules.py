#!/usr/bin/env python3
"""
Format Validation Rules - Format and consistency validation

Extracted from validation_rules.py for RM-DDD compliance.
Single responsibility: Format validation and consistency checking.
"""

import re
from typing import List, Optional, Dict, Any

from .models import ProjectMetadata
from .validation_models import (
    ValidationRule, ValidationIssue, ValidationSeverity, 
    ValidationCategory, ValidationContext
)


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
