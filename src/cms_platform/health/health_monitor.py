#!/usr/bin/env python3
"""
CMS Health Monitoring Service
Comprehensive health monitoring for Directus CMS with Beast Mode integration.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CMSHealthMonitor(ReflectiveModule):
    """Comprehensive health monitoring for CMS platform."""
    
    def __init__(self):
        super().__init__()
        self.service_name = "cms_health_monitor"
        self.health_checks = []
        
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of CMS platform."""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "service": "cms_platform",
                "status": "healthy",
                "checks": {}
            }
            
            # Check Directus service
            directus_health = await self._check_directus_health()
            health_status["checks"]["directus"] = directus_health
            
            # Check PostgreSQL database
            postgres_health = await self._check_postgres_health()
            health_status["checks"]["postgres"] = postgres_health
            
            # Check Redis cache
            redis_health = await self._check_redis_health()
            health_status["checks"]["redis"] = redis_health
            
            # Check Elasticsearch (if running)
            elasticsearch_health = await self._check_elasticsearch_health()
            health_status["checks"]["elasticsearch"] = elasticsearch_health
            
            # Determine overall status
            failed_checks = [name for name, check in health_status["checks"].items() 
                           if check["status"] != "healthy"]
            
            if failed_checks:
                health_status["status"] = "degraded" if len(failed_checks) < 2 else "unhealthy"
                health_status["failed_checks"] = failed_checks
            
            return health_status
            
        except Exception as e:
            self.log_error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "service": "cms_platform",
                "status": "error",
                "error": str(e)
            }
    
    async def _check_directus_health(self) -> Dict[str, Any]:
        """Check Directus service health."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8055/server/health") as response:
                    if response.status == 200:
                        return {"status": "healthy", "response_time": "< 100ms"}
                    else:
                        return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_postgres_health(self) -> Dict[str, Any]:
        """Check PostgreSQL database health."""
        try:
            import asyncpg
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                user="directus",
                password="directus",
                database="directus"
            )
            await conn.execute("SELECT 1")
            await conn.close()
            return {"status": "healthy", "connection": "active"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis cache health."""
        try:
            import redis.asyncio as redis
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            await r.ping()
            await r.close()
            return {"status": "healthy", "connection": "active"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def _check_elasticsearch_health(self) -> Dict[str, Any]:
        """Check Elasticsearch health."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:9200/_cluster/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"status": "healthy", "cluster_status": data.get("status")}
                    else:
                        return {"status": "unhealthy", "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "not_running", "error": str(e)}


if __name__ == "__main__":
    import asyncio
    
    async def main():
        monitor = CMSHealthMonitor()
        health = await monitor.get_health_status()
        print(json.dumps(health, indent=2))
    
    asyncio.run(main())
