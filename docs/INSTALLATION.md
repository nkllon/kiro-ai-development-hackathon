# 🛠️ Beast Mode Installation Guide

This comprehensive guide will help you install and configure the Beast Mode AI Development Framework on your system.

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows with WSL2

### Recommended Requirements
- **Python**: 3.11 or higher
- **Memory**: 8GB RAM or more
- **Storage**: 5GB free space
- **OS**: Linux (Ubuntu 20.04+) or macOS (10.15+)

### Optional Dependencies
- **Docker**: For containerized deployment
- **Redis**: For AI Memory Palace functionality
- **PostgreSQL**: For advanced data persistence
- **Jupyter**: For interactive notebooks

---

## 🚀 Quick Installation (Recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/kiro-ai-development-hackathon.git
cd kiro-ai-development-hackathon
```

### Step 2: Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using conda
conda create -n beastmode python=3.11
conda activate beastmode
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration (see Configuration section below)
```

### Step 5: Verify Installation
```bash
python examples/simple_beast_agent.py
```

**Expected Output:**
```
🐺 Beast Mode Agent Starting...
✅ ReflectiveModule initialized
✅ Health monitoring active
✅ Metrics collection started
🎯 Agent ready for systematic AI development!
```

---

## 🐳 Docker Installation

### Prerequisites
- Docker 20.10+ installed
- Docker Compose 2.0+ installed

### Quick Docker Setup
```bash
# Clone repository
git clone https://github.com/your-org/kiro-ai-development-hackathon.git
cd kiro-ai-development-hackathon

# Build and start services
docker-compose up -d

# Verify installation
docker-compose exec app python examples/simple_beast_agent.py

# Access Jupyter notebooks
docker-compose exec app jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
```

### Docker Services
The Docker setup includes:
- **app**: Main Beast Mode application
- **redis**: For AI Memory Palace
- **prometheus**: For metrics collection
- **grafana**: For monitoring dashboards

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### Core Configuration
```bash
# Application Settings
DEBUG=false
ENVIRONMENT=development
LOG_LEVEL=INFO

# Performance Settings
MAX_WORKERS=4
TIMEOUT_SECONDS=30
```

#### AI Memory Palace (Optional)
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password_here
REDIS_DB=0
```

#### External API Keys (Optional)
```bash
# AI Service APIs
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Cloud Services
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
```

#### Database Configuration (Optional)
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/beastmode
DATABASE_PASSWORD=your_db_password_here
```

### Configuration Validation

Verify your configuration:
```bash
python -c "from src.beast_mode.core import validate_config; validate_config()"
```

---

## 🔧 Advanced Installation Options

### Development Installation

For contributors and advanced users:

```bash
# Clone with development dependencies
git clone https://github.com/your-org/kiro-ai-development-hackathon.git
cd kiro-ai-development-hackathon

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest tests/
```

### Production Installation

For production deployments:

```bash
# Install with production optimizations
pip install -r requirements.txt --no-dev

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Configure logging
export LOG_LEVEL=WARNING
export LOG_FILE=/var/log/beastmode/app.log

# Start with production server
gunicorn src.beast_mode.app:app --workers 4 --bind 0.0.0.0:8000
```

### Custom Installation

For specific use cases:

```bash
# Minimal installation (core only)
pip install -r requirements-minimal.txt

# AI-focused installation
pip install -r requirements-ai.txt

# CMS-focused installation  
pip install -r requirements-cms.txt

# Full installation with all optional dependencies
pip install -r requirements-full.txt
```

---

## 🧪 Verification & Testing

### Basic Verification

1. **Import Test**:
```bash
python -c "from src.beast_mode import ReflectiveModule; print('✅ Import successful')"
```

2. **Health Check**:
```bash
python -c "
from src.beast_mode.core import HealthChecker
health = HealthChecker()
status = health.check_all()
print(f'Health Status: {status}')
"
```

3. **Example Execution**:
```bash
python examples/simple_beast_agent.py
```

### Comprehensive Testing

Run the full test suite:
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### Interactive Testing

Launch Jupyter notebooks for interactive testing:
```bash
jupyter notebook examples/notebook/

# Available test notebooks:
# - basic_functionality_test.ipynb
# - ai_memory_palace_test.ipynb  
# - dag_orchestration_test.ipynb
# - performance_benchmark.ipynb
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'src'
# Solution: Ensure you're in the project root directory
cd /path/to/kiro-ai-development-hackathon
python examples/simple_beast_agent.py
```

