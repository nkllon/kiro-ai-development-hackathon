"""Git Webhook Handler for CMS Sync"""

from fastapi import FastAPI, Request, BackgroundTasks
from typing import Dict
import asyncio


app = FastAPI(title="CMS Webhook Handler")


class WebhookHandler:
    """Handle Git webhooks for automatic synchronization."""

    def __init__(self, sync_service):
        self.sync_service = sync_service

    async def handle_push_event(self, payload: Dict) -> Dict:
        """Handle git push webhook event."""
        commits = payload.get('commits', [])
        branch = payload.get('ref', '').split('/')[-1]

        results = {
            'branch': branch,
            'commits_processed': len(commits),
            'files_synced': 0
        }

        for commit in commits:
            added = commit.get('added', [])
            modified = commit.get('modified', [])
            removed = commit.get('removed', [])

            # Sync added and modified files
            for file_path in added + modified:
                if file_path.endswith('.py'):
                    await asyncio.to_thread(self.sync_service.sync_code_file, file_path)
                    results['files_synced'] += 1
                elif file_path.endswith('.md'):
                    await asyncio.to_thread(self.sync_service.sync_document, file_path)
                    results['files_synced'] += 1

        return results


@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    """GitHub webhook endpoint."""
    payload = await request.json()
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'push':
        # Process webhook in background
        background_tasks.add_task(process_push_event, payload)
        return {"status": "accepted", "event": event_type}

    return {"status": "ignored", "event": event_type}


async def process_push_event(payload: Dict):
    """Background task to process push event."""
    # Initialize sync service and handle webhook
    # This would be properly configured with CMS client
    pass
