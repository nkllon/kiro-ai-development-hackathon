"""
🎯 SCA CONSOLIDATED MODULES
==========================
Consolidated modules for Enhanced SCA Procedure V2.
Split from monolithic file for better maintainability.

Modules:
- core_engine: Main SCA engine
- adaptive_intelligence: Adaptive subset sizing and thresholds
- metrics_calculator: Enhanced efficiency metrics
- phase_manager: Phase prioritization and management
- optimizer: Optimization recommendations

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from .core_engine import EnhancedSCAProcedureV2
from .adaptive_intelligence import AdaptiveIntelligenceModule
from .metrics_calculator import MetricsCalculatorModule
from .phase_manager import PhaseManagerModule
from .optimizer import OptimizationModule

__all__ = [
    "EnhancedSCAProcedureV2",
    "AdaptiveIntelligenceModule",
    "MetricsCalculatorModule",
    "PhaseManagerModule",
    "OptimizationModule",
]


