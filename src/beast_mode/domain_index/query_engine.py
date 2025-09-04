"""
Domain Query Engine

This module provides intelligent querying capabilities for domain information,
including pattern matching, content-based search, and natural language processing.
"""

import re
import time
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from pathlib import Path

from .base import CachedComponent
from .interfaces import QueryEngineInterface
from .models import Domain, QueryResult
from .exceptions import QueryEngineError, InvalidQueryError, QueryTimeoutError
from .config import get_config


class DomainQueryEngine(CachedComponent, QueryEngineInterface):
    """
    Intelligent query engine for domain information
    
    Provides comprehensive querying capabilities including:
    - Pattern-based search with wildcards and regex
    - Content-based search using indicators
    - Capability and functionality search
    - Relationship queries
    - Natural language query processing
    """
    
    def __init__(self, registry_manager=None, config: Optional[Dict[str, Any]] = None):
        super().__init__("domain_query_engine", config)
        
        # Configuration
        self.config_obj = get_config()
        self.query_timeout = self.config_obj.get("query_timeout_seconds", 30)
        self.max_results = self.config_obj.get("max_query_results", 100)
        self.suggestion_limit = self.config_obj.get("query_suggestion_limit", 5)
        
        # Registry manager (will be injected)
        self.registry_manager = registry_manager
        
        # Query statistics
        self.query_count = 0
        self.total_query_time = 0.0
        self.pattern_searches = 0
        self.content_searches = 0
        self.nl_queries = 0
        
        # Search indexes (will be built on first use)
        self._pattern_index = {}
        self._content_index = {}
        self._capability_index = {}
        self._index_built = False
        
        self.logger.info("Initialized DomainQueryEngine")
    
    def set_registry_manager(self, registry_manager):
        """Set the registry manager (dependency injection)"""
        self.registry_manager = registry_manager
        self._index_built = False  # Rebuild indexes when registry changes
    
    def _ensure_indexes_built(self):
        """Ensure search indexes are built"""
        if not self._index_built and self.registry_manager:
            self._build_search_indexes()
    
    def _build_search_indexes(self):
        """Build search indexes for efficient querying"""
        with self._time_operation("build_indexes"):
            try:
                domains = self.registry_manager.get_all_domains()
                
                # Clear existing indexes
                self._pattern_index = {}
                self._content_index = {}
                self._capability_index = {}
                
                # Build pattern index
                for domain_name, domain in domains.items():
                    # Index file patterns
                    for pattern in domain.patterns:
                        pattern_key = pattern.lower()
                        if pattern_key not in self._pattern_index:
                            self._pattern_index[pattern_key] = set()
                        self._pattern_index[pattern_key].add(domain_name)
                    
                    # Index content indicators
                    for indicator in domain.content_indicators:
                        indicator_key = indicator.lower()
                        if indicator_key not in self._content_index:
                            self._content_index[indicator_key] = set()
                        self._content_index[indicator_key].add(domain_name)
                    
                    # Index capabilities (from requirements and tools)
                    capabilities = domain.requirements + [domain.tools.linter, domain.tools.formatter]
                    for capability in capabilities:
                        if capability:
                            cap_key = capability.lower()
                            if cap_key not in self._capability_index:
                                self._capability_index[cap_key] = set()
                            self._capability_index[cap_key].add(domain_name)
                
                self._index_built = True
                self.logger.info(f"Built search indexes for {len(domains)} domains")
                
            except Exception as e:
                self._handle_error(e, "build_indexes")
    
    def natural_language_query(self, query: str) -> QueryResult:
        """Process natural language queries about domains"""
        with self._time_operation("natural_language_query"):
            start_time = time.time()
            self.nl_queries += 1
            
            try:
                # Simple natural language processing
                query_lower = query.lower().strip()
                
                # Extract keywords and intent
                keywords = self._extract_keywords(query_lower)
                intent = self._determine_intent(query_lower)
                
                # Route to appropriate search method
                if intent == "pattern_search":
                    domains = self._search_by_patterns(keywords)
                elif intent == "content_search":
                    domains = self._search_by_content(keywords)
                elif intent == "capability_search":
                    domains = self._search_by_capabilities(keywords)
                else:
                    # Default to combined search
                    domains = self._combined_search(keywords)
                
                # Generate suggestions
                suggestions = self._generate_query_suggestions(query_lower, keywords)
                
                # Calculate relevance scores
                relevance_scores = self._calculate_relevance_scores(domains, keywords)
                
                # Sort by relevance
                domains.sort(key=lambda d: relevance_scores.get(d.name, 0.0), reverse=True)
                
                # Limit results
                domains = domains[:self.max_results]
                
                query_time = (time.time() - start_time) * 1000
                
                return QueryResult(
                    domains=domains,
                    total_count=len(domains),
                    query_time_ms=query_time,
                    suggestions=suggestions,
                    filters_applied={"intent": intent, "keywords": keywords},
                    relevance_scores=relevance_scores
                )
                
            except Exception as e:
                self._handle_error(e, "natural_language_query")
                raise QueryEngineError(f"Natural language query failed: {str(e)}")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from natural language query"""
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Simple tokenization
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _determine_intent(self, query: str) -> str:
        """Determine the intent of the natural language query"""
        if any(word in query for word in ["pattern", "file", "path", "*.py", "src/"]):
            return "pattern_search"
        elif any(word in query for word in ["contains", "content", "indicator", "includes"]):
            return "content_search"
        elif any(word in query for word in ["tool", "capability", "can", "does", "supports", "run"]):
            return "capability_search"
        else:
            return "general_search"
    
    def pattern_search(self, pattern: str) -> List[Domain]:
        """Search domains by file patterns"""
        with self._time_operation("pattern_search"):
            self.pattern_searches += 1
            self._ensure_indexes_built()
            
            try:
                matching_domains = set()
                pattern_lower = pattern.lower()
                
                # Direct pattern matching
                if pattern_lower in self._pattern_index:
                    matching_domains.update(self._pattern_index[pattern_lower])
                
                # Wildcard and regex pattern matching
                for indexed_pattern, domain_names in self._pattern_index.items():
                    if self._pattern_matches(pattern_lower, indexed_pattern):
                        matching_domains.update(domain_names)
                
                # Get domain objects
                domains = []
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    for domain_name in matching_domains:
                        if domain_name in all_domains:
                            domains.append(all_domains[domain_name])
                
                return domains
                
            except Exception as e:
                self._handle_error(e, "pattern_search")
                return []
    
    def _pattern_matches(self, search_pattern: str, indexed_pattern: str) -> bool:
        """Check if search pattern matches indexed pattern"""
        # Simple wildcard matching
        if "*" in search_pattern:
            regex_pattern = search_pattern.replace("*", ".*")
            return bool(re.search(regex_pattern, indexed_pattern))
        
        # Substring matching
        return search_pattern in indexed_pattern
    
    def content_search(self, content_indicator: str) -> List[Domain]:
        """Search domains by content indicators"""
        with self._time_operation("content_search"):
            self.content_searches += 1
            self._ensure_indexes_built()
            
            try:
                matching_domains = set()
                indicator_lower = content_indicator.lower()
                
                # Direct indicator matching
                if indicator_lower in self._content_index:
                    matching_domains.update(self._content_index[indicator_lower])
                
                # Partial matching
                for indexed_indicator, domain_names in self._content_index.items():
                    if indicator_lower in indexed_indicator or indexed_indicator in indicator_lower:
                        matching_domains.update(domain_names)
                
                # Get domain objects
                domains = []
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    for domain_name in matching_domains:
                        if domain_name in all_domains:
                            domains.append(all_domains[domain_name])
                
                return domains
                
            except Exception as e:
                self._handle_error(e, "content_search")
                return []
    
    def capability_search(self, capability: str) -> List[Domain]:
        """Find domains by capability or functionality"""
        with self._time_operation("capability_search"):
            self._ensure_indexes_built()
            
            try:
                matching_domains = set()
                capability_lower = capability.lower()
                
                # Direct capability matching
                if capability_lower in self._capability_index:
                    matching_domains.update(self._capability_index[capability_lower])
                
                # Partial matching
                for indexed_capability, domain_names in self._capability_index.items():
                    if capability_lower in indexed_capability:
                        matching_domains.update(domain_names)
                
                # Get domain objects
                domains = []
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    for domain_name in matching_domains:
                        if domain_name in all_domains:
                            domains.append(all_domains[domain_name])
                
                return domains
                
            except Exception as e:
                self._handle_error(e, "capability_search")
                return []
    
    def relationship_query(self, domain: str, relationship_type: str) -> List[Domain]:
        """Query domain relationships"""
        with self._time_operation("relationship_query"):
            try:
                if not self.registry_manager:
                    return []
                
                target_domain = self.registry_manager.get_domain(domain)
                all_domains = self.registry_manager.get_all_domains()
                
                related_domains = []
                
                if relationship_type == "dependencies":
                    # Get domains this domain depends on
                    for dep_name in target_domain.dependencies:
                        if dep_name in all_domains:
                            related_domains.append(all_domains[dep_name])
                
                elif relationship_type == "dependents":
                    # Get domains that depend on this domain
                    for domain_name, domain_obj in all_domains.items():
                        if domain in domain_obj.dependencies:
                            related_domains.append(domain_obj)
                
                elif relationship_type == "similar":
                    # Get domains with similar patterns or content
                    target_patterns = set(target_domain.patterns)
                    target_indicators = set(target_domain.content_indicators)
                    
                    for domain_name, domain_obj in all_domains.items():
                        if domain_name == domain:
                            continue
                        
                        # Calculate similarity based on patterns and indicators
                        pattern_overlap = len(target_patterns.intersection(set(domain_obj.patterns)))
                        indicator_overlap = len(target_indicators.intersection(set(domain_obj.content_indicators)))
                        
                        if pattern_overlap > 0 or indicator_overlap > 0:
                            related_domains.append(domain_obj)
                
                return related_domains
                
            except Exception as e:
                self._handle_error(e, "relationship_query")
                return []
    
    def complex_query(self, query_spec: Dict[str, Any]) -> QueryResult:
        """Execute complex structured queries"""
        with self._time_operation("complex_query"):
            start_time = time.time()
            
            try:
                # Extract query components
                patterns = query_spec.get("patterns", [])
                content_indicators = query_spec.get("content_indicators", [])
                capabilities = query_spec.get("capabilities", [])
                filters = query_spec.get("filters", {})
                
                # Combine search results
                all_results = set()
                
                # Pattern search
                for pattern in patterns:
                    domains = self.pattern_search(pattern)
                    all_results.update(d.name for d in domains)
                
                # Content search
                for indicator in content_indicators:
                    domains = self.content_search(indicator)
                    all_results.update(d.name for d in domains)
                
                # Capability search
                for capability in capabilities:
                    domains = self.capability_search(capability)
                    all_results.update(d.name for d in domains)
                
                # Get domain objects and apply filters
                final_domains = []
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    for domain_name in all_results:
                        if domain_name in all_domains:
                            domain = all_domains[domain_name]
                            if self._apply_query_filters(domain, filters):
                                final_domains.append(domain)
                
                query_time = (time.time() - start_time) * 1000
                
                return QueryResult(
                    domains=final_domains[:self.max_results],
                    total_count=len(final_domains),
                    query_time_ms=query_time,
                    filters_applied=filters
                )
                
            except Exception as e:
                self._handle_error(e, "complex_query")
                raise QueryEngineError(f"Complex query failed: {str(e)}")
    
    def _apply_query_filters(self, domain: Domain, filters: Dict[str, Any]) -> bool:
        """Apply filters to query results"""
        for filter_key, filter_value in filters.items():
            if filter_key == "category":
                if domain.metadata.demo_role != filter_value:
                    return False
            elif filter_key == "status":
                if domain.metadata.status != filter_value:
                    return False
            elif filter_key == "min_complexity":
                # Will be implemented when we have complexity metrics
                pass
        
        return True
    
    def suggest_queries(self, partial_query: str) -> List[str]:
        """Suggest query completions"""
        with self._time_operation("suggest_queries"):
            try:
                suggestions = []
                partial_lower = partial_query.lower()
                
                # Suggest based on indexed patterns
                for pattern in self._pattern_index.keys():
                    if pattern.startswith(partial_lower):
                        suggestions.append(f"pattern:{pattern}")
                
                # Suggest based on content indicators
                for indicator in self._content_index.keys():
                    if indicator.startswith(partial_lower):
                        suggestions.append(f"content:{indicator}")
                
                # Suggest based on capabilities
                for capability in self._capability_index.keys():
                    if capability.startswith(partial_lower):
                        suggestions.append(f"capability:{capability}")
                
                # Common query patterns
                common_queries = [
                    "domains with testing",
                    "domains in core category",
                    "domains with *.py patterns",
                    "domains that depend on",
                    "similar domains to"
                ]
                
                for query in common_queries:
                    if query.startswith(partial_lower):
                        suggestions.append(query)
                
                return suggestions[:self.suggestion_limit]
                
            except Exception as e:
                self._handle_error(e, "suggest_queries")
                return []
    
    def _search_by_patterns(self, keywords: List[str]) -> List[Domain]:
        """Search domains by pattern keywords"""
        results = []
        seen_names = set()
        for keyword in keywords:
            for domain in self.pattern_search(keyword):
                if domain.name not in seen_names:
                    results.append(domain)
                    seen_names.add(domain.name)
        return results
    
    def _search_by_content(self, keywords: List[str]) -> List[Domain]:
        """Search domains by content keywords"""
        results = []
        seen_names = set()
        for keyword in keywords:
            for domain in self.content_search(keyword):
                if domain.name not in seen_names:
                    results.append(domain)
                    seen_names.add(domain.name)
        return results
    
    def _search_by_capabilities(self, keywords: List[str]) -> List[Domain]:
        """Search domains by capability keywords"""
        results = []
        seen_names = set()
        for keyword in keywords:
            for domain in self.capability_search(keyword):
                if domain.name not in seen_names:
                    results.append(domain)
                    seen_names.add(domain.name)
        return results
    
    def _combined_search(self, keywords: List[str]) -> List[Domain]:
        """Perform combined search across all indexes"""
        all_results = set()
        
        for keyword in keywords:
            # Search patterns
            pattern_results = self.pattern_search(keyword)
            all_results.update(d.name for d in pattern_results)
            
            # Search content
            content_results = self.content_search(keyword)
            all_results.update(d.name for d in content_results)
            
            # Search capabilities
            capability_results = self.capability_search(keyword)
            all_results.update(d.name for d in capability_results)
        
        # Convert back to domain objects
        domains = []
        if self.registry_manager:
            all_domains = self.registry_manager.get_all_domains()
            for domain_name in all_results:
                if domain_name in all_domains:
                    domains.append(all_domains[domain_name])
        
        return domains
    
    def _calculate_relevance_scores(self, domains: List[Domain], keywords: List[str]) -> Dict[str, float]:
        """Calculate relevance scores for search results"""
        scores = {}
        
        for domain in domains:
            score = 0.0
            
            # Score based on keyword matches in name (highest weight)
            for keyword in keywords:
                if keyword.lower() in domain.name.lower():
                    score += 3.0
            
            # Score based on keyword matches in description
            for keyword in keywords:
                if keyword.lower() in domain.description.lower():
                    score += 2.0
            
            # Score based on pattern matches
            for keyword in keywords:
                for pattern in domain.patterns:
                    if keyword.lower() in pattern.lower():
                        score += 1.0
            
            # Score based on content indicator matches
            for keyword in keywords:
                for indicator in domain.content_indicators:
                    if keyword.lower() in indicator.lower():
                        score += 1.5
            
            scores[domain.name] = score
        
        return scores
    
    def _generate_query_suggestions(self, query: str, keywords: List[str]) -> List[str]:
        """Generate query suggestions based on current query"""
        suggestions = []
        
        # Suggest refinements
        if len(keywords) == 1:
            suggestions.append(f"{query} in core category")
            suggestions.append(f"{query} with dependencies")
        
        # Suggest related searches
        suggestions.append(f"domains similar to {keywords[0] if keywords else 'current'}")
        suggestions.append(f"dependencies of {keywords[0] if keywords else 'domains'}")
        
        return suggestions[:self.suggestion_limit]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query engine statistics"""
        return {
            "total_queries": self.query_count,
            "pattern_searches": self.pattern_searches,
            "content_searches": self.content_searches,
            "natural_language_queries": self.nl_queries,
            "average_query_time_ms": self.total_query_time / max(self.query_count, 1),
            "indexes_built": self._index_built,
            "pattern_index_size": len(self._pattern_index),
            "content_index_size": len(self._content_index),
            "capability_index_size": len(self._capability_index),
            "cache_stats": self.get_cache_stats()
        }