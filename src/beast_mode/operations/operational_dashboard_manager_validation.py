"""
Operational Dashboard Manager Validation

This module was extracted from operational_dashboard_manager.py
as part of RM-DDD compliance refactoring.
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..integration.infrastructure_integration_manager import InfrastructureIntegrationManager
from ..integration.self_consistency_validator import SelfConsistencyValidator
from ..orchestration.tool_orchestration_engine import ToolOrchestrationEngine
from src.rm_ddd.core.health import ModuleHealth


def _validate_dashboard_config(self, config: DashboardConfig) -> bool:
    """Validate dashboard configuration"""
    if not config.dashboard_id or not config.title:
        return False
    if config.refresh_interval_seconds <= 0:
        return False
    if config.data_retention_hours <= 0:
        return False
    return True

def _check_data_retention_compliance(self) -> bool:
    """Check if data retention policies are being followed"""
    for dashboard_id, config in self.dashboards.items():
        if dashboard_id in self.data_history:
            cutoff_time = datetime.now() - timedelta(hours=config.data_retention_hours)
            old_entries = [entry for entry in self.data_history[dashboard_id] if entry.timestamp <= cutoff_time]
            if old_entries:
                return False
    return True

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

