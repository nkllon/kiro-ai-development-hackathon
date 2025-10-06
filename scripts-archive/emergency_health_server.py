#!/usr/bin/env python3
"""
🚨 EMERGENCY OBSERVATORY HEALTH SERVER
Minimal FastAPI server to restore Observatory health endpoints
"""

from fastapi import FastAPI
import uvicorn
import asyncio
import json
import os
from datetime import datetime

app = FastAPI(
    title="Observatory Emergency Health Server",
    description="Minimal health endpoints for Observatory recovery",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "emergency",
        "message": "Observatory emergency health server running"
    }

@app.get("/api/observatory/status")
async def observatory_status():
    """Observatory status endpoint"""
    return {
        "status": "degraded",
        "mode": "emergency", 
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "health": "ok",
            "api": "limited",
            "metrics": "unavailable",
            "websocket": "unavailable",
            "database": "unknown"
        },
        "message": "Observatory running in emergency mode - core health endpoints only",
        "uptime": "unknown",
        "version": "emergency-1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Observatory Emergency Health Server",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/api/observatory/status"
        },
        "message": "Emergency health server - limited functionality"
    }

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    return {
        "status": "emergency_mode",
        "metrics_available": False,
        "message": "Metrics unavailable in emergency mode"
    }

async def main():
    """Start the emergency health server"""
    print("🚨 STARTING OBSERVATORY EMERGENCY HEALTH SERVER")
    print("=" * 50)
    print("📊 Providing minimal health endpoints")
    print("🔗 Endpoints available:")
    print("  - GET /health")
    print("  - GET /api/observatory/status") 
    print("  - GET /")
    print("  - GET /metrics")
    print()
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8888,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        print("🚀 Starting server on http://0.0.0.0:8888")
        await server.serve()
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())