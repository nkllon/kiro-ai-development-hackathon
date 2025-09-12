"""
Domain Index System

This module provides efficient indexing and search capabilities for domains,
including full-text search, pattern matching, and relationship indexing.
"""

import re
import threading
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass

from .base import DomainSystemComponent
from .interfaces import IndexInterface
from .models import Domain, DomainCollection, QueryResult


@dataclass
class IndexEntry:
    """Individual index entry"""
    domain_name: str
    field_name: str
    value: str
    normalized_value: str
    weight: float
    
    def matches(self, query: str, fuzzy: bool = False) -> float:
        """Check if entry matches query and return relevance score"""
        query_lower = query.lower()
        normalized_lower = self.normalized_value.lower()
        
        # Exact match
        if query_lower == normalized_lower:
            return 1.0 * self.weight
        
        # Starts with
        if normalized_lower.startswith(query_lower):
            return 0.8 * self.weight
        
        # Contains
        if query_lower in normalized_lower:
            return 0.6 * self.weight
        
        # Fuzzy matching if enabled
        if fuzzy:
            similarity = self._calculate_similarity(query_lower, normalized_lower)
            if similarity > 0.7:
                return similarity * 0.4 * self.weight
        
        return 0.0
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using Levenshtein distance"""
        if len(s1) == 0:
            return len(s2)
        if len(s2) == 0:
            return len(s1)
        
        # Create matrix
        matrix = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
        
        # Initialize first row and column
        for i in range(len(s1) + 1):
            matrix[i][0] = i
        for j in range(len(s2) + 1):
            matrix[0][j] = j
        
        # Fill matrix
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i-1] == s2[j-1]:
                    cost = 0
                else:
                    cost = 1
                
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # deletion
                    matrix[i][j-1] + 1,      # insertion
                    matrix[i-1][j-1] + cost  # substitution
                )
        
        # Convert distance to similarity
        max_len = max(len(s1), len(s2))
        distance = matrix[len(s1)][len(s2)]
        return 1.0 - (distance / max_len)


class DomainIndex(DomainSystemComponent, IndexInterface):
    """
    Efficient indexing system for domain data
    
    Features:
    - Full-text search across all domain fields
    - Pattern-based indexing
    - Relationship indexing
    - Fuzzy matching
    - Relevance scoring
    - Incremental updates
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("domain_index", config)
        
        # Index configuration
        self.enable_fuzzy_search = self.config.get('enable_fuzzy_search', True)
        self.min_query_length = self.config.get('min_query_length', 2)
        self.max_results = self.config.get('max_search_results', 100)
        
        # Index storage
        self._text_index: Dict[str, List[IndexEntry]] = defaultdict(list)
        self._pattern_index: Dict[str, Set[str]] = defaultdict(set)
        self._dependency_index: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_dependency_index: Dict[str, Set[str]] = defaultdict(set)
        self._category_index: Dict[str, Set[str]] = defaultdict(set)
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Index metadata
        self._indexed_domains: Set[str] = set()
        self._last_build_time: Optional[datetime] = None
        self._index_version = 1
        self._lock = threading.RLock()
        
        # Statistics
        self.search_count = 0
        self.index_updates = 0
        self.total_entries = 0
        
        # Field weights for relevance scoring
        self._field_weights = {
            'name': 2.0,
            'description': 1.0,
            'patterns': 1.5,
            'content_indicators': 1.2,
            'requirements': 0.8,
            'tags': 1.3
        }
        
        self.logger.info("Initialized DomainIndex")
    
    def build_index(self, domains: DomainCollection) -> bool:
        """Build complete index from domain collection"""
        with self._lock:
            try:
                start_time = datetime.now()
                
                # Clear existing index
                self._clear_index()
                
                # Index each domain
                for domain in domains.values():
                    self._index_domain(domain)
                
                # Update metadata
                self._last_build_time = datetime.now()
                self._index_version += 1
                
                build_time = (datetime.now() - start_time).total_seconds()
                self.logger.info(f"Built index for {len(domains)} domains in {build_time:.2f}s")
                
                return True
                
            except Exception as e:
                self._handle_error(e, "build_index")
                return False
    
    def update_index(self, domain: Domain) -> bool:
        """Update index for a specific domain"""
        with self._lock:
            try:
                # Remove existing entries for this domain
                self._remove_domain_from_index(domain.name)
                
                # Add new entries
                self._index_domain(domain)
                
                self.index_updates += 1
                self.logger.debug(f"Updated index for domain: {domain.name}")
                
                return True
                
            except Exception as e:
                self._handle_error(e, "update_index")
                return False
    
    def search_index(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[str]:
        """Search index and return domain names"""
        with self._lock:
            self.search_count += 1
            
            if len(query) < self.min_query_length:
                return []
            
            # Collect matching entries with scores
            matches: Dict[str, float] = defaultdict(float)
            
            # Search text index
            query_terms = self._tokenize_query(query)
            for term in query_terms:
                for token, entries in self._text_index.items():
                    if term.lower() in token.lower():
                        for entry in entries:
                            score = entry.matches(term, self.enable_fuzzy_search)
                            if score > 0:
                                matches[entry.domain_name] += score
            
            # Apply filters
            if filters:
                matches = self._apply_search_filters(matches, filters)
            
            # Sort by relevance and limit results
            sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
            return [domain_name for domain_name, _ in sorted_matches[:self.max_results]]
    
    def search_by_pattern(self, pattern: str) -> List[str]:
        """Search domains by file pattern"""
        with self._lock:
            matching_domains = set()
            
            # Direct pattern match
            if pattern in self._pattern_index:
                matching_domains.update(self._pattern_index[pattern])
            
            # Fuzzy pattern matching
            for indexed_pattern, domains in self._pattern_index.items():
                if self._patterns_similar(pattern, indexed_pattern):
                    matching_domains.update(domains)
            
            return list(matching_domains)
    
    def search_by_dependency(self, dependency: str, reverse: bool = False) -> List[str]:
        """Search domains by dependency relationship"""
        with self._lock:
            if reverse:
                return list(self._reverse_dependency_index.get(dependency, set()))
            else:
                return list(self._dependency_index.get(dependency, set()))
    
    def search_by_category(self, category: str) -> List[str]:
        """Search domains by category"""
        with self._lock:
            return list(self._category_index.get(category, set()))
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Search domains by tag"""
        with self._lock:
            return list(self._tag_index.get(tag, set()))
    
    def get_domain_relationships(self, domain_name: str) -> Dict[str, List[str]]:
        """Get all relationships for a domain"""
        with self._lock:
            return {
                'dependencies': list(self._dependency_index.get(domain_name, set())),
                'dependents': list(self._reverse_dependency_index.get(domain_name, set())),
                'same_category': self._get_domains_in_same_category(domain_name),
                'similar_patterns': self._get_domains_with_similar_patterns(domain_name)
            }
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get comprehensive index statistics"""
        with self._lock:
            return {
                'indexed_domains': len(self._indexed_domains),
                'total_text_entries': sum(len(entries) for entries in self._text_index.values()),
                'total_patterns': len(self._pattern_index),
                'total_dependencies': sum(len(deps) for deps in self._dependency_index.values()),
                'categories': len(self._category_index),
                'tags': len(self._tag_index),
                'search_count': self.search_count,
                'index_updates': self.index_updates,
                'last_build_time': self._last_build_time.isoformat() if self._last_build_time else None,
                'index_version': self._index_version,
                'fuzzy_search_enabled': self.enable_fuzzy_search,
                'min_query_length': self.min_query_length,
                'max_results': self.max_results
            }
    
    def rebuild_index(self) -> bool:
        """Rebuild the entire index (placeholder - requires domain collection)"""
        # This would typically be called by the registry manager
        self.logger.warning("rebuild_index called without domain collection")
        return False
    
    def suggest_completions(self, partial_query: str) -> List[str]:
        """Suggest query completions"""
        with self._lock:
            if len(partial_query) < 2:
                return []
            
            suggestions = set()
            partial_lower = partial_query.lower()
            
            # Search in text index tokens
            for token in self._text_index.keys():
                if token.lower().startswith(partial_lower):
                    suggestions.add(token)
            
            # Search in domain names
            for domain_name in self._indexed_domains:
                if domain_name.lower().startswith(partial_lower):
                    suggestions.add(domain_name)
            
            return sorted(list(suggestions))[:10]
    
    def _index_domain(self, domain: Domain) -> None:
        """Index a single domain"""
        domain_name = domain.name
        
        # Index text fields
        self._add_text_entry(domain_name, 'name', domain.name, self._field_weights['name'])
        self._add_text_entry(domain_name, 'description', domain.description, self._field_weights['description'])
        
        # Index patterns
        for pattern in domain.patterns:
            self._add_text_entry(domain_name, 'patterns', pattern, self._field_weights['patterns'])
            self._pattern_index[pattern].add(domain_name)
        
        # Index content indicators
        for indicator in domain.content_indicators:
            self._add_text_entry(domain_name, 'content_indicators', indicator, self._field_weights['content_indicators'])
        
        # Index requirements
        for requirement in domain.requirements:
            self._add_text_entry(domain_name, 'requirements', requirement, self._field_weights['requirements'])
        
        # Index dependencies
        for dependency in domain.dependencies:
            self._dependency_index[domain_name].add(dependency)
            self._reverse_dependency_index[dependency].add(domain_name)
        
        # Index category
        category = domain.metadata.demo_role
        self._category_index[category].add(domain_name)
        
        # Index tags
        for tag in domain.metadata.tags:
            self._tag_index[tag].add(domain_name)
            self._add_text_entry(domain_name, 'tags', tag, self._field_weights['tags'])
        
        # Add to indexed domains
        self._indexed_domains.add(domain_name)
        self.total_entries += 1
    
    def _add_text_entry(self, domain_name: str, field_name: str, value: str, weight: float) -> None:
        """Add a text entry to the index"""
        normalized_value = self._normalize_text(value)
        entry = IndexEntry(domain_name, field_name, value, normalized_value, weight)
        
        # Tokenize and add to index
        tokens = self._tokenize_text(normalized_value)
        for token in tokens:
            self._text_index[token].append(entry)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for indexing"""
        # Convert to lowercase, remove special characters, normalize whitespace
        normalized = re.sub(r'[^\w\s-]', ' ', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into searchable terms"""
        # Split on whitespace and common separators
        tokens = re.split(r'[\s\-_\.]+', text)
        
        # Filter out short tokens and empty strings
        tokens = [token for token in tokens if len(token) >= 2]
        
        return tokens
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize search query"""
        return self._tokenize_text(self._normalize_text(query))
    
    def _remove_domain_from_index(self, domain_name: str) -> None:
        """Remove all entries for a domain from the index"""
        # Remove from text index
        for token, entries in list(self._text_index.items()):
            self._text_index[token] = [e for e in entries if e.domain_name != domain_name]
            if not self._text_index[token]:
                del self._text_index[token]
        
        # Remove from pattern index
        for pattern, domains in list(self._pattern_index.items()):
            domains.discard(domain_name)
            if not domains:
                del self._pattern_index[pattern]
        
        # Remove from dependency indexes
        self._dependency_index.pop(domain_name, None)
        for deps in self._reverse_dependency_index.values():
            deps.discard(domain_name)
        
        # Remove from category index
        for domains in self._category_index.values():
            domains.discard(domain_name)
        
        # Remove from tag index
        for domains in self._tag_index.values():
            domains.discard(domain_name)
        
        # Remove from indexed domains
        self._indexed_domains.discard(domain_name)
    
    def _clear_index(self) -> None:
        """Clear all index data"""
        self._text_index.clear()
        self._pattern_index.clear()
        self._dependency_index.clear()
        self._reverse_dependency_index.clear()
        self._category_index.clear()
        self._tag_index.clear()
        self._indexed_domains.clear()
        self.total_entries = 0
    
    def _apply_search_filters(self, matches: Dict[str, float], filters: Dict[str, Any]) -> Dict[str, float]:
        """Apply filters to search results"""
        filtered_matches = {}
        
        for domain_name, score in matches.items():
            include = True
            
            # Category filter
            if 'category' in filters:
                if domain_name not in self._category_index.get(filters['category'], set()):
                    include = False
            
            # Tag filter
            if 'tag' in filters and include:
                if domain_name not in self._tag_index.get(filters['tag'], set()):
                    include = False
            
            # Pattern filter
            if 'has_pattern' in filters and include:
                pattern = filters['has_pattern']
                domain_patterns = [p for p, domains in self._pattern_index.items() 
                                 if domain_name in domains]
                if not any(pattern in p for p in domain_patterns):
                    include = False
            
            if include:
                filtered_matches[domain_name] = score
        
        return filtered_matches
    
    def _patterns_similar(self, pattern1: str, pattern2: str) -> bool:
        """Check if two patterns are similar"""
        # Simple similarity check - could be enhanced
        return (pattern1 in pattern2 or pattern2 in pattern1 or
                pattern1.replace('*', '') in pattern2 or
                pattern2.replace('*', '') in pattern1)
    
    def _get_domains_in_same_category(self, domain_name: str) -> List[str]:
        """Get domains in the same category"""
        for category, domains in self._category_index.items():
            if domain_name in domains:
                return [d for d in domains if d != domain_name]
        return []
    
    def _get_domains_with_similar_patterns(self, domain_name: str) -> List[str]:
        """Get domains with similar file patterns"""
        similar_domains = set()
        
        # Get patterns for this domain
        domain_patterns = [p for p, domains in self._pattern_index.items() 
                          if domain_name in domains]
        
        # Find domains with similar patterns
        for pattern in domain_patterns:
            for other_pattern, domains in self._pattern_index.items():
                if self._patterns_similar(pattern, other_pattern):
                    similar_domains.update(domains)
        
        # Remove the domain itself
        similar_domains.discard(domain_name)
        return list(similar_domains)