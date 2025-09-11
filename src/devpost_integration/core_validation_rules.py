#!/usr/bin/env python3
"""
core_validation_rules - core_validation_rules module for DevPost integration

Refactored for RM-DDD compliance.
Single responsibility: core_validation_rules functionality.
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


class ContentQualityRule(ReflectiveModule):
    """ContentQualityRule with RM-DDD compliance with RM-DDD compliance"""
    
    def __init__(selfself):
        """Initialize core_validation_rules"""
        super().__init__(module_id="core_validation_rules", version="1.0.0")
        # Initialize module components
        self._start_time = datetime.now()
        self._operation_count = 0
        self._errors = 0
        register_module(self)
    
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


    
    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Core Validation Rules',
            'description': 'core_validation_rules module for DevPost integration',
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
        logger.info("Metrics reset for core_validation_rules module")
