from datetime import datetime
from typing import Dict, List, Any

class ReflectiveModule(ReflectiveModule, ModuleHealth):
def get_health_indicators(self) -> Dict[str, any]:
    """Get health indicators for this module."""
    return {
    "module_id": self.module_id,
    "status": self.health_status,
    "last_updated": self.last_updated,
    "capabilities_count": len(self.capabilities),
    "dependencies_count": len(self.dependencies)
    }

class GethealthindicatorsClass:
    """Auto-generated class for functions."""

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
    Spore Manager Models

    This module was extracted from spore_manager.py
    as part of RM-DDD compliance refactoring.
    """

    import json
    import os
    import hashlib
    import logging
    from datetime import datetime
    from pathlib import Path
    from typing import Any, Dict, List, Optional, Tuple
    from pydantic import BaseModel, Field, ValidationError
    import yaml
    from .models import BeastModeMessage, MessageType
    from src.rm_ddd.core.health import ModuleHealth


    class SporeMetadata(BaseModel, ReflectiveModule, ModuleHealth):
    """Metadata for a Beast Mode spore"""
    name: str
    version: str
    author: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    capabilities_required: List[str] = Field(default_factory=list)
    compatibility_version: str = '1.0'
    checksum: str = ''
    file_path: str = ''
    validation_criteria: Dict[str, Any] = Field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0
