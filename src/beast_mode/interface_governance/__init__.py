"""
Beast Mode Interface Governance

Provides interface registry and duplication prevention for Beast Mode
development workflow.
"""

from .interface_registry import (
    BeastModeInterfaceRegistry,
    InterfaceMetadata,
    InterfaceType,
    InterfaceStatus
)

__all__ = [
    'BeastModeInterfaceRegistry',
    'InterfaceMetadata', 
    'InterfaceType',
    'InterfaceStatus'
]
