#!/bin/bash
# Beast Mode AI Development Framework - Installation Script
# Supports: macOS, Linux (Ubuntu/Debian, CentOS/RHEL, Arch)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.9"
REDIS_DEFAULT_PORT="6379"
PROJECT_NAME="Beast Mode AI Development Framework"

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

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        PACKAGE_MANAGER="apt"
    elif [[ -f /etc/redhat-release ]]; then
        OS="redhat"
        PACKAGE_MANAGER="yum"
    elif [[ -f /etc/arch-release ]]; then
        OS="arch"
        PACKAGE_MANAGER="pacman"
    else
        OS="unknown"
        PACKAGE_MANAGER="unknown"
    fi
    
    log_info "Detected OS: $OS with package manager: $PACKAGE_MANAGER"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    log_info "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        log_error "Python is not installed. Please install Python $PYTHON_MIN_VERSION or later."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 9 ]]; then
        log_error "Python $PYTHON_VERSION is installed, but $PYTHON_MIN_VERSION or later is required."
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION is compatible"
}

# Install system dependencies
install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    case $OS in
        "macos")
            if ! command_exists brew; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            # Install Redis if not present
            if ! command_exists redis-server; then
                log_info "Installing Redis..."
                brew install redis
            fi
            
            # Install Git if not present
            if ! command_exists git; then
                log_info "Installing Git..."
                brew install git
            fi
            ;;
            
        "debian")
            log_info "Updating package lists..."
            sudo apt update
            
            # Install essential packages
            sudo apt install -y python3-pip python3-venv python3-dev build-essential
            
            # Install Redis if not present
            if ! command_exists redis-server; then
                log_info "Installing Redis..."
                sudo apt install -y redis-server
            fi
            
            # Install Git if not present
            if ! command_exists git; then
                log_info "Installing Git..."
                sudo apt install -y git
            fi
            ;;
            
        "redhat")
            # Install essential packages
            sudo yum install -y python3-pip python3-devel gcc gcc-c++ make
            
            # Install Redis if not present
            if ! command_exists redis-server; then
                log_info "Installing Redis..."
                sudo yum install -y redis
            fi
            
            # Install Git if not present
            if ! command_exists git; then
                log_info "Installing Git..."
                sudo yum install -y git
            fi
            ;;
            
        "arch")
            # Install essential packages
            sudo pacman -S --noconfirm python-pip base-devel
            
            # Install Redis if not present
            if ! command_exists redis-server; then
                log_info "Installing Redis..."
                sudo pacman -S --noconfirm redis
            fi
            
            # Install Git if not present
            if ! command_exists git; then
                log_info "Installing Git..."
                sudo pacman -S --noconfirm git
            fi
            ;;
            
        *)
            log_warning "Unknown OS. Please install Python 3.9+, pip, Redis, and Git manually."
            ;;
    esac
}

# Create virtual environment
create_virtual_environment() {
    log_info "Creating Python virtual environment..."
    
    if [[ -d ".venv" ]]; then
        log_warning "Virtual environment already exists. Removing old one..."
        rm -rf .venv
    fi
    
    $PYTHON_CMD -m venv .venv
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    log_success "Virtual environment created and activated"
}

# Install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Ensure we're in the virtual environment
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source .venv/bin/activate
    fi
    
    # Install core dependencies
    log_info "Installing core dependencies..."
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Configure environment
configure_environment() {
    log_info "Configuring environment..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        log_info "Creating .env file from template..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
        else
            # Create basic .env file
            cat > .env << EOF
# Beast Mode AI Development Framework Configuration
# Copy this file to ~/.env for global configuration

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Keys (set your actual keys)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Environment
ENVIRONMENT=development
DEBUG=true

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Observatory
OBSERVATORY_PORT=8080
OBSERVATORY_HOST=localhost
EOF
        fi
        
        log_warning "Please edit .env file and set your API keys and configuration"
    fi
    
    # Copy .env to home directory for global access
    if [[ -f ".env" ]] && [[ ! -f "$HOME/.env" ]]; then
        log_info "Copying .env to home directory for global access..."
        cp .env "$HOME/.env"
    fi
}

