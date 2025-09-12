#!/usr/bin/env python3
"""
Hackathon Demo Framework - Complete MVC Implementation

This framework provides a complete Model-View-Controller implementation
for the hackathon demo showcase, following Beast Mode principles with
RDI/RM-DDD compliance and systematic superiority demonstration.
"""

from .models import (
    # Core Models
    SpecToCodeModel,
    SystematicSuperiorityModel,
    MultiAgentCollaborationModel,
    ProductionInfrastructureModel,
    
    # Model Data Classes
    TransformationStatus,
    QualityLevel,
    RequirementLink,
    LearningPattern,
    TransformationResult,
    ApproachType,
    ComparisonMetric,
    Approach,
    ComparisonResult,
    EvidencePackage,
    AgentType,
    TaskStatus,
    ConflictType,
    Agent,
    Task,
    CollaborationResult,
    Conflict,
    HumanInput,
    DeploymentStatus,
    SecurityLevel,
    CostOptimizationLevel,
    GKEConfig,
    DeploymentResult,
    CostOptimizationResult,
    SecurityValidationResult
)

from .views import (
    # Views
    HackathonDemoView,
    DemoPhase,
    DemoContent
)

from .controllers import (
    # Controllers
    HackathonDemoController,
    DemoSession,
    TransformationResult as ControllerTransformationResult,
    CollaborationResult as ControllerCollaborationResult
)

# Framework version and metadata
__version__ = "1.0.0"
__author__ = "Beast Mode Development Team"
__description__ = "Hackathon Demo Framework - Complete MVC Implementation with RDI/RM-DDD Compliance"

# Export all public classes and functions
__all__ = [
    # Models
    'SpecToCodeModel',
    'SystematicSuperiorityModel', 
    'MultiAgentCollaborationModel',
    'ProductionInfrastructureModel',
    
    # Model Data Classes
    'TransformationStatus',
    'QualityLevel',
    'RequirementLink',
    'LearningPattern',
    'TransformationResult',
    'ApproachType',
    'ComparisonMetric',
    'Approach',
    'ComparisonResult',
    'EvidencePackage',
    'AgentType',
    'TaskStatus',
    'ConflictType',
    'Agent',
    'Task',
    'CollaborationResult',
    'Conflict',
    'HumanInput',
    'DeploymentStatus',
    'SecurityLevel',
    'CostOptimizationLevel',
    'GKEConfig',
    'DeploymentResult',
    'CostOptimizationResult',
    'SecurityValidationResult',
    
    # Views
    'HackathonDemoView',
    'DemoPhase',
    'DemoContent',
    
    # Controllers
    'HackathonDemoController',
    'DemoSession',
    'ControllerTransformationResult',
    'ControllerCollaborationResult'
]