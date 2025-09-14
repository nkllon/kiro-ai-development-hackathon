"""
Controller Handlers Validation

This module was extracted from controller_handlers.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..core.reflective_module import HealthIndicator, ModuleStatus, ReflectiveModule
from .models import DistributionPlan, DistributionStrategy, InstanceFailure, IntegrationReport, KiroInstance, RecoveryPlan, SwarmConfig, SwarmState, Task, TaskStatus
from .models import DeploymentTarget
from .models import PeacockTheme
from pathlib import Path
from .models import DeploymentTarget
from .models import PeacockTheme
from pathlib import Path

def _validate_swarm_config(self) -> None:
    """Validate swarm configuration for systematic compliance."""
    if self.config.instance_count < 1:
        raise ValueError('Instance count must be at least 1')
    if self.config.max_instances < self.config.min_instances:
        raise ValueError('Max instances must be >= min instances')
    if not self.config.deployment_targets and self.config.instance_count > 1:
        from .models import DeploymentTarget
        self.config.deployment_targets = [DeploymentTarget(name='local', type='local')]
