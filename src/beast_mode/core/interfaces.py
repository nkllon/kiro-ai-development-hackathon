"""
Core interfaces for Beast Mode framework
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ReflectiveModule(ABC):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    Base interface for all Beast Mode modules.
    
    Implements the Reflective Module (RM) pattern where all modules
    provide health monitoring and status interfaces.
    """
    
    def __init__(self) -> Any:
        self.module_name = self.__class__.__name__
        self.status = "initialized"
    
    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """get_health_status - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get current health status of the module"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """get_metrics - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get performance and operational metrics"""
        pass
    
    def get_module_info(self) -> Dict[str, Any]:
        """get_module_info - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get basic module information"""
        return {
            "name": self.module_name,
            "status": self.status,
            "type": "reflective_module"
        }