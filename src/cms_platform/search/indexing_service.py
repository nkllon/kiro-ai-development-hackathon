#!/usr/bin/env python3
"""
CMS Search Indexing Pipeline
Real-time content indexing for Elasticsearch.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from elasticsearch import AsyncElasticsearch
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CMSSearchIndexer(ReflectiveModule):
    """Search indexing pipeline for CMS content."""
    
    def __init__(self, es_host: str = "localhost:9200"):
        super().__init__()
        self.es_host = es_host
        self.es = None
        self.index_name = "cms_content"
        
    async def initialize(self):
        """Initialize Elasticsearch connection."""
        self.es = AsyncElasticsearch([self.es_host])
        await self._create_index_if_not_exists()
    
    async def _create_index_if_not_exists(self):
        """Create search index with proper mappings."""
        index_mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "standard"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "tags": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "metadata": {"type": "object"},
                    "stakeholder_type": {"type": "keyword"},
                    "content_type": {"type": "keyword"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {
                            "type": "standard",
                            "stopwords": "_english_"
                        }
                    }
                }
            }
        }
        
        if not await self.es.indices.exists(index=self.index_name):
            await self.es.indices.create(index=self.index_name, body=index_mapping)
    
    async def index_content(self, content_id: str, content: Dict[str, Any]) -> bool:
        """Index content for searching."""
        try:
            document = {
                **content,
                "indexed_at": datetime.now().isoformat(),
                "content_id": content_id
            }
            
            await self.es.index(
                index=self.index_name,
                id=content_id,
                document=document
            )
            return True
            
        except Exception as e:
            print(f"Indexing error: {e}")
            return False
    
    async def bulk_index(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Bulk index multiple content items."""
        try:
            actions = []
            for content in contents:
                action = {
                    "_index": self.index_name,
                    "_id": content.get("id", content.get("content_id")),
                    "_source": {
                        **content,
                        "indexed_at": datetime.now().isoformat()
                    }
                }
                actions.append(action)
            
            response = await self.es.bulk(operations=actions)
            return {
                "success": True,
                "indexed_count": len(actions),
                "errors": response.get("errors", [])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close Elasticsearch connection."""
        if self.es:
            await self.es.close()
