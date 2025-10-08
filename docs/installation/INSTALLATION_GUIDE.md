# 🚀 Beast Mode AI Framework - Complete Installation Guide

> **Transform your AI development workflow in under 5 minutes with systematic, production-ready tooling**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/Framework-Beast%20Mode-orange)](src/beast_mode/)

This comprehensive guide will get you from zero to productive AI development with Beast Mode in minutes, not hours.

---

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM 
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows with WSL2
- **Network**: Internet connection for package downloads

### Recommended Requirements
- **Python**: 3.11+ (for best performance)
- **Memory**: 8GB RAM (16GB for heavy ML workloads)
- **Storage**: 10GB free space (includes examples and data)
- **OS**: Linux or macOS (native Docker support)
- **Network**: Stable broadband connection

### Optional Dependencies
- **Redis**: For AI Memory Palace functionality (persistent AI memory)
- **Docker**: For containerized deployment and examples
- **Jupyter**: For interactive notebooks and tutorials
- **Git**: For version control and updates

---

## 🎯 Quick Installation (Recommended)

**The fastest path to Beast Mode productivity:**

```bash
# 1. Clone the repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# 2. One-command setup (installs everything you need)
make install

# 3. Run the 2-minute demo
make quick-start
```

**🎉 That's it!** You now have:
- ✅ Complete Beast Mode framework installed
- ✅ Environment configured with secure defaults
- ✅ Working examples ready to run
- ✅ AI Memory Palace with persistent memory
- ✅ Production-ready observability and monitoring

