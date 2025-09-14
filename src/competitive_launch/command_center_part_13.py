from datetime import datetime
from typing import Dict, List, Any

    def update_health_status(self, status: str):
        """Update module health status."""
        self.health_status = status
        self.last_updated = datetime.now().isoformat()

"""
Command Center Core Core Core

This module was extracted from command_center_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Command_Center - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for command_center.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/competitive_launch/command_center_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.503826
"""



from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from .models import MarketConditions, CompetitiveThreat, PlatformAllocation, StrategyExecution, ResponsePlan, AllocationPlan, PlatformType, CompetitorMove
from .platform_orchestrators import GKEPlatformOrchestrator, TiDBPlatformOrchestrator, KiroPlatformOrchestrator
from .intelligence_engine import CompetitiveIntelligenceEngine
from .deadline_manager import DeadlineManagementSystem
from src.rm_ddd.core.health import ModuleHealth

