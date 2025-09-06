#!/bin/bash
# Systematic PDCA Orchestrator - Local Development Server
# Runs exactly like Cloud Run but with hot reload for development

set -e

echo "🚀 Starting Systematic PDCA Orchestrator - Local Development Mode"
echo "================================================================="

# Check if Docker is running
if ! docker info &>/dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "project_model_registry.json" ]]; then
    echo "❌ project_model_registry.json not found. Run from project root."
    exit 1
fi

# Development mode options
MONITORING=${1:-"false"}
HOT_RELOAD=${2:-"true"}

echo "📋 Configuration:"
echo "   Hot Reload: $HOT_RELOAD"
echo "   Monitoring: $MONITORING"
echo "   Port: 8080"
echo "   Environment: development"

if [[ "$HOT_RELOAD" == "true" ]]; then
    echo ""
    echo "🔥 Hot Reload Mode:"
    echo "   Source code changes will be reflected immediately"
    echo "   Edit files in src/ and see changes without restart"
    
    # Run with uvicorn directly for hot reload
    echo ""
    echo "🚀 Starting development server with hot reload..."
    
    # Install dependencies if needed
    if [[ ! -d ".venv" ]]; then
        echo "📦 Installing dependencies..."
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    else
        source .venv/bin/activate
    fi
    
    # Set environment variables
    export PYTHONPATH=$(pwd)
    export ENVIRONMENT=development
    export LOG_LEVEL=DEBUG
    export PORT=8080
    
    echo "🌐 Starting FastAPI development server..."
    echo "   URL: http://localhost:8080"
    echo "   API Docs: http://localhost:8080/docs"
    echo "   Health: http://localhost:8080/health"
    echo ""
    echo "Press Ctrl+C to stop"
    
    # Start with hot reload
    uvicorn src.beast_mode.api.main:app --reload --host 0.0.0.0 --port 8080
    
else
    echo ""
    echo "🐳 Container Mode (Production-like):"
    echo "   Runs in Docker container exactly like Cloud Run"
    echo "   No hot reload, but identical to production"
    
    # Docker Compose profiles
    COMPOSE_PROFILES=""
    if [[ "$MONITORING" == "true" ]]; then
        COMPOSE_PROFILES="--profile monitoring"
        echo "   Monitoring: Prometheus (9090) + Grafana (3000)"
    fi
    
    echo ""
    echo "🚀 Starting with Docker Compose..."
    
    # Start services
    docker-compose -f deployment/local/docker-compose.yml up --build $COMPOSE_PROFILES
fi