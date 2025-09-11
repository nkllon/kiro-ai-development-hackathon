"""
Ghostbusters Framework - The Glue Between Humans and AI

Core philosophy: "We're the Glue Between Humans and AI"
- AI Agents Amplify Human Creativity
- Humans Remain the Core Team  
- Symbiotic Intelligence
- Systematic Capability Bridge

This framework provides foundational integration and coordination services
for specialized analysis and recovery across the Beast Mode ecosystem.
"""

__version__ = "1.0.0"
__author__ = "Beast Mode Development Team"

from .core.models import (
    AnalysisResult,
    Finding, 
    Recommendation,
    AnalysisContext,
    Delusion,
    RecoveryPlan,
    ValidationResult,
    ConsensusResult,
    MultiDimensionalResult
)

from .core.interfaces import (
    GhostbustersExpertAgent,
    RecoveryEngine,
    ValidationFramework,
    ConsensusEngine
)

__all__ = [
    "AnalysisResult",
    "Finding",
    "Recommendation", 
    "AnalysisContext",
    "Delusion",
    "RecoveryPlan",
    "ValidationResult",
    "ConsensusResult",
    "MultiDimensionalResult",
    "GhostbustersExpertAgent",
    "RecoveryEngine",
    "ValidationFramework",
    "ConsensusEngine"
]