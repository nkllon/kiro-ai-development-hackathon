"""
Spec Consistency and Technical Debt Reconciliation System

This module implements a comprehensive PCOR (Preventive Corrective Action Request) 
approach to eliminate existing spec fragmentation while implementing systematic 
prevention mechanisms.
"""

from .governance import GovernanceController
from .validation import ConsistencyValidator
from .consolidation import SpecConsolidator
from .monitoring import ContinuousMonitor
from .boundary_resolver import ComponentBoundaryResolver

__all__ = [
    'GovernanceController',
    'ConsistencyValidator',
    'SpecConsolidator',
    'ContinuousMonitor',
    'ComponentBoundaryResolver'
]