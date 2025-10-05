"""
Knowledge Base Search Engine

Advanced search and similar query detection with performance protection.
Provides semantic search, query suggestions, and intelligent recommendations.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json
import re
from collections import defaultdict, Counter
import statistics

from .results_storage import (
    ResultsStorageManager, SearchQuery, SearchResult, SearchType, 
    get_results_storage_manager
)
from .models import ConsultationResult, ConsultationQuery, QueryPriority
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import SearchError, ConsultationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class SimilarityMethod(str, Enum):
    """Methods for calculating query similarity"""
    LEXICAL = "lexical"  # Text-based similarity
    SEMANTIC = "semantic"  # Meaning-based similarity
    PATTERN = "pattern"  # Query pattern similarity
    HYBRID = "hybrid"  # Combination of methods


@dataclass
class QuerySuggestion:
    """Query suggestion with relevance scoring"""
    suggested_query: str
    similarity_score: float
    suggestion_type: str
    related_results_count: int
    avg_cost: float
    avg_processing_time: float
    success_rate: float
    last_used: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchInsights:
    """Insights about search patterns and recommendations"""
    total_searches: int
    unique_queries: int
    most_common_topics: List[Tuple[str, int]]
    avg_results_per_search: float
    search_success_rate: float
    popular_time_ranges: List[Tuple[str, int]]
    cost_analysis: Dict[str, float]
    performance_metrics: Dict[str, float]


@dataclass
class RetentionPolicy:
    """Data retention policy configuration"""
    max_age_days: int = 90
    max_results_per_user: int = 1000
    cleanup_batch_size: int = 100
    cleanup_interval_hours: int = 24
    preserve_high_value: bool = True
    high_value_threshold: float = 0.8  # Similarity score threshold


class KnowledgeBaseSearchEngine:
    """
    Advanced Knowledge Base Search Engine
    
    Features:
    - Semantic search with query similarity detection
    - Intelligent query suggestions and recommendations
    - Performance optimization with caching and rate limiting
    - Retention policies and automated cleanup
    - Circuit breaker protection for search operations
    - Advanced analytics and search insights
    """
    
    def __init__(
        self,
        max_suggestions: int = 10,
        similarity_threshold: float = 0.7,
        cache_size: int = 1000,
        rate_limit_per_minute: int = 100,
        enable_semantic_search: bool = True,
        retention_policy: Optional[RetentionPolicy] = None
    ):
        self.max_suggestions = max_suggestions
        self.similarity_threshold = similarity_threshold
        self.cache_size = cache_size
        self.rate_limit_per_minute = rate_limit_per_minute
        self.enable_semantic_search = enable_semantic_search
        self.retention_policy = retention_policy or RetentionPolicy()
        
        # Storage manager
        self.storage_manager: Optional[ResultsStorageManager] = None
        
        # Caching and performance
        self.suggestion_cache: Dict[str, Tuple[datetime, List[QuerySuggestion]]] = {}
        self.search_cache: Dict[str, Tuple[datetime, List[SearchResult]]] = {}
        self.rate_limit_tracker: Dict[str, List[datetime]] = {}
        
        # Analytics and insights
        self.search_analytics = {
            'total_searches': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'suggestions_generated': 0,
            'similarity_calculations': 0,
            'avg_search_time': 0.0,
            'avg_suggestion_time': 0.0,
            'rate_limit_hits': 0,
            'last_cleanup': None
        }
        
        # Query patterns and topics
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.topic_keywords: Dict[str, Set[str]] = defaultdict(set)
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> None:
        """Initialize the knowledge base search engine"""
        try:
            logger.info("Initializing Knowledge Base Search Engine")
            
            # Check if knowledge base search is enabled
            if not await feature_flags.is_enabled(FeatureFlag.KNOWLEDGE_BASE_SEARCH):
                logger.info("Knowledge base search is disabled via feature flag")
                return
            
            # Initialize storage manager
            self.storage_manager = await get_results_storage_manager()
            
            # Load existing query patterns
            await self._load_query_patterns()
            
            # Start background cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Knowledge Base Search Engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Base Search Engine: {e}")
            raise SearchError(f"Initialization failed: {str(e)}")
    
    async def _load_query_patterns(self) -> None:
        """Load existing query patterns from storage"""
        try:
            if not self.storage_manager:
                return
            
            # Get knowledge base stats to understand existing patterns
            stats = await self.storage_manager.get_knowledge_base_stats()
            
            # Extract patterns from most common topics
            for topic, count in stats.most_common_topics:
                self.query_patterns[topic] = count
                # Extract keywords from topic
                keywords = self._extract_keywords(topic)
                self.topic_keywords[topic].update(keywords)
            
            logger.info(f"Loaded {len(self.query_patterns)} query patterns")
            
        except Exception as e:
            logger.error(f"Failed to load query patterns: {e}")
    
    @with_circuit_breaker('knowledge_base_search')
    async def search_with_suggestions(
        self, 
        query_text: str, 
        user_id: Optional[str] = None,
        search_type: SearchType = SearchType.HYBRID,
        include_suggestions: bool = True,
        limit: int = 10
    ) -> Tuple[List[SearchResult], List[QuerySuggestion]]:
        """Search with intelligent suggestions"""
        start_time = time.time()
        
        try:
            # Check rate limiting
            if not await self._check_rate_limit(user_id or "anonymous"):
                raise SearchError("Rate limit exceeded")
            
            # Check feature flag
            if not await feature_flags.is_enabled(FeatureFlag.KNOWLEDGE_BASE_SEARCH):
                raise SearchError("Knowledge base search is disabled")
            
            # Perform search
            search_results = await self._perform_advanced_search(
                query_text, user_id, search_type, limit
            )
            
            # Generate suggestions if requested
            suggestions = []
            if include_suggestions:
                suggestions = await self._generate_query_suggestions(
                    query_text, user_id, search_results
                )
            
            # Update analytics
            self.search_analytics['total_searches'] += 1
            processing_time = time.time() - start_time
            self.search_analytics['avg_search_time'] = (
                (self.search_analytics['avg_search_time'] * (self.search_analytics['total_searches'] - 1) + processing_time) /
                self.search_analytics['total_searches']
            )
            
            # Update query patterns
            await self._update_query_patterns(query_text)
            
            return search_results, suggestions
            
        except Exception as e:
            logger.error(f"Search with suggestions failed: {e}")
            raise SearchError(f"Search failed: {str(e)}")
    
    async def _perform_advanced_search(
        self, 
        query_text: str, 
        user_id: Optional[str], 
        search_type: SearchType, 
        limit: int
    ) -> List[SearchResult]:
        """Perform advanced search with multiple strategies"""
        try:
            if not self.storage_manager:
                raise SearchError("Storage manager not initialized")
            
            # Check cache first
            cache_key = self._generate_search_cache_key(query_text, user_id, search_type, limit)
            cached_results = self._get_cached_search(cache_key)
            if cached_results:
                self.search_analytics['cache_hits'] += 1
                return cached_results
            
            self.search_analytics['cache_misses'] += 1
            
            # Determine search strategy
            if search_type == SearchType.HYBRID:
                # Use hybrid approach: combine multiple search types
                results = await self._hybrid_search(query_text, user_id, limit)
            else:
                # Use single search type
                search_query = SearchQuery(
                    query_text=query_text,
                    search_type=search_type,
                    user_id=user_id,
                    limit=limit,
                    min_similarity=self.similarity_threshold
                )
                results = await self.storage_manager.search_results(search_query)
            
            # Cache results
            self._cache_search_results(cache_key, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Advanced search failed: {e}")
            raise
    
    async def _hybrid_search(
        self, 
        query_text: str, 
        user_id: Optional[str], 
        limit: int
    ) -> List[SearchResult]:
        """Perform hybrid search combining multiple approaches"""
        try:
            all_results = []
            seen_result_ids = set()
            
            # 1. Exact search (highest priority)
            exact_query = SearchQuery(
                query_text=query_text,
                search_type=SearchType.EXACT,
                user_id=user_id,
                limit=limit // 4
            )
            exact_results = await self.storage_manager.search_results(exact_query)
            
            for result in exact_results:
                if result.result.result_id not in seen_result_ids:
                    result.relevance_score *= 1.5  # Boost exact matches
                    all_results.append(result)
                    seen_result_ids.add(result.result.result_id)
            
            # 2. Semantic search
            if self.enable_semantic_search:
                semantic_query = SearchQuery(
                    query_text=query_text,
                    search_type=SearchType.SEMANTIC,
                    user_id=user_id,
                    limit=limit // 2
                )
                semantic_results = await self.storage_manager.search_results(semantic_query)
                
                for result in semantic_results:
                    if result.result.result_id not in seen_result_ids:
                        result.relevance_score *= 1.2  # Boost semantic matches
                        all_results.append(result)
                        seen_result_ids.add(result.result.result_id)
            
            # 3. Similar search
            similar_query = SearchQuery(
                query_text=query_text,
                search_type=SearchType.SIMILAR,
                user_id=user_id,
                limit=limit // 2,
                min_similarity=self.similarity_threshold
            )
            similar_results = await self.storage_manager.search_results(similar_query)
            
            for result in similar_results:
                if result.result.result_id not in seen_result_ids:
                    all_results.append(result)
                    seen_result_ids.add(result.result.result_id)
            
            # 4. Keyword search (fallback)
            if len(all_results) < limit // 2:
                keyword_query = SearchQuery(
                    query_text=query_text,
                    search_type=SearchType.KEYWORD,
                    user_id=user_id,
                    limit=limit
                )
                keyword_results = await self.storage_manager.search_results(keyword_query)
                
                for result in keyword_results:
                    if result.result.result_id not in seen_result_ids:
                        all_results.append(result)
                        seen_result_ids.add(result.result.result_id)
            
            # Sort by relevance score and limit results
            all_results.sort(key=lambda x: x.relevance_score, reverse=True)
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise
    
    async def _generate_query_suggestions(
        self, 
        query_text: str, 
        user_id: Optional[str],
        search_results: List[SearchResult]
    ) -> List[QuerySuggestion]:
        """Generate intelligent query suggestions"""
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_suggestion_cache_key(query_text, user_id)
            cached_suggestions = self._get_cached_suggestions(cache_key)
            if cached_suggestions:
                return cached_suggestions
            
            suggestions = []
            
            # 1. Pattern-based suggestions
            pattern_suggestions = await self._generate_pattern_suggestions(query_text)
            suggestions.extend(pattern_suggestions)
            
            # 2. Topic-based suggestions
            topic_suggestions = await self._generate_topic_suggestions(query_text)
            suggestions.extend(topic_suggestions)
            
            # 3. Similar query suggestions
            similar_suggestions = await self._generate_similar_query_suggestions(query_text)
            suggestions.extend(similar_suggestions)
            
            # 4. Context-aware suggestions based on search results
            if search_results:
                context_suggestions = await self._generate_context_suggestions(
                    query_text, search_results
                )
                suggestions.extend(context_suggestions)
            
            # Remove duplicates and sort by relevance
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            unique_suggestions.sort(key=lambda x: x.similarity_score, reverse=True)
            
            # Limit to max suggestions
            final_suggestions = unique_suggestions[:self.max_suggestions]
            
            # Cache suggestions
            self._cache_suggestions(cache_key, final_suggestions)
            
            # Update analytics
            self.search_analytics['suggestions_generated'] += len(final_suggestions)
            processing_time = time.time() - start_time
            self.search_analytics['avg_suggestion_time'] = (
                (self.search_analytics['avg_suggestion_time'] * self.search_analytics['total_searches'] + processing_time) /
                (self.search_analytics['total_searches'] + 1)
            )
            
            return final_suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate query suggestions: {e}")
            return []
    
    async def _generate_pattern_suggestions(self, query_text: str) -> List[QuerySuggestion]:
        """Generate suggestions based on query patterns"""
        try:
            suggestions = []
            query_keywords = self._extract_keywords(query_text)
            
            for pattern, count in self.query_patterns.items():
                if count < 2:  # Skip patterns with low frequency
                    continue
                
                pattern_keywords = self._extract_keywords(pattern)
                similarity = self._calculate_keyword_similarity(query_keywords, pattern_keywords)
                
                if similarity >= self.similarity_threshold:
                    suggestion = QuerySuggestion(
                        suggested_query=pattern,
                        similarity_score=similarity,
                        suggestion_type="pattern",
                        related_results_count=count,
                        avg_cost=0.10,  # Default estimate
                        avg_processing_time=2.0,  # Default estimate
                        success_rate=0.9,  # Default estimate
                        last_used=datetime.utcnow(),
                        metadata={'pattern_frequency': count}
                    )
                    suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate pattern suggestions: {e}")
            return []
    
    async def _generate_topic_suggestions(self, query_text: str) -> List[QuerySuggestion]:
        """Generate suggestions based on topic analysis"""
        try:
            suggestions = []
            query_keywords = self._extract_keywords(query_text)
            
            for topic, keywords in self.topic_keywords.items():
                if len(keywords) < 2:
                    continue
                
                similarity = self._calculate_keyword_similarity(query_keywords, keywords)
                
                if similarity >= self.similarity_threshold * 0.8:  # Lower threshold for topics
                    # Generate topic-based query suggestions
                    topic_queries = [
                        f"What is the status of {topic}?",
                        f"Are there any issues with {topic}?",
                        f"Show me metrics for {topic}",
                        f"How is {topic} performing?"
                    ]
                    
                    for topic_query in topic_queries:
                        if self._calculate_text_similarity(query_text, topic_query) < 0.9:  # Avoid too similar
                            suggestion = QuerySuggestion(
                                suggested_query=topic_query,
                                similarity_score=similarity * 0.9,  # Slightly lower score
                                suggestion_type="topic",
                                related_results_count=self.query_patterns.get(topic, 1),
                                avg_cost=0.08,
                                avg_processing_time=1.8,
                                success_rate=0.85,
                                last_used=datetime.utcnow(),
                                metadata={'topic': topic, 'keywords': list(keywords)[:5]}
                            )
                            suggestions.append(suggestion)
            
            return suggestions[:5]  # Limit topic suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate topic suggestions: {e}")
            return []
    
    async def _generate_similar_query_suggestions(self, query_text: str) -> List[QuerySuggestion]:
        """Generate suggestions based on similar queries"""
        try:
            if not self.storage_manager:
                return []
            
            # Search for similar queries
            similar_query = SearchQuery(
                query_text=query_text,
                search_type=SearchType.SIMILAR,
                limit=20,
                min_similarity=self.similarity_threshold
            )
            
            similar_results = await self.storage_manager.search_results(similar_query)
            
            suggestions = []
            seen_queries = set()
            
            for result in similar_results:
                original_query = result.result.metadata.get('query_text', '')
                if not original_query or original_query in seen_queries:
                    continue
                
                seen_queries.add(original_query)
                
                suggestion = QuerySuggestion(
                    suggested_query=original_query,
                    similarity_score=result.similarity_score or result.relevance_score,
                    suggestion_type="similar",
                    related_results_count=1,
                    avg_cost=result.result.cost,
                    avg_processing_time=result.result.processing_time,
                    success_rate=1.0,  # Successful result
                    last_used=result.result.timestamp,
                    metadata={
                        'original_result_id': result.result.result_id,
                        'processing_mode': result.result.processing_mode
                    }
                )
                suggestions.append(suggestion)
            
            return suggestions[:8]  # Limit similar suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate similar query suggestions: {e}")
            return []
    
    async def _generate_context_suggestions(
        self, 
        query_text: str, 
        search_results: List[SearchResult]
    ) -> List[QuerySuggestion]:
        """Generate context-aware suggestions based on search results"""
        try:
            suggestions = []
            
            if not search_results:
                return suggestions
            
            # Analyze search results for context
            topics = []
            for result in search_results[:5]:  # Analyze top 5 results
                response_text = result.result.response_text
                extracted_topics = self._extract_topics_from_text(response_text)
                topics.extend(extracted_topics)
            
            # Generate follow-up questions based on topics
            topic_counter = Counter(topics)
            for topic, count in topic_counter.most_common(3):
                follow_up_queries = [
                    f"Tell me more about {topic}",
                    f"What are the best practices for {topic}?",
                    f"How can I troubleshoot {topic} issues?",
                    f"What metrics should I monitor for {topic}?"
                ]
                
                for follow_up in follow_up_queries:
                    if self._calculate_text_similarity(query_text, follow_up) < 0.7:
                        suggestion = QuerySuggestion(
                            suggested_query=follow_up,
                            similarity_score=0.8,
                            suggestion_type="context",
                            related_results_count=count,
                            avg_cost=0.12,
                            avg_processing_time=2.2,
                            success_rate=0.88,
                            last_used=datetime.utcnow(),
                            metadata={'context_topic': topic, 'frequency': count}
                        )
                        suggestions.append(suggestion)
            
            return suggestions[:4]  # Limit context suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate context suggestions: {e}")
            return []
    
    async def get_search_insights(
        self, 
        user_id: Optional[str] = None,
        time_range_days: int = 30
    ) -> SearchInsights:
        """Get comprehensive search insights and analytics"""
        try:
            if not self.storage_manager:
                raise SearchError("Storage manager not initialized")
            
            # Get knowledge base stats
            kb_stats = await self.storage_manager.get_knowledge_base_stats()
            
            # Calculate search-specific metrics
            total_searches = self.search_analytics['total_searches']
            cache_hit_rate = (
                self.search_analytics['cache_hits'] / 
                max(1, self.search_analytics['cache_hits'] + self.search_analytics['cache_misses'])
            )
            
            # Analyze query patterns
            most_common_topics = list(Counter(self.query_patterns).most_common(10))
            
            # Time-based analysis (simplified)
            current_hour = datetime.utcnow().hour
            popular_time_ranges = [
                (f"{current_hour-2:02d}:00-{current_hour:02d}:00", total_searches // 4),
                (f"{current_hour:02d}:00-{current_hour+2:02d}:00", total_searches // 2),
            ]
            
            insights = SearchInsights(
                total_searches=total_searches,
                unique_queries=len(self.query_patterns),
                most_common_topics=most_common_topics,
                avg_results_per_search=5.2,  # Estimated average
                search_success_rate=0.92,  # Estimated success rate
                popular_time_ranges=popular_time_ranges,
                cost_analysis={
                    'avg_cost_per_search': kb_stats.avg_cost_per_query,
                    'total_search_cost': kb_stats.total_cost,
                    'cost_savings_from_cache': cache_hit_rate * kb_stats.total_cost * 0.1
                },
                performance_metrics={
                    'avg_search_time': self.search_analytics['avg_search_time'],
                    'avg_suggestion_time': self.search_analytics['avg_suggestion_time'],
                    'cache_hit_rate': cache_hit_rate,
                    'rate_limit_hit_rate': self.search_analytics['rate_limit_hits'] / max(1, total_searches)
                }
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get search insights: {e}")
            raise SearchError(f"Insights retrieval failed: {str(e)}")
    
    async def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data according to retention policy"""
        try:
            if not self.storage_manager:
                return {'error': 'Storage manager not initialized'}
            
            cleanup_stats = {
                'cache_entries_removed': 0,
                'patterns_cleaned': 0,
                'suggestions_cleaned': 0
            }
            
            current_time = datetime.utcnow()
            
            # Clean up search cache
            expired_search_keys = []
            for key, (cache_time, _) in self.search_cache.items():
                if current_time - cache_time > timedelta(hours=1):  # 1 hour cache TTL
                    expired_search_keys.append(key)
            
            for key in expired_search_keys:
                del self.search_cache[key]
                cleanup_stats['cache_entries_removed'] += 1
            
            # Clean up suggestion cache
            expired_suggestion_keys = []
            for key, (cache_time, _) in self.suggestion_cache.items():
                if current_time - cache_time > timedelta(hours=2):  # 2 hour cache TTL
                    expired_suggestion_keys.append(key)
            
            for key in expired_suggestion_keys:
                del self.suggestion_cache[key]
                cleanup_stats['suggestions_cleaned'] += 1
            
            # Clean up low-frequency patterns
            low_freq_patterns = [
                pattern for pattern, count in self.query_patterns.items()
                if count < 2
            ]
            
            for pattern in low_freq_patterns:
                del self.query_patterns[pattern]
                if pattern in self.topic_keywords:
                    del self.topic_keywords[pattern]
                cleanup_stats['patterns_cleaned'] += 1
            
            # Update analytics
            self.search_analytics['last_cleanup'] = current_time.isoformat()
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {'error': str(e)}
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        try:
            while True:
                await asyncio.sleep(self.retention_policy.cleanup_interval_hours * 3600)
                
                try:
                    await self.cleanup_old_data()
                except Exception as e:
                    logger.error(f"Background cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text"""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Filter out common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                'what', 'how', 'when', 'where', 'why', 'who', 'which'
            }
            
            keywords = {word for word in words if len(word) > 2 and word not in stop_words}
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return set()
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from response text"""
        try:
            # Simple topic extraction based on common monitoring terms
            monitoring_terms = [
                'cpu', 'memory', 'disk', 'network', 'database', 'server', 'service',
                'application', 'api', 'endpoint', 'metric', 'alert', 'error', 'warning',
                'performance', 'latency', 'throughput', 'availability', 'uptime',
                'monitoring', 'dashboard', 'log', 'trace', 'span'
            ]
            
            text_lower = text.lower()
            found_topics = []
            
            for term in monitoring_terms:
                if term in text_lower:
                    found_topics.append(term)
            
            return found_topics
            
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
    
    def _calculate_keyword_similarity(self, keywords1: Set[str], keywords2: Set[str]) -> float:
        """Calculate similarity between two sets of keywords"""
        try:
            if not keywords1 or not keywords2:
                return 0.0
            
            intersection = keywords1.intersection(keywords2)
            union = keywords1.union(keywords2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Keyword similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple metrics"""
        try:
            # Simple Jaccard similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Text similarity calculation failed: {e}")
            return 0.0
    
    def _deduplicate_suggestions(self, suggestions: List[QuerySuggestion]) -> List[QuerySuggestion]:
        """Remove duplicate suggestions"""
        try:
            seen_queries = set()
            unique_suggestions = []
            
            for suggestion in suggestions:
                query_normalized = suggestion.suggested_query.lower().strip()
                if query_normalized not in seen_queries:
                    seen_queries.add(query_normalized)
                    unique_suggestions.append(suggestion)
            
            return unique_suggestions
            
        except Exception as e:
            logger.error(f"Suggestion deduplication failed: {e}")
            return suggestions
    
    async def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        try:
            current_time = datetime.utcnow()
            minute_ago = current_time - timedelta(minutes=1)
            
            # Clean old entries
            if identifier in self.rate_limit_tracker:
                self.rate_limit_tracker[identifier] = [
                    timestamp for timestamp in self.rate_limit_tracker[identifier]
                    if timestamp > minute_ago
                ]
            else:
                self.rate_limit_tracker[identifier] = []
            
            # Check rate limit
            if len(self.rate_limit_tracker[identifier]) >= self.rate_limit_per_minute:
                self.search_analytics['rate_limit_hits'] += 1
                return False
            
            # Add current request
            self.rate_limit_tracker[identifier].append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    async def _update_query_patterns(self, query_text: str) -> None:
        """Update query patterns with new query"""
        try:
            normalized_query = ' '.join(query_text.lower().split())
            self.query_patterns[normalized_query] += 1
            
            # Extract and store keywords
            keywords = self._extract_keywords(query_text)
            self.topic_keywords[normalized_query].update(keywords)
            
        except Exception as e:
            logger.error(f"Failed to update query patterns: {e}")
    
    def _generate_search_cache_key(
        self, 
        query_text: str, 
        user_id: Optional[str], 
        search_type: SearchType, 
        limit: int
    ) -> str:
        """Generate cache key for search results"""
        key_data = f"{query_text}:{user_id}:{search_type.value}:{limit}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _generate_suggestion_cache_key(self, query_text: str, user_id: Optional[str]) -> str:
        """Generate cache key for suggestions"""
        key_data = f"suggestions:{query_text}:{user_id}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_search(self, cache_key: str) -> Optional[List[SearchResult]]:
        """Get cached search results"""
        try:
            if cache_key in self.search_cache:
                cache_time, results = self.search_cache[cache_key]
                if datetime.utcnow() - cache_time < timedelta(minutes=10):  # 10 minute TTL
                    return results
                else:
                    del self.search_cache[cache_key]
            return None
        except Exception:
            return None
    
    def _get_cached_suggestions(self, cache_key: str) -> Optional[List[QuerySuggestion]]:
        """Get cached suggestions"""
        try:
            if cache_key in self.suggestion_cache:
                cache_time, suggestions = self.suggestion_cache[cache_key]
                if datetime.utcnow() - cache_time < timedelta(minutes=30):  # 30 minute TTL
                    return suggestions
                else:
                    del self.suggestion_cache[cache_key]
            return None
        except Exception:
            return None
    
    def _cache_search_results(self, cache_key: str, results: List[SearchResult]) -> None:
        """Cache search results"""
        try:
            self.search_cache[cache_key] = (datetime.utcnow(), results)
            
            # Limit cache size
            if len(self.search_cache) > self.cache_size:
                oldest_key = min(self.search_cache.keys(), 
                               key=lambda k: self.search_cache[k][0])
                del self.search_cache[oldest_key]
        except Exception as e:
            logger.warning(f"Failed to cache search results: {e}")
    
    def _cache_suggestions(self, cache_key: str, suggestions: List[QuerySuggestion]) -> None:
        """Cache suggestions"""
        try:
            self.suggestion_cache[cache_key] = (datetime.utcnow(), suggestions)
            
            # Limit cache size
            if len(self.suggestion_cache) > self.cache_size:
                oldest_key = min(self.suggestion_cache.keys(),
                               key=lambda k: self.suggestion_cache[k][0])
                del self.suggestion_cache[oldest_key]
        except Exception as e:
            logger.warning(f"Failed to cache suggestions: {e}")
    
    async def get_search_analytics(self) -> Dict[str, Any]:
        """Get search analytics and performance metrics"""
        try:
            return {
                'search_analytics': self.search_analytics.copy(),
                'cache_stats': {
                    'search_cache_size': len(self.search_cache),
                    'suggestion_cache_size': len(self.suggestion_cache),
                    'cache_hit_rate': (
                        self.search_analytics['cache_hits'] / 
                        max(1, self.search_analytics['cache_hits'] + self.search_analytics['cache_misses'])
                    )
                },
                'pattern_stats': {
                    'total_patterns': len(self.query_patterns),
                    'total_topics': len(self.topic_keywords),
                    'avg_pattern_frequency': (
                        statistics.mean(self.query_patterns.values()) 
                        if self.query_patterns else 0.0
                    )
                },
                'configuration': {
                    'max_suggestions': self.max_suggestions,
                    'similarity_threshold': self.similarity_threshold,
                    'cache_size': self.cache_size,
                    'rate_limit_per_minute': self.rate_limit_per_minute,
                    'enable_semantic_search': self.enable_semantic_search
                }
            }
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return {'error': str(e)}
    
    async def get_health_status(self) -> ComponentHealth:
        """Get search engine health status"""
        try:
            # Calculate performance metrics
            cache_hit_rate = (
                self.search_analytics['cache_hits'] / 
                max(1, self.search_analytics['cache_hits'] + self.search_analytics['cache_misses'])
            )
            
            rate_limit_hit_rate = (
                self.search_analytics['rate_limit_hits'] / 
                max(1, self.search_analytics['total_searches'])
            )
            
            # Determine health status
            if not self.storage_manager:
                status = "critical"
                error_message = "Storage manager not initialized"
            elif self.search_analytics['avg_search_time'] > 5.0:
                status = "degraded"
                error_message = f"Slow search performance: {self.search_analytics['avg_search_time']:.2f}s"
            elif rate_limit_hit_rate > 0.1:
                status = "degraded"
                error_message = f"High rate limit hit rate: {rate_limit_hit_rate:.1%}"
            elif cache_hit_rate < 0.3:
                status = "degraded"
                error_message = f"Low cache hit rate: {cache_hit_rate:.1%}"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="knowledge_base_search_engine",
                status=status,
                response_time=self.search_analytics['avg_search_time'] * 1000,
                error_message=error_message,
                metadata={
                    'total_searches': self.search_analytics['total_searches'],
                    'cache_hit_rate': cache_hit_rate,
                    'rate_limit_hit_rate': rate_limit_hit_rate,
                    'suggestions_generated': self.search_analytics['suggestions_generated'],
                    'pattern_count': len(self.query_patterns),
                    'avg_search_time': self.search_analytics['avg_search_time'],
                    'avg_suggestion_time': self.search_analytics['avg_suggestion_time']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="knowledge_base_search_engine",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def shutdown(self) -> None:
        """Shutdown the search engine"""
        try:
            logger.info("Shutting down Knowledge Base Search Engine")
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Clear caches
            self.search_cache.clear()
            self.suggestion_cache.clear()
            self.rate_limit_tracker.clear()
            
            logger.info("Knowledge Base Search Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during search engine shutdown: {e}")


# Global search engine instance
_knowledge_base_search_engine: Optional[KnowledgeBaseSearchEngine] = None


async def get_knowledge_base_search_engine() -> KnowledgeBaseSearchEngine:
    """Get the global knowledge base search engine instance"""
    global _knowledge_base_search_engine
    if _knowledge_base_search_engine is None:
        _knowledge_base_search_engine = KnowledgeBaseSearchEngine()
        await _knowledge_base_search_engine.initialize()
    return _knowledge_base_search_engine