from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from .models import MarketConditions, CompetitiveThreat, PlatformAllocation, StrategyExecution, ResponsePlan, AllocationPlan, PlatformType, CompetitorMove
from .platform_orchestrators import GKEPlatformOrchestrator, TiDBPlatformOrchestrator, KiroPlatformOrchestrator
from .intelligence_engine import CompetitiveIntelligenceEngine
from .deadline_manager import DeadlineManagementSystem
from .command_center_core_core import *
from src.rm_ddd.core.health import ModuleHealth


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

