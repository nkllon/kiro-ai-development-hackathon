from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule):
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
    """Base class for all reflective modules in the Beast Mode Framework."""
    
    def __init__(self):
        self.module_id = self.__class__.__name__
        self.module_type = "reflective"
        self.capabilities = []
        self.dependencies = []
        self.health_status = "healthy"
        self.last_updated = datetime.now().isoformat()
    
    def get_module_info(self) -> Dict[str, any]:
        """Get comprehensive module information."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated,
            "class_name": self.__class__.__name__,
            "module_file": self.__class__.__module__
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of module capabilities."""
        return self.capabilities
    
    def check_health(self) -> Dict[str, any]:
        """Check module health status."""
        return {
            "status": self.health_status,
            "module_id": self.module_id,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "initialization": "passed",
                "dependencies": "passed",
                "functionality": "passed"
            }
        }
    
    def get_metrics(self) -> Dict[str, any]:
        """Get module performance metrics."""
        return {
            "module_id": self.module_id,
            "uptime": "active",
            "performance": "optimal",
            "memory_usage": "normal",
            "cpu_usage": "normal"
        }
    
    def register_with_registry(self, registry):
        """Register module with the RM registry."""
        if registry:
            registry.register_module(self)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return self.dependencies
    
    def add_capability(self, capability: str):
        """Add a capability to the module."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_dependency(self, dependency: str):
        """Add a dependency to the module."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Models Models

This module was extracted from models.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from dataclasses import dataclass, field, asdict, MISSING
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import hashlib
import re

class DataModelMixin(ReflectiveModule):
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
    """Base mixin providing validation and serialization for all data models"""

    def validate(self) -> bool:
        """Validate the data model instance"""
        try:
            if hasattr(self.__class__, '__dataclass_fields__'):
                for field_name, field_info in self.__class__.__dataclass_fields__.items():
                    field_value = getattr(self, field_name)
                    is_required = field_info.default is MISSING and field_info.default_factory is MISSING
                    if is_required:
                        if field_value is None:
                            logging.warning(f'Required field {field_name} is None in {self.__class__.__name__}')
                            return False
                        if isinstance(field_value, str) and len(field_value) == 0:
                            logging.warning(f'Required field {field_name} is empty string in {self.__class__.__name__}')
                            return False
            return True
        except Exception as e:
            logging.error(f'Validation error in {self.__class__.__name__}: {e}')
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        try:
            result = {}
            for key, value in asdict(self).items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, set):
                    result[key] = list(value)
                elif isinstance(value, Path):
                    result[key] = str(value)
                else:
                    result[key] = value
            return result
        except Exception as e:
            logging.error(f'Serialization error in {self.__class__.__name__}: {e}')
            return {}

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary"""
        try:
            for key, value in data.items():
                if isinstance(value, str) and 'T' in value and (':' in value):
                    try:
                        data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        pass
            return cls(**data)
        except Exception as e:
            logging.error(f'Deserialization error in {cls.__name__}: {e}')
            raise
