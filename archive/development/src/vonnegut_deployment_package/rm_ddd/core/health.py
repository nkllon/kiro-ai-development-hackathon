#!/usr/bin/env python3
"""
Health Monitoring Module
=======================

Core health monitoring functionality for reflective modules.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide health monitoring capabilities
"""

from typing import Dict, Any
from datetime import datetime
from enum import Enum
from .base_reflective_module import ReflectiveModule


class ModuleStatus(Enum):
    """Status of an RM module."""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"


class ModuleHealth(ReflectiveModule):
    """Module health monitoring class."""

    def __init__(self):
        super().__init__()
        self.health_status = "healthy"
        self.last_updated = datetime.now()
        self.capabilities = []
        self.dependencies = []

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "status": self.health_status,
            "timestamp": self.last_updated.isoformat(),
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return self.get_health_status()

    def get_interface_metadata(self) -> Dict[str, Any]:
        """Get interface metadata for registry."""
        return {
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": self.dependencies,
            "capabilities": self.capabilities,
        }

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, "register"):
            registry.register(metadata)
