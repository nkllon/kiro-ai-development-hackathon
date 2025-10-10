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

BOOTSTRAP_STACK=false
INSTALL_DOCKER=false
NON_INTERACTIVE=false
DOCKER_AVAILABLE=false
COMPOSE_CMD=""
RUN_DEMO=false
INSTALL_DEV=false

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

show_help() {
    cat <<EOF
${PROJECT_NAME} Installer
Usage: ./install.sh [options]

Options:
  --bootstrap-stack        Start the Docker stack (docker compose up -d) after installation
  --install-docker         Attempt Docker/Compose installation when missing (Linux only, requires sudo)
  --non-interactive        Suppress guidance prompts; fail fast if prerequisites missing
  --with-demo              Run the quick start demo after installation completes
  -h, --help               Show this help message
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --bootstrap-stack|--with-stack|--start-stack)
                BOOTSTRAP_STACK=true
                ;;
            --install-docker)
                INSTALL_DOCKER=true
                ;;
            --non-interactive)
                NON_INTERACTIVE=true
                ;;
            --with-demo)
                RUN_DEMO=true
                ;;
            --dev)
                INSTALL_DEV=true
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_warning "Unknown option: $1"
                ;;
        esac
        shift
    done
}

# Ensure an environment file contains the default Redis password to prevent mismatches
ensure_redis_password_entry() {
    local env_file="$1"
    if [[ -z "$env_file" ]] || [[ ! -f "$env_file" ]]; then
        return 0
    fi

    "$PYTHON_CMD" - "$env_file" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
content = path.read_text().splitlines()
updated = False

for idx, line in enumerate(content):
    if line.startswith("REDIS_PASSWORD="):
        if line.strip() == "REDIS_PASSWORD=":
            content[idx] = "REDIS_PASSWORD=beastmode2025"
            updated = True
        break
else:
    content.append("REDIS_PASSWORD=beastmode2025")
    updated = True

if updated:
    path.write_text("\n".join(content) + ("\n" if content and content[-1] else ""))
PY
}

ensure_docker_available() {
    if command_exists docker; then
        DOCKER_AVAILABLE=true
        log_success "Docker detected: $(docker --version | head -n1)"
        return 0
    fi

    if [[ "$INSTALL_DOCKER" == true ]]; then
        case $OS in
            "debian")
                log_info "Installing Docker (requires sudo)..."
                sudo apt update
                sudo apt install -y ca-certificates curl gnupg lsb-release
                sudo install -m 0755 -d /etc/apt/keyrings
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                sudo chmod a+r /etc/apt/keyrings/docker.gpg
                echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
                sudo apt update
                sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
                sudo usermod -aG docker "$USER" || true
                sudo systemctl enable docker
                sudo systemctl start docker
                DOCKER_AVAILABLE=true
                log_success "Docker installed successfully."
                ;;
            "redhat")
                log_info "Installing Docker (requires sudo)..."
                sudo yum install -y yum-utils
                sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                sudo systemctl enable docker
                sudo systemctl start docker
                sudo usermod -aG docker "$USER" || true
                DOCKER_AVAILABLE=true
                log_success "Docker installed successfully."
                ;;
            "arch")
                log_info "Installing Docker (requires sudo)..."
                sudo pacman -Sy --noconfirm docker docker-compose
                sudo systemctl enable docker
                sudo systemctl start docker
                sudo usermod -aG docker "$USER" || true
                DOCKER_AVAILABLE=true
                log_success "Docker installed successfully."
                ;;
            *)
                log_warning "Automatic Docker installation is not supported on this OS. Please install Docker manually."
                ;;
        esac
    fi

    if [[ "$DOCKER_AVAILABLE" == false ]]; then
        log_warning "Docker not detected. Install Docker/Compose to run containerized services."
        if [[ "$NON_INTERACTIVE" == false ]]; then
            log_info "Reference: https://docs.docker.com/engine/install/"
        fi
    fi
}

ensure_compose_command() {
    if [[ "$DOCKER_AVAILABLE" == false ]]; then
        return 0
    fi

    if docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    elif command_exists docker-compose; then
        COMPOSE_CMD="docker-compose"
    else
        log_warning "Docker Compose not detected. Install the Compose plugin or docker-compose binary."
    fi
}

bootstrap_observatory_stack() {
    if [[ "$BOOTSTRAP_STACK" != true ]]; then
        return 0
    fi

    if [[ "$DOCKER_AVAILABLE" != true ]] || [[ -z "$COMPOSE_CMD" ]]; then
        log_error "Cannot bootstrap stack: Docker/Compose unavailable."
        return 0
    fi

    log_info "Starting Observatory stack via Docker..."
    $COMPOSE_CMD up -d --build
    log_success "Observatory stack started."
}

install_dev_dependencies() {
    if [[ "$INSTALL_DEV" != true ]]; then
        return 0
    fi

    log_info "Installing development dependencies..."
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source .venv/bin/activate
    fi
    pip install -r requirements-dev.txt
    log_success "Development dependencies installed."
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
    
    # Load home-level environment file if present so that POINT installs inherit passwords
    if [[ -f "$HOME/.env" ]]; then
        # shellcheck disable=SC1090
        source "$HOME/.env"
    fi

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
# Default Redis password matches Vonnegut deployment
REDIS_PASSWORD=beastmode2025

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
    
    # Ensure Redis password is present locally
    if [[ -f ".env" ]]; then
        ensure_redis_password_entry ".env"
    fi

    # Copy .env to home directory for global access
    if [[ -f ".env" ]] && [[ ! -f "$HOME/.env" ]]; then
        log_info "Copying .env to home directory for global access..."
        cp .env "$HOME/.env"
    fi

    # Ensure Redis password is present in the home-level environment file
    if [[ -f "$HOME/.env" ]]; then
        ensure_redis_password_entry "$HOME/.env"
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
    parse_args "$@"
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
    ensure_docker_available
    ensure_compose_command
    bootstrap_observatory_stack
    install_dev_dependencies
    
    # Optional: run quick start
    if [[ "$RUN_DEMO" == true ]]; then
        run_quick_start
    fi
    
    print_summary
}

main "$@"
