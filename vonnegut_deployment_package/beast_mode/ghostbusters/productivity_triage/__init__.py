"""
Ghostbusters Productivity Triage System
=======================================

This is it! The moment we should have trained for!

A systematic approach to coordinating "supernatural productivity explosions" 
where Beast Mode has generated so much valuable work that coordination becomes 
the bottleneck.

Components:
- ProductivityTriageOrchestrator: Main coordination system
- ContentDiscoveryEngine: Discovers and catalogs work artifacts
- WorkClassificationSystem: Categorizes work by domain and readiness
- ConflictDetectionEngine: Identifies potential integration conflicts
- IntegrationPlanningSystem: Creates systematic integration plans
- QualityGateValidator: Ensures no regressions during integration
- EmergencyProtocolManager: Handles critical failures with data preservation

Author: Beast Mode Framework + Ghostbusters
Date: 2025-09-24
Purpose: Coordinate the coordinators themselves!
"""

from .models import (
    WorkArtifact,
    TriageConfig,
    ExplosionAssessment,
    IntegrationPlan,
    TriageReport,
    ArtifactType,
    DomainType,
    CompletionStatus,
    ReadinessStatus,
    ComplexityLevel,
    TriageStrategy,
)

from .orchestrator import ProductivityTriageOrchestrator
from .interfaces import (
    IContentDiscoveryEngine,
    IWorkClassificationSystem, 
    IConflictDetectionEngine,
    IIntegrationPlanningSystem,
    IQualityGateValidator,
    IEmergencyProtocolManager,
    IProductivityTriageOrchestrator,
    ProductivityTriageError,
    CriticalTriageError,
)

__all__ = [
    # Data Models
    "WorkArtifact",
    "TriageConfig", 
    "ExplosionAssessment",
    "IntegrationPlan",
    "TriageReport",
    "ArtifactType",
    "DomainType", 
    "CompletionStatus",
    "ReadinessStatus",
    "ComplexityLevel",
    "TriageStrategy",
    
    # Main Orchestrator
    "ProductivityTriageOrchestrator",
    
    # Interfaces
    "IContentDiscoveryEngine",
    "IWorkClassificationSystem", 
    "IConflictDetectionEngine",
    "IIntegrationPlanningSystem",
    "IQualityGateValidator",
    "IEmergencyProtocolManager",
    "IProductivityTriageOrchestrator",
    
    # Exceptions
    "ProductivityTriageError",
    "CriticalTriageError",
]

__version__ = "1.0.0"