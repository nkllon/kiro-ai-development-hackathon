"""
Spec Consistency and Technical Debt Reconciliation System

This module implements a comprehensive PCOR (Preventive Corrective Action Request) 
approach to eliminate existing spec fragmentation while implementing systematic 
prevention mechanisms.
"""

from .governance import GovernanceController, GovernanceFramework
from .validation import ConsistencyValidator
from .consolidation import SpecConsolidator
from .monitoring import ContinuousMonitor
from .boundary_resolver import ComponentBoundaryResolver

# Import all data models
from .models import (
    # Base Classes
    ReflectiveModule,
    
    # Enums
    ValidationResult, OverlapSeverity, ConsolidationStatus, ConflictResolutionStrategy,
    DriftSeverity, CorrectionStatus, ConsistencyLevel, PreventionType,
    
    # Core Analysis Models
    SpecAnalysis, ConsolidationPlan, PreventionControl,
    
    # Overlap and Conflict Models
    OverlapAnalysis, ConsolidationOpportunity, ConflictReport, TerminologyIssue,
    InterfaceIssue, PreventionRecommendation,
    
    # Change and Migration Models
    InterfaceChange, TerminologyChange, MigrationStep, ValidationCriterion,
    
    # Traceability Models
    TraceabilityLink, TraceabilityMap,
    
    # Monitoring and Drift Models
    DriftDetection, DriftReport,
    
    # Control and Workflow Models
    TriggerCondition, ValidationRule, EnforcementAction, EscalationStep,
    MonitoringMetric,
    
    # Consistency and Validation Models
    TerminologyReport, ComplianceReport, PatternReport, ConsistencyMetrics,
    
    # Governance Models
    SpecProposal, OverlapReport, ApprovalStatus,
    
    # Workflow Models
    CorrectionWorkflow, ArchitecturalDecision,
    
    # Additional Models
    RequirementAnalysis, InconsistencyReport,
    
    # Utility functions
    get_model_class, create_model_instance, validate_all_models, MODEL_REGISTRY
)

__all__ = [
    # Core Components
    'GovernanceController',
    'GovernanceFramework',
    'ConsistencyValidator',
    'SpecConsolidator',
    'ContinuousMonitor',
    'ComponentBoundaryResolver',
    
    # Base Classes
    'ReflectiveModule',
    
    # Enums
    'ValidationResult', 'OverlapSeverity', 'ConsolidationStatus', 'ConflictResolutionStrategy',
    'DriftSeverity', 'CorrectionStatus', 'ConsistencyLevel', 'PreventionType',
    
    # Core Analysis Models
    'SpecAnalysis', 'ConsolidationPlan', 'PreventionControl',
    
    # Overlap and Conflict Models
    'OverlapAnalysis', 'ConsolidationOpportunity', 'ConflictReport', 'TerminologyIssue',
    'InterfaceIssue', 'PreventionRecommendation',
    
    # Change and Migration Models
    'InterfaceChange', 'TerminologyChange', 'MigrationStep', 'ValidationCriterion',
    
    # Traceability Models
    'TraceabilityLink', 'TraceabilityMap',
    
    # Monitoring and Drift Models
    'DriftDetection', 'DriftReport',
    
    # Control and Workflow Models
    'TriggerCondition', 'ValidationRule', 'EnforcementAction', 'EscalationStep',
    'MonitoringMetric',
    
    # Consistency and Validation Models
    'TerminologyReport', 'ComplianceReport', 'PatternReport', 'ConsistencyMetrics',
    
    # Governance Models
    'SpecProposal', 'OverlapReport', 'ApprovalStatus',
    
    # Workflow Models
    'CorrectionWorkflow', 'ArchitecturalDecision',
    
    # Additional Models
    'RequirementAnalysis', 'InconsistencyReport',
    
    # Utility functions
    'get_model_class', 'create_model_instance', 'validate_all_models', 'MODEL_REGISTRY'
]