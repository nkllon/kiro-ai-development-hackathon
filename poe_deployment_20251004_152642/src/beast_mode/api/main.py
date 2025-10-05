"""
Simple FastAPI application for Kiro AI Development Hackathon
This provides a basic web server for testing nginx integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import time
from datetime import datetime
from typing import Dict, Any

# Try to import Prometheus client
try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry
    PROMETHEUS_AVAILABLE = True

    # Create registry and metrics
    registry = CollectorRegistry()
    request_count = Counter('systematic_pdca_requests_total', 'Total request count', ['method', 'endpoint', 'status'], registry=registry)
    request_duration = Histogram('systematic_pdca_request_duration_seconds', 'Request duration', ['method', 'endpoint'], registry=registry)
    app_uptime = Gauge('systematic_pdca_uptime_seconds', 'Application uptime in seconds', registry=registry)
    start_time = time.time()
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="Kiro AI Development Hackathon API",
    description="Systematic PDCA Orchestrator API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "systematic-pdca-orchestrator",
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kiro AI Development Hackathon</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { color: #28a745; font-weight: bold; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Kiro AI Development Hackathon</h1>
            <p class="status">✅ Backend API is running</p>
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <strong>GET /health</strong> - Health check endpoint
            </div>
            <div class="endpoint">
                <strong>GET /api/status</strong> - API status information
            </div>
            <div class="endpoint">
                <strong>GET /api/metrics</strong> - System metrics (JSON)
            </div>
            <div class="endpoint">
                <strong>GET /metrics</strong> - Prometheus metrics (text format)
            </div>
            <div class="endpoint">
                <strong>GET /docs</strong> - API documentation (Swagger UI)
            </div>
            <div class="endpoint">
                <strong>GET /redoc</strong> - API documentation (ReDoc)
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get API status information"""
    return {
        "api_status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_path": os.getenv("PYTHONPATH", "/app"),
        "port": os.getenv("PORT", "8080"),
    }


# Metrics endpoint (JSON format for API)
@app.get("/api/metrics")
async def get_metrics():
    """Get basic system metrics in JSON format"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests_processed": 0,  # This would be tracked in a real implementation
            "uptime_seconds": time.time(),
            "memory_usage": "N/A",  # Would need psutil for real metrics
            "cpu_usage": "N/A",
        },
    }


# Prometheus metrics endpoint
@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint in text format"""
    if not PROMETHEUS_AVAILABLE:
        # Return basic metrics in Prometheus text format even without prometheus_client
        uptime = time.time() - start_time if 'start_time' in globals() else time.time()
        metrics_text = f"""# HELP systematic_pdca_uptime_seconds Application uptime in seconds
# TYPE systematic_pdca_uptime_seconds gauge
systematic_pdca_uptime_seconds {uptime}

# HELP systematic_pdca_info Application info
# TYPE systematic_pdca_info gauge
systematic_pdca_info{{version="1.0.0",service="systematic-pdca-orchestrator"}} 1
"""
        return PlainTextResponse(content=metrics_text, media_type="text/plain; version=0.0.4")

    # Update uptime gauge
    app_uptime.set(time.time() - start_time)

    # Generate Prometheus metrics
    metrics = generate_latest(registry)
    return PlainTextResponse(content=metrics, media_type=CONTENT_TYPE_LATEST)


# Test endpoint for nginx routing
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify nginx routing"""
    return {
        "message": "Nginx routing is working correctly",
        "timestamp": datetime.utcnow().isoformat(),
        "headers": {"x-forwarded-for": "N/A", "x-real-ip": "N/A"},
    }


# Error handling
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested resource was not found",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    # This allows running the app directly with python
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, log_level="info")
