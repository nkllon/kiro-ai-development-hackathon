"""Google Calendar MCP Server implementation.

This module provides the main MCP server class that handles Google Calendar integration
through the Model Context Protocol, following the Beast Mode framework patterns.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import GoogleCalendarReflectiveModule
from .interfaces.server_interfaces import MCPServerInterface
from .models import MCPRequest, MCPResponse, MCPError, ModuleHealth
from .request_router import MCPRequestRouter
from .profiling import profile, get_profiler


class GoogleCalendarMCPServer(GoogleCalendarReflectiveModule, MCPServerInterface):
    """Main MCP server for Google Calendar integration.
    
    This class implements the MCP protocol server that handles communication
    between Claude Desktop and Google Calendar API through various handlers.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Google Calendar MCP server.
        
        Args:
            config: Server configuration dictionary
        """
        super().__init__("google_calendar_mcp_server", config)
        
        # Server configuration
        self.host = self.config.get("host", "0.0.0.0")
        self.port = self.config.get("port", 3000)
        self.log_level = self.config.get("log_level", "info")
        
        # Component references (will be injected)
        self.auth_manager = None
        self.operations_handler = None
        self.error_handler = None
        self.config_manager = None
        
        # Request routing
        self.request_router = MCPRequestRouter()
        
        # Server state
        self.server = None
        self.is_running = False
        self.request_count = 0
        self.error_count = 0
        
        self.log_with_correlation(
            "info",
            "Google Calendar MCP Server initialized",
            host=self.host,
            port=self.port
        )
    
    def set_auth_manager(self, auth_manager):
        """Set the authentication manager dependency.
        
        Args:
            auth_manager: GoogleAuthManager instance
        """
        self.auth_manager = auth_manager
        self.add_mcp_dependency("auth_manager", "healthy")
        self._update_router_dependencies()
        self.log_with_correlation("info", "Auth manager dependency set")
    
    def set_operations_handler(self, operations_handler):
        """Set the calendar operations handler dependency.
        
        Args:
            operations_handler: CalendarOperationsHandler instance
        """
        self.operations_handler = operations_handler
        self.add_mcp_dependency("operations_handler", "healthy")
        self._update_router_dependencies()
        self.log_with_correlation("info", "Operations handler dependency set")
    
    def set_error_handler(self, error_handler):
        """Set the error handler dependency.
        
        Args:
            error_handler: ErrorHandler instance
        """
        self.error_handler = error_handler
        self.add_mcp_dependency("error_handler", "healthy")
        self.log_with_correlation("info", "Error handler dependency set")
    
    def set_config_manager(self, config_manager):
        """Set the configuration manager dependency.
        
        Args:
            config_manager: ConfigManager instance
        """
        self.config_manager = config_manager
        self.add_mcp_dependency("config_manager", "healthy")
        self.log_with_correlation("info", "Config manager dependency set")
    
    def _update_router_dependencies(self):
        """Update router dependencies when components are set."""
        if self.auth_manager and self.operations_handler:
            self.request_router.set_dependencies(
                self.auth_manager,
                self.operations_handler,
                self
            )
    
    def initialize(self) -> bool:
        """Initialize the MCP server and all dependencies.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Google Calendar MCP Server")
            
            # Validate dependencies
            if not self._validate_dependencies():
                self.log_with_correlation("error", "Missing dependencies")
                return False
            
            # Initialize authentication
            if not self.auth_manager.initialize():
                self.log_with_correlation("warning", "Auth manager initialization failed, continuing in stub mode")
                # Don't return False - continue in stub mode
            
            # Initialize operations handler
            if not self.operations_handler.initialize():
                self.log_with_correlation("warning", "Operations handler initialization failed, continuing in stub mode")
                # Don't return False - continue in stub mode
            self.logger.info("Google Calendar MCP Server initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to initialize server: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            # Health is managed by unified ReflectiveModule
            return False
    
    def _validate_dependencies(self) -> bool:
        """Validate that all required dependencies are set.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        required_deps = ["auth_manager", "operations_handler"]
        missing_deps = []
        
        for dep in required_deps:
            if getattr(self, dep) is None:
                missing_deps.append(dep)
        
        if missing_deps:
            self.logger.error(
                f"Missing required dependencies: {missing_deps}",
                extra={"correlation_id": self.correlation_id}
            )
            return False
        
        return True
    
    def start_server(self) -> bool:
        """Start the MCP server.
        
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            if self.is_running:
                self.logger.warning("Server is already running")
                return True
            
            self.logger.info(f"Starting MCP server on {self.host}:{self.port}")
            
            # For now, we'll implement a simple HTTP server
            # In a full implementation, this would start the actual MCP protocol server
            self.is_running = True
            
            # Health is managed by unified ReflectiveModule
            
            self.logger.info("MCP server started successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to start server: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            # Health is managed by unified ReflectiveModule
            return False
    
    def stop_server(self) -> bool:
        """Stop the MCP server.
        
        Returns:
            True if server stopped successfully, False otherwise
        """
        try:
            if not self.is_running:
                self.logger.warning("Server is not running")
                return True
            
            self.logger.info("Stopping MCP server")
            
            # Stop the server
            self.is_running = False
            
            # Health is managed by unified ReflectiveModule
            
            self.logger.info("MCP server stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to stop server: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    @profile("mcp_request_handling")
    def handle_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP request.
        
        Args:
            request_data: Raw MCP request data
            
        Returns:
            MCP response dictionary
        """
        try:
            self.request_count += 1
            
            # Parse MCP request
            try:
                request = MCPRequest(
                    method=request_data.get("method", ""),
                    params=request_data.get("params", {}),
                    id=request_data.get("id"),
                    jsonrpc=request_data.get("jsonrpc", "2.0")
                )
            except Exception as e:
                return self._create_error_response(
                    -32700, "Parse error", str(e), request_data.get("id")
                )
            
            self.log_with_correlation(
                "info",
                f"Handling MCP request: {request.method}",
                method=request.method,
                request_id=request.id
            )
            
            # Route request to appropriate handler
            response = self.request_router.route_request(request)
            
            return response.__dict__
            
        except Exception as e:
            self.error_count += 1
            self.log_with_correlation(
                "error",
                f"Error handling MCP request: {e}",
                error=str(e),
                request_data=request_data
            )
            
            return self._create_error_response(
                -32603, "Internal error", str(e), request_data.get("id")
            )
    

    
    def _create_error_response(self, code: int, message: str, data: str, request_id: Optional[str]) -> Dict[str, Any]:
        """Create an error response dictionary.
        
        Args:
            code: Error code
            message: Error message
            data: Error data
            request_id: Request ID
            
        Returns:
            Error response dictionary
        """
        error = MCPError(code=code, message=message, data={"details": data})
        response = MCPResponse(error=error, id=request_id)
        return response.__dict__
    
    def shutdown(self) -> bool:
        """Gracefully shutdown the server.
        
        Returns:
            True if shutdown successful, False otherwise
        """
        try:
            self.logger.info("Shutting down Google Calendar MCP Server")
            
            # Stop the server
            if not self.stop_server():
                self.logger.warning("Failed to stop server gracefully")
            
            # Shutdown dependencies
            if self.auth_manager:
                self.auth_manager.shutdown()
            
            if self.operations_handler:
                self.operations_handler.shutdown()
            
            # Health is managed by unified ReflectiveModule
            
            self.logger.info("Google Calendar MCP Server shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error during shutdown: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get server performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        base_metrics = super().get_metrics()
        
        server_metrics = {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "is_running": self.is_running,
            "host": self.host,
            "port": self.port
        }
        
        return {**base_metrics, **server_metrics}