#!/usr/bin/env python3
"""
Devpost Validation Engine - Centralized Validation System

Provides consistent validation across all Devpost integration components with:
- Centralized ValidationEngine for consistent validation
- Devpost requirement validation rules
- Configurable validation rules for different hackathons
- Validation error reporting with actionable suggestions

Requirements: 3.2, 3.5, 5.3, 5.5
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable, Union
from urllib.parse import urlparse
import json

from .models import (
    ProjectMetadata, DevpostProject, ValidationResult, ValidationRules,
    MediaType, SubmissionRequirement, TeamMember, ProjectLink, MediaFile
)
from .api_client import DevpostAPIClient


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationCategory(str, Enum):
    """Validation category types."""
    REQUIRED_FIELDS = "required_fields"
    CONTENT_QUALITY = "content_quality"
    MEDIA_REQUIREMENTS = "media_requirements"
    TEAM_VALIDATION = "team_validation"
    LINK_VALIDATION = "link_validation"
    HACKATHON_SPECIFIC = "hackathon_specific"
    FORMATTING = "formatting"
    COMPLETENESS = "completeness"


@dataclass
class ValidationIssue:
    """Represents a validation issue with actionable suggestions."""
    field_name: str
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    current_value: Any = None
    expected_value: Any = None
    suggestion: Optional[str] = None
    fix_action: Optional[str] = None
    help_url: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class ValidationContext:
    """Context information for validation operations."""
    hackathon_id: Optional[str] = None
    hackathon_name: Optional[str] = None
    submission_deadline: Optional[datetime] = None
    custom_rules: Dict[str, Any] = field(default_factory=dict)
    project_type: Optional[str] = None
    target_audience: Optional[str] = None


@dataclass
class ValidationReport:
    """Comprehensive validation report with actionable insights."""
    is_valid: bool
    overall_score: float  # 0-100 percentage
    issues: List[ValidationIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    validation_timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[ValidationContext] = None
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by severity level."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationIssue]:
        """Get issues filtered by category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical validation issues."""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    def has_errors(self) -> bool:
        """Check if there are any error-level issues."""
        return any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)


class ValidationRule:
    """Base class for validation rules."""
    
    def __init__(
        self, 
        rule_id: str, 
        name: str, 
        category: ValidationCategory,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        enabled: bool = True
    ):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.enabled = enabled
    
    def validate(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> List[ValidationIssue]:
        """
        Validate metadata against this rule.
        
        Args:
            metadata: Project metadata to validate
            context: Validation context
            
        Returns:
            List of validation issues found
        """
        raise NotImplementedError("Subclasses must implement validate method")


class RequiredFieldRule(ValidationRule):
    """Validation rule for required fields."""
    
    def __init__(
        self, 
        field_name: str, 
        min_length: int = 1,
        severity: ValidationSeverity = ValidationSeverity.ERROR
    ):
        super().__init__(
            rule_id=f"required_field_{field_name}",
            name=f"Required Field: {field_name}",
            category=ValidationCategory.REQUIRED_FIELDS,
            severity=severity
        )
        self.field_name = field_name
        self.min_length = min_length
    
    def validate(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> List[ValidationIssue]:
        """Validate that required field exists and meets minimum length."""
        issues = []
        
        value = getattr(metadata, self.field_name, None)
        
        if value is None:
            issues.append(ValidationIssue(
                field_name=self.field_name,
                category=self.category,
                severity=self.severity,
                message=f"Required field '{self.field_name}' is missing",
                current_value=None,
                expected_value=f"Non-empty {self.field_name}",
                suggestion=f"Please provide a {self.field_name} for your project",
                fix_action=f"Add {self.field_name} to your project metadata",
                rule_id=self.rule_id
            ))
        elif isinstance(value, str) and len(value.strip()) < self.min_length:
            issues.append(ValidationIssue(
                field_name=self.field_name,
                category=self.category,
                severity=self.severity,
                message=f"Field '{self.field_name}' must be at least {self.min_length} characters long",
                current_value=len(value.strip()) if value else 0,
                expected_value=f"At least {self.min_length} characters",
                suggestion=f"Expand your {self.field_name} to provide more detail",
                fix_action=f"Add more content to the {self.field_name} field",
                rule_id=self.rule_id
            ))
        
        return issues


class ContentQualityRule(ValidationRule):
    """Validation rule for content quality."""
    
    def __init__(
        self, 
        field_name: str, 
        min_length: int, 
        max_length: Optional[int] = None,
        min_words: Optional[int] = None,
        forbidden_patterns: Optional[List[str]] = None
    ):
        super().__init__(
            rule_id=f"content_quality_{field_name}",
            name=f"Content Quality: {field_name}",
            category=ValidationCategory.CONTENT_QUALITY,
            severity=ValidationSeverity.WARNING
        )
        self.field_name = field_name
        self.min_length = min_length
        self.max_length = max_length
        self.min_words = min_words
        self.forbidden_patterns = forbidden_patterns or []
    
    def validate(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> List[ValidationIssue]:
        """Validate content quality metrics."""
        issues = []
        
        value = getattr(metadata, self.field_name, None)
        if not isinstance(value, str):
            return issues
        
        content = value.strip()
        
        # Check minimum length
        if len(content) < self.min_length:
            issues.append(ValidationIssue(
                field_name=self.field_name,
                category=self.category,
                severity=ValidationSeverity.WARNING,
                message=f"{self.field_name.title()} should be at least {self.min_length} characters for better impact",
                current_value=len(content),
                expected_value=f"At least {self.min_length} characters",
                suggestion=f"Consider expanding your {self.field_name} to better showcase your project",
                fix_action=f"Add more detail to the {self.field_name}",
                rule_id=self.rule_id
            ))
        
        # Check maximum length
        if self.max_length and len(content) > self.max_length:
            issues.append(ValidationIssue(
                field_name=self.field_name,
                category=self.category,
                severity=ValidationSeverity.WARNING,
                message=f"{self.field_name.title()} is too long ({len(content)} chars, max {self.max_length})",
                current_value=len(content),
                expected_value=f"At most {self.max_length} characters",
                suggestion=f"Consider condensing your {self.field_name} for better readability",
                fix_action=f"Shorten the {self.field_name} to fit within limits",
                rule_id=self.rule_id
            ))
        
        # Check minimum words
        if self.min_words:
            word_count = len(content.split())
            if word_count < self.min_words:
                issues.append(ValidationIssue(
                    field_name=self.field_name,
                    category=self.category,
                    severity=ValidationSeverity.WARNING,
                    message=f"{self.field_name.title()} should have at least {self.min_words} words",
                    current_value=word_count,
                    expected_value=f"At least {self.min_words} words",
                    suggestion=f"Add more detail to reach the recommended word count",
                    fix_action=f"Expand the {self.field_name} with more information",
                    rule_id=self.rule_id
                ))
        
        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    field_name=self.field_name,
                    category=self.category,
                    severity=ValidationSeverity.WARNING,
                    message=f"{self.field_name.title()} contains discouraged content pattern",
                    current_value=pattern,
                    suggestion="Consider revising the content to be more professional",
                    fix_action=f"Remove or rephrase content matching pattern: {pattern}",
                    rule_id=self.rule_id
                ))
        
        return issues


class LinkValidationRule(ValidationRule):
    """Validation rule for project links."""
    
    def __init__(self):
        super().__init__(
            rule_id="link_validation",
            name="Link Validation",
            category=ValidationCategory.LINK_VALIDATION,
            severity=ValidationSeverity.WARNING
        )
    
    def validate(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> List[ValidationIssue]:
        """Validate project links."""
        issues = []
        
        # Check repository URL
        if metadata.repository_url:
            if not self._is_valid_url(metadata.repository_url):
                issues.append(ValidationIssue(
                    field_name="repository_url",
                    category=self.category,
                    severity=ValidationSeverity.ERROR,
                    message="Repository URL is not valid",
                    current_value=metadata.repository_url,
                    suggestion="Provide a valid repository URL (GitHub, GitLab, etc.)",
                    fix_action="Update repository_url with a valid URL",
                    rule_id=self.rule_id
                ))
            elif not self._is_repository_url(metadata.repository_url):
                issues.append(ValidationIssue(
                    field_name="repository_url",
                    category=self.category,
                    severity=ValidationSeverity.WARNING,
                    message="URL doesn't appear to be a code repository",
                    current_value=metadata.repository_url,
                    suggestion="Ensure this links to your project's source code",
                    fix_action="Verify the repository URL points to your code",
                    rule_id=self.rule_id
                ))
        
        # Check demo URL
        if metadata.demo_url:
            if not self._is_valid_url(metadata.demo_url):
                issues.append(ValidationIssue(
                    field_name="demo_url",
                    category=self.category,
                    severity=ValidationSeverity.ERROR,
                    message="Demo URL is not valid",
                    current_value=metadata.demo_url,
                    suggestion="Provide a valid demo URL",
                    fix_action="Update demo_url with a valid URL",
                    rule_id=self.rule_id
                ))
        
        # Check video URL
        if metadata.video_url:
            if not self._is_valid_url(metadata.video_url):
                issues.append(ValidationIssue(
                    field_name="video_url",
                    category=self.category,
                    severity=ValidationSeverity.ERROR,
                    message="Video URL is not valid",
                    current_value=metadata.video_url,
                    suggestion="Provide a valid video URL (YouTube, Vimeo, etc.)",
                    fix_action="Update video_url with a valid URL",
                    rule_id=self.rule_id
                ))
            elif not self._is_video_url(metadata.video_url):
                issues.append(ValidationIssue(
                    field_name="video_url",
                    category=self.category,
                    severity=ValidationSeverity.WARNING,
                    message="URL doesn't appear to be a video platform",
                    current_value=metadata.video_url,
                    suggestion="Use popular video platforms like YouTube or Vimeo",
                    fix_action="Upload video to a recognized platform",
                    rule_id=self.rule_id
                ))
        
        return issues
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_repository_url(self, url: str) -> bool:
        """Check if URL appears to be a code repository."""
        repo_domains = ['github.com', 'gitlab.com', 'bitbucket.org', 'sourceforge.net']
        try:
            domain = urlparse(url).netloc.lower()
            return any(repo_domain in domain for repo_domain in repo_domains)
        except Exception:
            return False
    
    def _is_video_url(self, url: str) -> bool:
        """Check if URL appears to be a video platform."""
        video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'wistia.com', 'loom.com']
        try:
            domain = urlparse(url).netloc.lower()
            return any(video_domain in domain for video_domain in video_domains)
        except Exception:
            return False


class TeamValidationRule(ValidationRule):
    """Validation rule for team composition."""
    
    def __init__(self, min_members: int = 1, max_members: int = 4):
        super().__init__(
            rule_id="team_validation",
            name="Team Validation",
            category=ValidationCategory.TEAM_VALIDATION,
            severity=ValidationSeverity.WARNING
        )
        self.min_members = min_members
        self.max_members = max_members
    
    def validate(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> List[ValidationIssue]:
        """Validate team composition."""
        issues = []
        
        team_count = len(metadata.team_members) if metadata.team_members else 0
        
        if team_count < self.min_members:
            issues.append(ValidationIssue(
                field_name="team_members",
                category=self.category,
                severity=ValidationSeverity.WARNING,
                message=f"Team should have at least {self.min_members} member(s)",
                current_value=team_count,
                expected_value=f"At least {self.min_members} members",
                suggestion="Add team member information to showcase collaboration",
                fix_action="Add team members to the project",
                rule_id=self.rule_id
            ))
        
        if team_count > self.max_members:
            issues.append(ValidationIssue(
                field_name="team_members",
                category=self.category,
                severity=ValidationSeverity.WARNING,
                message=f"Team has more than recommended {self.max_members} members",
                current_value=team_count,
                expected_value=f"At most {self.max_members} members",
                suggestion="Consider if all members actively contributed to the project",
                fix_action="Review team member list for active contributors",
                rule_id=self.rule_id
            ))
        
        return issues


class TagValidationRule(ValidationRule):
    """Validation rule for project tags."""
    
    def __init__(self, min_tags: int = 2, max_tags: int = 10):
        super().__init__(
            rule_id="tag_validation",
            name="Tag Validation",
            category=ValidationCategory.CONTENT_QUALITY,
            severity=ValidationSeverity.WARNING
        )
        self.min_tags = min_tags
        self.max_tags = max_tags
    
    def validate(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> List[ValidationIssue]:
        """Validate project tags."""
        issues = []
        
        tag_count = len(metadata.tags) if metadata.tags else 0
        
        if tag_count < self.min_tags:
            issues.append(ValidationIssue(
                field_name="tags",
                category=self.category,
                severity=ValidationSeverity.WARNING,
                message=f"Project should have at least {self.min_tags} tags for better discoverability",
                current_value=tag_count,
                expected_value=f"At least {self.min_tags} tags",
                suggestion="Add relevant technology and category tags",
                fix_action="Add more descriptive tags to your project",
                rule_id=self.rule_id
            ))
        
        if tag_count > self.max_tags:
            issues.append(ValidationIssue(
                field_name="tags",
                category=self.category,
                severity=ValidationSeverity.WARNING,
                message=f"Too many tags ({tag_count}), consider focusing on the most relevant ones",
                current_value=tag_count,
                expected_value=f"At most {self.max_tags} tags",
                suggestion="Keep only the most relevant and specific tags",
                fix_action="Remove less relevant tags",
                rule_id=self.rule_id
            ))
        
        # Check for duplicate tags
        if metadata.tags:
            unique_tags = set(tag.lower() for tag in metadata.tags)
            if len(unique_tags) < len(metadata.tags):
                issues.append(ValidationIssue(
                    field_name="tags",
                    category=self.category,
                    severity=ValidationSeverity.WARNING,
                    message="Duplicate tags found (case-insensitive)",
                    suggestion="Remove duplicate tags to avoid redundancy",
                    fix_action="Remove duplicate tags from the list",
                    rule_id=self.rule_id
                ))
        
        return issues


class ValidationEngine:
    """
    Centralized validation engine for Devpost integration.
    
    Provides consistent validation across all components with configurable
    rules, actionable error reporting, and hackathon-specific validation.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize validation engine with configuration."""
        self.config_path = config_path or Path('.devpost/validation_config.json')
        self.logger = logging.getLogger(__name__)
        
        # Built-in validation rules
        self.built_in_rules: List[ValidationRule] = []
        self.custom_rules: List[ValidationRule] = []
        
        # Rule registry for dynamic rule management
        self.rule_registry: Dict[str, ValidationRule] = {}
        
        # Load configuration and initialize rules
        self.config = self._load_config()
        self._initialize_built_in_rules()
        self._load_custom_rules()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load validation engine configuration."""
        default_config = {
            'enabled_rules': [],  # Empty means all rules enabled
            'disabled_rules': [],
            'severity_overrides': {},
            'hackathon_specific_rules': {},
            'custom_rule_definitions': [],
            'validation_timeout': 30,  # seconds
            'cache_results': True,
            'cache_ttl': 300  # seconds
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                self.logger.warning(f"Failed to load validation config: {e}, using defaults")
        
        return default_config
    
    def _save_config(self) -> None:
        """Save current configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save validation config: {e}")
    
    def _initialize_built_in_rules(self) -> None:
        """Initialize built-in validation rules."""
        # Required field rules
        self.built_in_rules.extend([
            RequiredFieldRule("title", min_length=3, severity=ValidationSeverity.CRITICAL),
            RequiredFieldRule("tagline", min_length=10, severity=ValidationSeverity.ERROR),
            RequiredFieldRule("description", min_length=50, severity=ValidationSeverity.ERROR),
        ])
        
        # Content quality rules
        self.built_in_rules.extend([
            ContentQualityRule("title", min_length=5, max_length=100),
            ContentQualityRule("tagline", min_length=20, max_length=200, min_words=3),
            ContentQualityRule(
                "description", 
                min_length=100, 
                max_length=5000, 
                min_words=20,
                forbidden_patterns=[r'\btodo\b', r'\bfixme\b', r'\btest\b.*\btest\b']
            ),
        ])
        
        # Other validation rules
        self.built_in_rules.extend([
            LinkValidationRule(),
            TeamValidationRule(min_members=1, max_members=4),
            TagValidationRule(min_tags=2, max_tags=10),
        ])
        
        # Register all built-in rules
        for rule in self.built_in_rules:
            self.rule_registry[rule.rule_id] = rule
    
    def _load_custom_rules(self) -> None:
        """Load custom validation rules from configuration."""
        self.custom_rules = []
        
        # Load hackathon-specific rules from configuration
        hackathon_rules = self.config.get('hackathon_specific_rules', {})
        
        for hackathon_id, rules_config in hackathon_rules.items():
            # Add hackathon-specific required fields
            for field_name in rules_config.get('required_fields', []):
                if field_name not in ['title', 'tagline', 'description']:  # Don't duplicate built-in rules
                    rule = RequiredFieldRule(
                        field_name, 
                        min_length=rules_config.get('min_lengths', {}).get(field_name, 1),
                        severity=ValidationSeverity.ERROR
                    )
                    rule.rule_id = f"hackathon_{hackathon_id}_{rule.rule_id}"
                    self.custom_rules.append(rule)
            
            # Add hackathon-specific content quality rules
            content_rules = rules_config.get('content_quality', {})
            for field_name, requirements in content_rules.items():
                if field_name not in ['title', 'tagline', 'description']:  # Don't duplicate built-in rules
                    rule = ContentQualityRule(
                        field_name,
                        min_length=requirements.get('min_length', 10),
                        max_length=requirements.get('max_length'),
                        min_words=requirements.get('min_words'),
                        forbidden_patterns=requirements.get('forbidden_patterns', [])
                    )
                    rule.rule_id = f"hackathon_{hackathon_id}_{rule.rule_id}"
                    self.custom_rules.append(rule)
        
        # Register custom rules
        for rule in self.custom_rules:
            self.rule_registry[rule.rule_id] = rule
    
    def add_custom_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule."""
        self.custom_rules.append(rule)
        self.rule_registry[rule.rule_id] = rule
        self.logger.info(f"Added custom validation rule: {rule.rule_id}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a validation rule by ID."""
        if rule_id in self.rule_registry:
            rule = self.rule_registry[rule_id]
            
            # Remove from appropriate list
            if rule in self.built_in_rules:
                self.built_in_rules.remove(rule)
            if rule in self.custom_rules:
                self.custom_rules.remove(rule)
            
            # Remove from registry
            del self.rule_registry[rule_id]
            
            self.logger.info(f"Removed validation rule: {rule_id}")
            return True
        
        return False
    
    def configure_hackathon_rules(
        self, 
        hackathon_id: str, 
        hackathon_name: str,
        rules_config: Dict[str, Any]
    ) -> None:
        """
        Configure hackathon-specific validation rules.
        
        Args:
            hackathon_id: Unique hackathon identifier
            hackathon_name: Human-readable hackathon name
            rules_config: Hackathon-specific validation configuration
        """
        # Update configuration
        if 'hackathon_specific_rules' not in self.config:
            self.config['hackathon_specific_rules'] = {}
        
        self.config['hackathon_specific_rules'][hackathon_id] = {
            'name': hackathon_name,
            **rules_config
        }
        
        # Reload custom rules to include new hackathon rules
        self._load_custom_rules()
        
        # Save updated configuration
        self._save_config()
        
        self.logger.info(f"Configured validation rules for hackathon: {hackathon_name} ({hackathon_id})")
    
    def get_hackathon_validation_summary(self, hackathon_id: str) -> Dict[str, Any]:
        """
        Get validation rule summary for a specific hackathon.
        
        Args:
            hackathon_id: Hackathon identifier
            
        Returns:
            Dictionary with validation rule summary
        """
        hackathon_rules = self.config.get('hackathon_specific_rules', {}).get(hackathon_id, {})
        
        # Get rules that apply to this hackathon
        context = ValidationContext(hackathon_id=hackathon_id)
        active_rules = self.get_active_rules(context)
        
        hackathon_specific_rules = [
            rule for rule in active_rules 
            if rule.rule_id.startswith(f"hackathon_{hackathon_id}_")
        ]
        
        return {
            'hackathon_id': hackathon_id,
            'hackathon_name': hackathon_rules.get('name', 'Unknown'),
            'total_rules': len(active_rules),
            'hackathon_specific_rules': len(hackathon_specific_rules),
            'built_in_rules': len(active_rules) - len(hackathon_specific_rules),
            'required_fields': hackathon_rules.get('required_fields', []),
            'content_quality_rules': list(hackathon_rules.get('content_quality', {}).keys()),
            'custom_requirements': hackathon_rules.get('custom_requirements', [])
        }
    
    def get_active_rules(self, context: Optional[ValidationContext] = None) -> List[ValidationRule]:
        """Get list of active validation rules based on configuration and context."""
        all_rules = self.built_in_rules + self.custom_rules
        
        # Filter by enabled/disabled rules
        enabled_rules = self.config.get('enabled_rules', [])
        disabled_rules = self.config.get('disabled_rules', [])
        
        active_rules = []
        for rule in all_rules:
            # Skip disabled rules
            if rule.rule_id in disabled_rules:
                continue
            
            # If enabled_rules is specified, only include those
            if enabled_rules and rule.rule_id not in enabled_rules:
                continue
            
            # Skip disabled rules
            if not rule.enabled:
                continue
            
            active_rules.append(rule)
        
        # Apply hackathon-specific rules if context provided
        if context and context.hackathon_id:
            hackathon_rules = self.config.get('hackathon_specific_rules', {}).get(context.hackathon_id, {})
            
            # Add hackathon-specific rules
            for rule_config in hackathon_rules.get('additional_rules', []):
                # This would create rules from configuration
                # For now, we'll just log that hackathon-specific rules are available
                self.logger.debug(f"Hackathon-specific rules available for {context.hackathon_id}")
        
        return active_rules
    
    def validate_metadata(
        self, 
        metadata: ProjectMetadata, 
        context: Optional[ValidationContext] = None
    ) -> ValidationReport:
        """
        Validate project metadata against all active rules.
        
        Args:
            metadata: Project metadata to validate
            context: Validation context for hackathon-specific rules
            
        Returns:
            Comprehensive validation report
        """
        start_time = datetime.now()
        
        # Get active rules for this validation
        active_rules = self.get_active_rules(context)
        
        # Collect all validation issues
        all_issues = []
        passed_checks = []
        
        for rule in active_rules:
            try:
                issues = rule.validate(metadata, context)
                
                if issues:
                    # Apply severity overrides from config
                    severity_overrides = self.config.get('severity_overrides', {})
                    for issue in issues:
                        if issue.rule_id in severity_overrides:
                            issue.severity = ValidationSeverity(severity_overrides[issue.rule_id])
                    
                    all_issues.extend(issues)
                else:
                    passed_checks.append(rule.name)
                    
            except Exception as e:
                self.logger.error(f"Error running validation rule {rule.rule_id}: {e}")
                # Add error as critical issue
                all_issues.append(ValidationIssue(
                    field_name="validation_engine",
                    category=ValidationCategory.COMPLETENESS,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation rule {rule.rule_id} failed to execute",
                    suggestion="Contact support if this persists",
                    fix_action="Check validation engine configuration",
                    rule_id="validation_engine_error"
                ))
        
        # Calculate overall validation metrics
        total_checks = len(active_rules)
        passed_count = len(passed_checks)
        
        # Calculate completion percentage
        completion_percentage = (passed_count / total_checks * 100) if total_checks > 0 else 0
        
        # Calculate overall score (weighted by severity)
        overall_score = self._calculate_overall_score(all_issues, total_checks)
        
        # Determine if validation passed
        critical_issues = [i for i in all_issues if i.severity == ValidationSeverity.CRITICAL]
        error_issues = [i for i in all_issues if i.severity == ValidationSeverity.ERROR]
        is_valid = len(critical_issues) == 0 and len(error_issues) == 0
        
        # Get missing fields
        missing_fields = [
            issue.field_name for issue in all_issues 
            if issue.category == ValidationCategory.REQUIRED_FIELDS and "missing" in issue.message.lower()
        ]
        
        validation_time = datetime.now() - start_time
        self.logger.info(f"Validation completed in {validation_time.total_seconds():.2f}s: {len(all_issues)} issues found")
        
        return ValidationReport(
            is_valid=is_valid,
            overall_score=overall_score,
            issues=all_issues,
            passed_checks=passed_checks,
            missing_fields=missing_fields,
            completion_percentage=completion_percentage,
            validation_timestamp=datetime.now(),
            context=context
        )
    
    def _calculate_overall_score(self, issues: List[ValidationIssue], total_checks: int) -> float:
        """Calculate overall validation score based on issues and their severity."""
        if total_checks == 0:
            return 100.0
        
        # Weight penalties by severity
        severity_weights = {
            ValidationSeverity.CRITICAL: 25,  # -25 points per critical issue
            ValidationSeverity.ERROR: 15,    # -15 points per error
            ValidationSeverity.WARNING: 5,   # -5 points per warning
            ValidationSeverity.INFO: 1       # -1 point per info
        }
        
        total_penalty = 0
        for issue in issues:
            total_penalty += severity_weights.get(issue.severity, 0)
        
        # Start with 100 and subtract penalties
        score = max(0, 100 - total_penalty)
        
        return score
    
    def validate_project(
        self, 
        project: DevpostProject, 
        context: Optional[ValidationContext] = None
    ) -> ValidationReport:
        """
        Validate a complete Devpost project.
        
        Args:
            project: Devpost project to validate
            context: Validation context
            
        Returns:
            Validation report for the project
        """
        # Convert DevpostProject to ProjectMetadata for validation
        metadata = ProjectMetadata(
            title=project.title,
            tagline=project.tagline,
            description=project.description,
            tags=project.tags,
            team_members=[member.name for member in project.team_members],
            repository_url=next((link.url for link in project.links if link.link_type == "github"), None),
            demo_url=next((link.url for link in project.links if link.link_type == "demo"), None),
            video_url=next((link.url for link in project.links if link.link_type == "video"), None)
        )
        
        # Create context if not provided
        if not context:
            context = ValidationContext(
                hackathon_id=project.hackathon_id,
                hackathon_name=project.hackathon_name,
                submission_deadline=project.deadline
            )
        
        return self.validate_metadata(metadata, context)
    
    def validate_submission_readiness(
        self, 
        metadata: ProjectMetadata, 
        hackathon_id: str,
        submission_requirements: List[SubmissionRequirement] = None
    ) -> ValidationReport:
        """
        Validate if project is ready for submission to a specific hackathon.
        
        Args:
            metadata: Project metadata to validate
            hackathon_id: Target hackathon ID
            submission_requirements: Optional list of specific submission requirements
            
        Returns:
            Comprehensive validation report for submission readiness
        """
        # Create context with submission requirements
        context = ValidationContext(
            hackathon_id=hackathon_id,
            custom_rules={'submission_requirements': submission_requirements or []}
        )
        
        # Run standard validation
        report = self.validate_metadata(metadata, context)
        
        # Add submission-specific validation
        submission_issues = []
        
        if submission_requirements:
            for requirement in submission_requirements:
                if requirement.required and not requirement.completed:
                    submission_issues.append(ValidationIssue(
                        field_name=requirement.requirement_id,
                        category=ValidationCategory.HACKATHON_SPECIFIC,
                        severity=ValidationSeverity.CRITICAL,
                        message=f"Required submission item not completed: {requirement.title}",
                        current_value=requirement.completed,
                        expected_value=True,
                        suggestion=requirement.description,
                        fix_action=f"Complete the requirement: {requirement.title}",
                        rule_id=f"submission_requirement_{requirement.requirement_id}"
                    ))
        
        # Add submission issues to report
        report.issues.extend(submission_issues)
        
        # Recalculate validation status
        critical_issues = [i for i in report.issues if i.severity == ValidationSeverity.CRITICAL]
        error_issues = [i for i in report.issues if i.severity == ValidationSeverity.ERROR]
        report.is_valid = len(critical_issues) == 0 and len(error_issues) == 0
        
        # Recalculate overall score
        total_checks = len(self.get_active_rules(context)) + len(submission_requirements or [])
        report.overall_score = self._calculate_overall_score(report.issues, total_checks)
        
        return report
    
    def get_missing_requirements(self, report: ValidationReport) -> List[str]:
        """
        Extract list of missing requirements from validation report.
        
        Args:
            report: Validation report to analyze
            
        Returns:
            List of missing requirement descriptions
        """
        missing = []
        
        for issue in report.issues:
            if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
                if issue.category == ValidationCategory.REQUIRED_FIELDS:
                    missing.append(f"Required field: {issue.field_name}")
                elif issue.category == ValidationCategory.HACKATHON_SPECIFIC:
                    missing.append(f"Hackathon requirement: {issue.message}")
                elif issue.fix_action:
                    missing.append(issue.fix_action)
                else:
                    missing.append(issue.message)
        
        return missing
    
    def get_validation_suggestions(self, report: ValidationReport) -> List[str]:
        """
        Get prioritized list of actionable suggestions from validation report.
        
        Args:
            report: Validation report to analyze
            
        Returns:
            List of prioritized suggestions
        """
        suggestions = []
        
        # Add overall status summary
        if report.has_critical_issues():
            suggestions.append("🚨 CRITICAL ISSUES FOUND: Your submission cannot be processed until these are resolved.")
        elif report.has_errors():
            suggestions.append("❌ ERRORS FOUND: Please fix these issues before submitting.")
        elif report.issues:
            suggestions.append("⚠️  IMPROVEMENTS SUGGESTED: Consider addressing these to enhance your submission.")
        else:
            suggestions.append("✅ VALIDATION PASSED: Your project meets all requirements!")
        
        suggestions.append("")  # Add spacing
        
        # Group suggestions by category for better organization
        category_suggestions = {}
        
        for issue in report.issues:
            if issue.suggestion:
                category = issue.category.value.replace('_', ' ').title()
                if category not in category_suggestions:
                    category_suggestions[category] = []
                
                priority_prefix = {
                    ValidationSeverity.CRITICAL: "🚨 CRITICAL",
                    ValidationSeverity.ERROR: "❌ ERROR",
                    ValidationSeverity.WARNING: "⚠️  WARNING",
                    ValidationSeverity.INFO: "ℹ️  INFO"
                }.get(issue.severity, "")
                
                suggestion_text = f"{priority_prefix}: {issue.suggestion}"
                if issue.fix_action:
                    suggestion_text += f" → {issue.fix_action}"
                
                category_suggestions[category].append(suggestion_text)
        
        # Add categorized suggestions
        for category, category_items in category_suggestions.items():
            suggestions.append(f"📋 {category}:")
            for item in category_items:
                suggestions.append(f"  • {item}")
            suggestions.append("")  # Add spacing between categories
        
        # Add completion guidance
        if report.completion_percentage < 100:
            missing_count = len(report.missing_fields)
            if missing_count > 0:
                suggestions.append(f"📝 COMPLETION STATUS: {report.completion_percentage:.1f}% complete")
                suggestions.append(f"   Missing fields: {', '.join(report.missing_fields)}")
            
            # Provide next steps
            critical_count = len(report.get_issues_by_severity(ValidationSeverity.CRITICAL))
            error_count = len(report.get_issues_by_severity(ValidationSeverity.ERROR))
            
            if critical_count > 0:
                suggestions.append(f"🎯 NEXT STEP: Fix {critical_count} critical issue(s) first")
            elif error_count > 0:
                suggestions.append(f"🎯 NEXT STEP: Address {error_count} error(s) to improve submission quality")
            else:
                suggestions.append("🎯 NEXT STEP: Consider addressing warnings to polish your submission")
        
        return [s for s in suggestions if s]  # Remove empty strings
    
    def export_validation_report(self, report: ValidationReport, format: str = "json") -> str:
        """
        Export validation report in specified format.
        
        Args:
            report: Validation report to export
            format: Export format ("json", "markdown", "html")
            
        Returns:
            Formatted report string
        """
        if format == "json":
            return self._export_json_report(report)
        elif format == "markdown":
            return self._export_markdown_report(report)
        elif format == "html":
            return self._export_html_report(report)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json_report(self, report: ValidationReport) -> str:
        """Export report as JSON."""
        report_dict = {
            "is_valid": report.is_valid,
            "overall_score": report.overall_score,
            "completion_percentage": report.completion_percentage,
            "validation_timestamp": report.validation_timestamp.isoformat(),
            "issues": [
                {
                    "field_name": issue.field_name,
                    "category": issue.category.value,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "fix_action": issue.fix_action,
                    "rule_id": issue.rule_id
                }
                for issue in report.issues
            ],
            "passed_checks": report.passed_checks,
            "missing_fields": report.missing_fields
        }
        
        return json.dumps(report_dict, indent=2)
    
    def _export_markdown_report(self, report: ValidationReport) -> str:
        """Export report as Markdown."""
        lines = [
            "# Validation Report",
            "",
            f"**Overall Score:** {report.overall_score:.1f}/100",
            f"**Completion:** {report.completion_percentage:.1f}%",
            f"**Status:** {'✅ Valid' if report.is_valid else '❌ Invalid'}",
            f"**Timestamp:** {report.validation_timestamp.isoformat()}",
            ""
        ]
        
        if report.issues:
            lines.extend([
                "## Issues Found",
                ""
            ])
            
            for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, ValidationSeverity.WARNING]:
                severity_issues = report.get_issues_by_severity(severity)
                if severity_issues:
                    severity_icon = {
                        ValidationSeverity.CRITICAL: "🚨",
                        ValidationSeverity.ERROR: "❌",
                        ValidationSeverity.WARNING: "⚠️"
                    }.get(severity, "ℹ️")
                    
                    lines.append(f"### {severity_icon} {severity.value.title()} Issues")
                    lines.append("")
                    
                    for issue in severity_issues:
                        lines.append(f"- **{issue.field_name}**: {issue.message}")
                        if issue.suggestion:
                            lines.append(f"  - *Suggestion: {issue.suggestion}*")
                        lines.append("")
        
        if report.passed_checks:
            lines.extend([
                "## Passed Checks",
                ""
            ])
            for check in report.passed_checks:
                lines.append(f"- ✅ {check}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _export_html_report(self, report: ValidationReport) -> str:
        """Export report as HTML."""
        # This would generate a full HTML report
        # For now, return a simple HTML structure
        html = f"""
        <html>
        <head><title>Validation Report</title></head>
        <body>
        <h1>Validation Report</h1>
        <p><strong>Overall Score:</strong> {report.overall_score:.1f}/100</p>
        <p><strong>Status:</strong> {'Valid' if report.is_valid else 'Invalid'}</p>
        <p><strong>Issues:</strong> {len(report.issues)}</p>
        </body>
        </html>
        """
        return html.strip()


# Utility functions for validation
def create_default_validation_engine() -> ValidationEngine:
    """Create a validation engine with default configuration."""
    return ValidationEngine()


def validate_project_metadata(
    metadata: ProjectMetadata, 
    hackathon_id: Optional[str] = None
) -> ValidationReport:
    """
    Quick validation function for project metadata.
    
    Args:
        metadata: Project metadata to validate
        hackathon_id: Optional hackathon ID for specific rules
        
    Returns:
        Validation report
    """
    engine = create_default_validation_engine()
    context = ValidationContext(hackathon_id=hackathon_id) if hackathon_id else None
    return engine.validate_metadata(metadata, context)


# Export all validation components
__all__ = [
    "ValidationEngine", "ValidationRule", "ValidationReport", "ValidationIssue",
    "ValidationContext", "ValidationSeverity", "ValidationCategory",
    "RequiredFieldRule", "ContentQualityRule", "LinkValidationRule",
    "TeamValidationRule", "TagValidationRule",
    "create_default_validation_engine", "validate_project_metadata"
]