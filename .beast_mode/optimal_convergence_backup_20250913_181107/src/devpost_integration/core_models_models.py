"""
Core Models Models

This module was extracted from core_models.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional
from enum import Enum

class ProjectMetadata(ReflectiveModule):
    """
    Manages project metadata and configuration.
    
    This class handles project-specific information including
    titles, descriptions, tags, and other metadata fields.
    """

    def __init__(self, metadata: Dict[str, Any]=None):
        """Initialize project metadata."""
        super().__init__()
        self.module_id = 'project_metadata'
        self.version = '1.0.0'
        self.metadata = metadata or {}
        self._operation_count = 0
        self._errors = 0
        register_module(self)

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {'module_id': self.module_id, 'version': self.version, 'metadata_count': len(self.metadata), 'operation_count': self._operation_count}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [ModuleCapability.METADATA_MANAGEMENT, ModuleCapability.VALIDATION, ModuleCapability.EXPORT_IMPORT]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ['reflective_module', 'typing']

    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        if self._errors > 0:
            issues.append(f'{self._errors} errors occurred')
        if not self.metadata:
            issues.append('No metadata available')
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        return ModuleHealth(module_id=self.module_id, status=status, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self.get_metrics(), last_check=datetime.now())

    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        return max(0.0, score)

    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        if self._errors > 0:
            issues.append(f'Metadata errors: {self._errors}')
        return issues

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {'max_metadata_size': 1000, 'required_fields': ['title', 'description'], 'optional_fields': ['tags', 'category', 'difficulty']}

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            return True
        except Exception as e:
            logger.error(f'Failed to update configuration: {e}')
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {'operation_count': self._operation_count, 'error_count': self._errors, 'metadata_count': len(self.metadata), 'uptime_seconds': 0}

    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0

    def set_metadata(self, key: str, value: Any) -> bool:
        """Set metadata value."""
        try:
            self.metadata[key] = value
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to set metadata: {e}')
            self._errors += 1
            return False

    def get_metadata(self, key: str=None) -> Any:
        """Get metadata value or all metadata."""
        try:
            if key is None:
                return self.metadata
            return self.metadata.get(key)
        except Exception as e:
            logger.error(f'Failed to get metadata: {e}')
            self._errors += 1
            return None

    def update_metadata(self, updates: Dict[str, Any]) -> bool:
        """Update multiple metadata fields."""
        try:
            self.metadata.update(updates)
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to update metadata: {e}')
            self._errors += 1
            return False

    def validate_metadata(self) -> bool:
        """Validate metadata fields."""
        try:
            required_fields = self.get_configuration().get('required_fields', [])
            for field in required_fields:
                if field not in self.metadata or not self.metadata[field]:
                    return False
            return True
        except Exception as e:
            logger.error(f'Metadata validation failed: {e}')
            self._errors += 1
            return False

    def clear_metadata(self) -> bool:
        """Clear all metadata."""
        try:
            self.metadata.clear()
            self._operation_count += 1
            return True
        except Exception as e:
            logger.error(f'Failed to clear metadata: {e}')
            self._errors += 1
            return False

    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f'Project metadata: {operation}')
