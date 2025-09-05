"""
Abstract interfaces for the Domain Index System

This module defines the abstract base classes and interfaces that all
domain system components must implement. This ensures consistent APIs
and enables dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
from datetime import datetime

from .models import (
    Domain,
    DomainCollection,
    HealthStatus,
    HealthStatusCollection,
    DomainMetrics,
    MetricsCollection,
    DependencyGraph,
    QueryResult,
    ValidationResult,
    SyncResult,
    DomainSuggestion,
    PatternChange,
    DomainChange,
    UpdateResult,
    ComplexityReport,
    EvolutionReport,
    ExtractionCandidate,
    MakeTarget,
    ExecutionResult
)


class DomainRegistryInterface(ABC):
    """Abstract interface for domain registry management"""
    
    @abstractmethod
    def load_registry(self) -> bool:
        """Load the domain registry from storage"""
        pass
    
    @abstractmethod
    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """Retrieve a specific domain by name"""
        pass
    
    @abstractmethod
    def get_all_domains(self) -> DomainCollection:
        """Retrieve all domains"""
        pass
    
    @abstractmethod
    def search_domains(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Domain]:
        """Search domains with optional filters"""
        pass
    
    @abstractmethod
    def get_dependencies(self, domain_name: str) -> DependencyGraph:
        """Get dependency graph for a domain"""
        pass
    
    @abstractmethod
    def validate_domain(self, domain: Domain) -> ValidationResult:
        """Validate domain structure and requirements"""
        pass
    
    @abstractmethod
    def update_domain(self, domain: Domain) -> bool:
        """Update a domain in the registry"""
        pass
    
    @abstractmethod
    def create_domain(self, domain: Domain) -> bool:
        """Create a new domain in the registry"""
        pass
    
    @abstractmethod
    def delete_domain(self, domain_name: str) -> bool:
        """Delete a domain from the registry"""
        pass


class QueryEngineInterface(ABC):
    """Abstract interface for domain querying capabilities"""
    
    @abstractmethod
    def natural_language_query(self, query: str) -> QueryResult:
        """Process natural language queries about domains"""
        pass
    
    @abstractmethod
    def pattern_search(self, pattern: str) -> List[Domain]:
        """Search domains by file patterns"""
        pass
    
    @abstractmethod
    def content_search(self, content_indicator: str) -> List[Domain]:
        """Search domains by content indicators"""
        pass
    
    @abstractmethod
    def capability_search(self, capability: str) -> List[Domain]:
        """Find domains by capability or functionality"""
        pass
    
    @abstractmethod
    def relationship_query(self, domain: str, relationship_type: str) -> List[Domain]:
        """Query domain relationships"""
        pass
    
    @abstractmethod
    def complex_query(self, query_spec: Dict[str, Any]) -> QueryResult:
        """Execute complex structured queries"""
        pass
    
    @abstractmethod
    def suggest_queries(self, partial_query: str) -> List[str]:
        """Suggest query completions"""
        pass


class HealthMonitorInterface(ABC):
    """Abstract interface for domain health monitoring"""
    
    @abstractmethod
    def check_domain_health(self, domain_name: str) -> HealthStatus:
        """Check health of a specific domain"""
        pass
    
    @abstractmethod
    def check_all_domains(self) -> HealthStatusCollection:
        """Check health of all domains"""
        pass
    
    @abstractmethod
    def validate_dependencies(self, domain_name: Optional[str] = None) -> List[str]:
        """Validate domain dependencies"""
        pass
    
    @abstractmethod
    def detect_orphaned_files(self) -> List[str]:
        """Find files not covered by any domain"""
        pass
    
    @abstractmethod
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains"""
        pass
    
    @abstractmethod
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        pass
    
    @abstractmethod
    def schedule_health_check(self, domain_name: str, interval_minutes: int) -> bool:
        """Schedule periodic health checks"""
        pass


class SyncEngineInterface(ABC):
    """Abstract interface for domain synchronization"""
    
    @abstractmethod
    def sync_with_filesystem(self) -> SyncResult:
        """Synchronize domain patterns with actual files"""
        pass
    
    @abstractmethod
    def suggest_domain_assignments(self, file_path: str) -> List[DomainSuggestion]:
        """Suggest appropriate domains for new files"""
        pass
    
    @abstractmethod
    def detect_pattern_changes(self) -> List[PatternChange]:
        """Detect changes in domain file patterns"""
        pass
    
    @abstractmethod
    def update_domain_registry(self, changes: List[DomainChange]) -> UpdateResult:
        """Apply changes to the domain registry"""
        pass
    
    @abstractmethod
    def resolve_conflicts(self, conflicts: List[str]) -> List[DomainSuggestion]:
        """Resolve domain assignment conflicts"""
        pass
    
    @abstractmethod
    def backup_registry(self) -> str:
        """Create backup of current registry"""
        pass
    
    @abstractmethod
    def restore_registry(self, backup_path: str) -> bool:
        """Restore registry from backup"""
        pass