**Next:** Jump to [Verify Installation](#-verify-installation) to confirm everything works.

---

## 📦 Detailed Installation Options

### Option 1: Standard Installation (Most Users)

Perfect for developers who want full control over their environment:

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Install Python dependencies
pip install -r requirements.txt

# Set up environment configuration
cp .env.example .env
# Edit .env with your settings (see Configuration section below)

# Verify installation
python examples/quick_start_demo.py
```

### Option 2: Virtual Environment (Recommended for Development)

Isolates Beast Mode dependencies from your system Python:

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Create and activate virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Verify installation
python examples/quick_start_demo.py
```

### Option 3: Docker Installation (Zero Dependencies)

Perfect for trying Beast Mode without installing anything on your system:

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Build and run with Docker
docker-compose up -d

# Run examples in container
docker-compose exec beast-mode python examples/quick_start_demo.py

# Access Jupyter notebooks
docker-compose exec beast-mode jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root

# Access at: http://localhost:8888
```

### Option 4: Development Installation (Contributors)

For contributors and advanced users who want to modify Beast Mode:

```bash
# Clone repository
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks (code quality)
pre-commit install

# Run tests to verify everything works
pytest tests/ -v

# Run quality checks
make lint
make test
```

---

## ⚙️ Environment Configuration

Beast Mode uses environment variables for secure configuration. **Never hardcode credentials in your code.**

### Quick Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim .env, code .env, etc.
```

### Required Configuration

Edit your `.env` file with these essential settings:

```bash
# =============================================================================
# BEAST MODE CONFIGURATION
# =============================================================================

# Application Settings
DEBUG=false
ENVIRONMENT=development
LOG_LEVEL=INFO

# =============================================================================
# AI MEMORY PALACE (Persistent AI Memory)
# =============================================================================
# Redis is required for AI Memory Palace functionality
# Install Redis: brew install redis (macOS) or apt install redis-server (Ubuntu)

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password_here

# =============================================================================
# API KEYS (Optional - for external integrations)
# =============================================================================
# Only needed if you plan to use external AI services

# OpenAI API (for GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API (for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# =============================================================================
# DATABASE CONFIGURATION (Optional)
# =============================================================================
# Only needed for advanced CMS and data persistence features

DATABASE_URL=postgresql://user:password@localhost:5432/beast_mode
DATABASE_PASSWORD=your_secure_database_password_here

# =============================================================================
# SECURITY SETTINGS
# =============================================================================
# These are automatically generated if not provided

JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

# Demo and testing passwords (change in production)
DEMO_PASSWORD=demo123
TEST_PASSWORD=test123
```

### Configuration Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEBUG` | Enable debug logging | `false` | No |
| `ENVIRONMENT` | Environment name | `development` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `REDIS_HOST` | Redis server host | `localhost` | Yes* |
| `REDIS_PORT` | Redis server port | `6379` | Yes* |
| `REDIS_PASSWORD` | Redis password | - | Yes* |
| `OPENAI_API_KEY` | OpenAI API key | - | No |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | No |
| `DATABASE_URL` | Database connection string | - | No |

*Required for AI Memory Palace functionality

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong passwords** for all credentials
3. **Rotate credentials regularly** in production
4. **Use environment-specific configurations** (dev/staging/prod)
5. **Validate all environment variables** are set before running

---

## 🔧 Dependency Installation

### Core Dependencies

Beast Mode automatically installs these when you run `pip install -r requirements.txt`:

- **Core Framework**: `pydantic`, `typer`, `rich`, `click`
- **AI/ML Libraries**: `transformers`, `torch`, `scikit-learn`, `numpy`
- **Data Processing**: `pandas`, `datasets`
- **Web Framework**: `fastapi`, `uvicorn`
- **Monitoring**: `prometheus-client`, `psutil`
- **Security**: `cryptography`
- **Testing**: `pytest`, `pytest-cov`, `coverage`

### Optional Dependencies

#### Redis (for AI Memory Palace)

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis

# Test Redis is working
redis-cli ping
# Should return: PONG
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis is working
redis-cli ping
# Should return: PONG
```

**Windows (using WSL2 or Docker):**
```bash
# Option 1: WSL2 (recommended)
sudo apt install redis-server
sudo service redis-server start

# Option 2: Docker
docker run -d -p 6379:6379 --name redis redis:alpine
```

#### Docker (for containerized deployment)

**macOS:**
```bash
# Install Docker Desktop
brew install --cask docker
# Start Docker Desktop from Applications
```

**Ubuntu:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Restart to apply group changes
sudo reboot
```

**Windows:**
```bash
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop
```

#### Jupyter (for interactive notebooks)

```bash
# Install Jupyter
pip install jupyter notebook jupyterlab

# Start Jupyter with Beast Mode examples
jupyter notebook examples/notebook/

# Or use JupyterLab (modern interface)
jupyter lab examples/notebook/
```

---

## ✅ Verify Installation

Run these verification steps to ensure everything is working correctly:

### 1. Quick Start Demo
```bash
python examples/quick_start_demo.py
```

**Expected Output:**
```
🐺 Beast Mode AI Framework - Quick Start Demo
✅ Core framework loaded successfully
✅ ReflectiveModule pattern working
✅ AI Memory Palace connected
✅ Health monitoring active
✅ Demo completed successfully!

🎉 Beast Mode is ready for systematic AI development!
```

### 2. Core Framework Test
```bash
python -c "
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.ai_memory_palace import MemoryPalace
print('✅ Beast Mode core imported successfully')
print('✅ AI Memory Palace available')
print('🐺 Ready for systematic AI development!')
"
```

### 3. Health Check
```bash
# Test all core components
python -c "
import sys
sys.path.append('.')

# Test core imports
try:
    from src.beast_mode.core import BeastModeFramework
    print('✅ Beast Mode Framework: OK')
except ImportError as e:
    print(f'❌ Beast Mode Framework: {e}')

# Test AI Memory Palace
try:
    from src.ai_memory_palace import MemoryPalace
    palace = MemoryPalace()
    print('✅ AI Memory Palace: OK')
except Exception as e:
    print(f'❌ AI Memory Palace: {e}')

# Test DAG Orchestration
try:
    from src.dag_orchestration import DAGOrchestrator
    print('✅ DAG Orchestration: OK')
except ImportError as e:
    print(f'❌ DAG Orchestration: {e}')

print('🎉 All core components verified!')
"
```

### 4. Run Test Suite (if installed in dev mode)
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 5. Interactive Notebooks
```bash
# Start Jupyter with Beast Mode examples
jupyter notebook examples/notebook/

# Available notebooks:
# - ai_memory_palace_demo.ipynb      # Persistent AI memory
# - dag_orchestration_demo.ipynb     # Task orchestration  
# - reflective_module_demo.ipynb     # Health monitoring
# - quick_start_tutorial.ipynb       # 5-minute tutorial
```

---

## 🚨 Troubleshooting

### Common Installation Issues

#### Issue: `ImportError: No module named 'src'`

**Cause:** Python can't find the Beast Mode modules.

**Solution:**
```bash
# Option 1: Set PYTHONPATH (temporary)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Option 2: Add to your shell profile (permanent)
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)"' >> ~/.bashrc
source ~/.bashrc

# Option 3: Install in development mode
pip install -e .
```

#### Issue: `Redis connection failed`

**Cause:** Redis server is not running or misconfigured.

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start Redis:
# macOS:
brew services start redis

# Ubuntu:
sudo systemctl start redis-server

# Check your .env file has correct Redis settings
grep REDIS .env
```

#### Issue: `Permission denied` errors

**Cause:** Insufficient file permissions.

**Solution:**
```bash
# Fix permissions for .env file
chmod 644 .env

# Fix permissions for scripts
chmod +x scripts/*.py

# If using Docker, check Docker permissions
sudo usermod -aG docker $USER
# Then logout and login again
```

#### Issue: `Python version not supported`

**Cause:** Using Python version < 3.9.

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.9+ if needed:
# macOS:
brew install python@3.11

# Ubuntu:
sudo apt install python3.11 python3.11-venv python3.11-dev

# Use specific Python version
python3.11 -m venv .venv
source .venv/bin/activate
```

#### Issue: `Docker container won't start`

**Cause:** Docker configuration or resource issues.

**Solution:**
```bash
# Check Docker is running
docker --version
docker ps

# Check Docker Compose configuration
docker-compose config

# View container logs
docker-compose logs beast-mode

# Restart Docker service
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop on macOS/Windows
```

#### Issue: `Jupyter notebook won't start`

**Cause:** Jupyter not installed or port conflicts.

**Solution:**
```bash
# Install Jupyter if missing
pip install jupyter notebook

# Start on different port if 8888 is busy
jupyter notebook --port=8889 examples/notebook/

# Check for port conflicts
lsof -i :8888  # macOS/Linux
netstat -an | grep 8888  # Windows
```

### Performance Issues

#### Issue: Slow startup times

**Solutions:**
```bash
# 1. Use SSD storage for better I/O performance
# 2. Increase available RAM
# 3. Use Python 3.11+ for better performance
# 4. Close unnecessary applications

# Check system resources
htop  # Linux/macOS
# Or Activity Monitor on macOS, Task Manager on Windows
```

#### Issue: High memory usage

**Solutions:**
```bash
# 1. Reduce batch sizes in ML examples
# 2. Use lighter ML models for development
# 3. Close unused Jupyter notebooks
# 4. Restart Python processes periodically

# Monitor memory usage
python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
print(f'Available: {psutil.virtual_memory().available / 1024**3:.1f} GB')
"
```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Most Beast Mode components provide detailed error messages
2. **Search documentation**: See [docs/](../README.md) for comprehensive guides
3. **Check existing issues**: Search [GitHub Issues](https://github.com/your-org/beast-mode-ai-framework/issues)
4. **Create a new issue** with:
   - Your operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce the issue
   - Your `.env` configuration (remove sensitive data)

---

## 🎯 Next Steps

Once installation is complete, here's your path to Beast Mode mastery:

### Immediate Next Steps (5 minutes)
1. **🚀 Run the Quick Start**: `python examples/quick_start_demo.py`
2. **📊 Check the Dashboard**: Open http://localhost:8888 (if using Docker)
3. **🧠 Test AI Memory**: Try the AI Memory Palace demo

### Learning Path (30 minutes)
1. **📚 Explore Notebooks**: `jupyter notebook examples/notebook/`
2. **🏗️ Build Your First Agent**: Follow the tutorial in `examples/notebook/quick_start_tutorial.ipynb`
3. **🔄 Try DAG Orchestration**: Run `examples/dag_orchestration_demo.py`

### Advanced Features (1 hour)
1. **🏛️ CMS Platform**: Explore content management capabilities
2. **📈 Monitoring Setup**: Configure Prometheus and Grafana
3. **🔒 Security Hardening**: Review security best practices

### Production Deployment (2 hours)
1. **🐳 Docker Deployment**: Set up containerized production environment
2. **☁️ Cloud Deployment**: Deploy to AWS, Azure, or GCP
3. **📊 Monitoring & Alerts**: Set up comprehensive monitoring

---

## 🔒 Security Considerations

### Environment Variables Security

**✅ DO:**
- Use environment variables for all sensitive data
- Keep `.env` files out of version control
- Use strong, unique passwords
- Rotate credentials regularly
- Validate all environment variables are set

**❌ DON'T:**
- Hardcode passwords or API keys in code
- Commit `.env` files to Git
- Use default or weak passwords
- Share credentials in plain text
- Skip environment variable validation

### Example Secure Configuration

```bash
# Generate secure passwords
python -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"

# Set proper file permissions
chmod 600 .env  # Only owner can read/write
```

---

## 📊 System Requirements by Use Case

### Basic Development (Learning & Prototyping)
- **CPU**: 2 cores, 2.4GHz+
- **RAM**: 4GB
- **Storage**: 2GB
- **Network**: Basic broadband
- **OS**: Any supported OS

### Production Development (Building Applications)
- **CPU**: 4 cores, 2.8GHz+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB SSD
- **Network**: Stable broadband
- **OS**: Linux or macOS preferred

### ML/AI Workloads (Heavy Processing)
- **CPU**: 8+ cores, 3.0GHz+
- **RAM**: 16GB+ (32GB for large models)
- **Storage**: 50GB+ SSD
- **GPU**: Optional but recommended for ML training
- **Network**: High-speed connection for model downloads

### Production Deployment (Serving Applications)
- **CPU**: 4+ cores per instance
- **RAM**: 8GB+ per instance
- **Storage**: 20GB+ SSD per instance
- **Network**: Low latency, high bandwidth
- **OS**: Linux (Ubuntu/CentOS recommended)

---

## 🎉 Installation Complete!

**Congratulations! You've successfully installed Beast Mode AI Framework! 🐺**

You now have access to:
- ✅ **Systematic AI Development**: No more "50 First Dates" problem
- ✅ **Mathematical Governance**: Impossible requirements detected automatically
- ✅ **Production-Ready Observability**: Complete visibility into your AI systems
- ✅ **ReflectiveModule Pattern**: Instant health monitoring and metrics
- ✅ **AI Memory Palace**: Persistent memory across AI sessions
- ✅ **DAG Orchestration**: Parallel task execution with dependency management

**Ready to transform your AI development workflow?**

🚀 **Start here**: `make quick-start`

📚 **Learn more**: [docs/guides/quick-start.md](../guides/quick-start.md)

🤝 **Get help**: [GitHub Discussions](https://github.com/your-org/beast-mode-ai-framework/discussions)

---

*Built with 🐺 by the Beast Mode community • [Star on GitHub](https://github.com/your-org/beast-mode-ai-framework) • [Read the Docs](../README.md)*