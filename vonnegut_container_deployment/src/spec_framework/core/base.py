"""
Base classes for the Spec Mode Framework.

Temporary implementation until beast_mode.core is available.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class ReflectiveModule(ABC):
    """
    Base class for reflective modules in the Spec Mode Framework.
    
    This is a temporary implementation that will be replaced with
    beast_mode.core.ReflectiveModule when available.
    """
    
    def __init__(self):
        """Initialize the reflective module."""
        pass
    
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Return health status of the module."""
        pass
    
    @abstractmethod
    def ready(self) -> bool:
        """Check if module is ready for operation."""
        pass
    
    @abstractmethod
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        pass
    
    @abstractmethod
    def status(self) -> str:
        """Return current operational status."""
        pass