#!/usr/bin/env python3
"""
Sync Service Monitoring and Alerting
Monitoring and alerting for repository synchronization.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class SyncMonitor(ReflectiveModule):
    """Monitoring and alerting for sync service."""
    
    def __init__(self):
        super().__init__()
        self.alert_thresholds = {
            "max_failed_jobs": 5,
            "max_processing_time": 3600,  # 1 hour
            "max_queue_size": 50
        }
    
    async def check_sync_health(self) -> Dict[str, Any]:
        """Check overall sync service health."""
        try:
            stats = await self._get_sync_statistics()
            alerts = await self._check_alerts(stats)
            
            health_status = {
                "status": "healthy" if not alerts else "warning",
                "statistics": stats,
                "alerts": alerts,
                "timestamp": datetime.now().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_sync_statistics(self) -> Dict[str, Any]:
        """Get sync service statistics."""
        jobs_file = Path("src/cms_platform/sync/sync_jobs.json")
        
        if not jobs_file.exists():
            return {"total_jobs": 0, "completed": 0, "failed": 0, "pending": 0}
        
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
        
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_jobs = [
            job for job in jobs 
            if datetime.fromisoformat(job.get("created_at", "1970-01-01")) > last_24h
        ]
        
        stats = {
            "total_jobs": len(jobs),
            "recent_jobs_24h": len(recent_jobs),
            "completed": len([j for j in jobs if j.get("status") == "completed"]),
            "failed": len([j for j in jobs if j.get("status") == "failed"]),
            "pending": len([j for j in jobs if j.get("status") == "queued"]),
            "processing": len([j for j in jobs if j.get("status") == "processing"]),
            "success_rate": 0
        }
        
        if stats["total_jobs"] > 0:
            stats["success_rate"] = (stats["completed"] / stats["total_jobs"]) * 100
        
        return stats
    
    async def _check_alerts(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions."""
        alerts = []
        
        # Check failed jobs threshold
        if stats["failed"] > self.alert_thresholds["max_failed_jobs"]:
            alerts.append({
                "type": "high_failure_rate",
                "severity": "warning",
                "message": f"High number of failed jobs: {stats['failed']}",
                "threshold": self.alert_thresholds["max_failed_jobs"]
            })
        
        # Check queue size
        if stats["pending"] > self.alert_thresholds["max_queue_size"]:
            alerts.append({
                "type": "large_queue",
                "severity": "warning", 
                "message": f"Large sync queue: {stats['pending']} pending jobs",
                "threshold": self.alert_thresholds["max_queue_size"]
            })
        
        # Check success rate
        if stats["success_rate"] < 80 and stats["total_jobs"] > 10:
            alerts.append({
                "type": "low_success_rate",
                "severity": "critical",
                "message": f"Low success rate: {stats['success_rate']:.1f}%",
                "threshold": "80%"
            })
        
        return alerts
    
    async def get_sync_metrics(self) -> Dict[str, Any]:
        """Get detailed sync metrics for monitoring."""
        try:
            health = await self.check_sync_health()
            
            # Convert to Prometheus-style metrics
            metrics = []
            stats = health.get("statistics", {})
            
            metrics.extend([
                f"cms_sync_jobs_total {stats.get('total_jobs', 0)}",
                f"cms_sync_jobs_completed {stats.get('completed', 0)}",
                f"cms_sync_jobs_failed {stats.get('failed', 0)}",
                f"cms_sync_jobs_pending {stats.get('pending', 0)}",
                f"cms_sync_jobs_processing {stats.get('processing', 0)}",
                f"cms_sync_success_rate {stats.get('success_rate', 0)}",
                f"cms_sync_health_status {1 if health['status'] == 'healthy' else 0}"
            ])
            
            return {
                "metrics": metrics,
                "health": health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
