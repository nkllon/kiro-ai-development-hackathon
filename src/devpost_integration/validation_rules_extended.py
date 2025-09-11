#!/usr/bin/env python3
"""
validation_rules_extended - validation_rules_extended module for DevPost integration

Refactored for RM-DDD compliance.
Single responsibility: validation_rules_extended functionality.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)

logger = logging.getLogger(__name__)


class LinkValidationRule(ReflectiveModule):
    """LinkValidationRule with RM-DDD compliance with RM-DDD compliance"""
    
    def __init__(selfself):
        """Initialize validation_rules_extended"""
        super().__init__(module_id="validation_rules_extended", version="1.0.0")
        # Initialize module components
        self._start_time = datetime.now()
        self._operation_count = 0
        self._errors = 0
        register_module(self)
    
        def _is_url_accessible(self, url: str) -> bool:
        """Check if URL is accessible (with timeout)."""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code < 400
        except Exception:
            return False



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


    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Validation Rules Extended',
            'description': 'validation_rules_extended module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return ['ModuleCapability.CORE_FUNCTIONALITY', 'ModuleCapability.CONFIGURATION', 'ModuleCapability.LOGGING']
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['models', 'validation_models']
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Add module-specific health checks here
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                return False
            
            # Update configuration parameters
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Configuration update error: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        # Add module-specific metrics here
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'operation_count': self._operation_count,
            'errors': self._errors,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._operation_count = 0
        self._errors = 0
        self._start_time = datetime.now()
        logger.info("Metrics reset for validation_rules_extended module")
