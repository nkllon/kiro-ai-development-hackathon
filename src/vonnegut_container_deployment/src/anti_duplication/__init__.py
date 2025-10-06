"""
Anti-Duplication System

Prevents duplicate development through mandatory capability discovery,
semantic similarity detection, and development workflow integration.
"""

__version__ = "1.0.0"
__author__ = "Anti-Duplication Team"

from .discovery_engine import CapabilityDiscoveryEngine
from .capability_registry import CapabilityRegistry
from .development_gate import DevelopmentGate
from .models import CapabilityInventory, OverlapAnalysis, DiscoveryAttestation

__all__ = [
    "CapabilityDiscoveryEngine",
    "CapabilityRegistry", 
    "DevelopmentGate",
    "CapabilityInventory",
    "OverlapAnalysis",
    "DiscoveryAttestation"
]