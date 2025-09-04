"""
Beast Mode Domain Index System

This module provides comprehensive domain indexing, querying, and management
capabilities for the Beast Mode framework's domain architecture.

Core Components:
- Domain Registry Manager: Enhanced management of project_model_registry.json
- Query Engine: Intelligent domain querying with natural language support
- Health Monitor: Continuous domain health monitoring and validation
- Sync Engine: Automated synchronization between registry and filesystem
- Analytics Engine: Domain metrics, trends, and extraction analysis
- Makefile Integrator: Integration with existing makefile system
"""

from .models import (
    Domain,
    DomainTools,
    DomainMetadata,
    HealthStatus,
    HealthIssue,
    HealthMetrics,
    DomainMetrics,
    DependencyGraph,
    QueryResult,
    ExtractionCandidate,
    ValidationResult,
    SyncResult,
    DomainSuggestion,
    PatternChange,
    DomainChange,
    UpdateResult,
    ComplexityReport,
    EvolutionReport,
    MakeTarget,
    ExecutionResult
)

from .interfaces import (
    DomainRegistryInterface,
    QueryEngineInterface,
    HealthMonitorInterface,
    SyncEngineInterface,
    AnalyticsEngineInterface,
    MakefileIntegratorInterface,
    CacheInterface,
    IndexInterface,
    EventInterface,
    DomainSystemInterface
)

from .base import (
    DomainSystemComponent,
    ConfigurableComponent,
    CachedComponent
)

from .exceptions import (
    DomainIndexError,
    DomainRegistryError,
    DomainNotFoundError,
    DomainValidationError,
    QueryEngineError,
    InvalidQueryError,
    QueryTimeoutError,
    HealthMonitorError,
    HealthCheckFailedError,
    SyncEngineError,
    SyncConflictError,
    RegistryCorruptionError,
    AnalyticsEngineError,
    MetricsCalculationError,
    MakefileIntegrationError,
    MakefileNotFoundError,
    MakeTargetExecutionError
)

__version__ = "1.0.0"
__author__ = "Beast Mode Framework"

__all__ = [
    # Data Models
    "Domain",
    "DomainTools", 
    "DomainMetadata",
    "HealthStatus",
    "HealthIssue",
    "HealthMetrics",
    "DomainMetrics",
    "DependencyGraph",
    "QueryResult",
    "ExtractionCandidate",
    "ValidationResult",
    "SyncResult",
    "DomainSuggestion",
    "PatternChange",
    "DomainChange",
    "UpdateResult",
    "ComplexityReport",
    "EvolutionReport",
    "MakeTarget",
    "ExecutionResult",
    
    # Interfaces
    "DomainRegistryInterface",
    "QueryEngineInterface", 
    "HealthMonitorInterface",
    "SyncEngineInterface",
    "AnalyticsEngineInterface",
    "MakefileIntegratorInterface",
    "CacheInterface",
    "IndexInterface",
    "EventInterface",
    "DomainSystemInterface",
    
    # Base Classes
    "DomainSystemComponent",
    "ConfigurableComponent", 
    "CachedComponent",
    
    # Exceptions
    "DomainIndexError",
    "DomainRegistryError",
    "DomainNotFoundError",
    "DomainValidationError",
    "QueryEngineError",
    "InvalidQueryError",
    "QueryTimeoutError",
    "HealthMonitorError",
    "HealthCheckFailedError",
    "SyncEngineError",
    "SyncConflictError",
    "RegistryCorruptionError",
    "AnalyticsEngineError",
    "MetricsCalculationError",
    "MakefileIntegrationError",
    "MakefileNotFoundError",
    "MakeTargetExecutionError"
]