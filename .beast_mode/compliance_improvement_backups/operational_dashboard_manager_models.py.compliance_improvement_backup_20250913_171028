"""
Operational Dashboard Manager Models

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

@dataclass
class DashboardData:
    """Data for dashboard display"""
    dashboard_id: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
