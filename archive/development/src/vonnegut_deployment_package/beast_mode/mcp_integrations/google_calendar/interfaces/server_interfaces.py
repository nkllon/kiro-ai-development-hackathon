"""MCP Server interface definitions.

This module contains interfaces related to MCP server functionality,
focusing solely on server lifecycle and request handling contracts.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class MCPServerInterface(ABC):
    """Interface for MCP server implementations.
    
    Defines the contract for MCP protocol servers that handle
    Model Context Protocol communication.
    """
    
    @abstractmethod
    def start_server(self) -> bool:
        """Start the MCP server.
        
        Returns:
            True if server started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def stop_server(self) -> bool:
        """Stop the MCP server.
        
        Returns:
            True if server stopped successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP request.
        
        Args:
            request: MCP request dictionary
            
        Returns:
            MCP response dictionary
        """
        pass