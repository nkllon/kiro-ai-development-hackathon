#!/usr/bin/env python3
"""
Validation Rules Extended - Extended validation rules for links, team, and tags

Extracted from validation_engine.py for RM-DDD compliance.
Single responsibility: Extended validation rules for complex project components.
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import requests

from .models import ProjectMetadata, ProjectLink, ProjectTeamMember
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
            link_issues = self._validate_single_link(link, i)
            issues.extend(link_issues)
        
        return issues
    
    def _validate_single_link(self, link: ProjectLink, index: int) -> List[ValidationIssue]:
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


class TeamValidationRule(ValidationRule):
    """Validation rule for team composition."""
    
    def __init__(self):
        super().__init__(
            name="team_validation",
            description="Validates team composition and member information",
            category=ValidationCategory.TEAM
        )
    
    def validate(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """Validate team composition."""
        issues = []
        
        if not metadata.team_members:
            issues.append(ValidationIssue(
                field="team_members",
                message="No team members specified",
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.TEAM,
                suggestion="Add at least one team member",
                fix_action="Specify team members for the project"
            ))
            return issues
        
        # Check team size
        team_size = len(metadata.team_members)
        if team_size == 0:
            issues.append(ValidationIssue(
                field="team_members",
                message="Team is empty",
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.TEAM,
                suggestion="Add team members",
                fix_action="Specify at least one team member"
            ))
        elif team_size > 10:
            issues.append(ValidationIssue(
                field="team_members",
                message="Team size is very large (more than 10 members)",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TEAM,
                suggestion="Consider if all members are necessary",
                fix_action="Review team composition"
            ))
        
        # Validate individual team members
        for i, member in enumerate(metadata.team_members):
            member_issues = self._validate_team_member(member, i)
            issues.extend(member_issues)
        
        # Check for duplicate members
        duplicate_issues = self._check_duplicate_members(metadata.team_members)
        issues.extend(duplicate_issues)
        
        return issues
    
    def _validate_team_member(self, member: ProjectTeamMember, index: int) -> List[ValidationIssue]:
        """Validate individual team member."""
        issues = []
        
        # Check name
        if not member.name or not member.name.strip():
            issues.append(ValidationIssue(
                field=f"team_members[{index}].name",
                message="Team member name is required",
                severity=ValidationSeverity.HIGH,
                category=ValidationCategory.TEAM,
                suggestion="Provide team member name",
                fix_action="Enter team member name"
            ))
        elif len(member.name.strip()) < 2:
            issues.append(ValidationIssue(
                field=f"team_members[{index}].name",
                message="Team member name is too short",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TEAM,
                suggestion="Provide full team member name",
                fix_action="Enter complete team member name"
            ))
        
        # Check email format
        if member.email and not self._is_valid_email(member.email):
            issues.append(ValidationIssue(
                field=f"team_members[{index}].email",
                message="Invalid email format",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TEAM,
                suggestion="Provide valid email address",
                fix_action="Enter properly formatted email"
            ))
        
        # Check role
        if not member.role or not member.role.strip():
            issues.append(ValidationIssue(
                field=f"team_members[{index}].role",
                message="Team member role is required",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TEAM,
                suggestion="Specify team member role",
                fix_action="Enter team member role"
            ))
        elif len(member.role.strip()) < 3:
            issues.append(ValidationIssue(
                field=f"team_members[{index}].role",
                message="Team member role is too brief",
                severity=ValidationSeverity.LOW,
                category=ValidationCategory.TEAM,
                suggestion="Provide more descriptive role",
                fix_action="Expand team member role description"
            ))
        
        return issues
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email has valid format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _check_duplicate_members(self, members: List[ProjectTeamMember]) -> List[ValidationIssue]:
        """Check for duplicate team members."""
        issues = []
        
        # Check for duplicate names
        names = [member.name.lower().strip() for member in members if member.name]
        duplicate_names = set([name for name in names if names.count(name) > 1])
        
        for duplicate_name in duplicate_names:
            issues.append(ValidationIssue(
                field="team_members",
                message=f"Duplicate team member name: {duplicate_name}",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TEAM,
                suggestion="Ensure team member names are unique",
                fix_action="Use unique names for each team member"
            ))
        
        # Check for duplicate emails
        emails = [member.email.lower().strip() for member in members if member.email]
        duplicate_emails = set([email for email in emails if emails.count(email) > 1])
        
        for duplicate_email in duplicate_emails:
            issues.append(ValidationIssue(
                field="team_members",
                message=f"Duplicate team member email: {duplicate_email}",
                severity=ValidationSeverity.MEDIUM,
                category=ValidationCategory.TEAM,
                suggestion="Ensure team member emails are unique",
                fix_action="Use unique emails for each team member"
            ))
        
        return issues


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
