#!/bin/bash
"""
Setup Local DNS for Kiro Development Stack
==========================================

This script sets up local DNS entries for easy access to development services.
Instead of remembering port numbers, you can use friendly hostnames.

Usage:
  ./scripts/setup_local_dns.sh install    # Add DNS entries
  ./scripts/setup_local_dns.sh remove     # Remove DNS entries
  ./scripts/setup_local_dns.sh show       # Show current services
  ./scripts/setup_local_dns.sh test       # Test DNS resolution
"""

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DNS_MANAGER="$SCRIPT_DIR/dynamic_dns_manager.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🌐 Kiro Local DNS Setup${NC}"
    echo "=========================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    # Check if Python script exists
    if [[ ! -f "$DNS_MANAGER" ]]; then
        print_error "DNS manager script not found: $DNS_MANAGER"
        exit 1
    fi
    
    # Check if running services
    if ! docker ps | grep -q "local-"; then
        print_warning "No local development services detected"
        print_warning "Run 'docker-compose -f docker-compose.local-dev.yml up -d' first"
    fi
}

install_dns() {
    print_header
    echo "Installing local DNS entries..."
    echo
    
    # Show what will be installed
    echo "📋 Services to be registered:"
    python "$DNS_MANAGER" show
    echo
    
    # Ask for confirmation
    read -p "Install these DNS entries? (requires sudo) [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 Installing DNS entries..."
        if sudo python "$DNS_MANAGER" update; then
            print_success "DNS entries installed successfully!"
            echo
            echo "🎉 You can now access services using:"
            echo "   • Grafana:    http://grafana.kiro.local:3000"
            echo "   • Prometheus: http://prometheus.kiro.local:9090"
            echo "   • Jaeger:     http://jaeger.kiro.local:16686"
            echo "   • Monitoring: http://monitoring.kiro.local:8000"
            echo
            echo "💡 Tip: Bookmark these URLs for easy access!"
        else
            print_error "Failed to install DNS entries"
            exit 1
        fi
    else
        echo "Installation cancelled."
    fi
}

remove_dns() {
    print_header
    echo "Removing local DNS entries..."
    echo
    
    read -p "Remove all Kiro DNS entries? (requires sudo) [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if sudo python "$DNS_MANAGER" remove; then
            print_success "DNS entries removed successfully!"
        else
            print_error "Failed to remove DNS entries"
            exit 1
        fi
    else
        echo "Removal cancelled."
    fi
}

show_services() {
    print_header
    python "$DNS_MANAGER" show
    echo
    
    # Show current /etc/hosts entries
    if grep -q "kiro.local" /etc/hosts 2>/dev/null; then
        echo "📝 Current DNS entries in /etc/hosts:"
        grep "kiro.local" /etc/hosts | sed 's/^/   /'
    else
        print_warning "No Kiro DNS entries found in /etc/hosts"
        echo "   Run '$0 install' to add them"
    fi
}

test_dns() {
    print_header
    echo "Testing DNS resolution..."
    echo
    
    # Test with ping (faster than nslookup)
    services=("grafana.kiro.local" "prometheus.kiro.local" "jaeger.kiro.local")
    
    for service in "${services[@]}"; do
        if ping -c 1 -W 1000 "$service" >/dev/null 2>&1; then
            print_success "$service resolves correctly"
        else
            print_error "$service does not resolve"
        fi
    done
    
    echo
    echo "🌐 Testing HTTP connectivity..."
    
    # Test HTTP endpoints
    endpoints=(
        "http://grafana.kiro.local:3000/api/health"
        "http://prometheus.kiro.local:9090/api/v1/status/buildinfo"
        "http://jaeger.kiro.local:16686/api/services"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -s --connect-timeout 2 "$endpoint" >/dev/null 2>&1; then
            print_success "$endpoint is accessible"
        else
            print_warning "$endpoint is not accessible (service may be down)"
        fi
    done
}

show_help() {
    echo "Kiro Local DNS Setup"
    echo "===================="
    echo
    echo "Usage: $0 <command>"
    echo
    echo "Commands:"
    echo "  install    Install DNS entries for local services"
    echo "  remove     Remove all Kiro DNS entries"
    echo "  show       Show discovered services"
    echo "  test       Test DNS resolution and connectivity"
    echo "  help       Show this help message"
    echo
    echo "Examples:"
    echo "  $0 install    # Add grafana.kiro.local, prometheus.kiro.local, etc."
    echo "  $0 show       # List all discovered services"
    echo "  $0 test       # Test that DNS entries work"
    echo "  $0 remove     # Clean up all DNS entries"
}

# Main script logic
case "${1:-help}" in
    install)
        check_requirements
        install_dns
        ;;
    remove)
        remove_dns
        ;;
    show)
        check_requirements
        show_services
        ;;
    test)
        test_dns
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac