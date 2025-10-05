"""Base classes and interfaces for Google Calendar MCP integration.

This module provides the foundational classes and interfaces that all components
in the Google Calendar MCP integration inherit from, following the Beast Mode
framework's ReflectiveModule pattern.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth
from .models import ModuleHealth as MCPModuleHealth


class GoogleCalendarReflectiveModule(ReflectiveModule):
    """Extended ReflectiveModule for Google Calendar MCP components.
    
    Provides MCP-specific extensions while inheriting all Beast Mode framework
    capabilities from the unified ReflectiveModule.
    """
    
    def __init__(self, module_name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the Google Calendar reflective module.
        
        Args:
            module_name: Unique identifier for this module
            config: Optional configuration dictionary
        """
        # Initialize parent ReflectiveModule (it handles all the base functionality)
        super().__init__()
        
        # MCP-specific extensions only
        self.module_name = module_name
        self.config = config or {}
        self.correlation_id = str(uuid4())
        self._mcp_dependencies: Dict[str, str] = {}
        
        # Set up MCP-specific logging
        self.logger = logging.getLogger(f"beast_mode.mcp.google_calendar.{self.module_name}")
    
    # Implement required abstract methods from unified ReflectiveModule
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant."""
        return {
            "module_id": self.module_name,
            "module_type": "google_calendar_mcp",
            "version": "1.0.0",
            "framework": "Beast Mode MCP Integration",
            "config_keys": list(self.config.keys()),
            "correlation_id": self.correlation_id,
            "dependencies": list(self._mcp_dependencies.keys())
        }
    
    def get_capabilities(self) -> List:
        """Get module capabilities - RDI Compliant."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.MONITORING,
            ModuleCapability.CORE_FUNCTIONALITY
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant."""
        from src.rm_ddd.core.unified_reflective_module import ModuleStatus
        
        # Determine status based on dependencies
        status = ModuleStatus.HEALTHY
        issues = []
        
        for dep_name, dep_status in self._mcp_dependencies.items():
            if dep_status == "unhealthy":
                status = ModuleStatus.ERROR
                issues.append(f"Dependency {dep_name} is unhealthy")
            elif dep_status == "degraded" and status == ModuleStatus.HEALTHY:
                status = ModuleStatus.WARNING
                issues.append(f"Dependency {dep_name} is degraded")
        
        return ModuleHealth(
            module_id=self.module_name,
            status=status,
            health_score=1.0 if status == ModuleStatus.HEALTHY else 0.5 if status == ModuleStatus.WARNING else 0.0,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation - RDI Compliant."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        try:
            # MCP-specific degradation logic
            degraded_capabilities = []
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.MONITORING
            ]
            
            # Check if API integration should be degraded
            if any(status != "healthy" for status in self._mcp_dependencies.values()):
                degraded_capabilities.append(ModuleCapability.API_INTEGRATION)
                remaining_capabilities.remove(ModuleCapability.API_INTEGRATION)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    # MCP-specific helper methods (not duplicating base functionality)
    def add_mcp_dependency(self, name: str, status: str):
        """Add or update an MCP-specific dependency status."""
        self._mcp_dependencies[name] = status
    
    def log_with_correlation(self, level: str, message: str, **kwargs):
        """Log message with MCP correlation ID."""
        extra = {"correlation_id": self.correlation_id}
        extra.update(kwargs)
        getattr(self.logger, level.lower())(message, extra=extra)
    
    # Abstract methods for MCP-specific implementations
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the MCP module and its dependencies."""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Gracefully shutdown the MCP module."""
        pass


class MCPServerInterface(ABC):
    """Interface for MCP server implementations."""
    
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


class AuthManagerInterface(ABC):
    """Interface for authentication managers."""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Perform authentication flow.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        pass
    
    @abstractmethod
    def get_access_token(self) -> Optional[str]:
        """Get current access token.
        
        Returns:
            Access token if available, None otherwise
        """
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """Refresh the access token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        pass


class CalendarOperationsInterface(ABC):
    """Interface for calendar operations."""
    
    @abstractmethod
    def get_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get calendar events in the specified time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of calendar events
        """
        pass
    
    @abstractmethod
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Created event data
        """
        pass
    
    @abstractmethod
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event.
        
        Args:
            event_id: ID of event to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated event data
        """
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event.
        
        Args:
            event_id: ID of event to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        pass


class ErrorHandlerInterface(ABC):
    """Interface for error handling components."""
    
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


class ConfigManagerInterface(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from all sources.
        
        Returns:
            Merged configuration dictionary
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration against schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        pass