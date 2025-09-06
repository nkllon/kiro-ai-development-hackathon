"""
Systematic Hubris Prevention Framework

This module implements automated detection and correction mechanisms for when actors
begin to believe they operate outside accountability chains - the classic "too big
for your britches" problem.

Core Components:
- HubrisDetector: Pattern recognition for hubris behaviors
- RealityChecker: Validation against objective criteria
- MamaDiscoverer: Accountability chain discovery and mapping
- HumilityEnforcer: Systematic humility enforcement mechanisms
"""

from .interfaces import (
    HubrisDetector,
    RealityChecker, 
    MamaDiscoverer,
    HumilityEnforcer,
    BoundaryManager,
    CorruptionPreventer
)

from .models import (
    AccountabilityChain,
    HubrisScore,
    RealityCheckResult,
    GovernanceIntervention,
    Decision,
    Actor
)

__all__ = [
    'HubrisDetector',
    'RealityChecker',
    'MamaDiscoverer', 
    'HumilityEnforcer',
    'BoundaryManager',
    'CorruptionPreventer',
    'AccountabilityChain',
    'HubrisScore',
    'RealityCheckResult',
    'GovernanceIntervention',
    'Decision',
    'Actor'
]