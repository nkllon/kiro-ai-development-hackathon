#!/usr/bin/env python3
"""
Git Webhook Handler
Secure webhook processing for repository synchronization.
"""

import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class WebhookPayload(BaseModel):
    """Webhook payload model."""
    repository: Dict[str, Any]
    commits: list = []
    ref: str = ""
    before: str = ""
    after: str = ""


class GitWebhookHandler(ReflectiveModule):
    """Git webhook handler for repository synchronization."""
    
    def __init__(self, webhook_secret: str = None):
        super().__init__()
        self.webhook_secret = webhook_secret or os.getenv("WEBHOOK_SECRET", "")
        self.supported_events = ["push", "pull_request", "release"]
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature for security."""
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def process_webhook(self, payload: WebhookPayload, event_type: str) -> Dict[str, Any]:
        """Process incoming webhook payload."""
        try:
            if event_type not in self.supported_events:
                return {"status": "ignored", "reason": f"Unsupported event: {event_type}"}
            
            repository_info = {
                "name": payload.repository.get("name", ""),
                "url": payload.repository.get("clone_url", ""),
                "branch": payload.ref.replace("refs/heads/", "") if payload.ref else "main",
                "commits": len(payload.commits),
                "event_type": event_type
            }
            
            # Queue synchronization job
            sync_job = await self._queue_sync_job(repository_info)
            
            return {
                "status": "accepted",
                "repository": repository_info["name"],
                "sync_job_id": sync_job["job_id"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _queue_sync_job(self, repository_info: Dict[str, Any]) -> Dict[str, Any]:
        """Queue repository synchronization job."""
        job_id = f"sync_{repository_info['name']}_{int(datetime.now().timestamp())}"
        
        sync_job = {
            "job_id": job_id,
            "repository": repository_info,
            "status": "queued",
            "created_at": datetime.now().isoformat()
        }
        
        # In a real implementation, this would use a job queue like Celery or RQ
        # For now, we'll store in a simple JSON file
        jobs_file = Path("src/cms_platform/sync/sync_jobs.json")
        jobs_file.parent.mkdir(parents=True, exist_ok=True)
        
        if jobs_file.exists():
            with open(jobs_file, 'r') as f:
                jobs = json.load(f)
        else:
            jobs = []
        
        jobs.append(sync_job)
        
        with open(jobs_file, 'w') as f:
            json.dump(jobs, f, indent=2)
        
        return sync_job


# FastAPI webhook endpoints
app = FastAPI(title="Git Webhook Handler", version="1.0.0")
webhook_handler = GitWebhookHandler()


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(None)
):
    """GitHub webhook endpoint."""
    try:
        payload = await request.body()
        
        # Verify signature
        if x_hub_signature_256 and not webhook_handler.verify_signature(payload, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse payload
        payload_data = json.loads(payload)
        webhook_payload = WebhookPayload(**payload_data)
        
        # Process webhook
        result = await webhook_handler.process_webhook(webhook_payload, x_github_event)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_event: str = Header(...),
    x_gitlab_token: str = Header(None)
):
    """GitLab webhook endpoint."""
    try:
        payload = await request.body()
        
        # Verify token
        expected_token = os.getenv("GITLAB_WEBHOOK_TOKEN", "")
        if expected_token and x_gitlab_token != expected_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Parse payload
        payload_data = json.loads(payload)
        webhook_payload = WebhookPayload(**payload_data)
        
        # Process webhook
        result = await webhook_handler.process_webhook(webhook_payload, x_gitlab_event)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/webhook/health")
async def webhook_health():
    """Webhook service health check."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
