"""
Interfaces Services

This module was extracted from interfaces.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from .models import Domain, DomainCollection, HealthStatus, HealthStatusCollection, DomainMetrics, MetricsCollection, DependencyGraph, QueryResult, ValidationResult, SyncResult, DomainSuggestion, PatternChange, DomainChange, UpdateResult, ComplexityReport, EvolutionReport, ExtractionCandidate, MakeTarget, ExecutionResult

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
    def get_extraction_candidates(self, min_score: float=0.7) -> List[ExtractionCandidate]:
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
