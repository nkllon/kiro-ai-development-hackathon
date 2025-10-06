#!/usr/bin/env python3
"""
Minimal Observatory Health Server - Emergency Fallback
Provides basic health endpoints when full Observatory fails
"""

from fastapi import FastAPI
import uvicorn
import asyncio
import sys
import os

app = FastAPI(title="Observatory Health Server - Emergency Mode")

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "emergency", "message": "Observatory running in minimal mode"}

@app.get("/ready")
async def ready():
    return {"status": "ready", "mode": "emergency", "message": "Observatory minimal mode ready"}

@app.get("/metrics")
async def metrics():
    return {"status": "unavailable", "mode": "emergency", "message": "Metrics unavailable in minimal mode"}

@app.get("/api/observatory/status") 
async def status():
    return {
        "status": "degraded",
        "mode": "emergency",
        "services": {
            "health": "ok",
            "metrics": "unavailable", 
            "websocket": "unavailable"
        },
        "message": "Observatory running in emergency mode - limited functionality"
    }

@app.get("/")
async def root():
    return {"message": "Observatory Emergency Health Server", "endpoints": ["/health", "/ready", "/metrics", "/api/observatory/status"]}

async def main():
    print("🚨 STARTING OBSERVATORY EMERGENCY HEALTH SERVER")
    print("📊 Limited functionality - health endpoints only")
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=8888,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
