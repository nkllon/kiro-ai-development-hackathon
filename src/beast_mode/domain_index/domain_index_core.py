#!/usr/bin/env python3
"""
Domain Index Core
=================

Core implementation of the Domain Index System for intelligent querying,
relationship analysis, and automated maintenance of domain architecture.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide intelligent domain querying and relationship analysis
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

from ..core.reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability


class DomainType(Enum):
    """Domain types in the architecture."""
    DEMO_CORE = "demo_core"
    DEMO_TOOLS = "demo_tools"
    DEMO_INFRASTRUCTURE = "demo_infrastructure"
    DEMO_VALIDATION = "demo_validation"
    DEMO_DOCUMENTATION = "demo_documentation"
    BEAST_MODE = "beast_mode"
    GHOSTBUSTERS = "ghostbusters"
    UNKNOWN = "unknown"


class DomainHealth(Enum):
    """Domain health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class DomainInfo:
    """Information about a domain."""
    name: str
    type: DomainType
    description: str
    patterns: List[str]
    dependencies: List[str]
    tools: List[str]
    requirements: List[str]
    health: DomainHealth
    extraction_potential: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryResult:
    """Result of a domain query."""
    domains: List[DomainInfo]
    total_count: int
    query_time_ms: float
    relevance_scores: Dict[str, float] = field(default_factory=dict)


