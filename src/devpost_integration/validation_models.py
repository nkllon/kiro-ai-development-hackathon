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
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime



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
class ValidationIssue(ReflectiveModule):
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

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Validation Models',
            'description': 'validation_models module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
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
            logger.error(f"Health check failed: {e}")
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
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


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
    

    # Registry Integration Enhancements
    def _register_with_registry(self):
        """Register module with RM registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            ReflectiveModuleRegistry.register(self)
            logger.info(f"Module {self.module_id} registered with RM registry")
        except Exception as e:
            logger.error(f"Failed to register module {self.module_id}: {e}")
    
    def _unregister_from_registry(self):
        """Unregister module from RM registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            ReflectiveModuleRegistry.unregister(self.module_id)
            logger.info(f"Module {self.module_id} unregistered from RM registry")
        except Exception as e:
            logger.error(f"Failed to unregister module {self.module_id}: {e}")
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry integration status."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            is_registered = ReflectiveModuleRegistry.get_module(self.module_id) is not None
            all_modules = list(ReflectiveModuleRegistry.get_all_modules().keys())
            
            return {
                'is_registered': is_registered,
                'module_id': self.module_id,
                'total_registered_modules': len(all_modules),
                'all_module_ids': all_modules,
                'registry_available': True
            }
        except Exception as e:
            return {
                'is_registered': False,
                'module_id': self.module_id,
                'total_registered_modules': 0,
                'all_module_ids': [],
                'registry_available': False,
                'error': str(e)
            }
    
    def discover_related_modules(self) -> List[str]:
        """Discover related modules in the registry."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            all_modules = ReflectiveModuleRegistry.get_all_modules()
            related_modules = []
            
            # Find modules with similar names or dependencies
            for module_id, module in all_modules.items():
                if module_id != self.module_id:
                    # Check if modules are related by name similarity
                    if any(word in module_id.lower() for word in module_name.lower().split('_')):
                        related_modules.append(module_id)
                    # Check if modules are related by dependencies
                    elif module_id in self.get_dependencies():
                        related_modules.append(module_id)
            
            return related_modules
        except Exception as e:
            logger.error(f"Failed to discover related modules: {e}")
            return []
    
    def get_registry_health(self) -> Dict[str, Any]:
        """Get registry health information."""
        try:
            from .reflective_module import ReflectiveModuleRegistry
            all_modules = ReflectiveModuleRegistry.get_all_modules()
            
            healthy_modules = 0
            degraded_modules = 0
            unhealthy_modules = 0
            
            for module_id, module in all_modules.items():
                try:
                    health = module.check_health()
                    if health.status.value == 'healthy':
                        healthy_modules += 1
                    elif health.status.value == 'degraded':
                        degraded_modules += 1
                    else:
                        unhealthy_modules += 1
                except Exception:
                    unhealthy_modules += 1
            
            total_modules = len(all_modules)
            health_percentage = (healthy_modules / total_modules * 100) if total_modules > 0 else 0
            
            return {
                'total_modules': total_modules,
                'healthy_modules': healthy_modules,
                'degraded_modules': degraded_modules,
                'unhealthy_modules': unhealthy_modules,
                'health_percentage': health_percentage,
                'registry_status': 'healthy' if health_percentage >= 80 else 'degraded' if health_percentage >= 60 else 'unhealthy'
            }
        except Exception as e:
            return {
                'total_modules': 0,
                'healthy_modules': 0,
                'degraded_modules': 0,
                'unhealthy_modules': 0,
                'health_percentage': 0,
                'registry_status': 'error',
                'error': str(e)
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
