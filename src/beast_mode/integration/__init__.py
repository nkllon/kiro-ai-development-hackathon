"""
Beast Mode Framework - Integration Module
Implements UC-25: Self-Consistency Validation through infrastructure integration
"""

from .infrastructure_integration_manager import (
    InfrastructureIntegrationManager,
    IntegrationStatus,
    ValidationResult
)

from .self_consistency_validator import (
    SelfConsistencyValidator,
    ConsistencyCheck,
    ConsistencyResult
)

__all__ = [
    'InfrastructureIntegrationManager',
    'IntegrationStatus',
    'ValidationResult',
    'SelfConsistencyValidator',
    'ConsistencyCheck',
    'ConsistencyResult'
]