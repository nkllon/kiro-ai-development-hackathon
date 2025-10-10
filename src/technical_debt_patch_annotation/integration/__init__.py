"""
Integration module for Technical Debt Patch Annotation System.

This module provides integration capabilities with external systems including:
- CI/CD pipeline integration
- Issue tracking systems
- Development workflow tools
"""

from .cicd_integration import (
    CICDIntegration,
    ThresholdConfiguration,
    PatchImpactReport,
    CIPipelineResult,
    ValidationIssue,
    MergeBlockReason,
    CIPipelineStage,
    create_github_actions_workflow,
    create_gitlab_ci_config,
    create_jenkins_pipeline
)

__all__ = [
    "CICDIntegration",
    "ThresholdConfiguration", 
    "PatchImpactReport",
    "CIPipelineResult",
    "ValidationIssue",
    "MergeBlockReason",
    "CIPipelineStage",
    "create_github_actions_workflow",
    "create_gitlab_ci_config", 
    "create_jenkins_pipeline"
]