#### 2. Redis Connection Issues
```bash
# Error: ConnectionError: Error connecting to Redis
# Solution: Start Redis server or update configuration
redis-server  # Start Redis locally
# Or update REDIS_HOST in .env file
```

#### 3. Permission Errors
```bash
# Error: PermissionError: [Errno 13] Permission denied
# Solution: Check file permissions and virtual environment
chmod +x scripts/*.sh
source .venv/bin/activate
```

#### 4. Memory Issues
```bash
# Error: MemoryError or slow performance
# Solution: Increase available memory or reduce batch sizes
export BEAST_MODE_MAX_MEMORY=2048  # MB
export BEAST_MODE_BATCH_SIZE=32
```

### Diagnostic Tools

#### System Information
```bash
python scripts/system_diagnostics.py
```

#### Configuration Check
```bash
python scripts/config_validator.py
```

#### Performance Benchmark
```bash
python scripts/performance_benchmark.py
```

### Getting Help

If you encounter issues:

1. **Check Logs**: Look in `logs/` directory for error details
2. **Run Diagnostics**: Use the diagnostic tools above
3. **Search Issues**: Check [GitHub Issues](https://github.com/your-org/kiro-ai-development-hackathon/issues)
4. **Ask Community**: Post in [GitHub Discussions](https://github.com/your-org/kiro-ai-development-hackathon/discussions)
5. **Contact Support**: Email [support@beastmode.dev](mailto:support@beastmode.dev)

---

## 🚀 Next Steps

After successful installation:

1. **📚 Read the [User Guide](USER_GUIDE.md)** - Learn Beast Mode concepts
2. **🎓 Try the [Quick Start Tutorial](QUICK_START.md)** - 15-minute hands-on introduction  
3. **🔬 Explore [Examples](../examples/)** - Working code examples
4. **📖 Browse [API Documentation](api/)** - Detailed API reference
5. **🏗️ Build Your First Agent** - Create your own Beast Mode application

### Recommended Learning Path

1. **Simple Beast Agent** (`examples/simple_beast_agent.py`)
2. **AI Memory Palace Demo** (`examples/notebook/ai_memory_palace_demo.ipynb`)
3. **DAG Orchestration Tutorial** (`examples/notebook/dag_orchestration_demo.ipynb`)
4. **Complete Use Cases** (`examples/notebook/5D2_Complete_Use_Cases_Exploration.ipynb`)

---

## 📊 Installation Verification Checklist

Use this checklist to ensure your installation is complete:

- [ ] **Python 3.9+** installed and accessible
- [ ] **Virtual environment** created and activated
- [ ] **Dependencies** installed without errors
- [ ] **Environment variables** configured in `.env`
- [ ] **Basic import** test passes
- [ ] **Simple example** runs successfully
- [ ] **Health check** returns positive status
- [ ] **Tests** pass (at least basic unit tests)
- [ ] **Jupyter notebooks** accessible (if using)
- [ ] **Documentation** accessible locally

### Installation Success Indicators

✅ **Successful Installation Signs:**
- No import errors when running examples
- Health check returns "healthy" status
- Examples complete in under 30 seconds
- Jupyter notebooks load without errors
- Tests pass with >90% success rate

❌ **Installation Issues Signs:**
- Import errors or module not found
- Health check returns "unhealthy" status  
- Examples timeout or crash
- Jupyter notebooks fail to load
- Tests fail with <50% success rate

---

## 🔄 Updating Beast Mode

### Regular Updates
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migration scripts (if any)
python scripts/migrate_config.py

# Verify update
python examples/simple_beast_agent.py
```

### Version Management
```bash
# Check current version
python -c "from src.beast_mode import __version__; print(__version__)"

# List available versions
git tag -l

# Switch to specific version
git checkout v1.2.0
pip install -r requirements.txt
```

---

<div align="center">

**🐺 Beast Mode Installation Complete!**

*Ready for systematic AI development with mathematical governance*

[📖 User Guide](USER_GUIDE.md) • [🎓 Quick Start](QUICK_START.md) • [🔬 Examples](../examples/)

</div>