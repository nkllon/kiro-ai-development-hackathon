#!/bin/bash

# Nginx Docker Service Manager for Kiro AI Development Hackathon
# This script manages the nginx service and provides easy commands for development

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
NGINX_SERVICE="nginx"
BACKEND_SERVICE="systematic-pdca-orchestrator"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        error "Docker and docker-compose are required but not installed."
        exit 1
    fi
    
    # Use docker compose (newer) if available, otherwise docker-compose
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    log "Using: $COMPOSE_CMD"
}

# Build nginx service
build_nginx() {
    log "Building nginx service..."
    $COMPOSE_CMD -f $COMPOSE_FILE build $NGINX_SERVICE
    success "Nginx service built successfully"
}

# Start all services
start_services() {
    log "Starting all services..."
    $COMPOSE_CMD -f $COMPOSE_FILE up -d
    success "Services started successfully"
}

# Start only nginx service
start_nginx() {
    log "Starting nginx service..."
    $COMPOSE_CMD -f $COMPOSE_FILE up -d $NGINX_SERVICE
    success "Nginx service started successfully"
}

# Stop all services
stop_services() {
    log "Stopping all services..."
    $COMPOSE_CMD -f $COMPOSE_FILE down
    success "Services stopped successfully"
}

# Stop only nginx service
stop_nginx() {
    log "Stopping nginx service..."
    $COMPOSE_CMD -f $COMPOSE_FILE stop $NGINX_SERVICE
    success "Nginx service stopped successfully"
}

# Restart nginx service
restart_nginx() {
    log "Restarting nginx service..."
    $COMPOSE_CMD -f $COMPOSE_FILE restart $NGINX_SERVICE
    success "Nginx service restarted successfully"
}

# Show service status
status() {
    log "Checking service status..."
    $COMPOSE_CMD -f $COMPOSE_FILE ps
}

# Show nginx logs
logs_nginx() {
    log "Showing nginx logs..."
    $COMPOSE_CMD -f $COMPOSE_FILE logs -f $NGINX_SERVICE
}

# Show all logs
logs_all() {
    log "Showing all service logs..."
    $COMPOSE_CMD -f $COMPOSE_FILE logs -f
}

# Test nginx health
test_nginx() {
    log "Testing nginx health..."
    
    # Wait a moment for services to be ready
    sleep 5
    
    # Test nginx health endpoint
    if curl -f http://localhost/nginx-health &> /dev/null; then
        success "Nginx health check passed"
    else
        error "Nginx health check failed"
        return 1
    fi
    
    # Test backend health through nginx
    if curl -f http://localhost/health &> /dev/null; then
        success "Backend health check through nginx passed"
    else
        warning "Backend health check through nginx failed (backend might not be ready yet)"
    fi
    
    # Test main page
    if curl -f http://localhost/ &> /dev/null; then
        success "Main page accessible through nginx"
    else
        error "Main page not accessible through nginx"
        return 1
    fi
}

# Clean up (remove containers and volumes)
cleanup() {
    log "Cleaning up containers and volumes..."
    $COMPOSE_CMD -f $COMPOSE_FILE down -v --remove-orphans
    success "Cleanup completed"
}

# Show help
show_help() {
    echo "Nginx Docker Service Manager for Kiro AI Development Hackathon"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build nginx service"
    echo "  start       Start all services"
    echo "  start-nginx Start only nginx service"
    echo "  stop        Stop all services"
    echo "  stop-nginx  Stop only nginx service"
    echo "  restart     Restart nginx service"
    echo "  status      Show service status"
    echo "  logs        Show nginx logs"
    echo "  logs-all    Show all service logs"
    echo "  test        Test nginx health and connectivity"
    echo "  cleanup     Remove containers and volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 start    # Build and start all services"
    echo "  $0 test                 # Test nginx functionality"
    echo "  $0 logs                 # View nginx logs"
}

# Main script logic
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Check prerequisites
    check_docker_compose
    
    case "${1:-help}" in
        build)
            build_nginx
            ;;
        start)
            start_services
            ;;
        start-nginx)
            start_nginx
            ;;
        stop)
            stop_services
            ;;
        stop-nginx)
            stop_nginx
            ;;
        restart)
            restart_nginx
            ;;
        status)
            status
            ;;
        logs)
            logs_nginx
            ;;
        logs-all)
            logs_all
            ;;
        test)
            test_nginx
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
