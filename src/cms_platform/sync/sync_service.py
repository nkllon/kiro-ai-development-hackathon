#!/usr/bin/env python3
"""
Repository Synchronization Service
Real-time synchronization with change detection and error handling.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from .content_processor import ContentProcessor


class RepositorySyncService(ReflectiveModule):
    """Repository synchronization service with real-time capabilities."""
    
    def __init__(self):
        super().__init__()
        self.content_processor = ContentProcessor()
        self.sync_jobs = {}
        self.sync_status = "idle"
        self.last_sync = None
    
    async def start_sync_service(self):
        """Start the synchronization service."""
        self.sync_status = "running"
        
        while self.sync_status == "running":
            try:
                # Check for pending sync jobs
                pending_jobs = await self._get_pending_jobs()
                
                for job in pending_jobs:
                    await self._process_sync_job(job)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Sync service error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def stop_sync_service(self):
        """Stop the synchronization service."""
        self.sync_status = "stopping"
    
    async def _get_pending_jobs(self) -> List[Dict[str, Any]]:
        """Get pending synchronization jobs."""
        jobs_file = Path("src/cms_platform/sync/sync_jobs.json")
        
        if not jobs_file.exists():
            return []
        
        try:
            with open(jobs_file, 'r') as f:
                all_jobs = json.load(f)
            
            # Filter pending jobs
            pending_jobs = [job for job in all_jobs if job.get("status") == "queued"]
            return pending_jobs
            
        except Exception as e:
            print(f"Error reading sync jobs: {e}")
            return []
    
    async def _process_sync_job(self, job: Dict[str, Any]):
        """Process a synchronization job."""
        try:
            job_id = job["job_id"]
            repository_info = job["repository"]
            
            print(f"Processing sync job: {job_id}")
            
            # Update job status
            await self._update_job_status(job_id, "processing")
            
            # Process repository content
            result = await self.content_processor.process_repository(repository_info)
            
            if result["status"] == "success":
                await self._update_job_status(job_id, "completed", result)
                print(f"Sync job completed: {job_id}")
            else:
                await self._update_job_status(job_id, "failed", result)
                print(f"Sync job failed: {job_id} - {result.get('message', 'Unknown error')}")
            
        except Exception as e:
            await self._update_job_status(job["job_id"], "failed", {"error": str(e)})
            print(f"Sync job error: {job['job_id']} - {e}")
    
    async def _update_job_status(self, job_id: str, status: str, result: Dict[str, Any] = None):
        """Update job status in storage."""
        jobs_file = Path("src/cms_platform/sync/sync_jobs.json")
        
        if not jobs_file.exists():
            return
        
        try:
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
            
            # Find and update job
            for job in jobs:
                if job["job_id"] == job_id:
                    job["status"] = status
                    job["updated_at"] = datetime.now().isoformat()
                    if result:
                        job["result"] = result
                    break
            
            # Save updated jobs
            with open(jobs_file, 'w') as f:
                json.dump(jobs, f, indent=2)
            
        except Exception as e:
            print(f"Error updating job status: {e}")
    
    async def get_sync_statistics(self) -> Dict[str, Any]:
        """Get synchronization statistics."""
        jobs_file = Path("src/cms_platform/sync/sync_jobs.json")
        
        if not jobs_file.exists():
            return {"total_jobs": 0, "completed": 0, "failed": 0, "pending": 0}
        
        try:
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
            
            stats = {
                "total_jobs": len(jobs),
                "completed": len([j for j in jobs if j.get("status") == "completed"]),
                "failed": len([j for j in jobs if j.get("status") == "failed"]),
                "pending": len([j for j in jobs if j.get("status") == "queued"]),
                "processing": len([j for j in jobs if j.get("status") == "processing"]),
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    async def manual_sync_repository(self, repository_url: str, branch: str = "main") -> Dict[str, Any]:
        """Manually trigger repository synchronization."""
        try:
            repository_info = {
                "name": repository_url.split("/")[-1].replace(".git", ""),
                "url": repository_url,
                "branch": branch,
                "event_type": "manual"
            }
            
            # Process immediately
            result = await self.content_processor.process_repository(repository_info)
            
            return {
                "status": "success",
                "repository": repository_info["name"],
                "sync_result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
