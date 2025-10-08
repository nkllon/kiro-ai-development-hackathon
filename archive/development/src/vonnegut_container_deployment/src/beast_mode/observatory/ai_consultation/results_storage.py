"""
Results Storage Manager

Manages storage and retrieval of consultation results with searchable knowledge base functionality.
Provides database integration with migration safety and brownfield compatibility.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
from contextlib import asynccontextmanager

from .models import ConsultationResult, ConsultationQuery, QueryPriority
from .database import get_database_connection, DatabaseConnection
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import StorageError, ConsultationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class SearchType(str, Enum):
    """Types of search operations"""
    EXACT = "exact"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    SIMILAR = "similar"


@dataclass
class SearchQuery:
    """Search query parameters"""
    query_text: str
    search_type: SearchType = SearchType.KEYWORD
    user_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 10
    offset: int = 0
    include_metadata: bool = True
    min_similarity: float = 0.7


@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    result: ConsultationResult
    relevance_score: float
    similarity_score: Optional[float] = None
    match_type: str = "keyword"
    matched_fields: List[str] = None
    
    def __post_init__(self):
        if self.matched_fields is None:
            self.matched_fields = []


@dataclass
class KnowledgeBaseStats:
    """Knowledge base statistics"""
    total_results: int
    unique_users: int
    date_range: Tuple[datetime, datetime]
    avg_cost_per_query: float
    total_cost: float
    most_common_topics: List[Tuple[str, int]]
    success_rate: float
    storage_size_mb: float


class ResultsStorageManager:
    """
    Results Storage Manager with searchable knowledge base
    
    Features:
    - Consultation result storage with full metadata
    - Searchable knowledge base with multiple search types
    - Result retrieval and history management
    - Database migration safety and brownfield compatibility
    - Performance optimization with indexing and caching
    - Circuit breaker protection for database operations
    """
    
    def __init__(
        self,
        connection_pool_size: int = 10,
        query_timeout: float = 30.0,
        cache_ttl: int = 300,  # 5 minutes
        max_search_results: int = 100,
        enable_full_text_search: bool = True
    ):
        self.connection_pool_size = connection_pool_size
        self.query_timeout = query_timeout
        self.cache_ttl = cache_ttl
        self.max_search_results = max_search_results
        self.enable_full_text_search = enable_full_text_search
        
        # Database connection
        self.db: Optional[DatabaseConnection] = None
        
        # In-memory cache for frequent queries
        self.search_cache: Dict[str, Tuple[datetime, List[SearchResult]]] = {}
        self.stats_cache: Optional[Tuple[datetime, KnowledgeBaseStats]] = None
        
        # Performance metrics
        self.metrics = {
            'results_stored': 0,
            'searches_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_search_time': 0.0,
            'avg_storage_time': 0.0,
            'database_errors': 0,
            'last_cleanup': None
        }
    
    async def initialize(self) -> None:
        """Initialize the results storage manager"""
        try:
            logger.info("Initializing Results Storage Manager")
            
            # Check if results storage is enabled
            if not await feature_flags.is_enabled(FeatureFlag.RESULTS_STORAGE):
                logger.info("Results storage is disabled via feature flag")
                return
            
            # Initialize database connection
            self.db = await get_database_connection()
            
            # Create tables if they don't exist
            await self._create_tables()
            
            # Create indexes for performance
            await self._create_indexes()
            
            # Start background cleanup task
            asyncio.create_task(self._cleanup_task())
            
            logger.info("Results Storage Manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Results Storage Manager: {e}")
            raise StorageError(f"Initialization failed: {str(e)}")
    
    async def _create_tables(self) -> None:
        """Create database tables for consultation results"""
        try:
            if not self.db:
                raise StorageError("Database connection not initialized")
            
            # Consultation results table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS consultation_results (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    result_id VARCHAR(255) UNIQUE NOT NULL,
                    query_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    query_text TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    processing_time FLOAT NOT NULL,
                    cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    processing_mode VARCHAR(50) NOT NULL,
                    metadata JSONB,
                    query_hash VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Query patterns table for similarity detection
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS query_patterns (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    pattern_hash VARCHAR(64) UNIQUE NOT NULL,
                    normalized_query TEXT NOT NULL,
                    query_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    avg_cost FLOAT,
                    avg_processing_time FLOAT,
                    success_rate FLOAT DEFAULT 1.0
                )
            """)
            
            # User consultation history table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS user_consultation_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(255) NOT NULL,
                    result_id VARCHAR(255) NOT NULL,
                    consultation_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    cost FLOAT NOT NULL,
                    satisfaction_rating INTEGER,
                    feedback TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (result_id) REFERENCES consultation_results(result_id)
                )
            """)
            
            # Knowledge base topics table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base_topics (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    topic_name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    query_count INTEGER DEFAULT 0,
                    avg_relevance FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise StorageError(f"Table creation failed: {str(e)}")
    
    async def _create_indexes(self) -> None:
        """Create database indexes for performance optimization"""
        try:
            if not self.db:
                return
            
            # Indexes for consultation_results table
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_user_id ON consultation_results(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_timestamp ON consultation_results(timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_query_hash ON consultation_results(query_hash)",
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_cost ON consultation_results(cost)",
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_processing_mode ON consultation_results(processing_mode)",
                
                # Full-text search index
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_query_text ON consultation_results USING gin(to_tsvector('english', query_text))",
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_response_text ON consultation_results USING gin(to_tsvector('english', response_text))",
                
                # JSONB metadata index
                "CREATE INDEX IF NOT EXISTS idx_consultation_results_metadata ON consultation_results USING gin(metadata)",
                
                # Indexes for query_patterns table
                "CREATE INDEX IF NOT EXISTS idx_query_patterns_hash ON query_patterns(pattern_hash)",
                "CREATE INDEX IF NOT EXISTS idx_query_patterns_count ON query_patterns(query_count DESC)",
                "CREATE INDEX IF NOT EXISTS idx_query_patterns_last_seen ON query_patterns(last_seen DESC)",
                
                # Indexes for user_consultation_history table
                "CREATE INDEX IF NOT EXISTS idx_user_history_user_id ON user_consultation_history(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_user_history_date ON user_consultation_history(consultation_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_user_history_cost ON user_consultation_history(cost)",
                
                # Indexes for knowledge_base_topics table
                "CREATE INDEX IF NOT EXISTS idx_topics_name ON knowledge_base_topics(topic_name)",
                "CREATE INDEX IF NOT EXISTS idx_topics_count ON knowledge_base_topics(query_count DESC)"
            ]
            
            for index_sql in indexes:
                try:
                    await self.db.execute(index_sql)
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
    
    @with_circuit_breaker('results_storage')
    async def store_result(self, result: ConsultationResult) -> bool:
        """Store a consultation result in the database"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.db:
                raise StorageError("Database connection not initialized")
            
            # Check if results storage is enabled
            if not await feature_flags.is_enabled(FeatureFlag.RESULTS_STORAGE):
                logger.debug("Results storage is disabled, skipping storage")
                return False
            
            # Generate query hash for similarity detection
            query_hash = self._generate_query_hash(result.query_id, result.metadata.get('query_text', ''))
            
            # Store the consultation result
            await self.db.execute("""
                INSERT INTO consultation_results (
                    result_id, query_id, user_id, query_text, response_text,
                    processing_time, cost, timestamp, processing_mode, metadata, query_hash
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (result_id) DO UPDATE SET
                    response_text = EXCLUDED.response_text,
                    processing_time = EXCLUDED.processing_time,
                    cost = EXCLUDED.cost,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """, 
                result.result_id,
                result.query_id,
                result.metadata.get('user_id', 'unknown'),
                result.metadata.get('query_text', ''),
                result.response_text,
                result.processing_time,
                result.cost,
                result.timestamp,
                result.processing_mode.value if hasattr(result.processing_mode, 'value') else str(result.processing_mode),
                json.dumps(result.metadata) if result.metadata else '{}',
                query_hash
            )
            
            # Update query patterns
            await self._update_query_patterns(result, query_hash)
            
            # Update user consultation history
            await self._update_user_history(result)
            
            # Update metrics
            self.metrics['results_stored'] += 1
            processing_time = asyncio.get_event_loop().time() - start_time
            self.metrics['avg_storage_time'] = (
                (self.metrics['avg_storage_time'] * (self.metrics['results_stored'] - 1) + processing_time) /
                self.metrics['results_stored']
            )
            
            # Clear relevant caches
            self._clear_search_cache()
            
            logger.debug(f"Stored consultation result {result.result_id}")
            return True
            
        except Exception as e:
            self.metrics['database_errors'] += 1
            logger.error(f"Failed to store consultation result {result.result_id}: {e}")
            raise StorageError(f"Storage failed: {str(e)}")
    
    async def _update_query_patterns(self, result: ConsultationResult, query_hash: str) -> None:
        """Update query patterns for similarity detection"""
        try:
            normalized_query = self._normalize_query(result.metadata.get('query_text', ''))
            
            await self.db.execute("""
                INSERT INTO query_patterns (
                    pattern_hash, normalized_query, query_count, first_seen, last_seen,
                    avg_cost, avg_processing_time, success_rate
                ) VALUES ($1, $2, 1, NOW(), NOW(), $3, $4, 1.0)
                ON CONFLICT (pattern_hash) DO UPDATE SET
                    query_count = query_patterns.query_count + 1,
                    last_seen = NOW(),
                    avg_cost = (query_patterns.avg_cost * query_patterns.query_count + $3) / (query_patterns.query_count + 1),
                    avg_processing_time = (query_patterns.avg_processing_time * query_patterns.query_count + $4) / (query_patterns.query_count + 1),
                    success_rate = (query_patterns.success_rate * query_patterns.query_count + 1.0) / (query_patterns.query_count + 1)
            """, query_hash, normalized_query, result.cost, result.processing_time)
            
        except Exception as e:
            logger.error(f"Failed to update query patterns: {e}")
    
    async def _update_user_history(self, result: ConsultationResult) -> None:
        """Update user consultation history"""
        try:
            user_id = result.metadata.get('user_id', 'unknown')
            
            await self.db.execute("""
                INSERT INTO user_consultation_history (
                    user_id, result_id, consultation_date, cost
                ) VALUES ($1, $2, $3, $4)
            """, user_id, result.result_id, result.timestamp, result.cost)
            
        except Exception as e:
            logger.error(f"Failed to update user history: {e}")
    
    @with_circuit_breaker('results_search')
    async def search_results(self, search_query: SearchQuery) -> List[SearchResult]:
        """Search consultation results with various search types"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if not self.db:
                raise StorageError("Database connection not initialized")
            
            # Check cache first
            cache_key = self._generate_search_cache_key(search_query)
            cached_result = self._get_cached_search(cache_key)
            if cached_result:
                self.metrics['cache_hits'] += 1
                return cached_result
            
            self.metrics['cache_misses'] += 1
            
            # Perform search based on type
            if search_query.search_type == SearchType.EXACT:
                results = await self._exact_search(search_query)
            elif search_query.search_type == SearchType.SEMANTIC:
                results = await self._semantic_search(search_query)
            elif search_query.search_type == SearchType.SIMILAR:
                results = await self._similar_search(search_query)
            else:  # KEYWORD
                results = await self._keyword_search(search_query)
            
            # Cache the results
            self._cache_search_results(cache_key, results)
            
            # Update metrics
            self.metrics['searches_performed'] += 1
            processing_time = asyncio.get_event_loop().time() - start_time
            self.metrics['avg_search_time'] = (
                (self.metrics['avg_search_time'] * (self.metrics['searches_performed'] - 1) + processing_time) /
                self.metrics['searches_performed']
            )
            
            return results
            
        except Exception as e:
            self.metrics['database_errors'] += 1
            logger.error(f"Failed to search results: {e}")
            raise StorageError(f"Search failed: {str(e)}")
    
    async def _keyword_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Perform keyword-based search"""
        try:
            # Build WHERE clause
            where_conditions = []
            params = []
            param_count = 0
            
            # Full-text search on query and response text
            if self.enable_full_text_search:
                param_count += 1
                where_conditions.append(f"""
                    (to_tsvector('english', query_text) @@ plainto_tsquery('english', ${param_count})
                     OR to_tsvector('english', response_text) @@ plainto_tsquery('english', ${param_count}))
                """)
                params.append(search_query.query_text)
            else:
                # Fallback to ILIKE search
                param_count += 1
                where_conditions.append(f"""
                    (query_text ILIKE ${param_count} OR response_text ILIKE ${param_count})
                """)
                params.append(f"%{search_query.query_text}%")
            
            # User filter
            if search_query.user_id:
                param_count += 1
                where_conditions.append(f"user_id = ${param_count}")
                params.append(search_query.user_id)
            
            # Date range filter
            if search_query.date_from:
                param_count += 1
                where_conditions.append(f"timestamp >= ${param_count}")
                params.append(search_query.date_from)
            
            if search_query.date_to:
                param_count += 1
                where_conditions.append(f"timestamp <= ${param_count}")
                params.append(search_query.date_to)
            
            # Build final query
            where_clause = " AND ".join(where_conditions) if where_conditions else "TRUE"
            
            # Add ranking for full-text search
            if self.enable_full_text_search:
                rank_expression = f"ts_rank(to_tsvector('english', query_text || ' ' || response_text), plainto_tsquery('english', $1))"
            else:
                rank_expression = "1.0"
            
            query = f"""
                SELECT 
                    result_id, query_id, user_id, query_text, response_text,
                    processing_time, cost, timestamp, processing_mode, metadata,
                    {rank_expression} as relevance_score
                FROM consultation_results
                WHERE {where_clause}
                ORDER BY relevance_score DESC, timestamp DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            
            params.extend([search_query.limit, search_query.offset])
            
            rows = await self.db.fetch(query, *params)
            
            # Convert to SearchResult objects
            results = []
            for row in rows:
                consultation_result = ConsultationResult(
                    result_id=row['result_id'],
                    query_id=row['query_id'],
                    response_text=row['response_text'],
                    processing_time=row['processing_time'],
                    cost=row['cost'],
                    timestamp=row['timestamp'],
                    processing_mode=row['processing_mode'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                
                search_result = SearchResult(
                    result=consultation_result,
                    relevance_score=float(row['relevance_score']),
                    match_type="keyword",
                    matched_fields=["query_text", "response_text"]
                )
                
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            raise
    
    async def _exact_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Perform exact text match search"""
        try:
            where_conditions = ["(query_text = $1 OR response_text = $1)"]
            params = [search_query.query_text]
            param_count = 1
            
            # Add additional filters
            if search_query.user_id:
                param_count += 1
                where_conditions.append(f"user_id = ${param_count}")
                params.append(search_query.user_id)
            
            if search_query.date_from:
                param_count += 1
                where_conditions.append(f"timestamp >= ${param_count}")
                params.append(search_query.date_from)
            
            if search_query.date_to:
                param_count += 1
                where_conditions.append(f"timestamp <= ${param_count}")
                params.append(search_query.date_to)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT 
                    result_id, query_id, user_id, query_text, response_text,
                    processing_time, cost, timestamp, processing_mode, metadata,
                    1.0 as relevance_score
                FROM consultation_results
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            
            params.extend([search_query.limit, search_query.offset])
            
            rows = await self.db.fetch(query, *params)
            
            results = []
            for row in rows:
                consultation_result = ConsultationResult(
                    result_id=row['result_id'],
                    query_id=row['query_id'],
                    response_text=row['response_text'],
                    processing_time=row['processing_time'],
                    cost=row['cost'],
                    timestamp=row['timestamp'],
                    processing_mode=row['processing_mode'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                
                search_result = SearchResult(
                    result=consultation_result,
                    relevance_score=1.0,
                    match_type="exact",
                    matched_fields=["query_text" if row['query_text'] == search_query.query_text else "response_text"]
                )
                
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Exact search failed: {e}")
            raise
    
    async def _semantic_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Perform semantic similarity search (simplified implementation)"""
        try:
            # For now, use enhanced keyword search with similarity scoring
            # In a full implementation, this would use vector embeddings
            
            # Generate query hash for similarity
            query_hash = self._generate_query_hash("semantic", search_query.query_text)
            
            # Find similar query patterns
            similar_patterns = await self.db.fetch("""
                SELECT pattern_hash, normalized_query, query_count, avg_cost, success_rate
                FROM query_patterns
                WHERE normalized_query ILIKE $1
                ORDER BY query_count DESC, success_rate DESC
                LIMIT 10
            """, f"%{self._normalize_query(search_query.query_text)}%")
            
            if not similar_patterns:
                # Fallback to keyword search
                return await self._keyword_search(search_query)
            
            # Get results from similar patterns
            pattern_hashes = [p['pattern_hash'] for p in similar_patterns]
            placeholders = ','.join(f'${i+1}' for i in range(len(pattern_hashes)))
            
            query = f"""
                SELECT 
                    result_id, query_id, user_id, query_text, response_text,
                    processing_time, cost, timestamp, processing_mode, metadata,
                    query_hash
                FROM consultation_results
                WHERE query_hash IN ({placeholders})
                ORDER BY timestamp DESC
                LIMIT ${{len(pattern_hashes) + 1}} OFFSET ${{len(pattern_hashes) + 2}}
            """
            
            params = pattern_hashes + [search_query.limit, search_query.offset]
            rows = await self.db.fetch(query, *params)
            
            results = []
            for row in rows:
                # Calculate similarity score based on pattern match
                pattern_match = next((p for p in similar_patterns if p['pattern_hash'] == row['query_hash']), None)
                similarity_score = 0.8 if pattern_match else 0.5
                
                consultation_result = ConsultationResult(
                    result_id=row['result_id'],
                    query_id=row['query_id'],
                    response_text=row['response_text'],
                    processing_time=row['processing_time'],
                    cost=row['cost'],
                    timestamp=row['timestamp'],
                    processing_mode=row['processing_mode'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                
                search_result = SearchResult(
                    result=consultation_result,
                    relevance_score=similarity_score,
                    similarity_score=similarity_score,
                    match_type="semantic",
                    matched_fields=["query_pattern"]
                )
                
                results.append(search_result)
            
            # Sort by similarity score
            results.sort(key=lambda x: x.similarity_score or 0, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            raise
    
    async def _similar_search(self, search_query: SearchQuery) -> List[SearchResult]:
        """Find similar queries based on patterns and content"""
        try:
            query_hash = self._generate_query_hash("similar", search_query.query_text)
            normalized_query = self._normalize_query(search_query.query_text)
            
            # Find similar queries using multiple criteria
            query = """
                WITH similar_queries AS (
                    SELECT 
                        cr.*,
                        CASE 
                            WHEN cr.query_hash = $1 THEN 1.0
                            WHEN qp.normalized_query ILIKE $2 THEN 0.9
                            WHEN similarity(cr.query_text, $3) > $4 THEN similarity(cr.query_text, $3)
                            ELSE 0.0
                        END as similarity_score
                    FROM consultation_results cr
                    LEFT JOIN query_patterns qp ON cr.query_hash = qp.pattern_hash
                    WHERE (
                        cr.query_hash = $1 
                        OR qp.normalized_query ILIKE $2
                        OR similarity(cr.query_text, $3) > $4
                    )
                )
                SELECT 
                    result_id, query_id, user_id, query_text, response_text,
                    processing_time, cost, timestamp, processing_mode, metadata,
                    similarity_score
                FROM similar_queries
                WHERE similarity_score >= $4
                ORDER BY similarity_score DESC, timestamp DESC
                LIMIT $5 OFFSET $6
            """
            
            params = [
                query_hash,
                f"%{normalized_query}%",
                search_query.query_text,
                search_query.min_similarity,
                search_query.limit,
                search_query.offset
            ]
            
            rows = await self.db.fetch(query, *params)
            
            results = []
            for row in rows:
                consultation_result = ConsultationResult(
                    result_id=row['result_id'],
                    query_id=row['query_id'],
                    response_text=row['response_text'],
                    processing_time=row['processing_time'],
                    cost=row['cost'],
                    timestamp=row['timestamp'],
                    processing_mode=row['processing_mode'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                
                search_result = SearchResult(
                    result=consultation_result,
                    relevance_score=float(row['similarity_score']),
                    similarity_score=float(row['similarity_score']),
                    match_type="similar",
                    matched_fields=["query_text"]
                )
                
                results.append(search_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Similar search failed: {e}")
            # Fallback to keyword search
            return await self._keyword_search(search_query)
    
    async def get_result_by_id(self, result_id: str) -> Optional[ConsultationResult]:
        """Retrieve a specific consultation result by ID"""
        try:
            if not self.db:
                raise StorageError("Database connection not initialized")
            
            row = await self.db.fetchrow("""
                SELECT 
                    result_id, query_id, user_id, query_text, response_text,
                    processing_time, cost, timestamp, processing_mode, metadata
                FROM consultation_results
                WHERE result_id = $1
            """, result_id)
            
            if not row:
                return None
            
            return ConsultationResult(
                result_id=row['result_id'],
                query_id=row['query_id'],
                response_text=row['response_text'],
                processing_time=row['processing_time'],
                cost=row['cost'],
                timestamp=row['timestamp'],
                processing_mode=row['processing_mode'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            
        except Exception as e:
            logger.error(f"Failed to get result by ID {result_id}: {e}")
            raise StorageError(f"Retrieval failed: {str(e)}")
    
    async def get_user_history(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ConsultationResult]:
        """Get consultation history for a specific user"""
        try:
            if not self.db:
                raise StorageError("Database connection not initialized")
            
            rows = await self.db.fetch("""
                SELECT 
                    cr.result_id, cr.query_id, cr.user_id, cr.query_text, cr.response_text,
                    cr.processing_time, cr.cost, cr.timestamp, cr.processing_mode, cr.metadata
                FROM consultation_results cr
                WHERE cr.user_id = $1
                ORDER BY cr.timestamp DESC
                LIMIT $2 OFFSET $3
            """, user_id, limit, offset)
            
            results = []
            for row in rows:
                result = ConsultationResult(
                    result_id=row['result_id'],
                    query_id=row['query_id'],
                    response_text=row['response_text'],
                    processing_time=row['processing_time'],
                    cost=row['cost'],
                    timestamp=row['timestamp'],
                    processing_mode=row['processing_mode'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get user history for {user_id}: {e}")
            raise StorageError(f"History retrieval failed: {str(e)}")
    
    async def get_knowledge_base_stats(self) -> KnowledgeBaseStats:
        """Get comprehensive knowledge base statistics"""
        try:
            if not self.db:
                raise StorageError("Database connection not initialized")
            
            # Check cache first
            if self.stats_cache:
                cache_time, cached_stats = self.stats_cache
                if datetime.utcnow() - cache_time < timedelta(minutes=5):
                    return cached_stats
            
            # Get basic statistics
            basic_stats = await self.db.fetchrow("""
                SELECT 
                    COUNT(*) as total_results,
                    COUNT(DISTINCT user_id) as unique_users,
                    MIN(timestamp) as earliest_date,
                    MAX(timestamp) as latest_date,
                    AVG(cost) as avg_cost_per_query,
                    SUM(cost) as total_cost,
                    AVG(CASE WHEN response_text IS NOT NULL AND response_text != '' THEN 1.0 ELSE 0.0 END) as success_rate,
                    pg_size_pretty(pg_total_relation_size('consultation_results')) as storage_size
                FROM consultation_results
            """)
            
            # Get most common topics (simplified - based on query patterns)
            topic_stats = await self.db.fetch("""
                SELECT normalized_query, query_count
                FROM query_patterns
                ORDER BY query_count DESC
                LIMIT 10
            """)
            
            most_common_topics = [(row['normalized_query'][:50], row['query_count']) for row in topic_stats]
            
            # Parse storage size (remove 'bytes', 'kB', etc.)
            storage_size_str = basic_stats['storage_size'] or '0 bytes'
            storage_size_mb = self._parse_storage_size(storage_size_str)
            
            stats = KnowledgeBaseStats(
                total_results=basic_stats['total_results'] or 0,
                unique_users=basic_stats['unique_users'] or 0,
                date_range=(
                    basic_stats['earliest_date'] or datetime.utcnow(),
                    basic_stats['latest_date'] or datetime.utcnow()
                ),
                avg_cost_per_query=float(basic_stats['avg_cost_per_query'] or 0.0),
                total_cost=float(basic_stats['total_cost'] or 0.0),
                most_common_topics=most_common_topics,
                success_rate=float(basic_stats['success_rate'] or 0.0),
                storage_size_mb=storage_size_mb
            )
            
            # Cache the stats
            self.stats_cache = (datetime.utcnow(), stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get knowledge base stats: {e}")
            raise StorageError(f"Stats retrieval failed: {str(e)}")
    
    def _generate_query_hash(self, query_id: str, query_text: str) -> str:
        """Generate a hash for query similarity detection"""
        try:
            normalized = self._normalize_query(query_text)
            content = f"{query_id}:{normalized}"
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.sha256(f"{query_id}:{query_text}".encode()).hexdigest()[:16]
    
    def _normalize_query(self, query_text: str) -> str:
        """Normalize query text for similarity detection"""
        try:
            # Convert to lowercase and remove extra whitespace
            normalized = ' '.join(query_text.lower().split())
            
            # Remove common stop words and punctuation
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
            words = [word.strip('.,!?;:"()[]{}') for word in normalized.split()]
            words = [word for word in words if word and word not in stop_words]
            
            return ' '.join(words)
        except Exception:
            return query_text.lower().strip()
    
    def _generate_search_cache_key(self, search_query: SearchQuery) -> str:
        """Generate cache key for search query"""
        key_data = {
            'query_text': search_query.query_text,
            'search_type': search_query.search_type.value,
            'user_id': search_query.user_id,
            'date_from': search_query.date_from.isoformat() if search_query.date_from else None,
            'date_to': search_query.date_to.isoformat() if search_query.date_to else None,
            'limit': search_query.limit,
            'offset': search_query.offset,
            'min_similarity': search_query.min_similarity
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_search(self, cache_key: str) -> Optional[List[SearchResult]]:
        """Get cached search results"""
        try:
            if cache_key in self.search_cache:
                cache_time, results = self.search_cache[cache_key]
                if datetime.utcnow() - cache_time < timedelta(seconds=self.cache_ttl):
                    return results
                else:
                    # Remove expired cache entry
                    del self.search_cache[cache_key]
            return None
        except Exception:
            return None
    
    def _cache_search_results(self, cache_key: str, results: List[SearchResult]) -> None:
        """Cache search results"""
        try:
            self.search_cache[cache_key] = (datetime.utcnow(), results)
            
            # Limit cache size
            if len(self.search_cache) > 100:
                # Remove oldest entries
                oldest_keys = sorted(
                    self.search_cache.keys(),
                    key=lambda k: self.search_cache[k][0]
                )[:20]
                for key in oldest_keys:
                    del self.search_cache[key]
        except Exception as e:
            logger.warning(f"Failed to cache search results: {e}")
    
    def _clear_search_cache(self) -> None:
        """Clear search cache"""
        try:
            self.search_cache.clear()
            self.stats_cache = None
        except Exception as e:
            logger.warning(f"Failed to clear search cache: {e}")
    
    def _parse_storage_size(self, size_str: str) -> float:
        """Parse PostgreSQL storage size string to MB"""
        try:
            size_str = size_str.lower().strip()
            
            if 'bytes' in size_str:
                return float(size_str.split()[0]) / (1024 * 1024)
            elif 'kb' in size_str:
                return float(size_str.split()[0]) / 1024
            elif 'mb' in size_str:
                return float(size_str.split()[0])
            elif 'gb' in size_str:
                return float(size_str.split()[0]) * 1024
            else:
                return 0.0
        except Exception:
            return 0.0
    
    async def _cleanup_task(self) -> None:
        """Background task for cache cleanup and maintenance"""
        try:
            while True:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                try:
                    # Clean up expired cache entries
                    current_time = datetime.utcnow()
                    expired_keys = []
                    
                    for key, (cache_time, _) in self.search_cache.items():
                        if current_time - cache_time > timedelta(seconds=self.cache_ttl):
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.search_cache[key]
                    
                    # Clear stats cache if expired
                    if self.stats_cache:
                        cache_time, _ = self.stats_cache
                        if current_time - cache_time > timedelta(minutes=5):
                            self.stats_cache = None
                    
                    self.metrics['last_cleanup'] = current_time.isoformat()
                    
                    if expired_keys:
                        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                        
                except Exception as e:
                    logger.error(f"Error in cleanup task: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
    
    async def get_storage_metrics(self) -> Dict[str, Any]:
        """Get storage performance metrics"""
        try:
            return {
                'storage_metrics': self.metrics.copy(),
                'cache_stats': {
                    'search_cache_size': len(self.search_cache),
                    'stats_cache_active': self.stats_cache is not None,
                    'cache_hit_rate': (
                        self.metrics['cache_hits'] / 
                        max(1, self.metrics['cache_hits'] + self.metrics['cache_misses'])
                    )
                },
                'configuration': {
                    'connection_pool_size': self.connection_pool_size,
                    'query_timeout': self.query_timeout,
                    'cache_ttl': self.cache_ttl,
                    'max_search_results': self.max_search_results,
                    'enable_full_text_search': self.enable_full_text_search
                }
            }
        except Exception as e:
            logger.error(f"Failed to get storage metrics: {e}")
            return {'error': str(e)}
    
    async def get_health_status(self) -> ComponentHealth:
        """Get storage manager health status"""
        try:
            # Check database connection
            if not self.db:
                return ComponentHealth(
                    component="results_storage_manager",
                    status="critical",
                    response_time=0.0,
                    error_message="Database connection not initialized",
                    metadata={},
                    last_check=datetime.utcnow()
                )
            
            # Test database connectivity
            start_time = asyncio.get_event_loop().time()
            try:
                await self.db.fetchval("SELECT 1")
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            except Exception as e:
                return ComponentHealth(
                    component="results_storage_manager",
                    status="critical",
                    response_time=0.0,
                    error_message=f"Database connectivity failed: {str(e)}",
                    metadata={},
                    last_check=datetime.utcnow()
                )
            
            # Determine health status
            error_rate = self.metrics['database_errors'] / max(1, self.metrics['results_stored'] + self.metrics['searches_performed'])
            
            if error_rate > 0.1:
                status = "critical"
                error_message = f"High error rate: {error_rate:.1%}"
            elif error_rate > 0.05:
                status = "degraded"
                error_message = f"Elevated error rate: {error_rate:.1%}"
            elif response_time > 1000:  # 1 second
                status = "degraded"
                error_message = f"Slow database response: {response_time:.0f}ms"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="results_storage_manager",
                status=status,
                response_time=response_time,
                error_message=error_message,
                metadata={
                    'results_stored': self.metrics['results_stored'],
                    'searches_performed': self.metrics['searches_performed'],
                    'error_rate': error_rate,
                    'cache_hit_rate': (
                        self.metrics['cache_hits'] / 
                        max(1, self.metrics['cache_hits'] + self.metrics['cache_misses'])
                    ),
                    'avg_search_time': self.metrics['avg_search_time'],
                    'avg_storage_time': self.metrics['avg_storage_time']
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="results_storage_manager",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def shutdown(self) -> None:
        """Shutdown the results storage manager"""
        try:
            logger.info("Shutting down Results Storage Manager")
            
            # Clear caches
            self._clear_search_cache()
            
            # Close database connection
            if self.db:
                await self.db.close()
                self.db = None
            
            logger.info("Results Storage Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Results Storage Manager shutdown: {e}")


# Global storage manager instance
_results_storage_manager: Optional[ResultsStorageManager] = None


async def get_results_storage_manager() -> ResultsStorageManager:
    """Get the global results storage manager instance"""
    global _results_storage_manager
    if _results_storage_manager is None:
        _results_storage_manager = ResultsStorageManager()
        await _results_storage_manager.initialize()
    return _results_storage_manager