# Start Redis service
start_redis_service() {
    log_info "Starting Redis service..."
    
    case $OS in
        "macos")
            if ! pgrep -x "redis-server" > /dev/null; then
                brew services start redis
                log_success "Redis service started"
            else
                log_info "Redis service is already running"
            fi
            ;;
            
        "debian"|"redhat")
            if ! pgrep -x "redis-server" > /dev/null; then
                sudo systemctl start redis
                sudo systemctl enable redis
                log_success "Redis service started and enabled"
            else
                log_info "Redis service is already running"
            fi
            ;;
            
        "arch")
            if ! pgrep -x "redis-server" > /dev/null; then
                sudo systemctl start redis
                sudo systemctl enable redis
                log_success "Redis service started and enabled"
            else
                log_info "Redis service is already running"
            fi
            ;;
            
        *)
            log_warning "Please start Redis service manually"
            ;;
    esac
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    # Check if virtual environment is active
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source .venv/bin/activate
    fi
    
    # Test Python imports
    log_info "Testing core imports..."
    $PYTHON_CMD -c "
import sys
import pydantic
import fastapi
import redis
import requests
import cryptography
print('✅ All core imports successful')
print(f'Python version: {sys.version}')
print(f'Virtual environment: {sys.prefix}')
"
    
    # Test Redis connection
    log_info "Testing Redis connection..."
    $PYTHON_CMD -c "
import redis
import os
try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD', '') or None,
        decode_responses=True
    )
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'⚠️  Redis connection failed: {e}')
    print('Please check Redis service and configuration')
"
    
    log_success "Installation validation complete"
}

# Run quick start example
run_quick_start() {
    log_info "Running quick start example..."
    
    if [[ -f "examples/quick_start.py" ]]; then
        $PYTHON_CMD examples/quick_start.py
    elif [[ -f "examples/demos/quick_start_demo.py" ]]; then
        $PYTHON_CMD examples/demos/quick_start_demo.py
    else
        log_warning "Quick start example not found. Skipping..."
    fi
}

# Print installation summary
print_summary() {
    echo
    log_success "🎉 $PROJECT_NAME installation complete!"
    echo
    echo "📋 Installation Summary:"
    echo "  ✅ Python $PYTHON_VERSION"
    echo "  ✅ Virtual environment: .venv"
    echo "  ✅ Dependencies installed"
    echo "  ✅ Redis service configured"
    echo "  ✅ Environment configured"
    echo
    echo "🚀 Next Steps:"
    echo "  1. Activate virtual environment: source .venv/bin/activate"
    echo "  2. Edit .env file with your API keys"
    echo "  3. Run quick start: python examples/demos/quick_start_demo.py"
    echo "  4. View documentation: docs/README.md"
    echo
    echo "🔧 Development Setup:"
    echo "  • Install dev dependencies: pip install -r requirements-dev.txt"
    echo "  • Run tests: pytest"
    echo "  • Format code: black src/"
    echo "  • Lint code: ruff check src/"
    echo
    echo "📚 Documentation:"
    echo "  • Installation guide: docs/installation/INSTALLATION_GUIDE.md"
    echo "  • API reference: docs/api/README.md"
    echo "  • Examples: examples/README.md"
    echo
}

# Main installation process
main() {
    echo "🚀 Installing $PROJECT_NAME..."
    echo
    
    # Check if we're in the project directory
    if [[ ! -f "requirements.txt" ]]; then
        log_error "requirements.txt not found. Please run this script from the project root directory."
        exit 1
    fi
    
    detect_os
    check_python_version
    install_system_dependencies
    create_virtual_environment
    install_python_dependencies
    configure_environment
    start_redis_service
    validate_installation
    
    # Optional: run quick start
    if [[ "$1" == "--with-demo" ]]; then
        run_quick_start
    fi
    
    print_summary
}

# Handle command line arguments
case "$1" in
    "--help"|"-h")
        echo "Beast Mode AI Development Framework - Installation Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --with-demo       Run quick start demo after installation"
        echo "  --dev             Install development dependencies"
        echo
        echo "Examples:"
        echo "  $0                Install core framework"
        echo "  $0 --with-demo    Install and run demo"
        echo "  $0 --dev          Install with development tools"
        echo
        exit 0
        ;;
    "--dev")
        # Install development dependencies after main installation
        main
        log_info "Installing development dependencies..."
        source .venv/bin/activate
        pip install -r requirements-dev.txt
        log_success "Development dependencies installed"
        ;;
    *)
        main "$@"
        ;;
esac