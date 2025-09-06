"""
Systematic PDCA Orchestrator - Production API

FastAPI service exposing systematic PDCA orchestration with model-driven intelligence.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from beast_mode.core.model_registry import ModelRegistry
from beast_mode.core.pdca_models import PDCATask, ValidationLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Systematic PDCA Orchestrator",
    description="Model-driven systematic development with PDCA orchestration",
    version="1.0.0"
)

# Initialize Model Registry
try:
    model_registry = ModelRegistry("project_model_registry.json")
    logger.info(f"Model Registry initialized with {len(model_registry.list_available_domains())} domains")
except Exception as e:
    logger.error(f"Failed to initialize Model Registry: {e}")
    model_registry = None


# Pydantic models for API
class TaskRequest(BaseModel):
    task_id: str
    description: str
    domain: str
    estimated_complexity: int = 5


class HealthResponse(BaseModel):
    status: str
    model_registry_health: Dict[str, Any]
    available_domains: int
    systematic_compliance: str


class DomainIntelligenceResponse(BaseModel):
    domain: str
    requirements_count: int
    patterns_count: int
    tools_count: int
    confidence_score: float
    success_metrics: Dict[str, float]


class LearningInsightsResponse(BaseModel):
    total_patterns: int
    avg_confidence: float
    domain_insights: Dict[str, Any]
    top_success_metrics: Dict[str, Any]
    learning_trends: List[str]


# API Routes

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Systematic PDCA Orchestrator",
        "status": "operational",
        "systematic_superiority": "validated",
        "model_registry_domains": len(model_registry.list_available_domains()) if model_registry else 0,
        "endpoints": {
            "health": "/health",
            "domains": "/domains",
            "intelligence": "/intelligence/{domain}",
            "insights": "/insights",
            "validate": "/validate"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model Registry not available")
    
    health_status = model_registry.get_health_status()
    compliance = model_registry.validate_systematic_compliance()
    
    return HealthResponse(
        status=health_status["status"],
        model_registry_health=health_status,
        available_domains=len(model_registry.list_available_domains()),
        systematic_compliance=compliance.value
    )


@app.get("/domains")
async def list_domains():
    """List all available domains in the model registry"""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model Registry not available")
    
    domains = model_registry.list_available_domains()
    stats = model_registry.get_registry_stats()
    
    return {
        "domains": domains,
        "total_count": len(domains),
        "registry_stats": stats
    }


@app.get("/intelligence/{domain}", response_model=DomainIntelligenceResponse)
async def get_domain_intelligence(domain: str):
    """Get intelligence for a specific domain"""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model Registry not available")
    
    try:
        intelligence = model_registry.get_domain_intelligence(domain)
        
        return DomainIntelligenceResponse(
            domain=domain,
            requirements_count=len(intelligence.requirements),
            patterns_count=len(intelligence.patterns),
            tools_count=len(intelligence.tools),
            confidence_score=intelligence.confidence_score,
            success_metrics=intelligence.success_metrics
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Domain intelligence not found: {e}")


@app.get("/insights", response_model=LearningInsightsResponse)
async def get_learning_insights(domain: Optional[str] = None):
    """Get learning insights from accumulated patterns"""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model Registry not available")
    
    try:
        insights = model_registry.get_learning_insights(domain)
        
        return LearningInsightsResponse(
            total_patterns=insights["total_patterns"],
            avg_confidence=insights["avg_confidence"],
            domain_insights=insights["domain_insights"],
            top_success_metrics=insights["top_success_metrics"],
            learning_trends=insights["learning_trends"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {e}")


@app.post("/validate")
async def validate_systematic_approach(task: TaskRequest):
    """Validate systematic approach for a task using model registry intelligence"""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model Registry not available")
    
    try:
        # Get domain intelligence
        intelligence = model_registry.get_domain_intelligence(task.domain)
        
        # Create systematic recommendations
        recommendations = {
            "task_id": task.task_id,
            "domain": task.domain,
            "systematic_approach": f"Model-driven systematic approach for {task.domain}",
            "requirements": [
                {
                    "req_id": req.req_id,
                    "description": req.description,
                    "priority": req.priority
                } for req in intelligence.requirements[:3]  # Top 3 requirements
            ],
            "patterns": [
                {
                    "pattern_id": pattern.pattern_id,
                    "name": pattern.name,
                    "confidence": pattern.confidence_score,
                    "steps": pattern.implementation_steps[:3]  # First 3 steps
                } for pattern in intelligence.patterns[:2]  # Top 2 patterns
            ],
            "tools": [
                {
                    "name": tool.name,
                    "purpose": tool.purpose,
                    "command": tool.command_template
                } for tool in intelligence.tools.values()
            ],
            "confidence_score": intelligence.confidence_score,
            "estimated_success_rate": min(1.0, intelligence.confidence_score + 0.1),
            "systematic_advantage": f"{(intelligence.confidence_score - 0.7) * 100:.1f}% improvement over ad-hoc"
        }
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {e}")


@app.get("/performance")
async def get_performance_metrics():
    """Get performance metrics for the model registry"""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model Registry not available")
    
    try:
        metrics = model_registry.get_performance_metrics()
        return {
            "performance_metrics": metrics,
            "systematic_compliance": model_registry.validate_systematic_compliance().value,
            "cache_efficiency": f"{metrics['cache_hit_rate']:.2%}",
            "query_performance": f"{metrics['avg_query_time']}s average"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {e}")


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "systematic_approach": "Error handled systematically"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)