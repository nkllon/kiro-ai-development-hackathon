#!/usr/bin/env python3
"""
Team Validation Rule - Team composition validation

Extracted from validation_rules_extended.py for RM-DDD compliance.
Single responsibility: Team composition and member validation.
"""

import re
from typing import List, Optional, Dict, Any

from .models import ProjectMetadata, ProjectTeamMember
from .validation_models import (
    ValidationRule, ValidationIssue, ValidationSeverity, 
    ValidationCategory, ValidationContext
)


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
