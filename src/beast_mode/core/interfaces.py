"""
Core interfaces for Beast Mode framework
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ReflectiveModule(ABC):
    """
    Base interface for all Beast Mode modules.
    
    Implements the Reflective Module (RM) pattern where all modules
    provide health monitoring and status interfaces.
    """
    
    def __init__(self):
        self.module_name = self.__class__.__name__
        self.status = "initialized"
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of the module"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance and operational metrics"""
        pass
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get basic module information"""
        return {
            "name": self.module_name,
            "status": self.status,
            "type": "reflective_module"
        }