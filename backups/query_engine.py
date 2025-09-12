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
        """Process natural language queries about domains with advanced NLP"""
        with self._time_operation("natural_language_query"):
            start_time = time.time()
            self.nl_queries += 1
            
            try:
                # Parse the natural language query into structured components
                parsed_query = self._parse_natural_language_query(query)
                
                # Execute the structured query
                domains = self._execute_parsed_query(parsed_query)
                
                # Apply filters from the parsed query
                if parsed_query.get("filters"):
                    domains = self._apply_parsed_filters(domains, parsed_query["filters"])
                
                # Generate intelligent suggestions
                suggestions = self._generate_intelligent_suggestions(query, parsed_query, domains)
                
                # Calculate enhanced relevance scores
                relevance_scores = self._calculate_enhanced_relevance_scores(domains, parsed_query)
                
                # Sort by relevance with tie-breaking
                domains.sort(key=lambda d: (
                    relevance_scores.get(d.name, 0.0),
                    d.name  # Tie-breaker for consistent ordering
                ), reverse=True)
                
                # Apply result ranking and filtering
                domains = self._rank_and_filter_results(domains, parsed_query)
                
                # Limit results
                domains = domains[:self.max_results]
                
                query_time = (time.time() - start_time) * 1000
                
                return QueryResult(
                    domains=domains,
                    total_count=len(domains),
                    query_time_ms=query_time,
                    suggestions=suggestions,
                    filters_applied={
                        "intent": parsed_query.get("intent", "unknown"),
                        "keywords": parsed_query.get("keywords", []),
                        "entities": parsed_query.get("entities", {}),
                        "filters": parsed_query.get("filters", {}),
                        "query_type": parsed_query.get("query_type", "general")
                    },
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
        """Find domains by capability or functionality with advanced matching"""
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
                
                # Advanced capability matching using domain requirements and tools
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    
                    for domain_name, domain in all_domains.items():
                        # Check requirements for capability matches
                        for requirement in domain.requirements:
                            if self._capability_matches(capability_lower, requirement.lower()):
                                matching_domains.add(domain_name)
                        
                        # Check tools for capability matches
                        tool_capabilities = [
                            domain.tools.linter,
                            domain.tools.formatter,
                            domain.tools.validator
                        ]
                        tool_capabilities.extend(domain.tools.custom_tools.values())
                        
                        for tool in tool_capabilities:
                            if tool and self._capability_matches(capability_lower, tool.lower()):
                                matching_domains.add(domain_name)
                        
                        # Check content indicators for functional capabilities
                        for indicator in domain.content_indicators:
                            if self._capability_matches(capability_lower, indicator.lower()):
                                matching_domains.add(domain_name)
                
                # Get domain objects and calculate relevance scores
                domains = []
                if self.registry_manager:
                    all_domains = self.registry_manager.get_all_domains()
                    for domain_name in matching_domains:
                        if domain_name in all_domains:
                            domains.append(all_domains[domain_name])
                
                # Sort by capability relevance
                domains.sort(key=lambda d: self._calculate_capability_relevance(d, capability_lower), reverse=True)
                
                return domains
                
            except Exception as e:
                self._handle_error(e, "capability_search")
                return []
    
    def _capability_matches(self, search_capability: str, target_capability: str) -> bool:
        """Check if a search capability matches a target capability"""
        # Exact match
        if search_capability == target_capability:
            return True
        
        # Substring match
        if search_capability in target_capability or target_capability in search_capability:
            return True
        
        # Semantic matching for common capability synonyms
        capability_synonyms = {
            "test": ["testing", "pytest", "unittest", "test_", "_test"],
            "lint": ["linting", "pylint", "flake8", "ruff"],
            "format": ["formatting", "black", "autopep8", "yapf"],
            "type": ["typing", "mypy", "type_check", "annotations"],
            "doc": ["documentation", "docs", "sphinx", "readme"],
            "build": ["building", "setup", "packaging", "wheel"],
            "deploy": ["deployment", "docker", "kubernetes", "helm"],
            "monitor": ["monitoring", "logging", "metrics", "observability"],
            "security": ["sec", "auth", "authentication", "authorization"],
            "api": ["rest", "graphql", "endpoint", "service"],
            "data": ["database", "db", "sql", "nosql", "storage"],
            "ml": ["machine_learning", "ai", "model", "training"],
            "web": ["http", "server", "client", "browser"],
            "cli": ["command", "terminal", "console", "script"]
        }
        
        for base_capability, synonyms in capability_synonyms.items():
            if search_capability == base_capability or search_capability in synonyms:
                if target_capability == base_capability or any(syn in target_capability for syn in synonyms):
                    return True
            if target_capability == base_capability or target_capability in synonyms:
                if search_capability == base_capability or any(syn in search_capability for syn in synonyms):
                    return True
        
        return False
    
    def _calculate_capability_relevance(self, domain: Domain, capability: str) -> float:
        """Calculate how relevant a domain is for a given capability"""
        relevance_score = 0.0
        
        # Check domain name for capability match (highest weight)
        if capability in domain.name.lower():
            relevance_score += 3.0
        
        # Check requirements for capability matches
        for requirement in domain.requirements:
            if self._capability_matches(capability, requirement.lower()):
                relevance_score += 2.0
        
        # Check tools for capability matches
        tool_capabilities = [
            domain.tools.linter,
            domain.tools.formatter,
            domain.tools.validator
        ]
        tool_capabilities.extend(domain.tools.custom_tools.values())
        
        for tool in tool_capabilities:
            if tool and self._capability_matches(capability, tool.lower()):
                relevance_score += 1.5
        
        # Check content indicators
        for indicator in domain.content_indicators:
            if self._capability_matches(capability, indicator.lower()):
                relevance_score += 1.0
        
        # Check patterns for capability-related file types
        for pattern in domain.patterns:
            if self._pattern_suggests_capability(pattern, capability):
                relevance_score += 0.5
        
        return relevance_score
    
    def _pattern_suggests_capability(self, pattern: str, capability: str) -> bool:
        """Check if a file pattern suggests a particular capability"""
        pattern_lower = pattern.lower()
        
        capability_patterns = {
            "test": ["test_", "_test", "tests/", "/test/", "*.test.*"],
            "doc": ["docs/", "/doc/", "*.md", "*.rst", "readme"],
            "config": ["config", "settings", "*.yaml", "*.yml", "*.json", "*.toml"],
            "script": ["scripts/", "*.sh", "*.py", "bin/"],
            "web": ["*.html", "*.css", "*.js", "templates/", "static/"],
            "data": ["*.sql", "*.db", "data/", "migrations/"],
            "api": ["api/", "endpoints/", "routes/", "handlers/"],
            "cli": ["cli/", "commands/", "*.py"]
        }
        
        if capability in capability_patterns:
            return any(cap_pattern in pattern_lower for cap_pattern in capability_patterns[capability])
        
        return False
    
    def relationship_query(self, domain: str, relationship_type: str) -> List[Domain]:
        """Query domain relationships with advanced analysis"""
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
                
                elif relationship_type == "transitive_dependencies":
                    # Get all transitive dependencies using graph traversal
                    related_domains = self._get_transitive_dependencies(domain, all_domains)
                
                elif relationship_type == "transitive_dependents":
                    # Get all domains that transitively depend on this domain
                    related_domains = self._get_transitive_dependents(domain, all_domains)
                
                elif relationship_type == "similar":
                    # Get domains with similar patterns or content
                    related_domains = self._find_similar_domains(target_domain, all_domains)
                
                elif relationship_type == "circular":
                    # Find circular dependency chains involving this domain
                    circular_chains = self._detect_circular_dependencies(domain, all_domains)
                    # Flatten the chains and get unique domains
                    circular_domain_names = set()
                    for chain in circular_chains:
                        circular_domain_names.update(chain)
                    circular_domain_names.discard(domain)  # Remove self
                    
                    for domain_name in circular_domain_names:
                        if domain_name in all_domains:
                            related_domains.append(all_domains[domain_name])
                
                elif relationship_type == "coupling_high":
                    # Find domains with high coupling to this domain
                    related_domains = self._find_high_coupling_domains(target_domain, all_domains)
                
                elif relationship_type == "extraction_related":
                    # Find domains that would be affected by extracting this domain
                    related_domains = self._find_extraction_related_domains(target_domain, all_domains)
                
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
        """Suggest query completions with advanced NLP"""
        with self._time_operation("suggest_queries"):
            try:
                suggestions = []
                partial_lower = partial_query.lower().strip()
                
                # Handle empty or very short queries
                if len(partial_lower) < 2:
                    return self._get_popular_query_templates()
                
                # Parse partial query to understand intent
                partial_parsed = self._parse_partial_query(partial_lower)
                
                # Generate context-aware suggestions
                suggestions.extend(self._generate_contextual_suggestions(partial_lower, partial_parsed))
                
                # Generate completion suggestions
                suggestions.extend(self._generate_completion_suggestions(partial_lower))
                
                # Generate template-based suggestions
                suggestions.extend(self._generate_template_suggestions(partial_lower, partial_parsed))
                
                # Remove duplicates while preserving order
                seen = set()
                unique_suggestions = []
                for suggestion in suggestions:
                    if suggestion not in seen:
                        seen.add(suggestion)
                        unique_suggestions.append(suggestion)
                
                return unique_suggestions[:self.suggestion_limit]
                
            except Exception as e:
                self._handle_error(e, "suggest_queries")
                return []
    
    def _parse_partial_query(self, partial_query: str) -> Dict[str, Any]:
        """Parse partial query to understand user intent"""
        partial_info = {
            "tokens": partial_query.split(),
            "last_token": partial_query.split()[-1] if partial_query.split() else "",
            "intent_indicators": [],
            "entity_hints": [],
            "incomplete_type": "unknown"
        }
        
        # Detect intent indicators
        intent_words = {
            "pattern": ["pattern", "file", "path", "*.py", "src/"],
            "content": ["contains", "content", "indicator", "has"],
            "capability": ["can", "tool", "capability", "run", "support"],
            "relationship": ["depend", "similar", "related", "connect"],
            "analysis": ["analyze", "metrics", "health", "report"]
        }
        
        for intent, indicators in intent_words.items():
            if any(indicator in partial_query for indicator in indicators):
                partial_info["intent_indicators"].append(intent)
        
        # Detect entity hints
        if "_domain" in partial_query or "domain" in partial_query:
            partial_info["entity_hints"].append("domain_name")
        
        if any(ext in partial_query for ext in [".py", ".js", ".md", ".yaml"]):
            partial_info["entity_hints"].append("file_pattern")
        
        # Determine incompleteness type
        if partial_query.endswith(" "):
            partial_info["incomplete_type"] = "expecting_next_word"
        elif partial_query.split()[-1] if partial_query.split() else "":
            partial_info["incomplete_type"] = "partial_word"
        else:
            partial_info["incomplete_type"] = "empty"
        
        return partial_info
    
    def _generate_contextual_suggestions(self, partial_query: str, partial_info: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on query context"""
        suggestions = []
        
        # Intent-based suggestions
        for intent in partial_info["intent_indicators"]:
            if intent == "pattern":
                suggestions.extend([
                    f"{partial_query} src/**/*.py",
                    f"{partial_query} tests/**/*.py",
                    f"{partial_query} *.yaml"
                ])
            elif intent == "capability":
                suggestions.extend([
                    f"{partial_query} pytest",
                    f"{partial_query} linting",
                    f"{partial_query} formatting"
                ])
            elif intent == "relationship":
                suggestions.extend([
                    f"{partial_query} core_domain",
                    f"{partial_query} test_domain",
                    f"{partial_query} api_domain"
                ])
        
        # Entity-based suggestions
        if "domain_name" in partial_info["entity_hints"]:
            if self.registry_manager:
                all_domains = self.registry_manager.get_all_domains()
                for domain_name in list(all_domains.keys())[:5]:  # Limit to 5
                    if domain_name.lower().startswith(partial_info["last_token"].lower()):
                        suggestions.append(partial_query.rsplit(" ", 1)[0] + f" {domain_name}")
        
        return suggestions
    
    def _generate_completion_suggestions(self, partial_query: str) -> List[str]:
        """Generate word completion suggestions"""
        suggestions = []
        self._ensure_indexes_built()
        
        last_word = partial_query.split()[-1] if partial_query.split() else partial_query
        
        # Complete based on indexed patterns
        for pattern in self._pattern_index.keys():
            if pattern.startswith(last_word.lower()):
                completed_query = partial_query.rsplit(" ", 1)[0] + f" {pattern}" if " " in partial_query else pattern
                suggestions.append(completed_query)
        
        # Complete based on content indicators
        for indicator in self._content_index.keys():
            if indicator.startswith(last_word.lower()):
                completed_query = partial_query.rsplit(" ", 1)[0] + f" {indicator}" if " " in partial_query else indicator
                suggestions.append(completed_query)
        
        # Complete based on capabilities
        for capability in self._capability_index.keys():
            if capability.startswith(last_word.lower()):
                completed_query = partial_query.rsplit(" ", 1)[0] + f" {capability}" if " " in partial_query else capability
                suggestions.append(completed_query)
        
        return suggestions
    
    def _generate_template_suggestions(self, partial_query: str, partial_info: Dict[str, Any]) -> List[str]:
        """Generate template-based suggestions"""
        suggestions = []
        
        # Query templates based on common patterns
        templates = [
            "find domains with {capability}",
            "domains that depend on {domain}",
            "domains similar to {domain}",
            "domains in {category} category",
            "domains with pattern {pattern}",
            "analyze {domain} relationships",
            "show {domain} dependencies",
            "domains with high coupling",
            "domains suitable for extraction",
            "healthy domains in {category}",
            "domains containing {content}",
            "domains that can run {tool}"
        ]
        
        # Fill templates with partial query content
        for template in templates:
            if any(word in partial_query for word in template.split() if word not in ["{capability}", "{domain}", "{category}", "{pattern}", "{content}", "{tool}"]):
                # Try to fill template with detected entities
                filled_template = template
                if "{domain}" in template and self.registry_manager:
                    domains = list(self.registry_manager.get_all_domains().keys())[:3]
                    for domain in domains:
                        suggestions.append(filled_template.replace("{domain}", domain))
                elif "{capability}" in template:
                    capabilities = ["testing", "linting", "formatting", "deployment"]
                    for cap in capabilities:
                        suggestions.append(filled_template.replace("{capability}", cap))
                elif "{category}" in template:
                    categories = ["core", "tools", "infrastructure", "demo"]
                    for cat in categories:
                        suggestions.append(filled_template.replace("{category}", cat))
                else:
                    suggestions.append(filled_template)
        
        return suggestions
    
    def _get_popular_query_templates(self) -> List[str]:
        """Get popular query templates for empty queries"""
        templates = [
            "find domains with testing capabilities",
            "show all core domains",
            "domains that depend on core_domain",
            "domains with *.py patterns",
            "analyze domain relationships",
            "healthy domains",
            "domains suitable for extraction",
            "domains with high complexity",
            "similar domains to test_domain",
            "domains in infrastructure category"
        ]
        return templates[:self.suggestion_limit]
    
    def suggest_query_corrections(self, query: str) -> List[str]:
        """Suggest corrections for potentially misspelled or ambiguous queries"""
        with self._time_operation("suggest_query_corrections"):
            try:
                corrections = []
                query_lower = query.lower()
                
                # Common misspellings and corrections
                corrections_map = {
                    "dependancies": "dependencies",
                    "dependant": "dependent",
                    "similiar": "similar",
                    "analize": "analyze",
                    "analisis": "analysis",
                    "capabilty": "capability",
                    "capabilties": "capabilities",
                    "patern": "pattern",
                    "paterns": "patterns",
                    "domian": "domain",
                    "domians": "domains"
                }
                
                corrected_query = query_lower
                for misspelling, correction in corrections_map.items():
                    if misspelling in corrected_query:
                        corrected_query = corrected_query.replace(misspelling, correction)
                        corrections.append(corrected_query)
                
                # Suggest alternative phrasings
                alternative_phrasings = {
                    "find": ["show", "list", "get", "search for"],
                    "domains with": ["domains that have", "domains containing"],
                    "depends on": ["requires", "needs", "uses"],
                    "similar to": ["like", "resembling", "comparable to"]
                }
                
                for original, alternatives in alternative_phrasings.items():
                    if original in query_lower:
                        for alt in alternatives:
                            alt_query = query_lower.replace(original, alt)
                            corrections.append(alt_query)
                
                # Remove duplicates and limit results
                unique_corrections = list(set(corrections))
                return unique_corrections[:self.suggestion_limit]
                
            except Exception as e:
                self._handle_error(e, "suggest_query_corrections")
                return []
    
    def explain_query_results(self, query: str, results: QueryResult) -> Dict[str, Any]:
        """Explain why certain results were returned for a query"""
        with self._time_operation("explain_query_results"):
            try:
                explanation = {
                    "query_interpretation": {},
                    "matching_strategy": "",
                    "result_ranking": {},
                    "suggestions_for_improvement": []
                }
                
                # Parse the query to understand interpretation
                parsed_query = self._parse_natural_language_query(query)
                explanation["query_interpretation"] = {
                    "detected_intent": parsed_query.get("intent"),
                    "extracted_keywords": parsed_query.get("keywords"),
                    "identified_entities": parsed_query.get("entities"),
                    "query_type": parsed_query.get("query_type")
                }
                
                # Explain matching strategy
                intent = parsed_query.get("intent", "general_search")
                if intent == "pattern_search":
                    explanation["matching_strategy"] = "Searched for domains with matching file patterns"
                elif intent == "capability_search":
                    explanation["matching_strategy"] = "Searched for domains with matching capabilities or tools"
                elif intent == "content_search":
                    explanation["matching_strategy"] = "Searched for domains with matching content indicators"
                else:
                    explanation["matching_strategy"] = "Performed combined search across patterns, content, and capabilities"
                
                # Explain result ranking
                if results.domains:
                    top_domain = results.domains[0]
                    relevance_score = results.relevance_scores.get(top_domain.name, 0.0)
                    explanation["result_ranking"] = {
                        "top_result": top_domain.name,
                        "relevance_score": relevance_score,
                        "ranking_factors": self._explain_relevance_factors(top_domain, parsed_query)
                    }
                
                # Suggest improvements
                if len(results.domains) == 0:
                    explanation["suggestions_for_improvement"] = [
                        "Try using broader search terms",
                        "Check spelling of domain names or capabilities",
                        "Use wildcard patterns like *.py or src/**",
                        "Try searching for related concepts or synonyms"
                    ]
                elif len(results.domains) > 50:
                    explanation["suggestions_for_improvement"] = [
                        "Add more specific filters to narrow results",
                        "Include category filters like 'in core category'",
                        "Add status filters like 'healthy domains'",
                        "Use more specific keywords or patterns"
                    ]
                
                return explanation
                
            except Exception as e:
                self._handle_error(e, "explain_query_results")
                return {}
    
    def _explain_relevance_factors(self, domain: Domain, parsed_query: Dict[str, Any]) -> List[str]:
        """Explain why a domain has high relevance for a query"""
        factors = []
        keywords = parsed_query.get("keywords", [])
        entities = parsed_query.get("entities", {})
        
        # Check name matches
        for keyword in keywords:
            if keyword.lower() in domain.name.lower():
                factors.append(f"Domain name contains '{keyword}'")
        
        # Check description matches
        for keyword in keywords:
            if keyword.lower() in domain.description.lower():
                factors.append(f"Description mentions '{keyword}'")
        
        # Check pattern matches
        for keyword in keywords:
            matching_patterns = [p for p in domain.patterns if keyword.lower() in p.lower()]
            if matching_patterns:
                factors.append(f"File patterns match '{keyword}': {matching_patterns[0]}")
        
        # Check capability matches
        for capability in entities.get("capabilities", []):
            if capability in domain.requirements or capability in [domain.tools.linter, domain.tools.formatter]:
                factors.append(f"Domain supports '{capability}' capability")
        
        return factors
    
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
        """Calculate enhanced relevance scores for search results"""
        scores = {}
        
        for domain in domains:
            score = 0.0
            
            # Score based on keyword matches in name (highest weight)
            for keyword in keywords:
                if keyword.lower() == domain.name.lower():
                    score += 5.0  # Exact name match
                elif keyword.lower() in domain.name.lower():
                    score += 3.0  # Partial name match
            
            # Score based on keyword matches in description
            for keyword in keywords:
                if keyword.lower() in domain.description.lower():
                    # Higher score for exact word matches
                    if f" {keyword.lower()} " in f" {domain.description.lower()} ":
                        score += 2.5
                    else:
                        score += 2.0
            
            # Score based on pattern matches
            for keyword in keywords:
                for pattern in domain.patterns:
                    if keyword.lower() in pattern.lower():
                        score += 1.0
            
            # Score based on content indicator matches
            for keyword in keywords:
                for indicator in domain.content_indicators:
                    if keyword.lower() == indicator.lower():
                        score += 2.0  # Exact indicator match
                    elif keyword.lower() in indicator.lower():
                        score += 1.5  # Partial indicator match
            
            # Score based on requirement matches
            for keyword in keywords:
                for requirement in domain.requirements:
                    if keyword.lower() in requirement.lower():
                        score += 1.2
            
            # Score based on tool matches
            tool_names = [domain.tools.linter, domain.tools.formatter, domain.tools.validator]
            tool_names.extend(domain.tools.custom_tools.values())
            
            for keyword in keywords:
                for tool in tool_names:
                    if tool and keyword.lower() in tool.lower():
                        score += 1.0
            
            # Score based on metadata matches
            for keyword in keywords:
                if keyword.lower() in domain.metadata.demo_role.lower():
                    score += 1.5
                
                for tag in domain.metadata.tags:
                    if keyword.lower() in tag.lower():
                        score += 1.0
            
            # Boost score for domains with better health status
            if domain.health_status:
                if domain.health_status.status.value == "healthy":
                    score *= 1.1
                elif domain.health_status.status.value == "degraded":
                    score *= 0.9
                elif domain.health_status.status.value == "failed":
                    score *= 0.7
            
            # Boost score for extraction candidates
            if domain.metadata.extraction_candidate == "high":
                score *= 1.05
            
            scores[domain.name] = score
        
        return scores
    
    def _parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured components"""
        query_lower = query.lower().strip()
        
        # Initialize parsed query structure
        parsed_query = {
            "original_query": query,
            "keywords": [],
            "entities": {},
            "intent": "general_search",
            "query_type": "search",
            "filters": {},
            "modifiers": [],
            "relationship_type": None,
            "target_domain": None
        }
        
        # Extract entities (domain names, patterns, capabilities)
        entities = self._extract_entities(query_lower)
        parsed_query["entities"] = entities
        
        # Extract keywords (improved version)
        keywords = self._extract_enhanced_keywords(query_lower)
        parsed_query["keywords"] = keywords
        
        # Determine query intent with more sophistication
        intent = self._determine_enhanced_intent(query_lower, entities)
        parsed_query["intent"] = intent
        
        # Determine query type (search, relationship, analysis, etc.)
        query_type = self._determine_query_type(query_lower)
        parsed_query["query_type"] = query_type
        
        # Extract filters and modifiers
        filters = self._extract_query_filters(query_lower)
        parsed_query["filters"] = filters
        
        modifiers = self._extract_query_modifiers(query_lower)
        parsed_query["modifiers"] = modifiers
        
        # Extract relationship information for relationship queries
        if query_type == "relationship":
            relationship_info = self._extract_relationship_info(query_lower, entities)
            parsed_query.update(relationship_info)
        
        return parsed_query
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract named entities from the query"""
        entities = {
            "domain_names": [],
            "patterns": [],
            "capabilities": [],
            "categories": [],
            "tools": []
        }
        
        # Extract potential domain names (words ending with _domain or containing domain)
        domain_patterns = [
            r'\b(\w+_domain)\b',
            r'\b(\w+domain)\b',
            r'\bdomain[_\s]+(\w+)\b'
        ]
        
        for pattern in domain_patterns:
            matches = re.findall(pattern, query)
            entities["domain_names"].extend(matches)
        
        # Extract file patterns
        pattern_indicators = [
            r'(\*\*?/[^/\s]+)',
            r'([^/\s]+\.\w+)',
            r'(src/[^/\s]+)',
            r'(tests?/[^/\s]+)'
        ]
        
        for pattern in pattern_indicators:
            matches = re.findall(pattern, query)
            entities["patterns"].extend(matches)
        
        # Extract capabilities and tools
        capability_keywords = [
            "pytest", "unittest", "test", "testing",
            "pylint", "flake8", "ruff", "lint", "linting",
            "black", "autopep8", "format", "formatting",
            "mypy", "type", "typing", "annotations",
            "docker", "kubernetes", "deploy", "deployment",
            "api", "rest", "graphql", "endpoint",
            "database", "sql", "nosql", "storage"
        ]
        
        for capability in capability_keywords:
            if capability in query:
                entities["capabilities"].append(capability)
        
        # Extract categories
        category_keywords = ["core", "tools", "infrastructure", "demo", "test", "api", "data"]
        for category in category_keywords:
            if category in query:
                entities["categories"].append(category)
        
        return entities
    
    def _extract_enhanced_keywords(self, query: str) -> List[str]:
        """Extract keywords with improved processing"""
        # Enhanced stop words list
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "can", "must", "shall",
            "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
            "me", "him", "her", "us", "them", "my", "your", "his", "her", "its", "our", "their",
            "what", "which", "who", "when", "where", "why", "how",
            "find", "show", "get", "list", "search", "look", "want", "need"
        }
        
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = []
        
        for word in words:
            # Skip stop words and very short words
            if word not in stop_words and len(word) > 2:
                # Include word stems and variations
                keywords.append(word)
                
                # Add common variations
                if word.endswith('ing'):
                    base = word[:-3]
                    if len(base) > 2:
                        keywords.append(base)
                elif word.endswith('ed'):
                    base = word[:-2]
                    if len(base) > 2:
                        keywords.append(base)
        
        return list(set(keywords))  # Remove duplicates
    
    def _determine_enhanced_intent(self, query: str, entities: Dict[str, List[str]]) -> str:
        """Determine query intent with enhanced logic"""
        # Pattern-based intent indicators
        pattern_indicators = ["pattern", "file", "path", "*.py", "src/", "tests/", "**"]
        content_indicators = ["contains", "content", "indicator", "includes", "has"]
        capability_indicators = ["tool", "capability", "can", "does", "supports", "run", "use", "using"]
        relationship_indicators = ["depend", "similar", "related", "connect", "link", "couple"]
        analysis_indicators = ["analyze", "analysis", "metrics", "stats", "health", "report"]
        
        # Count indicators
        pattern_count = sum(1 for indicator in pattern_indicators if indicator in query)
        content_count = sum(1 for indicator in content_indicators if indicator in query)
        capability_count = sum(1 for indicator in capability_indicators if indicator in query)
        relationship_count = sum(1 for indicator in relationship_indicators if indicator in query)
        analysis_count = sum(1 for indicator in analysis_indicators if indicator in query)
        
        # Add entity-based scoring
        if entities["patterns"]:
            pattern_count += 2
        if entities["capabilities"]:
            capability_count += 2
        
        # Determine intent based on highest score
        scores = {
            "pattern_search": pattern_count,
            "content_search": content_count,
            "capability_search": capability_count,
            "relationship_search": relationship_count,
            "analysis_search": analysis_count
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return "general_search"
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query being asked"""
        # Relationship query patterns
        relationship_patterns = [
            r'\b(depend\w*\s+on|depends?\s+on)\b',
            r'\b(similar\s+to|like)\b',
            r'\b(related\s+to|connected\s+to)\b',
            r'\b(circular\s+depend|cycle)\b',
            r'\b(coupling|coupled)\b',
            r'\b(extract\w*\s+impact|extraction)\b'
        ]
        
        for pattern in relationship_patterns:
            if re.search(pattern, query):
                return "relationship"
        
        # Analysis query patterns
        analysis_patterns = [
            r'\b(analy[sz]e|analysis)\b',
            r'\b(metrics?|statistics?|stats)\b',
            r'\b(health|status|report)\b',
            r'\b(complexity|coupling|quality)\b'
        ]
        
        for pattern in analysis_patterns:
            if re.search(pattern, query):
                return "analysis"
        
        # Comparison query patterns
        comparison_patterns = [
            r'\b(compare|comparison|versus|vs)\b',
            r'\b(difference|different|differ)\b',
            r'\b(better|worse|best|worst)\b'
        ]
        
        for pattern in comparison_patterns:
            if re.search(pattern, query):
                return "comparison"
        
        return "search"
    
    def _extract_query_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from the query"""
        filters = {}
        
        # Category filters
        category_patterns = [
            r'\bin\s+(\w+)\s+category\b',
            r'\b(\w+)\s+category\b',
            r'\btype\s+(\w+)\b'
        ]
        
        for pattern in category_patterns:
            matches = re.findall(pattern, query)
            if matches:
                filters["category"] = matches[0]
        
        # Status filters
        status_patterns = [
            r'\b(healthy|degraded|failed)\s+domains?\b',
            r'\bdomains?\s+that\s+are\s+(healthy|degraded|failed)\b'
        ]
        
        for pattern in status_patterns:
            matches = re.findall(pattern, query)
            if matches:
                filters["status"] = matches[0]
        
        # Complexity filters
        complexity_patterns = [
            r'\b(simple|complex|high|low)\s+complexity\b',
            r'\bcomplexity\s+(above|below|over|under)\s+(\d+(?:\.\d+)?)\b'
        ]
        
        for pattern in complexity_patterns:
            matches = re.findall(pattern, query)
            if matches:
                if isinstance(matches[0], tuple):
                    filters["complexity_threshold"] = float(matches[0][1])
                    filters["complexity_operator"] = matches[0][0]
                else:
                    filters["complexity_level"] = matches[0]
        
        return filters
    
    def _extract_query_modifiers(self, query: str) -> List[str]:
        """Extract query modifiers (sorting, limiting, etc.)"""
        modifiers = []
        
        # Sorting modifiers
        if re.search(r'\bsort\w*\s+by\s+(\w+)\b', query):
            sort_field = re.findall(r'\bsort\w*\s+by\s+(\w+)\b', query)[0]
            modifiers.append(f"sort_by:{sort_field}")
        
        # Ordering modifiers
        if "ascending" in query or "asc" in query:
            modifiers.append("order:asc")
        elif "descending" in query or "desc" in query:
            modifiers.append("order:desc")
        
        # Limit modifiers
        limit_matches = re.findall(r'\b(?:top|first|limit)\s+(\d+)\b', query)
        if limit_matches:
            modifiers.append(f"limit:{limit_matches[0]}")
        
        return modifiers
    
    def _extract_relationship_info(self, query: str, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Extract relationship information from query"""
        relationship_info = {
            "relationship_type": None,
            "target_domain": None
        }
        
        # Determine relationship type
        if "depend" in query:
            if "circular" in query or "cycle" in query:
                relationship_info["relationship_type"] = "circular"
            elif "transitive" in query:
                relationship_info["relationship_type"] = "transitive_dependencies"
            else:
                relationship_info["relationship_type"] = "dependencies"
        elif "similar" in query or "like" in query:
            relationship_info["relationship_type"] = "similar"
        elif "coupling" in query or "coupled" in query:
            relationship_info["relationship_type"] = "coupling_high"
        elif "extract" in query:
            relationship_info["relationship_type"] = "extraction_related"
        
        # Extract target domain
        if entities["domain_names"]:
            relationship_info["target_domain"] = entities["domain_names"][0]
        else:
            # Try to extract domain name from context
            domain_matches = re.findall(r'\b(\w+(?:_domain)?)\b', query)
            for match in domain_matches:
                if match.endswith('_domain') or match in ["core", "test", "api", "data"]:
                    relationship_info["target_domain"] = match
                    break
        
        return relationship_info
    
    def _execute_parsed_query(self, parsed_query: Dict[str, Any]) -> List[Domain]:
        """Execute the parsed query"""
        query_type = parsed_query["query_type"]
        intent = parsed_query["intent"]
        keywords = parsed_query["keywords"]
        entities = parsed_query["entities"]
        
        if query_type == "relationship":
            # Handle relationship queries
            target_domain = parsed_query.get("target_domain")
            relationship_type = parsed_query.get("relationship_type")
            
            if target_domain and relationship_type:
                return self.relationship_query(target_domain, relationship_type)
            else:
                # Fallback to general search
                return self._combined_search(keywords)
        
        elif query_type == "analysis":
            # Handle analysis queries - return domains for analysis
            return self._combined_search(keywords)
        
        else:
            # Handle search queries based on intent
            if intent == "pattern_search":
                domains = []
                for pattern in entities.get("patterns", []):
                    domains.extend(self.pattern_search(pattern))
                if not domains:
                    domains = self._search_by_patterns(keywords)
                return domains
            
            elif intent == "content_search":
                return self._search_by_content(keywords)
            
            elif intent == "capability_search":
                domains = []
                for capability in entities.get("capabilities", []):
                    domains.extend(self.capability_search(capability))
                if not domains:
                    domains = self._search_by_capabilities(keywords)
                return domains
            
            else:
                # Default to combined search
                return self._combined_search(keywords)
    
    def _apply_parsed_filters(self, domains: List[Domain], filters: Dict[str, Any]) -> List[Domain]:
        """Apply filters extracted from the parsed query"""
        filtered_domains = []
        
        for domain in domains:
            # Apply category filter
            if "category" in filters:
                if domain.metadata.demo_role != filters["category"]:
                    continue
            
            # Apply status filter
            if "status" in filters:
                if not domain.health_status or domain.health_status.status.value != filters["status"]:
                    continue
            
            # Apply complexity filters
            if "complexity_level" in filters:
                # This would require complexity calculation - placeholder for now
                pass
            
            filtered_domains.append(domain)
        
        return filtered_domains
    
    def _generate_intelligent_suggestions(self, original_query: str, parsed_query: Dict[str, Any], results: List[Domain]) -> List[str]:
        """Generate intelligent query suggestions"""
        suggestions = []
        keywords = parsed_query.get("keywords", [])
        entities = parsed_query.get("entities", {})
        query_type = parsed_query.get("query_type", "search")
        
        # Suggest refinements based on results
        if len(results) == 0:
            suggestions.append(f"Try broader terms: {' OR '.join(keywords[:3])}")
            suggestions.append("Search for similar capabilities or patterns")
            if entities.get("domain_names"):
                suggestions.append(f"Check if domain '{entities['domain_names'][0]}' exists")
        
        elif len(results) > 20:
            suggestions.append("Add more specific filters to narrow results")
            if not parsed_query.get("filters"):
                suggestions.append("Try adding category or status filters")
        
        # Suggest related queries
        if keywords:
            primary_keyword = keywords[0]
            suggestions.append(f"Find domains similar to {primary_keyword}")
            suggestions.append(f"Show dependencies of {primary_keyword} domains")
            suggestions.append(f"Analyze {primary_keyword} domain relationships")
        
        # Suggest query type variations
        if query_type == "search":
            suggestions.append("Try relationship analysis: 'domains that depend on X'")
            suggestions.append("Try capability search: 'domains that can run tests'")
        
        # Suggest entity-based refinements
        if entities.get("capabilities"):
            cap = entities["capabilities"][0]
            suggestions.append(f"Find all domains using {cap}")
        
        if entities.get("patterns"):
            pattern = entities["patterns"][0]
            suggestions.append(f"Find domains with similar patterns to {pattern}")
        
        return suggestions[:self.suggestion_limit]
    
    def _calculate_enhanced_relevance_scores(self, domains: List[Domain], parsed_query: Dict[str, Any]) -> Dict[str, float]:
        """Calculate relevance scores using parsed query information"""
        scores = {}
        keywords = parsed_query.get("keywords", [])
        entities = parsed_query.get("entities", {})
        intent = parsed_query.get("intent", "general_search")
        
        for domain in domains:
            score = 0.0
            
            # Base relevance from keywords
            base_scores = self._calculate_relevance_scores([domain], keywords)
            score += base_scores.get(domain.name, 0.0)
            
            # Boost based on entity matches
            for domain_name in entities.get("domain_names", []):
                if domain_name.lower() in domain.name.lower():
                    score += 5.0
            
            for pattern in entities.get("patterns", []):
                if any(pattern.lower() in p.lower() for p in domain.patterns):
                    score += 3.0
            
            for capability in entities.get("capabilities", []):
                if self._calculate_capability_relevance(domain, capability) > 0:
                    score += 2.0
            
            # Intent-based scoring
            if intent == "capability_search":
                score += self._calculate_capability_relevance(domain, " ".join(keywords))
            elif intent == "pattern_search":
                pattern_matches = sum(1 for keyword in keywords 
                                    for pattern in domain.patterns 
                                    if keyword.lower() in pattern.lower())
                score += pattern_matches * 1.5
            
            scores[domain.name] = score
        
        return scores
    
    def _rank_and_filter_results(self, domains: List[Domain], parsed_query: Dict[str, Any]) -> List[Domain]:
        """Apply ranking and filtering based on query modifiers"""
        modifiers = parsed_query.get("modifiers", [])
        
        # Apply sorting
        sort_field = None
        sort_order = "desc"  # Default to descending
        
        for modifier in modifiers:
            if modifier.startswith("sort_by:"):
                sort_field = modifier.split(":")[1]
            elif modifier.startswith("order:"):
                sort_order = modifier.split(":")[1]
        
        if sort_field:
            if sort_field == "name":
                domains.sort(key=lambda d: d.name, reverse=(sort_order == "desc"))
            elif sort_field == "complexity":
                # Would need complexity calculation
                pass
            elif sort_field == "dependencies":
                domains.sort(key=lambda d: len(d.dependencies), reverse=(sort_order == "desc"))
        
        # Apply limit
        for modifier in modifiers:
            if modifier.startswith("limit:"):
                limit = int(modifier.split(":")[1])
                domains = domains[:limit]
                break
        
        return domains
    
    def _generate_query_suggestions(self, query: str, keywords: List[str]) -> List[str]:
        """Generate query suggestions based on current query (legacy method)"""
        suggestions = []
        
        # Suggest refinements
        if len(keywords) == 1:
            suggestions.append(f"{query} in core category")
            suggestions.append(f"{query} with dependencies")
        
        # Suggest related searches
        suggestions.append(f"domains similar to {keywords[0] if keywords else 'current'}")
        suggestions.append(f"dependencies of {keywords[0] if keywords else 'domains'}")
        
        return suggestions[:self.suggestion_limit]
    
    def _get_transitive_dependencies(self, domain_name: str, all_domains: Dict[str, Domain], visited: Optional[Set[str]] = None) -> List[Domain]:
        """Get all transitive dependencies using depth-first search"""
        if visited is None:
            visited = set()
        
        if domain_name in visited or domain_name not in all_domains:
            return []
        
        visited.add(domain_name)
        transitive_deps = []
        
        domain = all_domains[domain_name]
        for dep_name in domain.dependencies:
            if dep_name in all_domains:
                # Add direct dependency
                transitive_deps.append(all_domains[dep_name])
                # Add transitive dependencies recursively
                transitive_deps.extend(self._get_transitive_dependencies(dep_name, all_domains, visited))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_deps = []
        for dep in transitive_deps:
            if dep.name not in seen:
                seen.add(dep.name)
                unique_deps.append(dep)
        
        return unique_deps
    
    def _get_transitive_dependents(self, domain_name: str, all_domains: Dict[str, Domain]) -> List[Domain]:
        """Get all domains that transitively depend on this domain"""
        transitive_dependents = []
        
        # Build reverse dependency map
        reverse_deps = {}
        for name, domain in all_domains.items():
            for dep in domain.dependencies:
                if dep not in reverse_deps:
                    reverse_deps[dep] = []
                reverse_deps[dep].append(name)
        
        # Use BFS to find all transitive dependents
        visited = set()
        queue = [domain_name]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Add direct dependents
            if current in reverse_deps:
                for dependent in reverse_deps[current]:
                    if dependent not in visited and dependent in all_domains:
                        transitive_dependents.append(all_domains[dependent])
                        queue.append(dependent)
        
        return transitive_dependents
    
    def _find_similar_domains(self, target_domain: Domain, all_domains: Dict[str, Domain]) -> List[Domain]:
        """Find domains similar to the target domain"""
        similar_domains = []
        target_patterns = set(target_domain.patterns)
        target_indicators = set(target_domain.content_indicators)
        target_requirements = set(target_domain.requirements)
        
        for domain_name, domain_obj in all_domains.items():
            if domain_name == target_domain.name:
                continue
            
            # Calculate similarity scores
            pattern_overlap = len(target_patterns.intersection(set(domain_obj.patterns)))
            indicator_overlap = len(target_indicators.intersection(set(domain_obj.content_indicators)))
            requirement_overlap = len(target_requirements.intersection(set(domain_obj.requirements)))
            
            # Calculate similarity score (0.0 to 1.0)
            total_patterns = len(target_patterns.union(set(domain_obj.patterns)))
            total_indicators = len(target_indicators.union(set(domain_obj.content_indicators)))
            total_requirements = len(target_requirements.union(set(domain_obj.requirements)))
            
            pattern_similarity = pattern_overlap / max(total_patterns, 1)
            indicator_similarity = indicator_overlap / max(total_indicators, 1)
            requirement_similarity = requirement_overlap / max(total_requirements, 1)
            
            # Weighted similarity score
            overall_similarity = (
                pattern_similarity * 0.4 +
                indicator_similarity * 0.3 +
                requirement_similarity * 0.3
            )
            
            # Include domains with similarity > 0.2
            if overall_similarity > 0.2:
                similar_domains.append(domain_obj)
        
        # Sort by similarity (highest first)
        similar_domains.sort(key=lambda d: self._calculate_domain_similarity(target_domain, d), reverse=True)
        
        return similar_domains
    
    def _calculate_domain_similarity(self, domain1: Domain, domain2: Domain) -> float:
        """Calculate similarity score between two domains"""
        patterns1 = set(domain1.patterns)
        patterns2 = set(domain2.patterns)
        indicators1 = set(domain1.content_indicators)
        indicators2 = set(domain2.content_indicators)
        requirements1 = set(domain1.requirements)
        requirements2 = set(domain2.requirements)
        
        # Jaccard similarity for each category
        pattern_jaccard = len(patterns1.intersection(patterns2)) / len(patterns1.union(patterns2)) if patterns1.union(patterns2) else 0
        indicator_jaccard = len(indicators1.intersection(indicators2)) / len(indicators1.union(indicators2)) if indicators1.union(indicators2) else 0
        requirement_jaccard = len(requirements1.intersection(requirements2)) / len(requirements1.union(requirements2)) if requirements1.union(requirements2) else 0
        
        # Weighted average
        return pattern_jaccard * 0.4 + indicator_jaccard * 0.3 + requirement_jaccard * 0.3
    
    def _detect_circular_dependencies(self, domain_name: str, all_domains: Dict[str, Domain]) -> List[List[str]]:
        """Detect circular dependency chains involving the given domain"""
        circular_chains = []
        
        def dfs_cycle_detection(current: str, path: List[str], visited: Set[str]) -> None:
            if current in path:
                # Found a cycle
                cycle_start = path.index(current)
                cycle = path[cycle_start:] + [current]
                if domain_name in cycle:  # Only include cycles involving our target domain
                    circular_chains.append(cycle)
                return
            
            if current in visited or current not in all_domains:
                return
            
            visited.add(current)
            path.append(current)
            
            # Explore dependencies
            for dep in all_domains[current].dependencies:
                dfs_cycle_detection(dep, path.copy(), visited.copy())
        
        # Start DFS from the target domain
        dfs_cycle_detection(domain_name, [], set())
        
        return circular_chains
    
    def _find_high_coupling_domains(self, target_domain: Domain, all_domains: Dict[str, Domain]) -> List[Domain]:
        """Find domains with high coupling to the target domain"""
        high_coupling_domains = []
        
        for domain_name, domain_obj in all_domains.items():
            if domain_name == target_domain.name:
                continue
            
            coupling_score = self._calculate_coupling_score(target_domain, domain_obj)
            
            # Include domains with coupling score > 0.5
            if coupling_score > 0.5:
                high_coupling_domains.append(domain_obj)
        
        # Sort by coupling score (highest first)
        high_coupling_domains.sort(key=lambda d: self._calculate_coupling_score(target_domain, d), reverse=True)
        
        return high_coupling_domains
    
    def _calculate_coupling_score(self, domain1: Domain, domain2: Domain) -> float:
        """Calculate coupling score between two domains"""
        score = 0.0
        
        # Dependency coupling
        if domain2.name in domain1.dependencies:
            score += 0.4
        if domain1.name in domain2.dependencies:
            score += 0.4
        
        # Pattern overlap coupling
        pattern_overlap = len(set(domain1.patterns).intersection(set(domain2.patterns)))
        if pattern_overlap > 0:
            score += 0.2 * min(pattern_overlap / len(domain1.patterns), 1.0)
        
        # Tool coupling
        if domain1.tools.linter == domain2.tools.linter:
            score += 0.1
        if domain1.tools.formatter == domain2.tools.formatter:
            score += 0.1
        
        return min(score, 1.0)
    
    def _find_extraction_related_domains(self, target_domain: Domain, all_domains: Dict[str, Domain]) -> List[Domain]:
        """Find domains that would be affected by extracting the target domain"""
        related_domains = []
        
        # Find direct dependents
        for domain_name, domain_obj in all_domains.items():
            if target_domain.name in domain_obj.dependencies:
                related_domains.append(domain_obj)
        
        # Find domains with overlapping patterns (potential conflicts)
        target_patterns = set(target_domain.patterns)
        for domain_name, domain_obj in all_domains.items():
            if domain_name == target_domain.name:
                continue
            
            pattern_overlap = len(target_patterns.intersection(set(domain_obj.patterns)))
            if pattern_overlap > 0:
                related_domains.append(domain_obj)
        
        # Remove duplicates
        seen = set()
        unique_related = []
        for domain in related_domains:
            if domain.name not in seen:
                seen.add(domain.name)
                unique_related.append(domain)
        
        return unique_related
    
    def advanced_relationship_analysis(self, domain_name: str) -> Dict[str, Any]:
        """Perform comprehensive relationship analysis for a domain"""
        with self._time_operation("advanced_relationship_analysis"):
            try:
                if not self.registry_manager:
                    return {}
                
                all_domains = self.registry_manager.get_all_domains()
                target_domain = all_domains.get(domain_name)
                
                if not target_domain:
                    return {}
                
                analysis = {
                    "domain": domain_name,
                    "direct_dependencies": [d.name for d in self.relationship_query(domain_name, "dependencies")],
                    "direct_dependents": [d.name for d in self.relationship_query(domain_name, "dependents")],
                    "transitive_dependencies": [d.name for d in self.relationship_query(domain_name, "transitive_dependencies")],
                    "transitive_dependents": [d.name for d in self.relationship_query(domain_name, "transitive_dependents")],
                    "similar_domains": [d.name for d in self.relationship_query(domain_name, "similar")],
                    "circular_dependencies": self._detect_circular_dependencies(domain_name, all_domains),
                    "high_coupling_domains": [d.name for d in self.relationship_query(domain_name, "coupling_high")],
                    "extraction_impact": [d.name for d in self.relationship_query(domain_name, "extraction_related")]
                }
                
                # Calculate relationship metrics
                analysis["metrics"] = {
                    "dependency_depth": len(analysis["transitive_dependencies"]),
                    "dependent_count": len(analysis["transitive_dependents"]),
                    "similarity_count": len(analysis["similar_domains"]),
                    "coupling_count": len(analysis["high_coupling_domains"]),
                    "circular_dependency_count": len(analysis["circular_dependencies"]),
                    "extraction_impact_count": len(analysis["extraction_impact"])
                }
                
                return analysis
                
            except Exception as e:
                self._handle_error(e, "advanced_relationship_analysis")
                return {}
    
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