class DomainIndexCore(ReflectiveModule):
    """
    Domain Index System for intelligent querying and analysis of domain architecture.
    
    Provides intelligent domain discovery, relationship analysis, and automated
    maintenance of the domain registry.
    """

    def __init__(self):
        super().__init__()
        self.module_id = "domain_index_core"
        self.capabilities = [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION
        ]
        self.dependencies = []
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Load domain registry
        self.domain_registry = self._load_domain_registry()
        self.domain_cache: Dict[str, DomainInfo] = {}
        self.relationship_graph: Dict[str, Set[str]] = {}
        
        # Build index
        self._build_domain_index()
        self._build_relationship_graph()
        
        self.logger.info('🔍 Domain Index System initialized - ready for intelligent queries!')

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': self.module_id,
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': self.dependencies,
            'capabilities': [cap.value for cap in self.capabilities],
            'total_domains': len(self.domain_cache),
            'registry_loaded': bool(self.domain_registry)
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=100.0,
            issues=[],
            last_check=datetime.now()
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            'success': True,
            'degraded_capabilities': [],
            'remaining_capabilities': [cap.value for cap in self.capabilities]
        }

    def query_domain(self, domain_name: str) -> Optional[DomainInfo]:
        """Query domain information by name."""
        return self.domain_cache.get(domain_name)

    def search_domains_by_capability(self, capability: str) -> QueryResult:
        """Search domains by capability or pattern."""
        start_time = datetime.now()
        matching_domains = []
        relevance_scores = {}
        
        for domain_name, domain_info in self.domain_cache.items():
            score = self._calculate_relevance_score(domain_info, capability)
            if score > 0.1:  # Threshold for relevance
                matching_domains.append(domain_info)
                relevance_scores[domain_name] = score
        
        # Sort by relevance score
        matching_domains.sort(key=lambda d: relevance_scores[d.name], reverse=True)
        
        query_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return QueryResult(
            domains=matching_domains,
            total_count=len(matching_domains),
            query_time_ms=query_time,
            relevance_scores=relevance_scores
        )

    def get_domain_relationships(self, domain_name: str) -> Dict[str, Any]:
        """Get domain relationships and dependency analysis."""
        dependencies = list(self.relationship_graph.get(domain_name, set()))
        
        # Find dependents (domains that depend on this one)
        dependents = []
        for dep_domain, deps in self.relationship_graph.items():
            if domain_name in deps:
                dependents.append(dep_domain)
        
        # Calculate impact score
        impact_score = len(dependents) + len(dependencies) * 0.5
        
        return {
            'domain': domain_name,
            'dependencies': dependencies,
            'dependents': dependents,
            'impact_score': impact_score
        }

    def analyze_cross_domain_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across domains."""
        pattern_frequency = {}
        common_patterns = []
        
        # Count pattern frequency across all domains
        for domain_info in self.domain_cache.values():
            for pattern in domain_info.patterns:
                pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
        
        # Find common patterns (used by 3+ domains)
        for pattern, count in pattern_frequency.items():
            if count >= 3:
                common_patterns.append({
                    'pattern': pattern,
                    'frequency': count,
                    'domains': [d.name for d in self.domain_cache.values() if pattern in d.patterns]
                })
        
        return {
            'total_patterns': len(pattern_frequency),
            'common_patterns': common_patterns,
            'pattern_diversity': len(pattern_frequency) / max(1, len(self.domain_cache))
        }

    def perform_health_check(self) -> Dict[str, Any]:
        """Perform domain health check."""
        health_report = {
            'total_domains': len(self.domain_cache),
            'healthy_domains': 0,
            'warning_domains': 0,
            'error_domains': 0
        }
        
        # Check domain health
        for domain_info in self.domain_cache.values():
            if domain_info.health == DomainHealth.HEALTHY:
                health_report['healthy_domains'] += 1
            elif domain_info.health == DomainHealth.WARNING:
                health_report['warning_domains'] += 1
            else:
                health_report['error_domains'] += 1
        
        return health_report

    def _load_domain_registry(self) -> Dict[str, Any]:
        """Load the project domain registry."""
        registry_path = Path("project_model_registry.json")
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load domain registry: {e}")
        
        return {}

    def _build_domain_index(self):
        """Build the domain index from registry."""
        if not self.domain_registry.get("domain_architecture"):
            return
        
        # Extract domains from each category
        for category_name, category_info in self.domain_registry["domain_architecture"].items():
            if isinstance(category_info, dict) and "domains" in category_info:
                domain_type = self._determine_domain_type(category_name)
                
                for domain_name in category_info["domains"]:
                    domain_info = DomainInfo(
                        name=domain_name,
                        type=domain_type,
                        description=category_info.get("description", ""),
                        patterns=category_info.get("patterns", []),
                        dependencies=category_info.get("dependencies", []),
                        tools=category_info.get("tools", []),
                        requirements=category_info.get("requirements", []),
                        health=DomainHealth.HEALTHY,
                        extraction_potential=self._assess_extraction_potential(domain_name, category_info)
                    )
                    
                    self.domain_cache[domain_name] = domain_info

    def _build_relationship_graph(self):
        """Build relationship graph from domain dependencies."""
        for domain_name, domain_info in self.domain_cache.items():
            self.relationship_graph[domain_name] = set(domain_info.dependencies)

    def _determine_domain_type(self, category_name: str) -> DomainType:
        """Determine domain type from category name."""
        if "demo_core" in category_name:
            return DomainType.DEMO_CORE
        elif "demo_tools" in category_name:
            return DomainType.DEMO_TOOLS
        elif "demo_infrastructure" in category_name:
            return DomainType.DEMO_INFRASTRUCTURE
        elif "demo_validation" in category_name:
            return DomainType.DEMO_VALIDATION
        elif "demo_documentation" in category_name:
            return DomainType.DEMO_DOCUMENTATION
        elif "beast_mode" in category_name:
            return DomainType.BEAST_MODE
        elif "ghostbusters" in category_name:
            return DomainType.GHOSTBUSTERS
        else:
            return DomainType.UNKNOWN

    def _assess_extraction_potential(self, domain_name: str, category_info: Dict[str, Any]) -> bool:
        """Assess if domain has PyPI extraction potential."""
        tools = category_info.get("tools", [])
        patterns = category_info.get("patterns", [])
        return len(tools) >= 2 and len(patterns) >= 2

    def _calculate_relevance_score(self, domain_info: DomainInfo, capability: str) -> float:
        """Calculate relevance score for capability search."""
        score = 0.0
        capability_lower = capability.lower()
        
        # Check name match
        if capability_lower in domain_info.name.lower():
            score += 0.8
        
        # Check description match
        if capability_lower in domain_info.description.lower():
            score += 0.6
        
        # Check patterns match
        for pattern in domain_info.patterns:
            if capability_lower in pattern.lower():
                score += 0.4
        
        return min(score, 1.0)

    def suggest_domain_assignment(self, file_path: str) -> List[Tuple[str, float]]:
        """Suggest domain assignment for a new file."""
        suggestions = []
        
        # Analyze file path and content patterns
        for domain_name, domain_info in self.domain_cache.items():
            score = self._calculate_assignment_score(file_path, domain_info)
            if score > 0.1:
                suggestions.append((domain_name, score))
        
        # Sort by score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return suggestions

    def _calculate_assignment_score(self, file_path: str, domain_info: DomainInfo) -> float:
        """Calculate domain assignment score for a file."""
        score = 0.0
        
        # Check if path matches domain name
        if domain_info.name.lower() in str(file_path).lower():
            score += 0.8
        
        # Check if path matches domain type
        if domain_info.type.value in str(file_path).lower():
            score += 0.6
        
        return min(score, 1.0)

    def get_index_summary(self) -> Dict[str, Any]:
        """Get summary of the domain index."""
        domain_types = {}
        for domain_info in self.domain_cache.values():
            domain_type = domain_info.type.value
            domain_types[domain_type] = domain_types.get(domain_type, 0) + 1
        
        return {
            'total_domains': len(self.domain_cache),
            'domain_types': domain_types,
            'extraction_candidates': len([d for d in self.domain_cache.values() if d.extraction_potential]),
            'total_relationships': sum(len(deps) for deps in self.relationship_graph.values()),
            'index_built_at': datetime.now().isoformat()
        }