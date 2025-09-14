"""
Mpm Dashboard Core Core Validation

This module was extracted from mpm_dashboard_core_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from .models import BacklogItem, MPMValidation, DependencySpec
from .enums import StrategicTrack, BeastReadinessStatus, ApprovalStatus, StakeholderType, RiskLevel
from .dependency_manager import BacklogDependencyManager
from src.rm_ddd.core.health import ModuleHealth


def _invalidate_cache(self) -> None:
    """Invalidate cached portfolio status"""
    self._cached_portfolio_status = None
    self._cache_timestamp = None

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

