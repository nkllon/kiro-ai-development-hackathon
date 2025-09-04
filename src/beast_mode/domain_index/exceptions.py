"""
Exception classes for the Domain Index System

This module defines custom exceptions used throughout the domain index system
to provide clear error handling and debugging information.
"""


class DomainIndexError(Exception):
    """Base exception for all domain index system errors"""
    
    def __init__(self, message: str, component: str = None, operation: str = None):
        super().__init__(message)
        self.component = component
        self.operation = operation
        self.message = message
    
    def __str__(self):
        parts = [self.message]
        if self.component:
            parts.append(f"Component: {self.component}")
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        return " | ".join(parts)


class DomainRegistryError(DomainIndexError):
    """Errors related to domain registry operations"""
    pass


class DomainNotFoundError(DomainRegistryError):
    """Raised when a requested domain is not found"""
    
    def __init__(self, domain_name: str):
        super().__init__(f"Domain not found: {domain_name}", "registry", "get_domain")
        self.domain_name = domain_name


class DomainValidationError(DomainRegistryError):
    """Raised when domain validation fails"""
    
    def __init__(self, domain_name: str, validation_errors: list):
        message = f"Domain validation failed for {domain_name}: {', '.join(validation_errors)}"
        super().__init__(message, "registry", "validate_domain")
        self.domain_name = domain_name
        self.validation_errors = validation_errors


class QueryEngineError(DomainIndexError):
    """Errors related to query engine operations"""
    pass


class InvalidQueryError(QueryEngineError):
    """Raised when a query is malformed or invalid"""
    
    def __init__(self, query: str, reason: str):
        super().__init__(f"Invalid query '{query}': {reason}", "query_engine", "execute_query")
        self.query = query
        self.reason = reason


class QueryTimeoutError(QueryEngineError):
    """Raised when a query times out"""
    
    def __init__(self, query: str, timeout_seconds: int):
        super().__init__(f"Query timed out after {timeout_seconds}s: {query}", "query_engine", "execute_query")
        self.query = query
        self.timeout_seconds = timeout_seconds


class HealthMonitorError(DomainIndexError):
    """Errors related to health monitoring operations"""
    pass


class HealthCheckFailedError(HealthMonitorError):
    """Raised when a health check fails unexpectedly"""
    
    def __init__(self, domain_name: str, check_type: str, reason: str):
        super().__init__(f"Health check failed for {domain_name} ({check_type}): {reason}", 
                        "health_monitor", "check_health")
        self.domain_name = domain_name
        self.check_type = check_type
        self.reason = reason


class SyncEngineError(DomainIndexError):
    """Errors related to synchronization operations"""
    pass


class SyncConflictError(SyncEngineError):
    """Raised when synchronization encounters conflicts"""
    
    def __init__(self, conflicts: list):
        message = f"Synchronization conflicts detected: {', '.join(conflicts)}"
        super().__init__(message, "sync_engine", "sync_with_filesystem")
        self.conflicts = conflicts


class RegistryCorruptionError(SyncEngineError):
    """Raised when the domain registry is corrupted"""
    
    def __init__(self, registry_path: str, corruption_details: str):
        super().__init__(f"Registry corruption detected in {registry_path}: {corruption_details}",
                        "sync_engine", "load_registry")
        self.registry_path = registry_path
        self.corruption_details = corruption_details


class AnalyticsEngineError(DomainIndexError):
    """Errors related to analytics operations"""
    pass


class MetricsCalculationError(AnalyticsEngineError):
    """Raised when metrics calculation fails"""
    
    def __init__(self, domain_name: str, metric_type: str, reason: str):
        super().__init__(f"Failed to calculate {metric_type} metrics for {domain_name}: {reason}",
                        "analytics_engine", "calculate_metrics")
        self.domain_name = domain_name
        self.metric_type = metric_type
        self.reason = reason


class MakefileIntegrationError(DomainIndexError):
    """Errors related to makefile integration"""
    pass


class MakefileNotFoundError(MakefileIntegrationError):
    """Raised when required makefile is not found"""
    
    def __init__(self, makefile_path: str):
        super().__init__(f"Makefile not found: {makefile_path}", "makefile_integrator", "load_makefile")
        self.makefile_path = makefile_path


class MakeTargetExecutionError(MakefileIntegrationError):
    """Raised when makefile target execution fails"""
    
    def __init__(self, target: str, exit_code: int, error_output: str):
        super().__init__(f"Make target '{target}' failed with exit code {exit_code}: {error_output}",
                        "makefile_integrator", "execute_target")
        self.target = target
        self.exit_code = exit_code
        self.error_output = error_output


class CacheError(DomainIndexError):
    """Errors related to caching operations"""
    pass


class CacheCorruptionError(CacheError):
    """Raised when cache data is corrupted"""
    
    def __init__(self, cache_key: str, corruption_details: str):
        super().__init__(f"Cache corruption detected for key '{cache_key}': {corruption_details}",
                        "cache", "get_value")
        self.cache_key = cache_key
        self.corruption_details = corruption_details


class IndexError(DomainIndexError):
    """Errors related to indexing operations"""
    pass


class IndexCorruptionError(IndexError):
    """Raised when search index is corrupted"""
    
    def __init__(self, index_type: str, corruption_details: str):
        super().__init__(f"Index corruption detected in {index_type}: {corruption_details}",
                        "index", "search")
        self.index_type = index_type
        self.corruption_details = corruption_details


class IndexRebuildRequiredError(IndexError):
    """Raised when index needs to be rebuilt"""
    
    def __init__(self, index_type: str, reason: str):
        super().__init__(f"Index rebuild required for {index_type}: {reason}",
                        "index", "search")
        self.index_type = index_type
        self.reason = reason


class ConfigurationError(DomainIndexError):
    """Errors related to system configuration"""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid"""
    
    def __init__(self, config_key: str, config_value: str, reason: str):
        super().__init__(f"Invalid configuration for '{config_key}' = '{config_value}': {reason}",
                        "configuration", "validate_config")
        self.config_key = config_key
        self.config_value = config_value
        self.reason = reason


class ConfigurationFileError(ConfigurationError):
    """Raised when configuration file cannot be loaded"""
    
    def __init__(self, config_file: str, reason: str):
        super().__init__(f"Failed to load configuration file '{config_file}': {reason}",
                        "configuration", "load_config")
        self.config_file = config_file
        self.reason = reason


# Utility functions for error handling
def handle_domain_error(func):
    """Decorator for handling domain system errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DomainIndexError:
            # Re-raise domain system errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions in DomainIndexError
            raise DomainIndexError(f"Unexpected error in {func.__name__}: {str(e)}")
    return wrapper


def create_error_context(component: str, operation: str):
    """Create error context for consistent error reporting"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DomainIndexError as e:
                # Add context if not already present
                if not e.component:
                    e.component = component
                if not e.operation:
                    e.operation = operation
                raise
            except Exception as e:
                # Wrap in DomainIndexError with context
                raise DomainIndexError(str(e), component, operation)
        return wrapper
    return decorator