#!/usr/bin/env python3
"""
Data models for service auto-start framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

from .enums import Platform, ServiceStatus, RestartPolicy, ConfigurationResult, ValidationResult


@dataclass
class ServiceDefinition:
    """Complete service definition for auto-start configuration."""
    name: str
    command: str
    working_directory: str
    environment: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    health_check_url: Optional[str] = None
    restart_policy: RestartPolicy = RestartPolicy.ALWAYS
    user: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate service definition after initialization."""
        if not self.name:
            raise ValueError("Service name cannot be empty")
        if not self.command:
            raise ValueError("Service command cannot be empty")
        if not self.working_directory:
            raise ValueError("Working directory cannot be empty")


@dataclass
class HealthCheckConfig:
    """Health check configuration for services."""
    url: str
    timeout: int = 30
    interval: int = 30
    retries: int = 3
    start_period: int = 60
    expected_status: int = 200
    
    def __post_init__(self):
        """Validate health check configuration."""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.interval <= 0:
            raise ValueError("Interval must be positive")
        if self.retries < 0:
            raise ValueError("Retries cannot be negative")


@dataclass
class PlatformConfig:
    """Platform-specific configuration settings."""
    platform: Platform
    config_path: str
    template_path: Optional[str] = None
    service_user: Optional[str] = None
    service_group: Optional[str] = None
    additional_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceRegistration:
    """Complete service registration with metadata."""
    definition: ServiceDefinition
    platform: Platform
    status: ServiceStatus = ServiceStatus.REGISTERED
    auto_start_enabled: bool = False
    last_health_check: Optional[datetime] = None
    configuration_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_status(self, new_status: ServiceStatus):
        """Update service status with timestamp."""
        self.status = new_status
        self.updated_at = datetime.now()


@dataclass
class AutoStartResult:
    """Result of auto-start configuration operation."""
    service_name: str
    platform: Platform
    result: ConfigurationResult
    message: str
    configuration_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if operation was successful."""
        return self.result == ConfigurationResult.SUCCESS
    
    @property
    def has_errors(self) -> bool:
        """Check if operation had errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if operation had warnings."""
        return len(self.warnings) > 0


@dataclass
class ValidationReport:
    """Validation report for service configurations."""
    service_name: str
    platform: Platform
    overall_result: ValidationResult
    checks: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_check(self, name: str, result: ValidationResult, message: str, details: Optional[Dict[str, Any]] = None):
        """Add a validation check result."""
        self.checks.append({
            "name": name,
            "result": result,
            "message": message,
            "details": details or {}
        })
    
    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.overall_result == ValidationResult.PASSED
    
    @property
    def failed_checks(self) -> List[Dict[str, Any]]:
        """Get list of failed checks."""
        return [check for check in self.checks if check["result"] == ValidationResult.FAILED]
    
    @property
    def warning_checks(self) -> List[Dict[str, Any]]:
        """Get list of checks with warnings."""
        return [check for check in self.checks if check["result"] == ValidationResult.WARNING]


@dataclass
class DependencyGraph:
    """Service dependency graph for startup ordering."""
    services: Dict[str, ServiceDefinition] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_service(self, service: ServiceDefinition):
        """Add service to dependency graph."""
        self.services[service.name] = service
        self.dependencies[service.name] = service.dependencies.copy()
    
    def remove_service(self, service_name: str):
        """Remove service from dependency graph."""
        if service_name in self.services:
            del self.services[service_name]
        if service_name in self.dependencies:
            del self.dependencies[service_name]
        
        # Remove from other services' dependencies
        for deps in self.dependencies.values():
            if service_name in deps:
                deps.remove(service_name)
    
    def get_startup_order(self) -> List[str]:
        """Calculate startup order using topological sort."""
        from collections import defaultdict, deque
        
        # Build adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize all services with 0 in-degree
        for service_name in self.services:
            in_degree[service_name] = 0
        
        # Build graph and calculate in-degrees
        for service_name, deps in self.dependencies.items():
            for dep in deps:
                if dep in self.services:  # Only include registered dependencies
                    graph[dep].append(service_name)
                    in_degree[service_name] += 1
        
        # Topological sort using Kahn's algorithm
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(self.services):
            remaining = set(self.services.keys()) - set(result)
            raise ValueError(f"Circular dependency detected among services: {remaining}")
        
        return result