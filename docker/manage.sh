#!/bin/bash
# Docker Management Script for Beast Mode AI Development Framework
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="beast-mode"
COMPOSE_FILE="docker-compose.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Build images
build() {
    local env=${1:-production}
    
    log_info "Building Docker images for $env environment..."
    
    if [ "$env" = "development" ]; then
        docker-compose -f $DEV_COMPOSE_FILE build
    else
        docker-compose -f $COMPOSE_FILE build
    fi
    
    log_success "Docker images built successfully"
}

# Start services
start() {
    local env=${1:-production}
    
    log_info "Starting $PROJECT_NAME services ($env environment)..."
    
    if [ "$env" = "development" ]; then
        docker-compose -f $DEV_COMPOSE_FILE up -d
    else
        docker-compose -f $COMPOSE_FILE up -d
    fi
    
    log_success "Services started successfully"
    
    # Show service URLs
    echo
    log_info "Service URLs:"
    echo "  🌐 Observatory: http://localhost:8080"
    echo "  📊 Prometheus: http://localhost:9090"
    echo "  📈 Grafana: http://localhost:3000 (admin/admin)"
    
    if [ "$env" = "development" ]; then
        echo "  📓 Jupyter: http://localhost:8888"
        echo "  📧 Mailhog: http://localhost:8025"
        echo "  🗄️  PostgreSQL: localhost:5432"
    fi
}

# Stop services
stop() {
    local env=${1:-production}
    
    log_info "Stopping $PROJECT_NAME services..."
    
    if [ "$env" = "development" ]; then
        docker-compose -f $DEV_COMPOSE_FILE down
    else
        docker-compose -f $COMPOSE_FILE down
    fi
    
    log_success "Services stopped successfully"
}

# Restart services
restart() {
    local env=${1:-production}
    
    log_info "Restarting $PROJECT_NAME services..."
    stop $env
    start $env
}

# Show logs
logs() {
    local env=${1:-production}
    local service=${2:-}
    
    if [ "$env" = "development" ]; then
        if [ -n "$service" ]; then
            docker-compose -f $DEV_COMPOSE_FILE logs -f $service
        else
            docker-compose -f $DEV_COMPOSE_FILE logs -f
        fi
    else
        if [ -n "$service" ]; then
            docker-compose -f $COMPOSE_FILE logs -f $service
        else
            docker-compose -f $COMPOSE_FILE logs -f
        fi
    fi
}

# Show status
status() {
    local env=${1:-production}
    
    log_info "Service status:"
    
    if [ "$env" = "development" ]; then
        docker-compose -f $DEV_COMPOSE_FILE ps
    else
        docker-compose -f $COMPOSE_FILE ps
    fi
}

# Execute command in container
exec_cmd() {
    local env=${1:-production}
    local service=${2:-beast-mode}
    shift 2
    local cmd="$@"
    
    if [ "$env" = "development" ]; then
        service="${service}-dev"
    fi
    
    docker-compose -f $([ "$env" = "development" ] && echo $DEV_COMPOSE_FILE || echo $COMPOSE_FILE) exec $service $cmd
}

# Clean up
cleanup() {
    local env=${1:-production}
    
    log_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up $PROJECT_NAME environment..."
        
        if [ "$env" = "development" ]; then
            docker-compose -f $DEV_COMPOSE_FILE down -v --remove-orphans
        else
            docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        fi
        
        # Remove unused images
        docker image prune -f
        
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Health check
health() {
    local env=${1:-production}
    
    log_info "Checking service health..."
    
    # Check if services are running
    if [ "$env" = "development" ]; then
        running_services=$(docker-compose -f $DEV_COMPOSE_FILE ps --services --filter "status=running")
    else
        running_services=$(docker-compose -f $COMPOSE_FILE ps --services --filter "status=running")
    fi
    
    if [ -z "$running_services" ]; then
        log_error "No services are running"
        exit 1
    fi
    
    # Test service endpoints
    log_info "Testing service endpoints..."
    
    # Test Observatory
    if curl -f -s http://localhost:8080/health >/dev/null 2>&1; then
        log_success "Observatory is healthy"
    else
        log_warning "Observatory health check failed"
    fi
    
    # Test Prometheus
    if curl -f -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
        log_success "Prometheus is healthy"
    else
        log_warning "Prometheus health check failed"
    fi
    
    # Test Grafana
    if curl -f -s http://localhost:3000/api/health >/dev/null 2>&1; then
        log_success "Grafana is healthy"
    else
        log_warning "Grafana health check failed"
    fi
    
    log_success "Health check completed"
}

# Show help
show_help() {
    echo "Beast Mode AI Development Framework - Docker Management"
    echo
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo
    echo "Commands:"
    echo "  build [env]           Build Docker images (env: production|development)"
    echo "  start [env]           Start services (env: production|development)"
    echo "  stop [env]            Stop services"
    echo "  restart [env]         Restart services"
    echo "  logs [env] [service]  Show logs (optionally for specific service)"
    echo "  status [env]          Show service status"
    echo "  exec [env] [service] [cmd]  Execute command in container"
    echo "  health [env]          Check service health"
    echo "  cleanup [env]         Clean up containers, networks, and volumes"
    echo "  help                  Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start development  Start development environment"
    echo "  $0 logs production beast-mode  Show logs for production beast-mode service"
    echo "  $0 exec development beast-mode bash  Open bash in development container"
    echo "  $0 health production  Check health of production services"
    echo
}

# Main script logic
main() {
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Parse command
    case "${1:-help}" in
        build)
            build "${2:-production}"
            ;;
        start)
            build "${2:-production}"
            start "${2:-production}"
            ;;
        stop)
            stop "${2:-production}"
            ;;
        restart)
            restart "${2:-production}"
            ;;
        logs)
            logs "${2:-production}" "${3:-}"
            ;;
        status)
            status "${2:-production}"
            ;;
        exec)
            exec_cmd "${2:-production}" "${3:-beast-mode}" "${@:4}"
            ;;
        health)
            health "${2:-production}"
            ;;
        cleanup)
            cleanup "${2:-production}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"