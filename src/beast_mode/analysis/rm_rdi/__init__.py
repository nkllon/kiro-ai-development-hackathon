"""
RM-RDI Analysis System - Operator-Safe Analysis Framework

SAFETY GUARANTEES:
- READ-ONLY operations only
- Isolated process space
- Resource limited with kill switches
- Cannot impact existing RM/RDI systems
- Easily removable with zero impact

Emergency Commands:
- make analysis-kill        # INSTANT STOP
- make analysis-throttle    # REDUCE RESOURCES  
- make analysis-stop        # GRACEFUL SHUTDOWN
- make analysis-uninstall   # COMPLETE REMOVAL
"""

from .data_models import (
    AnalysisResult,
    ArchitectureAnalysis,
    QualityReport,
    ComplianceReport,
    TechnicalDebtReport,
    PerformanceReport,
    MetricsReport,
    Recommendation,
    Priority,
    RecommendationCategory,
    EffortEstimate,
    ImpactAssessment
)

from .safety import (
    OperatorSafetyManager,
    ResourceMonitor,
    KillSwitch,
    SafetyValidator
)

__all__ = [
    # Data Models
    'AnalysisResult',
    'ArchitectureAnalysis', 
    'QualityReport',
    'ComplianceReport',
    'TechnicalDebtReport',
    'PerformanceReport',
    'MetricsReport',
    'Recommendation',
    'Priority',
    'RecommendationCategory',
    'EffortEstimate',
    'ImpactAssessment',
    
    # Safety Systems
    'OperatorSafetyManager',
    'ResourceMonitor',
    'KillSwitch',
    'SafetyValidator'
]

# Version and safety information
__version__ = "1.0.0"
__safety_level__ = "OPERATOR_SAFE"
__guarantees__ = [
    "READ_ONLY_OPERATIONS",
    "ISOLATED_PROCESSES", 
    "RESOURCE_LIMITED",
    "KILL_SWITCH_ENABLED",
    "ZERO_DOWNTIME_RISK"
]