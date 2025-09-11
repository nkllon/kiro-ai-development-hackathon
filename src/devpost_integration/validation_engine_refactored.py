#!/usr/bin/env python3
"""
Validation Engine - Refactored validation orchestration

Composed from decomposed modules for RM-DDD compliance.
Single responsibility: Validation orchestration and engine coordination.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .models import ProjectMetadata
from .validation_models import (
    ValidationReport, ValidationContext, ValidationSeverity, ValidationCategory
)
from .validation_rules import (
    RequiredFieldRule, ContentQualityRule, FormatValidationRule, ConsistencyRule
)
from .validation_rules_extended import (
    LinkValidationRule, TeamValidationRule, TagValidationRule
)

logger = logging.getLogger(__name__)


class ValidationEngine:
    """
    Refactored validation engine for Devpost project validation.
    
    Orchestrates specialized validation rules to provide comprehensive
    project validation with actionable feedback.
    """
    
    def __init__(self, project_id: str):
        """
        Initialize validation engine.
        
        Args:
            project_id: Unique identifier for the project
        """
        self.project_id = project_id
        self.validation_rules = self._initialize_validation_rules()
        
        # Statistics
        self.stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'last_validation': None
        }
    
    def _initialize_validation_rules(self) -> List[Any]:
        """Initialize all validation rules."""
        return [
            RequiredFieldRule(),
            ContentQualityRule(),
            FormatValidationRule(),
            ConsistencyRule(),
            LinkValidationRule(),
            TeamValidationRule(),
            TagValidationRule()
        ]
    
    def validate_project(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> ValidationReport:
        """
        Validate project metadata comprehensively.
        
        Args:
            metadata: Project metadata to validate
            context: Optional validation context
            
        Returns:
            Comprehensive validation report
        """
        logger.info(f"Starting validation for project: {self.project_id}")
        
        # Create validation report
        report = ValidationReport(
            project_id=self.project_id,
            validation_timestamp=context.validation_timestamp if context else None,
            context=context
        )
        
        # Run all validation rules
        for rule in self.validation_rules:
            try:
                rule_issues = rule.validate(metadata, context)
                for issue in rule_issues:
                    report.add_issue(issue)
                
                logger.debug(f"Rule '{rule.name}' found {len(rule_issues)} issues")
                
            except Exception as e:
                logger.error(f"Error in validation rule '{rule.name}': {e}")
                # Add error issue
                report.add_issue(ValidationIssue(
                    field="validation_engine",
                    message=f"Validation rule '{rule.name}' failed: {str(e)}",
                    severity=ValidationSeverity.HIGH,
                    category=ValidationCategory.FORMAT,
                    suggestion="Check validation engine configuration",
                    fix_action="Review validation rule implementation"
                ))
        
        # Calculate final score and generate recommendations
        report.calculate_score()
        report.generate_recommendations()
        
        # Update statistics
        self._update_statistics(report)
        
        logger.info(f"Validation complete: {report.overall_score:.1f}/100, {report.total_issues} issues")
        return report
    
    def validate_field(self, field_name: str, value: Any, metadata: ProjectMetadata, 
                      context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """
        Validate specific field.
        
        Args:
            field_name: Name of field to validate
            value: Field value to validate
            metadata: Complete project metadata
            context: Optional validation context
            
        Returns:
            List of validation issues for the field
        """
        issues = []
        
        # Find relevant rules for the field
        relevant_rules = [rule for rule in self.validation_rules 
                         if hasattr(rule, 'validate_field')]
        
        for rule in relevant_rules:
            try:
                rule_issues = rule.validate_field(field_name, value, metadata, context)
                issues.extend(rule_issues)
            except Exception as e:
                logger.error(f"Error validating field '{field_name}' with rule '{rule.name}': {e}")
        
        return issues
    
    def get_validation_summary(self, report: ValidationReport) -> Dict[str, Any]:
        """
        Get validation summary.
        
        Args:
            report: Validation report to summarize
            
        Returns:
            Dictionary with validation summary
        """
        return {
            'project_id': report.project_id,
            'overall_score': report.overall_score,
            'is_valid': report.is_valid,
            'total_issues': report.total_issues,
            'critical_issues': report.critical_issues,
            'high_issues': report.high_issues,
            'medium_issues': report.medium_issues,
            'low_issues': report.low_issues,
            'info_issues': report.info_issues,
            'categories': {cat.value: count for cat, count in report.categories.items()},
            'recommendations': report.recommendations
        }
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation engine statistics."""
        return {
            **self.stats,
            'total_rules': len(self.validation_rules),
            'rule_names': [rule.name for rule in self.validation_rules]
        }
    
    def add_custom_rule(self, rule: Any) -> None:
        """
        Add custom validation rule.
        
        Args:
            rule: Custom validation rule instance
        """
        if hasattr(rule, 'validate') and hasattr(rule, 'name'):
            self.validation_rules.append(rule)
            logger.info(f"Added custom validation rule: {rule.name}")
        else:
            logger.error("Custom rule must have 'validate' method and 'name' attribute")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove validation rule by name.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        for i, rule in enumerate(self.validation_rules):
            if rule.name == rule_name:
                del self.validation_rules[i]
                logger.info(f"Removed validation rule: {rule_name}")
                return True
        
        logger.warning(f"Validation rule not found: {rule_name}")
        return False
    
    def _update_statistics(self, report: ValidationReport) -> None:
        """Update validation statistics."""
        self.stats['total_validations'] += 1
        
        if report.is_valid:
            self.stats['successful_validations'] += 1
        else:
            self.stats['failed_validations'] += 1
        
        self.stats['last_validation'] = report.validation_timestamp


def create_default_validation_engine(project_id: str) -> ValidationEngine:
    """Create a validation engine with default configuration."""
    return ValidationEngine(project_id)


def validate_project_metadata(
    metadata: ProjectMetadata,
    project_id: str,
    context: Optional[ValidationContext] = None
) -> ValidationReport:
    """
    Convenience function for validating project metadata.
    
    Args:
        metadata: Project metadata to validate
        project_id: Unique project identifier
        context: Optional validation context
        
    Returns:
        Validation report
    """
    engine = create_default_validation_engine(project_id)
    return engine.validate_project(metadata, context)


def quick_validate(metadata: ProjectMetadata, project_id: str) -> Dict[str, Any]:
    """
    Quick validation with summary only.
    
    Args:
        metadata: Project metadata to validate
        project_id: Unique project identifier
        
    Returns:
        Validation summary dictionary
    """
    engine = create_default_validation_engine(project_id)
    report = engine.validate_project(metadata)
    return engine.get_validation_summary(report)
