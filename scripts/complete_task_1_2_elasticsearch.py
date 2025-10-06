#!/usr/bin/env python3
"""
Complete Task 1.2: Search Engine Integration
Deploy and configure Elasticsearch with AI-powered semantic search.
"""

import os
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def complete_task_1_2() -> Dict[str, Any]:
    """Complete Task 1.2: Search Engine Integration."""
    try:
        logger.info("Starting Task 1.2: Search Engine Integration")
        
        results = {
            "task_id": "task_1_2",
            "task_name": "Search Engine Integration",
            "completion_timestamp": datetime.now().isoformat(),
            "steps": []
        }
        
        # Step 1: Deploy Elasticsearch service
        elasticsearch_result = deploy_elasticsearch()
        results["steps"].append(elasticsearch_result)
        
        # Step 2: Create search indexing pipeline
        indexing_result = create_search_indexing_pipeline()
        results["steps"].append(indexing_result)
        
        # Step 3: Implement AI semantic search
        semantic_result = implement_semantic_search()
        results["steps"].append(semantic_result)
        
        # Step 4: Create search API endpoints
        api_result = create_search_api()
        results["steps"].append(api_result)
        
        # Step 5: Validate implementation
        validation_result = validate_search_implementation()
        results["steps"].append(validation_result)
        
        # Determine overall status
        failed_steps = [step for step in results["steps"] if step.get("status") != "success"]
        results["overall_status"] = "success" if not failed_steps else "partial"
        
        logger.info("Task 1.2 completion finished")
        return results
        
    except Exception as e:
        logger.error(f"Task 1.2 completion failed: {e}")
        return {"status": "error", "message": str(e)}


def deploy_elasticsearch() -> Dict[str, Any]:
    """Deploy Elasticsearch service with proper configuration."""
    try:
        logger.info("Deploying Elasticsearch service")
        
        # Check if Elasticsearch is already running
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:9200/_cluster/health"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                logger.info("Elasticsearch already running")
                return {"status": "success", "message": "Elasticsearch already deployed"}
        except Exception:
            pass
        
        # Start Elasticsearch using Docker Compose
        compose_file = Path("src/cms_platform/docker/docker-compose.yml")
        if compose_file.exists():
            try:
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "up", "-d", "elasticsearch"],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    logger.info("Elasticsearch deployed successfully")
                    return {"status": "success", "message": "Elasticsearch deployed"}
                else:
                    logger.error(f"Docker compose failed: {result.stderr}")
                    return {"status": "error", "message": result.stderr}
            except Exception as e:
                logger.error(f"Docker deployment failed: {e}")
                return {"status": "error", "message": str(e)}
        else:
            logger.warning("Docker compose file not found, creating minimal deployment")
            return {"status": "partial", "message": "Manual Elasticsearch deployment required"}
            
    except Exception as e:
        logger.error(f"Elasticsearch deployment failed: {e}")
        return {"status": "error", "message": str(e)}


def create_search_indexing_pipeline() -> Dict[str, Any]:
    """Create search indexing pipeline for content synchronization."""
    try:
        logger.info("Creating search indexing pipeline")
        
        # Create indexing service
        indexing_service_code = '''#!/usr/bin/env python3
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
'''
        
        # Save indexing service
        indexing_path = Path("src/cms_platform/search/indexing_service.py")
        indexing_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(indexing_path, 'w') as f:
            f.write(indexing_service_code)
        
        logger.info("Search indexing pipeline created")
        return {"status": "success", "message": "Search indexing pipeline implemented"}
        
    except Exception as e:
        logger.error(f"Indexing pipeline creation failed: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    result = complete_task_1_2()
    print("=" * 60)
    print("Task 1.2: Search Engine Integration Results")
    print("=" * 60)
    print(json.dumps(result, indent=2))