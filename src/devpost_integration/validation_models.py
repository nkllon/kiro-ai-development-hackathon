#!/usr/bin/env python3
"""
Validation Models - Data models for validation system

Extracted from validation_engine.py for RM-DDD compliance.
Single responsibility: Data models and enums for validation system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from .models import ProjectMetadata, ProjectLink, ProjectTeamMember


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationCategory(str, Enum):
    """Validation category types."""
    REQUIRED_FIELDS = "required_fields"
    CONTENT_QUALITY = "content_quality"
    LINKS = "links"
    TEAM = "team"
    TAGS = "tags"
    FORMAT = "format"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"


@dataclass
class ValidationIssue:
    """Represents a validation issue with actionable suggestions."""
    
    field: str
    message: str
    severity: ValidationSeverity
    category: ValidationCategory
    suggestion: Optional[str] = None
    fix_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.field}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'field': self.field,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'suggestion': self.suggestion,
            'fix_action': self.fix_action,
            'metadata': self.metadata
        }


@dataclass
class ValidationContext:
    """Context information for validation operations."""
    
    project_path: Optional[Path] = None
    validation_timestamp: datetime = field(default_factory=datetime.now)
    validation_rules: Set[str] = field(default_factory=set)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_rule(self, rule_name: str) -> None:
        """Add validation rule to context."""
        self.validation_rules.add(rule_name)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add custom metadata to context."""
        self.custom_metadata[key] = value


@dataclass
class ValidationReport:
    """Comprehensive validation report with actionable insights."""
    
    project_id: str
    validation_timestamp: datetime
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    categories: Dict[ValidationCategory, int] = field(default_factory=dict)
    overall_score: float = 0.0
    is_valid: bool = True
    recommendations: List[str] = field(default_factory=list)
    context: Optional[ValidationContext] = None
    
    def add_issue(self, issue: ValidationIssue) -> None:
        """Add validation issue to report."""
        self.issues.append(issue)
        self.total_issues += 1
        
        # Update severity counts
        if issue.severity == ValidationSeverity.CRITICAL:
            self.critical_issues += 1
        elif issue.severity == ValidationSeverity.HIGH:
            self.high_issues += 1
        elif issue.severity == ValidationSeverity.MEDIUM:
            self.medium_issues += 1
        elif issue.severity == ValidationSeverity.LOW:
            self.low_issues += 1
        elif issue.severity == ValidationSeverity.INFO:
            self.info_issues += 1
        
        # Update category counts
        self.categories[issue.category] = self.categories.get(issue.category, 0) + 1
        
        # Update validity
        if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
            self.is_valid = False
    
    def calculate_score(self) -> float:
        """Calculate overall validation score."""
        if not self.issues:
            return 100.0
        
        # Weight issues by severity
        total_weight = 0
        weighted_score = 0
        
        for issue in self.issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                weight = 10
            elif issue.severity == ValidationSeverity.HIGH:
                weight = 5
            elif issue.severity == ValidationSeverity.MEDIUM:
                weight = 3
            elif issue.severity == ValidationSeverity.LOW:
                weight = 1
            else:  # INFO
                weight = 0.5
            
            total_weight += weight
            weighted_score += weight * 0  # Each issue reduces score
        
        if total_weight == 0:
            return 100.0
        
        # Calculate score as percentage
        self.overall_score = max(0.0, 100.0 - (weighted_score / total_weight * 100))
        return self.overall_score
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_critical_issues(self) -> List[ValidationIssue]:
        """Get all critical issues."""
        return self.get_issues_by_severity(ValidationSeverity.CRITICAL)
    
    def get_high_priority_issues(self) -> List[ValidationIssue]:
        """Get high priority issues (critical and high severity)."""
        return [issue for issue in self.issues 
                if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on issues."""
        recommendations = []
        
        # Critical issues recommendations
        critical_issues = self.get_critical_issues()
        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical issues immediately")
        
        # Category-specific recommendations
        for category, count in self.categories.items():
            if count > 0:
                if category == ValidationCategory.REQUIRED_FIELDS:
                    recommendations.append("Complete all required project fields")
                elif category == ValidationCategory.CONTENT_QUALITY:
                    recommendations.append("Improve content quality and descriptions")
                elif category == ValidationCategory.LINKS:
                    recommendations.append("Verify and fix project links")
                elif category == ValidationCategory.TEAM:
                    recommendations.append("Review team composition and member information")
                elif category == ValidationCategory.TAGS:
                    recommendations.append("Add relevant project tags")
        
        # Overall recommendations
        if self.overall_score < 50:
            recommendations.append("Project requires significant improvements before submission")
        elif self.overall_score < 80:
            recommendations.append("Project needs minor improvements for optimal presentation")
        else:
            recommendations.append("Project is well-prepared for submission")
        
        self.recommendations = recommendations
        return recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            'project_id': self.project_id,
            'validation_timestamp': self.validation_timestamp.isoformat(),
            'total_issues': self.total_issues,
            'critical_issues': self.critical_issues,
            'high_issues': self.high_issues,
            'medium_issues': self.medium_issues,
            'low_issues': self.low_issues,
            'info_issues': self.info_issues,
            'issues': [issue.to_dict() for issue in self.issues],
            'categories': {cat.value: count for cat, count in self.categories.items()},
            'overall_score': self.overall_score,
            'is_valid': self.is_valid,
            'recommendations': self.recommendations,
            'context': {
                'project_path': str(self.context.project_path) if self.context else None,
                'validation_rules': list(self.context.validation_rules) if self.context else [],
                'custom_metadata': self.context.custom_metadata if self.context else {}
            } if self.context else None
        }
    
    def __str__(self) -> str:
        """String representation of validation report."""
        lines = [
            f"Validation Report for Project: {self.project_id}",
            f"Timestamp: {self.validation_timestamp}",
            f"Overall Score: {self.overall_score:.1f}/100",
            f"Valid: {'Yes' if self.is_valid else 'No'}",
            f"Total Issues: {self.total_issues}",
            f"  Critical: {self.critical_issues}",
            f"  High: {self.high_issues}",
            f"  Medium: {self.medium_issues}",
            f"  Low: {self.low_issues}",
            f"  Info: {self.info_issues}",
            ""
        ]
        
        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                lines.append(f"  {issue}")
        
        if self.recommendations:
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(f"  - {rec}")
        
        return "\n".join(lines)
