"""MCP Request Router for Google Calendar integration.

This module handles routing of MCP requests to appropriate handlers,
extracted from the main server to reduce module size and improve maintainability.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .models import MCPRequest, MCPResponse, MCPError
from .profiling import profile


class MCPRequestRouter:
    """Routes MCP requests to appropriate handlers."""
    
    def __init__(self):
        """Initialize the request router."""
        self.auth_manager = None
        self.operations_handler = None
        self.server = None
    
    def set_dependencies(self, auth_manager, operations_handler, server):
        """Set the required dependencies.
        
        Args:
            auth_manager: GoogleAuthManager instance
            operations_handler: CalendarOperationsHandler instance
            server: GoogleCalendarMCPServer instance
        """
        self.auth_manager = auth_manager
        self.operations_handler = operations_handler
        self.server = server
    
    @profile("mcp_request_routing")
    def route_request(self, request: MCPRequest) -> MCPResponse:
        """Route MCP request to appropriate handler.
        
        Args:
            request: Parsed MCP request
            
        Returns:
            MCP response
        """
        method = request.method
        params = request.params
        
        try:
            # Authentication methods
            if method.startswith("auth."):
                return self._handle_auth_request(method, params, request.id)
            
            # Calendar operation methods
            elif method.startswith("calendar."):
                return self._handle_calendar_request(method, params, request.id)
            
            # Health and monitoring methods
            elif method.startswith("health."):
                return self._handle_health_request(method, params, request.id)
            
            else:
                error = MCPError(
                    code=-32601,
                    message="Method not found",
                    data={"method": method}
                )
                return MCPResponse(error=error, id=request.id)
                
        except Exception as e:
            error = MCPError(
                code=-32603,
                message="Internal error",
                data={"error": str(e)}
            )
            return MCPResponse(error=error, id=request.id)
    
    @profile("auth_request_handling")
    def _handle_auth_request(self, method: str, params: Dict[str, Any], request_id: Optional[str]) -> MCPResponse:
        """Handle authentication-related requests.
        
        Args:
            method: Authentication method name
            params: Request parameters
            request_id: Request ID
            
        Returns:
            MCP response for authentication request
        """
        if method == "auth.status":
            result = {
                "authenticated": self.auth_manager.is_authenticated(),
                "token_valid": self.auth_manager.get_access_token() is not None
            }
            return MCPResponse(result=result, id=request_id)
        
        elif method == "auth.authenticate":
            success = self.auth_manager.authenticate()
            result = {"success": success}
            return MCPResponse(result=result, id=request_id)
        
        elif method == "auth.revoke":
            success = self.auth_manager.revoke_authentication()
            result = {"success": success}
            return MCPResponse(result=result, id=request_id)
        
        else:
            error = MCPError(
                code=-32601,
                message="Authentication method not found",
                data={"method": method}
            )
            return MCPResponse(error=error, id=request_id)
    
    @profile("calendar_request_handling")
    def _handle_calendar_request(self, method: str, params: Dict[str, Any], request_id: Optional[str]) -> MCPResponse:
        """Handle calendar operation requests.
        
        Args:
            method: Calendar method name
            params: Request parameters
            request_id: Request ID
            
        Returns:
            MCP response for calendar request
        """
        if method == "calendar.get_events":
            start_time_str = params.get("start_time")
            end_time_str = params.get("end_time")
            
            # Handle ISO format with Z suffix
            if start_time_str and start_time_str.endswith('Z'):
                start_time_str = start_time_str[:-1] + '+00:00'
            if end_time_str and end_time_str.endswith('Z'):
                end_time_str = end_time_str[:-1] + '+00:00'
            
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            events = self.operations_handler.get_events(start_time, end_time)
            return MCPResponse(result={"events": events}, id=request_id)
        
        elif method == "calendar.create_event":
            event_data = params.get("event_data", {})
            event = self.operations_handler.create_event(event_data)
            return MCPResponse(result={"event": event}, id=request_id)
        
        elif method == "calendar.update_event":
            event_id = params.get("event_id")
            updates = params.get("updates", {})
            event = self.operations_handler.update_event(event_id, updates)
            return MCPResponse(result={"event": event}, id=request_id)
        
        elif method == "calendar.delete_event":
            event_id = params.get("event_id")
            success = self.operations_handler.delete_event(event_id)
            return MCPResponse(result={"success": success}, id=request_id)
        
        elif method == "calendar.check_availability":
            start_time_str = params.get("start_time")
            end_time_str = params.get("end_time")
            
            # Handle ISO format with Z suffix
            if start_time_str and start_time_str.endswith('Z'):
                start_time_str = start_time_str[:-1] + '+00:00'
            if end_time_str and end_time_str.endswith('Z'):
                end_time_str = end_time_str[:-1] + '+00:00'
            
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            availability = self.operations_handler.check_availability(start_time, end_time)
            return MCPResponse(result={"availability": availability}, id=request_id)
        
        else:
            error = MCPError(
                code=-32601,
                message="Calendar method not found",
                data={"method": method}
            )
            return MCPResponse(error=error, id=request_id)
    
    @profile("health_request_handling")
    def _handle_health_request(self, method: str, params: Dict[str, Any], request_id: Optional[str]) -> MCPResponse:
        """Handle health and monitoring requests.
        
        Args:
            method: Health method name
            params: Request parameters
            request_id: Request ID
            
        Returns:
            MCP response for health request
        """
        if method == "health.status":
            health = self.server.get_health_status()
            return MCPResponse(result=health.__dict__, id=request_id)
        
        elif method == "health.metrics":
            metrics = self.server.get_metrics()
            return MCPResponse(result=metrics, id=request_id)
        
        elif method == "health.profiling_report":
            from .profiling import get_profiler
            profiler = get_profiler()
            report = profiler.generate_performance_report()
            return MCPResponse(result=report, id=request_id)
        
        elif method == "health.slow_operations":
            from .profiling import get_profiler
            threshold_ms = params.get("threshold_ms", 1000.0)
            profiler = get_profiler()
            slow_ops = profiler.get_slow_operations(threshold_ms)
            result = [op.__dict__ for op in slow_ops]
            return MCPResponse(result={"slow_operations": result}, id=request_id)
        
        else:
            error = MCPError(
                code=-32601,
                message="Health method not found",
                data={"method": method}
            )
            return MCPResponse(error=error, id=request_id)