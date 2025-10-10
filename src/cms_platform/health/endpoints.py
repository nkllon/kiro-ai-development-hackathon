#!/usr/bin/env python3
"""
CMS Health Endpoints
FastAPI endpoints for health monitoring and metrics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import asyncio
from datetime import datetime

from .health_monitor import CMSHealthMonitor

app = FastAPI(title="CMS Health API", version="1.0.0")
health_monitor = CMSHealthMonitor()


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all service status."""
    try:
        health_status = await health_monitor.get_health_status()
        return JSONResponse(content=health_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/Docker."""
    try:
        health_status = await health_monitor.get_health_status()
        if health_status["status"] in ["healthy", "degraded"]:
            return {"status": "ready", "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    try:
        health_status = await health_monitor.get_health_status()
        
        # Convert to Prometheus format
        metrics = []
        metrics.append("# HELP cms_health_status CMS service health status")
        metrics.append("# TYPE cms_health_status gauge")
        
        status_value = 1 if health_status["status"] == "healthy" else 0
        metrics.append(f'cms_health_status{{service="cms_platform"}} {status_value}')
        
        for service, check in health_status.get("checks", {}).items():
            service_value = 1 if check["status"] == "healthy" else 0
            metrics.append(f'cms_service_health{{service="{service}"}} {service_value}')
        
        return "\n".join(metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
