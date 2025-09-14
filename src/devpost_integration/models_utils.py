"""
Models Utils

This module was extracted from models.py
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

def add_file_format(self, file_format: str) -> bool:
    """Add allowed file format"""
    try:
        self._update_metrics('add_file_format')
        if 'file_formats' not in self.requirement_data:
            self.requirement_data['file_formats'] = []
        if file_format not in self.requirement_data['file_formats']:
            self.requirement_data['file_formats'].append(file_format)
            self.updated_at = datetime.now()
            self._metrics['requirement_updates'] += 1
            self._logger.info(f'File format {file_format} added to requirement {self.requirement_id}')
            return True
        else:
            self._logger.info(f'File format {file_format} already exists')
            return True
    except Exception as e:
        self._logger.error(f'Failed to add file format: {e}')
        self._metrics['error_count'] += 1
        return False

def remove_file_format(self, file_format: str) -> bool:
    """Remove allowed file format"""
    try:
        self._update_metrics('remove_file_format')
        if 'file_formats' in self.requirement_data and file_format in self.requirement_data['file_formats']:
            self.requirement_data['file_formats'].remove(file_format)
            self.updated_at = datetime.now()
            self._metrics['requirement_updates'] += 1
            self._logger.info(f'File format {file_format} removed from requirement {self.requirement_id}')
            return True
        else:
            self._logger.warning(f'File format {file_format} not found')
            return False
    except Exception as e:
        self._logger.error(f'Failed to remove file format: {e}')
        self._metrics['error_count'] += 1
        return False

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

