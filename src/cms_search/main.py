#!/usr/bin/env python3
"""
CMS Search Service
==================

FastAPI service providing advanced search capabilities for the CMS Architecture.
Integrates with Elasticsearch for full-text and semantic search.

Author: Beast Mode Framework
Date: 2025-10-05
Purpose: CMS search functionality with AI-powered semantic search
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis
from sentence_transformers import SentenceTransformer

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., description="Search query string")
    content_types: Optional[List[str]] = Field(default=None, description="Filter by content types")
    stakeholder_role: Optional[str] = Field(default=None, description="Filter by stakeholder role")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    semantic: bool = Field(default=False, description="Enable semantic search")


class SearchResult(BaseModel):
    """Search result model."""
    id: str
    title: str
    content: str
    content_type: str
    stakeholder_role: Optional[str]
    score: float
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Search response model."""
    results: List[SearchResult]
    total: int
    query: str
    took_ms: int


class CMSSearchService(ReflectiveModule):
    """CMS Search Service with Beast Mode compliance."""
    
    def __init__(self):
        super().__init__()
        self.elasticsearch_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.directus_url = os.getenv('DIRECTUS_URL', 'http://localhost:8055')
        
        self.es_client: Optional[AsyncElasticsearch] = None
        self.redis_client: Optional[redis.Redis] = None
        self.sentence_model: Optional[SentenceTransformer] = None
        
    async def initialize(self):
        """Initialize service connections."""
        try:
            # Initialize Elasticsearch
            self.es_client = AsyncElasticsearch([self.elasticsearch_url])
            
            # Initialize Redis
            self.redis_client = redis.from_url(self.redis_url)
            
            # Initialize sentence transformer for semantic search
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create search indexes if they don't exist
            await self._create_indexes()
            
            logger.info("CMS Search Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize CMS Search Service", error=str(e))
            raise
    
    async def shutdown(self):
        """Shutdown service connections."""
        try:
            if self.es_client:
                await self.es_client.close()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("CMS Search Service shutdown completed")
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))
    
    async def _create_indexes(self):
        """Create Elasticsearch indexes for CMS content."""
        indexes = {
            'cms_content': {
                'mappings': {
                    'properties': {
                        'title': {'type': 'text', 'analyzer': 'standard'},
                        'content': {'type': 'text', 'analyzer': 'standard'},
                        'content_type': {'type': 'keyword'},
                        'stakeholder_role': {'type': 'keyword'},
                        'tags': {'type': 'keyword'},
                        'created_at': {'type': 'date'},
                        'updated_at': {'type': 'date'},
                        'metadata': {'type': 'object'},
                        'embedding': {'type': 'dense_vector', 'dims': 384}
                    }
                }
            }
        }
        
        for index_name, index_config in indexes.items():
            try:
                exists = await self.es_client.indices.exists(index=index_name)
                if not exists:
                    await self.es_client.indices.create(index=index_name, body=index_config)
                    logger.info(f"Created Elasticsearch index: {index_name}")
            except Exception as e:
                logger.error(f"Failed to create index {index_name}", error=str(e))
    
    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform search with optional semantic capabilities."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            if query.semantic and self.sentence_model:
                return await self._semantic_search(query)
            else:
                return await self._text_search(query)
                
        except Exception as e:
            logger.error("Search failed", query=query.query, error=str(e))
            raise HTTPException(status_code=500, detail="Search failed")
        finally:
            end_time = asyncio.get_event_loop().time()
            took_ms = int((end_time - start_time) * 1000)
            logger.info("Search completed", query=query.query, took_ms=took_ms)
    
    async def _text_search(self, query: SearchQuery) -> SearchResponse:
        """Perform traditional text-based search."""
        search_body = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'multi_match': {
                                'query': query.query,
                                'fields': ['title^2', 'content'],
                                'type': 'best_fields',
                                'fuzziness': 'AUTO'
                            }
                        }
                    ],
                    'filter': []
                }
            },
            'size': query.limit,
            'from': query.offset,
            'sort': [{'_score': {'order': 'desc'}}]
        }
        
        # Add filters
        if query.content_types:
            search_body['query']['bool']['filter'].append({
                'terms': {'content_type': query.content_types}
            })
        
        if query.stakeholder_role:
            search_body['query']['bool']['filter'].append({
                'term': {'stakeholder_role': query.stakeholder_role}
            })
        
        response = await self.es_client.search(index='cms_content', body=search_body)
        
        return self._format_search_response(response, query.query, 0)
    
    async def _semantic_search(self, query: SearchQuery) -> SearchResponse:
        """Perform semantic search using vector embeddings."""
        # Generate embedding for query
        query_embedding = self.sentence_model.encode(query.query).tolist()
        
        search_body = {
            'query': {
                'bool': {
                    'should': [
                        # Semantic similarity
                        {
                            'script_score': {
                                'query': {'match_all': {}},
                                'script': {
                                    'source': "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                    'params': {'query_vector': query_embedding}
                                }
                            }
                        },
                        # Text relevance
                        {
                            'multi_match': {
                                'query': query.query,
                                'fields': ['title^2', 'content'],
                                'type': 'best_fields'
                            }
                        }
                    ],
                    'filter': []
                }
            },
            'size': query.limit,
            'from': query.offset
        }
        
        # Add filters
        if query.content_types:
            search_body['query']['bool']['filter'].append({
                'terms': {'content_type': query.content_types}
            })
        
        if query.stakeholder_role:
            search_body['query']['bool']['filter'].append({
                'term': {'stakeholder_role': query.stakeholder_role}
            })
        
        response = await self.es_client.search(index='cms_content', body=search_body)
        
        return self._format_search_response(response, query.query, 0)
    
    def _format_search_response(self, es_response: Dict, query: str, took_ms: int) -> SearchResponse:
        """Format Elasticsearch response to SearchResponse model."""
        results = []
        
        for hit in es_response['hits']['hits']:
            source = hit['_source']
            result = SearchResult(
                id=hit['_id'],
                title=source.get('title', ''),
                content=source.get('content', ''),
                content_type=source.get('content_type', ''),
                stakeholder_role=source.get('stakeholder_role'),
                score=hit['_score'],
                metadata=source.get('metadata', {})
            )
            results.append(result)
        
        return SearchResponse(
            results=results,
            total=es_response['hits']['total']['value'],
            query=query,
            took_ms=took_ms
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Beast Mode compliance."""
        return {
            "service": "cms-search",
            "status": "healthy",
            "elasticsearch": "connected" if self.es_client else "disconnected",
            "redis": "connected" if self.redis_client else "disconnected",
            "semantic_model": "loaded" if self.sentence_model else "not_loaded"
        }


# Global service instance
search_service = CMSSearchService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await search_service.initialize()
    yield
    # Shutdown
    await search_service.shutdown()


# Create FastAPI application
app = FastAPI(
    title="CMS Search Service",
    description="Advanced search service for CMS Architecture with semantic capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return search_service.get_health_status()


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    health = search_service.get_health_status()
    if health["elasticsearch"] == "connected":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/search", response_model=SearchResponse)
async def search_content(query: SearchQuery):
    """Search CMS content."""
    return await search_service.search(query)


@app.get("/search", response_model=SearchResponse)
async def search_content_get(
    q: str = Query(..., description="Search query"),
    content_types: Optional[str] = Query(None, description="Comma-separated content types"),
    stakeholder_role: Optional[str] = Query(None, description="Stakeholder role filter"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    semantic: bool = Query(False, description="Enable semantic search")
):
    """Search CMS content via GET request."""
    query_obj = SearchQuery(
        query=q,
        content_types=content_types.split(',') if content_types else None,
        stakeholder_role=stakeholder_role,
        limit=limit,
        offset=offset,
        semantic=semantic
    )
    return await search_service.search(query_obj)


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return search_service.get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8056,
        reload=False,
        log_config=None
    )