class AnalyticsEngineInterface(ABC):
    """Abstract interface for domain analytics"""
    
    @abstractmethod
    def get_domain_metrics(self, domain_name: str) -> DomainMetrics:
        """Get comprehensive metrics for a domain"""
        pass
    
    @abstractmethod
    def get_all_metrics(self) -> MetricsCollection:
        """Get metrics for all domains"""
        pass
    
    @abstractmethod
    def get_complexity_analysis(self) -> ComplexityReport:
        """Analyze domain complexity and coupling"""
        pass
    
    @abstractmethod
    def get_extraction_candidates(self, min_score: float = 0.7) -> List[ExtractionCandidate]:
        """Identify domains suitable for extraction"""
        pass
    
    @abstractmethod
    def track_evolution(self, timeframe: str) -> EvolutionReport:
        """Track domain changes over time"""
        pass
    
    @abstractmethod
    def generate_insights(self) -> Dict[str, Any]:
        """Generate actionable insights about domain architecture"""
        pass
    
    @abstractmethod
    def compare_domains(self, domain1: str, domain2: str) -> Dict[str, Any]:
        """Compare two domains across multiple dimensions"""
        pass


class MakefileIntegratorInterface(ABC):
    """Abstract interface for makefile integration"""
    
    @abstractmethod
    def get_domain_targets(self, domain_name: str) -> List[MakeTarget]:
        """Get available makefile targets for a domain"""
        pass
    
    @abstractmethod
    def execute_domain_operation(self, domain: str, operation: str) -> ExecutionResult:
        """Execute makefile operation for a domain"""
        pass
    
    @abstractmethod
    def generate_domain_targets(self, domain: Domain) -> List[MakeTarget]:
        """Generate makefile targets for a domain"""
        pass
    
    @abstractmethod
    def validate_makefile_integration(self) -> ValidationResult:
        """Validate makefile integration completeness"""
        pass
    
    @abstractmethod
    def update_makefile_targets(self, domain: Domain, targets: List[MakeTarget]) -> bool:
        """Update makefile targets for a domain"""
        pass
    
    @abstractmethod
    def get_makefile_health(self) -> Dict[str, Any]:
        """Get health status of makefile integration"""
        pass


class CacheInterface(ABC):
    """Abstract interface for caching layer"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        pass


class IndexInterface(ABC):
    """Abstract interface for domain indexing"""
    
    @abstractmethod
    def build_index(self, domains: DomainCollection) -> bool:
        """Build search index from domains"""
        pass
    
    @abstractmethod
    def update_index(self, domain: Domain) -> bool:
        """Update index for a specific domain"""
        pass
    
    @abstractmethod
    def search_index(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[str]:
        """Search index and return domain names"""
        pass
    
    @abstractmethod
    def get_index_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        pass
    
    @abstractmethod
    def rebuild_index(self) -> bool:
        """Rebuild the entire index"""
        pass


class EventInterface(ABC):
    """Abstract interface for event handling"""
    
    @abstractmethod
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Emit an event"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, callback: callable) -> str:
        """Subscribe to events"""
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        pass
    
    @abstractmethod
    def get_event_history(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get event history"""
        pass


# Composite interface for the complete domain system
class DomainSystemInterface(ABC):
    """Complete domain system interface"""
    
    @property
    @abstractmethod
    def registry(self) -> DomainRegistryInterface:
        """Domain registry manager"""
        pass
    
    @property
    @abstractmethod
    def query_engine(self) -> QueryEngineInterface:
        """Query engine"""
        pass
    
    @property
    @abstractmethod
    def health_monitor(self) -> HealthMonitorInterface:
        """Health monitor"""
        pass
    
    @property
    @abstractmethod
    def sync_engine(self) -> SyncEngineInterface:
        """Synchronization engine"""
        pass
    
    @property
    @abstractmethod
    def analytics(self) -> AnalyticsEngineInterface:
        """Analytics engine"""
        pass
    
    @property
    @abstractmethod
    def makefile_integrator(self) -> MakefileIntegratorInterface:
        """Makefile integrator"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the complete system"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the system gracefully"""
        pass
    
    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        pass