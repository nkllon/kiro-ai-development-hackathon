"""
Competitive Launch Strategy Implementation

This module implements the systematic competitive launch strategy to beat Meta
and other tech giants to market through coordinated deployment across GKE, TiDB,
and Kiro platforms.

Based on von Moltke's principle: "No plan survives contact with the enemy,
but planning is everything" - creating adaptive systems that can pivot
systematically under competitive pressure.
"""

from .command_center import CompetitiveCommandCenter
from .platform_orchestrators import (
    GKEPlatformOrchestrator,
    TiDBPlatformOrchestrator,
    KiroPlatformOrchestrator
)
from .intelligence_engine import CompetitiveIntelligenceEngine
from .deadline_manager import DeadlineManagementSystem
from .models import (
    MarketConditions,
    CompetitiveThreat,
    PlatformAllocation,
    MultiPlatformDeployment,
    CompetitiveAdvantage
)

__all__ = [
    "CompetitiveCommandCenter",
    "GKEPlatformOrchestrator",
    "TiDBPlatformOrchestrator", 
    "KiroPlatformOrchestrator",
    "CompetitiveIntelligenceEngine",
    "DeadlineManagementSystem",
    "MarketConditions",
    "CompetitiveThreat",
    "PlatformAllocation",
    "MultiPlatformDeployment",
    "CompetitiveAdvantage"
]

__version__ = "1.0.0"
__author__ = "Beast Mode Development Team"
