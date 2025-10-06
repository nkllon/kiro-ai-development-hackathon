#!/usr/bin/env python3
"""
CMS Repository Sync Service
============================

Service for synchronizing repository content with the CMS.
Handles Git webhooks, content extraction, and real-time updates.

Author: Beast Mode Framework
Date: 2025-10-05
Purpose: Repository synchronization for CMS Architecture
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog
import git
import redis.asyncio as redis
import httpx
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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


class WebhookPayload(BaseModel):
    """Git webhook payload model."""
    repository: Dict[str, Any]
    commits: List[Dict[str, Any]]
    ref: str
    before: str
    after: str


class SyncResult(BaseModel):
    """Sync operation result."""
    success: bool
    files_processed: int
    errors: List[str]
    duration_ms: int


class RepositoryChangeHandler(FileSystemEventHandler):
    """File system event handler for repository changes."""
    
    def __init__(self, sync_service):
        self.sync_service = sync_service
        
    def on_modified(self, event):
        if not event.is_directory:
            asyncio.create_task(self.sync_service.process_file_change(event.src_path))


class CMSRepoSyncService(ReflectiveModule):
    """CMS Repository Sync Service with Beast Mode compliance."""
    
    def __init__(self):
        super().__init__()
        self.directus_url = os.getenv('DIRECTUS_URL', 'http://localhost:8055')
        self.directus_token = os.getenv('DIRECTUS_TOKEN')
        self.elasticsearch_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.repositories_path = Path('/app/repositories')
        self.observer: Optional[Observer] = None
        
    async def initialize(self):
        """Initialize service connections."""
        try:
            # Initialize Redis
            self.redis_client = redis.from_url(self.redis_url)
            
            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            # Create repositories directory
            self.repositories_path.mkdir(exist_ok=True)
            
            # Start file system watcher
            self._start_file_watcher()
            
            logger.info("CMS Repository Sync Service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize CMS Repository Sync Service", error=str(e))
            raise
    
    async def shutdown(self):
        """Shutdown service connections."""
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            
            if self.redis_client:
                await self.redis_client.close()
                
            if self.http_client:
                await self.http_client.aclose()
                
            logger.info("CMS Repository Sync Service shutdown completed")
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))
    
    def _start_file_watcher(self):
        """Start file system watcher for repository changes."""
        try:
            self.observer = Observer()
            event_handler = RepositoryChangeHandler(self)
            self.observer.schedule(event_handler, str(self.repositories_path), recursive=True)
            self.observer.start()
            logger.info("File system watcher started")
        except Exception as e:
            logger.error("Failed to start file system watcher", error=str(e))
    
    async def handle_webhook(self, payload: WebhookPayload) -> SyncResult:
        """Handle Git webhook payload."""
        start_time = asyncio.get_event_loop().time()
        errors = []
        files_processed = 0
        
        try:
            repo_name = payload.repository['name']
            repo_url = payload.repository['clone_url']
            
            # Clone or update repository
            repo_path = self.repositories_path / repo_name
            
            if repo_path.exists():
                # Update existing repository
                repo = git.Repo(repo_path)
                repo.remotes.origin.pull()
                logger.info(f"Updated repository: {repo_name}")
            else:
                # Clone new repository
                git.Repo.clone_from(repo_url, repo_path)
                logger.info(f"Cloned repository: {repo_name}")
            
            # Process changed files
            for commit in payload.commits:
                for file_path in commit.get('added', []) + commit.get('modified', []):
                    try:
                        await self.process_file(repo_path / file_path, repo_name)
                        files_processed += 1
                    except Exception as e:
                        errors.append(f"Failed to process {file_path}: {str(e)}")
            
            # Update sync status in Redis
            await self._update_sync_status(repo_name, 'completed', files_processed)
            
        except Exception as e:
            error_msg = f"Webhook processing failed: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        end_time = asyncio.get_event_loop().time()
        duration_ms = int((end_time - start_time) * 1000)
        
        return SyncResult(
            success=len(errors) == 0,
            files_processed=files_processed,
            errors=errors,
            duration_ms=duration_ms
        )
    
    async def process_file(self, file_path: Path, repo_name: str):
        """Process a single file and sync to CMS."""
        try:
            if not file_path.exists():
                return
            
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Extract metadata
            metadata = {
                'repository': repo_name,
                'file_path': str(file_path.relative_to(self.repositories_path / repo_name)),
                'file_type': file_path.suffix,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime
            }
            
            # Determine content type and stakeholder relevance
            content_type, stakeholder_role = self._classify_content(file_path, content)
            
            # Create or update content in Directus
            await self._sync_to_directus(file_path, content, content_type, stakeholder_role, metadata)
            
            # Index in Elasticsearch
            await self._index_in_elasticsearch(file_path, content, content_type, stakeholder_role, metadata)
            
            logger.info(f"Processed file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}", error=str(e))
            raise
    
    def _classify_content(self, file_path: Path, content: str) -> tuple[str, Optional[str]]:
        """Classify content type and determine stakeholder relevance."""
        file_ext = file_path.suffix.lower()
        file_name = file_path.name.lower()
        
        # Determine content type
        if file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
            content_type = 'code'
        elif file_ext in ['.md', '.rst', '.txt']:
            content_type = 'documentation'
        elif file_ext in ['.yml', '.yaml', '.json', '.toml', '.ini']:
            content_type = 'configuration'
        elif file_ext in ['.sql']:
            content_type = 'database'
        elif file_path.name.startswith('Dockerfile') or file_name in ['docker-compose.yml', 'docker-compose.yaml']:
            content_type = 'infrastructure'
        else:
            content_type = 'other'
        
        # Determine stakeholder relevance
        stakeholder_role = None
        
        if 'devops' in file_name or 'deploy' in file_name or content_type == 'infrastructure':
            stakeholder_role = 'devops'
        elif 'cost' in file_name or 'budget' in file_name or 'financial' in file_name:
            stakeholder_role = 'cfo'
        elif 'architecture' in file_name or 'design' in file_name or 'adr' in file_name:
            stakeholder_role = 'architect'
        elif 'strategy' in file_name or 'roadmap' in file_name:
            stakeholder_role = 'cto'
        elif content_type == 'code':
            stakeholder_role = 'developer'
        
        return content_type, stakeholder_role
    
    async def _sync_to_directus(self, file_path: Path, content: str, content_type: str, 
                               stakeholder_role: Optional[str], metadata: Dict[str, Any]):
        """Sync content to Directus CMS."""
        if not self.directus_token:
            logger.warning("Directus token not configured, skipping sync")
            return
        
        headers = {
            'Authorization': f'Bearer {self.directus_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': file_path.name,
            'content': content,
            'content_type': content_type,
            'stakeholder_role': stakeholder_role,
            'metadata': metadata,
            'file_path': str(file_path),
            'status': 'published'
        }
        
        try:
            # Check if item already exists
            search_url = f"{self.directus_url}/items/cms_content"
            search_params = {'filter': {'file_path': {'_eq': str(file_path)}}}
            
            response = await self.http_client.get(search_url, headers=headers, params=search_params)
            
            if response.status_code == 200:
                existing_items = response.json().get('data', [])
                
                if existing_items:
                    # Update existing item
                    item_id = existing_items[0]['id']
                    update_url = f"{self.directus_url}/items/cms_content/{item_id}"
                    await self.http_client.patch(update_url, headers=headers, json=data)
                    logger.info(f"Updated Directus item for {file_path}")
                else:
                    # Create new item
                    create_url = f"{self.directus_url}/items/cms_content"
                    await self.http_client.post(create_url, headers=headers, json=data)
                    logger.info(f"Created Directus item for {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to sync to Directus: {file_path}", error=str(e))
    
    async def _index_in_elasticsearch(self, file_path: Path, content: str, content_type: str,
                                    stakeholder_role: Optional[str], metadata: Dict[str, Any]):
        """Index content in Elasticsearch."""
        try:
            doc = {
                'title': file_path.name,
                'content': content,
                'content_type': content_type,
                'stakeholder_role': stakeholder_role,
                'metadata': metadata,
                'file_path': str(file_path),
                'created_at': metadata.get('modified'),
                'updated_at': metadata.get('modified')
            }
            
            # Use file path as document ID for consistency
            doc_id = str(file_path).replace('/', '_').replace('\\', '_')
            
            index_url = f"{self.elasticsearch_url}/cms_content/_doc/{doc_id}"
            
            response = await self.http_client.put(index_url, json=doc)
            
            if response.status_code in [200, 201]:
                logger.info(f"Indexed in Elasticsearch: {file_path}")
            else:
                logger.error(f"Failed to index in Elasticsearch: {file_path}", 
                           status_code=response.status_code)
                
        except Exception as e:
            logger.error(f"Failed to index in Elasticsearch: {file_path}", error=str(e))
    
    async def _update_sync_status(self, repo_name: str, status: str, files_processed: int):
        """Update sync status in Redis."""
        try:
            status_data = {
                'repository': repo_name,
                'status': status,
                'files_processed': files_processed,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            await self.redis_client.hset(f"sync_status:{repo_name}", mapping=status_data)
            logger.info(f"Updated sync status for {repo_name}: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update sync status for {repo_name}", error=str(e))
    
    async def process_file_change(self, file_path: str):
        """Process file system change event."""
        try:
            path = Path(file_path)
            
            # Determine repository name
            repo_name = None
            for part in path.parts:
                if (self.repositories_path / part).exists():
                    repo_name = part
                    break
            
            if repo_name:
                await self.process_file(path, repo_name)
            
        except Exception as e:
            logger.error(f"Failed to process file change: {file_path}", error=str(e))
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Beast Mode compliance."""
        return {
            "service": "cms-repo-sync",
            "status": "healthy",
            "redis": "connected" if self.redis_client else "disconnected",
            "file_watcher": "running" if self.observer and self.observer.is_alive() else "stopped",
            "repositories_path": str(self.repositories_path),
            "directus_configured": bool(self.directus_token)
        }


