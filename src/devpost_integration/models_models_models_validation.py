"""
Models Models Models Validation

This module was extracted from models_models_models.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional
from enum import Enum
from typing import Dict, Any, List, Optional
from pathlib import Path
from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, ModuleConfiguration, register_module
import uuid
import uuid
import uuid
import uuid
import uuid
import os
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid

def check_health(self) -> ModuleHealth:
    """Perform health check"""
    try:
        health_score = self._calculate_health_score()
        issues = self._identify_health_issues()
        return ModuleHealth(module_id='projectmetadata', status=ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
    except Exception as e:
        self._logger.error(f'Health check failed: {e}')
        return ModuleHealth(module_id='projectmetadata', status=ModuleStatus.UNHEALTHY, health_score=0.0, issues=[f'Health check error: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())

def validate_metadata(self) -> bool:
    """Validate metadata structure and content"""
    try:
        self._update_metrics('validate_metadata')
        required_fields = ['title', 'description', 'version']
        for field in required_fields:
            if field not in self.metadata or not self.metadata[field]:
                self._logger.warning(f'Missing required metadata field: {field}')
                return False
        return True
    except Exception as e:
        self._logger.error(f'Metadata validation failed: {e}')
        self._metrics['error_count'] += 1
        return False

def check_health(self) -> ModuleHealth:
    """Perform health check"""
    try:
        health_score = self._calculate_health_score()
        issues = self._identify_health_issues()
        return ModuleHealth(module_id='previewdata', status=ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.DEGRADED, health_score=health_score, issues=issues, capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())
    except Exception as e:
        self._logger.error(f'Health check failed: {e}')
        return ModuleHealth(module_id='previewdata', status=ModuleStatus.UNHEALTHY, health_score=0.0, issues=[f'Health check error: {str(e)}'], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics=self._metrics, last_check=datetime.now())

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

