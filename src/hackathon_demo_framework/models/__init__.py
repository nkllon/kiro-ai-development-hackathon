#!/usr/bin/env python3
"""
Hackathon Demo Framework Models - RDI/RM-DDD Compliant

This module exports all models for the hackathon demo framework,
following Beast Mode principles with systematic validation.
"""

from .spec_to_code_model import (
    SpecToCodeModel,
    TransformationStatus,
    QualityLevel,
    RequirementLink,
    LearningPattern,
    TransformationResult
)

from .systematic_superiority_model import (
    SystematicSuperiorityModel,
    ApproachType,
    ComparisonMetric,
    Approach,
    ComparisonResult,
    EvidencePackage
)

from .multi_agent_collaboration_model import (
    MultiAgentCollaborationModel,
    AgentType,
    TaskStatus,
    ConflictType,
    Agent,
    Task,
    CollaborationResult,
    Conflict,
    HumanInput
)

from .production_infrastructure_model import (
    ProductionInfrastructureModel,
    DeploymentStatus,
    SecurityLevel,
    CostOptimizationLevel,
    GKEConfig,
    DeploymentResult,
    CostOptimizationResult,
    SecurityValidationResult
)

# Export all models and related classes
__all__ = [
    # SpecToCodeModel
    'SpecToCodeModel',
    'TransformationStatus',
    'QualityLevel', 
    'RequirementLink',
    'LearningPattern',
    'TransformationResult',
    
    # SystematicSuperiorityModel
    'SystematicSuperiorityModel',
    'ApproachType',
    'ComparisonMetric',
    'Approach',
    'ComparisonResult',
    'EvidencePackage',
    
    # MultiAgentCollaborationModel
    'MultiAgentCollaborationModel',
    'AgentType',
    'TaskStatus',
    'ConflictType',
    'Agent',
    'Task',
    'CollaborationResult',
    'Conflict',
    'HumanInput',
    
    # ProductionInfrastructureModel
    'ProductionInfrastructureModel',
    'DeploymentStatus',
    'SecurityLevel',
    'CostOptimizationLevel',
    'GKEConfig',
    'DeploymentResult',
    'CostOptimizationResult',
    'SecurityValidationResult'
]