# Global service instance
sync_service = CMSRepoSyncService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await sync_service.initialize()
    yield
    # Shutdown
    await sync_service.shutdown()


# Create FastAPI application
app = FastAPI(
    title="CMS Repository Sync Service",
    description="Repository synchronization service for CMS Architecture",
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
    return sync_service.get_health_status()


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    health = sync_service.get_health_status()
    if health["redis"] == "connected":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/webhook", response_model=SyncResult)
async def handle_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """Handle Git webhook."""
    # Process webhook in background
    result = await sync_service.handle_webhook(payload)
    return result


@app.post("/sync/{repo_name}")
async def manual_sync(repo_name: str):
    """Manually trigger repository sync."""
    try:
        repo_path = sync_service.repositories_path / repo_name
        if not repo_path.exists():
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Process all files in repository
        files_processed = 0
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                await sync_service.process_file(file_path, repo_name)
                files_processed += 1
        
        return {"success": True, "files_processed": files_processed}
        
    except Exception as e:
        logger.error(f"Manual sync failed for {repo_name}", error=str(e))
        raise HTTPException(status_code=500, detail="Sync failed")


@app.get("/status/{repo_name}")
async def get_sync_status(repo_name: str):
    """Get sync status for repository."""
    try:
        status_data = await sync_service.redis_client.hgetall(f"sync_status:{repo_name}")
        if not status_data:
            raise HTTPException(status_code=404, detail="Repository status not found")
        
        return status_data
        
    except Exception as e:
        logger.error(f"Failed to get status for {repo_name}", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get status")


@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    return sync_service.get_metrics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8057,
        reload=False,
        log_config=None
    )