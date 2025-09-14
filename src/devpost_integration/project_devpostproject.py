"""
Project DevpostProject Module

Extracted from project_models.py for RDI compliance.
This module contains the DevpostProject class implementation.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import ProjectStatus, ProjectPriority
from typing import Dict, List, Any, Optionalfrom ..interfaces.devpostproject_interface import DevpostProject


class DevpostProject(ReflectiveModule):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    Manages DevPost project data and operations.
    
    This class handles project information including
    metadata, team members, submissions, and status.
    """

    def __init__(self, project_data: Dict[str, Any]=None):
        """Initialize DevPost project."""
        super().__init__()
        self.module_id = 'devpost_project'
        self.version = '1.0.0'
        self.project_data = project_data or {}
        self.project_id = self.project_data.get('project_id', '')
        self.title = self.project_data.get('title', '')
        self.description = self.project_data.get('description', '')
        self.status = self.project_data.get('status', SubmissionStatus.DRAFT)
        self.team_members = self.project_data.get('team_members', [])
        self.submission_deadline = self.project_data.get('submission_deadline', None)
        self._operation_count = 0
        self._errors = 0
        register_module(self)

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'project_id': self.project_id, 'title': self.title, 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'team_member_count': len(self.team_members)}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.PROJECT_MANAGEMENT, ModuleCapability.TEAM_MANAGEMENT, ModuleCapability.SUBMISSION_TRACKING, ModuleCapability.DEADLINE_MANAGEMENT]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['reflective_module', 'datetime', 'typing', 'enum_models']

    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} internal errors occurred')
        if not self.project_id:
            issues.append('No project ID specified')
        if not self.title:
            issues.append('No project title specified')
        if not self.description:
            issues.append('No project description specified')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        if not self.project_id:
            score -= 0.3
        if not self.title:
            score -= 0.2
        if not self.description:
            score -= 0.2
        return max(0.0, score)

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Internal errors: {self._errors}')
        if not self.project_id:
            issues.append('Missing project ID')
        if not self.title:
            issues.append('Missing project title')
        if not self.description:
            issues.append('Missing project description')
        return issues

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'max_title_length': 200, 'max_description_length': 5000, 'max_team_members': 10, 'required_fields': ['project_id', 'title', 'description']}

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'project_id': self.project_id, 'team_member_count': len(self.team_members), 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'has_deadline': self.submission_deadline is not None}

    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0

    def update_project_data(self, updates: Dict[str, Any]) -> bool:
        """Update project data."""
        try:
            self.project_data.update(updates)
            if 'project_id' in updates:
                self.project_id = updates['project_id']
            if 'title' in updates:
                self.title = updates['title']
            if 'description' in updates:
                self.description = updates['description']
            if 'status' in updates:
                self.status = updates['status']
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to update project data: {e}')
            self._errors += 1
            return False

    def add_team_member(self, member_data: Dict[str, Any]) -> bool:
        """Add team member to project."""
        try:
            self.team_members.append(member_data)
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to add team member: {e}')
            self._errors += 1
            return False

    def remove_team_member(self, member_id: str) -> bool:
        """Remove team member from project."""
        try:
            self.team_members = [m for m in self.team_members if m.get('id') != member_id]
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to remove team member: {e}')
            self._errors += 1
            return False

    def get_project_summary(self) -> Dict[str, Any]:
        """Get project summary."""
        return {'project_id': self.project_id, 'title': self.title, 'description': self.description[:200] + '...' if len(self.description) > 200 else self.description, 'status': self.status.value if hasattr(self.status, 'value') else str(self.status), 'team_member_count': len(self.team_members), 'submission_deadline': self.submission_deadline.isoformat() if self.submission_deadline else None}

    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'DevPost project: {operation}')

