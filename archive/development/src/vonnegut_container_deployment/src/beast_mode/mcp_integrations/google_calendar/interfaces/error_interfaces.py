"""Error handling interface definitions.

This module contains interfaces related to error handling and recovery,
focusing solely on error management contracts.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ErrorHandlerInterface(ABC):
    """Interface for error handling components.
    
    Defines the contract for systematic error handling and recovery
    across different types of failures in the MCP integration.
    """
    
    @abstractmethod
    def handle_auth_error(self, error: Exception) -> Dict[str, Any]:
        """Handle authentication-related errors.
        
        Args:
            error: The authentication error
            
        Returns:
            Error response dictionary
        """
        pass
    
    @abstractmethod
    def handle_api_error(self, error: Exception) -> Dict[str, Any]:
        """Handle API-related errors.
        
        Args:
            error: The API error
            
        Returns:
            Error response dictionary
        """
        pass
    
    @abstractmethod
    def handle_mcp_error(self, error: Exception) -> Dict[str, Any]:
        """Handle MCP protocol errors.
        
        Args:
            error: The MCP error
            
        Returns:
            Error response dictionary
        """
        pass