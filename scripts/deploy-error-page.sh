#!/bin/bash
#
# Cloudflare Error Page Deployment Wrapper
# ========================================
#
# Convenience script to set up and run the Playwright automation for
# deploying custom error pages to Cloudflare Dashboard.
#
# Usage:
#     ./deploy-error-page.sh --setup     # Install dependencies
#     ./deploy-error-page.sh --deploy    # Run deployment
#     ./deploy-error-page.sh --help      # Show help
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOMATION_SCRIPT="$SCRIPT_DIR/cloudflare-dashboard-automation.py"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements-automation.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🚀 Cloudflare Error Page Deployment${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

setup_dependencies() {
    print_header
    echo
    print_info "Setting up Playwright automation dependencies..."

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi

    print_info "Installing Python dependencies..."
    pip3 install -r "$REQUIREMENTS_FILE"

    print_info "Installing Playwright browsers..."
    python3 -m playwright install chromium

    print_success "Setup completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Ensure you have Cloudflare Pro plan for Custom Error Pages"
    echo "  2. Have your Cloudflare login credentials ready"
    echo "  3. Run: ./deploy-error-page.sh --deploy"
}

run_deployment() {
    print_header
    echo

    # Check if automation script exists
    if [[ ! -f "$AUTOMATION_SCRIPT" ]]; then
        print_error "Automation script not found: $AUTOMATION_SCRIPT"
        exit 1
    fi

    # Check if HTML file exists
    HTML_FILE="cloudflare/error-pages/1033-enhanced.html"
    if [[ ! -f "$HTML_FILE" ]]; then
        print_error "HTML file not found: $HTML_FILE"
        print_info "Make sure the error page HTML file exists"
        exit 1
    fi

    print_info "HTML file found: $HTML_FILE ($(wc -c < "$HTML_FILE" | xargs) bytes)"

    # Prompt for credentials
    echo
    read -p "Cloudflare email: " CLOUDFLARE_EMAIL

    if [[ -z "$CLOUDFLARE_EMAIL" ]]; then
        print_error "Email is required"
        exit 1
    fi

    # Ask about headless mode
    echo
    read -p "Run in headless mode? (y/N): " HEADLESS_MODE
    HEADLESS_FLAG=""
    if [[ "$HEADLESS_MODE" =~ ^[Yy]$ ]]; then
        HEADLESS_FLAG="--headless"
        print_info "Running in headless mode"
    else
        print_info "Running with browser UI (you can watch the automation)"
    fi

    echo
    print_info "Starting deployment automation..."
    print_warning "Make sure your tunnel is currently RUNNING for the deployment to be testable"

    # Run the automation
    python3 "$AUTOMATION_SCRIPT" \
        --email "$CLOUDFLARE_EMAIL" \
        --interactive \
        --zone "nkllon.com" \
        --error-code 1033 \
        --html-file "$HTML_FILE" \
        $HEADLESS_FLAG

    if [[ $? -eq 0 ]]; then
        echo
        print_success "Deployment automation completed!"
        echo
        print_info "Testing instructions:"
        echo "  1. Stop your tunnel: make tunnel-stop"
        echo "  2. Visit: https://observatory.nkllon.com"
        echo "  3. Verify custom error page appears"
        echo "  4. Restart tunnel: make tunnel-start"
    else
        print_error "Deployment failed"
        exit 1
    fi
}

show_help() {
    print_header
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  --setup     Install Playwright and dependencies"
    echo "  --deploy    Run the deployment automation"
    echo "  --help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 --setup"
    echo "  $0 --deploy"
    echo
    echo "Prerequisites:"
    echo "  • Cloudflare account with nkllon.com zone"
    echo "  • Pro plan or higher (for Custom Error Pages)"
    echo "  • Python 3.7+ installed"
    echo "  • Valid HTML error page file"
    echo
    echo "The automation will:"
    echo "  1. Open Cloudflare Dashboard in browser"
    echo "  2. Login with your credentials"
    echo "  3. Navigate to Custom Error Pages"
    echo "  4. Upload and deploy the 1033 error page"
    echo "  5. Verify deployment"
}

# Main script logic
case "${1:-}" in
    --setup)
        setup_dependencies
        ;;
    --deploy)
        run_deployment
        ;;
    --help)
        show_help
        ;;
    *)
        print_error "Invalid option or no option provided"
        echo
        show_help
        exit 1
        ;;
esac