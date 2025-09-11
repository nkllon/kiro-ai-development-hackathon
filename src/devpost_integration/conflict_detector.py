#!/usr/bin/env python3
"""
Conflict Detector - Conflict detection logic

Extracted from conflict_resolution.py for RM-DDD compliance.
Single responsibility: Conflict detection logic.
"""

import logging
from typing import Dict, Any, List
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Conflict Detector',
            'description': 'conflict_detector module for DevPost integration',
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


class ConflictDetector(ReflectiveModule):
    """Conflict detection logic for multi-project management."""
    
    def __init__(self):
        super().__init__(module_id="conflict_detector", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize conflict detector."""
        pass
    
    def detect_conflicts(self, project_ids: List[str], project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts between projects."""
        conflicts = []
        
        try:
            # Check for resource conflicts
            resource_conflicts = self._detect_resource_conflicts(project_ids, project_data)
            conflicts.extend(resource_conflicts)
            
            # Check for naming conflicts
            naming_conflicts = self._detect_naming_conflicts(project_ids, project_data)
            conflicts.extend(naming_conflicts)
            
            # Check for dependency conflicts
            dependency_conflicts = self._detect_dependency_conflicts(project_ids, project_data)
            conflicts.extend(dependency_conflicts)
            
            # Check for configuration conflicts
            config_conflicts = self._detect_configuration_conflicts(project_ids, project_data)
            conflicts.extend(config_conflicts)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {e}")
            return []
    
    def _detect_resource_conflicts(self, project_ids: List[str], project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect resource conflicts between projects."""
        conflicts = []
        
        # Check for shared resource usage
        shared_resources = set()
        for project_id in project_ids:
            project_resources = project_data.get(project_id, {}).get('resources', [])
            for resource in project_resources:
                if resource in shared_resources:
                    conflicts.append({
                        'type': 'resource_conflict',
                        'resource': resource,
                        'projects': [p for p in project_ids if resource in project_data.get(p, {}).get('resources', [])],
                        'severity': 'high'
                    })
                shared_resources.add(resource)
        
        return conflicts
    
    def _detect_naming_conflicts(self, project_ids: List[str], project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect naming conflicts between projects."""
        conflicts = []
        
        # Check for duplicate project names
        project_names = {}
        for project_id in project_ids:
            project_name = project_data.get(project_id, {}).get('name', '')
            if project_name in project_names:
                conflicts.append({
                    'type': 'naming_conflict',
                    'name': project_name,
                    'projects': [project_names[project_name], project_id],
                    'severity': 'medium'
                })
            project_names[project_name] = project_id
        
        return conflicts
    
    def _detect_dependency_conflicts(self, project_ids: List[str], project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect dependency conflicts between projects."""
        conflicts = []
        
        # Check for circular dependencies
        for project_id in project_ids:
            dependencies = project_data.get(project_id, {}).get('dependencies', [])
            if project_id in dependencies:
                conflicts.append({
                    'type': 'circular_dependency',
                    'project': project_id,
                    'severity': 'high'
                })
        
        return conflicts
    
    def _detect_configuration_conflicts(self, project_ids: List[str], project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect configuration conflicts between projects."""
        conflicts = []
        
        # Check for conflicting configuration values
        config_keys = set()
        for project_id in project_ids:
            project_config = project_data.get(project_id, {}).get('config', {})
            for key, value in project_config.items():
                if key in config_keys:
                    conflicts.append({
                        'type': 'config_conflict',
                        'key': key,
                        'projects': [p for p in project_ids if key in project_data.get(p, {}).get('config', {})],
                        'severity': 'low'
                    })
                config_keys.add(key)
        
        return conflicts
    
    def get_conflict_summary(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of detected conflicts."""
        if not conflicts:
            return {
                'total_conflicts': 0,
                'by_type': {},
                'by_severity': {},
                'projects_affected': set()
            }
        
        by_type = {}
        by_severity = {}
        projects_affected = set()
        
        for conflict in conflicts:
            # Count by type
            conflict_type = conflict.get('type', 'unknown')
            by_type[conflict_type] = by_type.get(conflict_type, 0) + 1
            
            # Count by severity
            severity = conflict.get('severity', 'unknown')
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Track affected projects
            if 'projects' in conflict:
                projects_affected.update(conflict['projects'])
            elif 'project' in conflict:
                projects_affected.add(conflict['project'])
        
        return {
            'total_conflicts': len(conflicts),
            'by_type': by_type,
            'by_severity': by_severity,
            'projects_affected': list(projects_affected)
        }
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> List[str]:
        """Validate project data for potential conflicts."""
        validation_errors = []
        
        # Check for required fields
        required_fields = ['name', 'status']
        for field in required_fields:
            if field not in project_data:
                validation_errors.append(f"Missing required field: {field}")
        
        # Check for valid status values
        valid_statuses = ['active', 'inactive', 'completed', 'cancelled']
        if 'status' in project_data and project_data['status'] not in valid_statuses:
            validation_errors.append(f"Invalid status value: {project_data['status']}")
        
        # Check for valid resource format
        if 'resources' in project_data:
            if not isinstance(project_data['resources'], list):
                validation_errors.append("Resources must be a list")
            else:
                for resource in project_data['resources']:
                    if not isinstance(resource, str):
                        validation_errors.append("All resources must be strings")
        
        return validation_errors
